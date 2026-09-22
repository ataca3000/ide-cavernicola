#!/usr/bin/env python3
"""
IDC Cognitive Queries: Architectural Analytics & Codebase Telemetry over SQLite
Executes analytical SQL queries over memory/idc.db to extract structural insights,
hotspots, technical debt distribution, and modular complexity.
Authored by Luis Felipe Durán Salinas (ATACA3000 / Brecha Soluciones DS).
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DB_PATH = Path("memory/idc.db")


class IDCAnalytics:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Base de datos {db_path} no encontrada. Ejecuta 'python scripts/idc_ingest.py' primero."
            )
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def close(self):
        self.conn.close()

    # --- Query 1: Cognitive Inventory Summary ---
    def get_inventory_summary(self) -> Dict[str, Any]:
        """Returns macro counts of detected symbols, debt, and file types."""
        sql = """
        SELECT 
            COUNT(DISTINCT file_path) AS total_files,
            SUM(CASE WHEN event_type = 'class_detected' THEN 1 ELSE 0 END) AS classes,
            SUM(CASE WHEN event_type = 'function_detected' THEN 1 ELSE 0 END) AS functions,
            SUM(CASE WHEN event_type = 'import_detected' THEN 1 ELSE 0 END) AS imports,
            SUM(CASE WHEN event_type LIKE '%_detected' AND event_type NOT IN ('class_detected', 'function_detected', 'import_detected') THEN 1 ELSE 0 END) AS tech_debt,
            SUM(occurrences) AS total_observations
        FROM episodes;
        """
        row = self.conn.execute(sql).fetchone()
        return dict(row)

    # --- Query 2: Technical Debt Breakdown by Severity ---
    def get_technical_debt_breakdown(self) -> List[Dict[str, Any]]:
        """Returns technical debt counts grouped by event type and severity."""
        sql = """
        SELECT 
            event_type,
            severity,
            COUNT(*) AS unique_items,
            SUM(occurrences) AS total_occurrences
        FROM episodes
        WHERE event_type IN ('todo_detected', 'fixme_detected', 'hack_detected', 'bug_detected', 'deprecated_detected')
        GROUP BY event_type, severity
        ORDER BY severity DESC, unique_items DESC;
        """
        rows = self.conn.execute(sql).fetchall()
        return [dict(r) for r in rows]

    # --- Query 3: Top Hotspot Files with Technical Debt ---
    def get_top_debt_hotspots(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Identifies files with the highest concentration of technical debt."""
        sql = """
        SELECT 
            file_path,
            COUNT(*) AS debt_count,
            GROUP_CONCAT(DISTINCT event_type) AS debt_types
        FROM episodes
        WHERE event_type IN ('todo_detected', 'fixme_detected', 'hack_detected', 'bug_detected', 'deprecated_detected')
        GROUP BY file_path
        ORDER BY debt_count DESC
        LIMIT ?;
        """
        rows = self.conn.execute(sql, (limit,)).fetchall()
        return [dict(r) for r in rows]

    # --- Query 4: Architectural Complexity (Top Modules by Classes & Functions) ---
    def get_most_complex_modules(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Finds modules with the highest number of classes and functions."""
        sql = """
        SELECT 
            file_path,
            SUM(CASE WHEN event_type = 'class_detected' THEN 1 ELSE 0 END) AS classes_count,
            SUM(CASE WHEN event_type = 'function_detected' THEN 1 ELSE 0 END) AS functions_count,
            COUNT(*) AS total_symbols
        FROM episodes
        WHERE event_type IN ('class_detected', 'function_detected')
        GROUP BY file_path
        ORDER BY total_symbols DESC
        LIMIT ?;
        """
        rows = self.conn.execute(sql, (limit,)).fetchall()
        return [dict(r) for r in rows]

    # --- Query 5: Internal Dependency Map ---
    def get_most_imported_internal_symbols(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Finds internal symbols/modules most frequently imported across the codebase."""
        sql = """
        SELECT 
            symbol_name,
            COUNT(DISTINCT file_path) AS imported_by_file_count
        FROM episodes
        WHERE event_type = 'import_detected'
          AND (symbol_name LIKE 'core.%' OR symbol_name LIKE 'contracts.%' OR symbol_name LIKE 'plugins.%')
        GROUP BY symbol_name
        ORDER BY imported_by_file_count DESC
        LIMIT ?;
        """
        rows = self.conn.execute(sql, (limit,)).fetchall()
        return [dict(r) for r in rows]


def print_analytics_report(analytics: IDCAnalytics):
    print("=" * 70)
    print("   IDC COGNITIVE ANALYTICS: METRICAS ARQUITECTONICAS DEL REPOSITORIO")
    print("=" * 70)

    # 1. Inventory Summary
    inv = analytics.get_inventory_summary()
    print("\n[1. INVENTARIO SEMANTICO GLOBAL]:")
    print(f"  * Archivos Indexados:         {inv.get('total_files', 0)}")
    print(f"  * Clases Detectadas:          {inv.get('classes', 0)}")
    print(f"  * Funciones / Metodos:        {inv.get('functions', 0)}")
    print(f"  * Declaraciones de Import:    {inv.get('imports', 0)}")
    print(f"  * Puntos de Deuda Tecnica:    {inv.get('tech_debt', 0)}")
    print(f"  * Observaciones Acumuladas:   {inv.get('total_observations', 0)}")

    # 2. Technical Debt Breakdown
    print("\n[2. DESGLOSE DE DEUDA TECNICA POR SEVERIDAD]:")
    debts = analytics.get_technical_debt_breakdown()
    if not debts:
        print("  (No se detecto deuda tecnica)")
    else:
        for d in debts:
            print(f"  * [{d['severity'].upper()}] {d['event_type']}: {d['unique_items']} items ({d['total_occurrences']} obs)")

    # 3. Hotspots
    print("\n[3. TOP PUNTOS CRITICOS DE DEUDA TECNICA]:")
    hotspots = analytics.get_top_debt_hotspots(5)
    for h in hotspots:
        print(f"  * {h['file_path']} -> {h['debt_count']} items ({h['debt_types']})")

    # 4. Complexity
    print("\n[4. MODULOS CON MAYOR DENSIDAD ARQUITECTONICA]:")
    complex_mods = analytics.get_most_complex_modules(6)
    for m in complex_mods:
        print(f"  * {m['file_path']}: {m['classes_count']} clases, {m['functions_count']} funciones (Total: {m['total_symbols']})")

    # 5. Dependency Hubs
    print("\n[5. COMPONENTES INTERNOS MAS IMPORTADOS (HUBS ARQUITECTONICOS)]:")
    hubs = analytics.get_most_imported_internal_symbols(6)
    for hub in hubs:
        print(f"  * {hub['symbol_name']} -> Importado en {hub['imported_by_file_count']} archivos")

    print("\n" + "=" * 70 + "\n")


def main():
    try:
        analytics = IDCAnalytics()
        print_analytics_report(analytics)
        analytics.close()
    except Exception as e:
        print(f"Error ejecutando analitica: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
