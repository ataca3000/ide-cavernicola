#!/usr/bin/env python3
"""
IDC Ingest: Cognitive Repository Sensor & Episodic SQLite Database
Parses Python, JavaScript, TypeScript, and architectural patterns using native AST
and ast-grep (sg) with strict SQLite deduplication and occurrence tracking.
Authored by Luis Felipe Durán Salinas (ATACA3000 / Brecha Soluciones DS).
"""

import ast
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DB_PATH = Path("memory/idc.db")
ROOT = Path(".")
IGNORE_DIRS = {".venv", "venv", "env", "__pycache__", ".git", "build", "dist", ".pytest_cache", "node_modules"}


def get_current_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_database(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """
    Initializes SQLite database with deduplication constraints and indexing.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))

    # Enable WAL mode for high concurrency and speed
    conn.execute("PRAGMA journal_mode=WAL;")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS episodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        file_path TEXT NOT NULL,
        symbol_name TEXT,
        line_number INTEGER,
        severity TEXT DEFAULT 'low',
        metadata_json TEXT,
        occurrences INTEGER DEFAULT 1,
        last_seen_at TEXT NOT NULL,
        UNIQUE(event_type, file_path, line_number, symbol_name)
    );
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_episodes_type ON episodes(event_type);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_episodes_file ON episodes(file_path);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_episodes_severity ON episodes(severity);")
    conn.commit()
    return conn


def record_episode(
    conn: sqlite3.Connection,
    event_type: str,
    file_path: str,
    symbol_name: Optional[str] = None,
    line_number: Optional[int] = None,
    severity: str = "low",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Inserts or updates an episode with strict deduplication.
    If the event already exists at that file and line, it increments occurrences and updates last_seen_at.
    """
    now = get_current_utc_iso()
    meta_json = json.dumps(metadata or {}, ensure_ascii=False)
    file_norm = file_path.replace("\\", "/")
    # Guarantee non-null symbol_name and line_number so SQLite UNIQUE index handles NULL equality properly
    sym = symbol_name or ""
    line = line_number if line_number is not None else 0

    query = """
    INSERT INTO episodes (
        timestamp, event_type, file_path, symbol_name, line_number, severity, metadata_json, occurrences, last_seen_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
    ON CONFLICT(event_type, file_path, line_number, symbol_name) DO UPDATE SET
        occurrences = episodes.occurrences + 1,
        last_seen_at = excluded.last_seen_at,
        metadata_json = excluded.metadata_json,
        severity = excluded.severity;
    """

    conn.execute(
        query,
        (now, event_type, file_norm, sym, line, severity, meta_json, now),
    )


def scan_technical_debt(conn: sqlite3.Connection, root: Path = ROOT) -> int:
    """Scans for TODO, FIXME, HACK, BUG, and DEPRECATED comments across all code files."""
    count = 0
    patterns = [
        ("fixme_detected", re.compile(r"\bFIXME\b[:\s-]*(.*)", re.IGNORECASE), "high"),
        ("hack_detected", re.compile(r"\bHACK\b[:\s-]*(.*)", re.IGNORECASE), "high"),
        ("bug_detected", re.compile(r"\bBUG\b[:\s-]*(.*)", re.IGNORECASE), "high"),
        ("todo_detected", re.compile(r"\bTODO\b[:\s-]*(.*)", re.IGNORECASE), "medium"),
        ("deprecated_detected", re.compile(r"\bDEPRECATED\b[:\s-]*(.*)", re.IGNORECASE), "medium"),
    ]

    valid_exts = {".py", ".js", ".jsx", ".ts", ".tsx", ".yaml", ".yml", ".toml", ".sql", ".sh"}

    for p in root.rglob("*.*"):
        if any(ignored in p.parts for ignored in IGNORE_DIRS):
            continue
        if p.suffix not in valid_exts:
            continue

        rel_path = str(p.relative_to(root)).replace("\\", "/")
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                for lineno, line in enumerate(f, 1):
                    for event_type, regex, severity in patterns:
                        match = regex.search(line)
                        if match:
                            detail = match.group(1).strip()
                            record_episode(
                                conn=conn,
                                event_type=event_type,
                                file_path=rel_path,
                                symbol_name=None,
                                line_number=lineno,
                                severity=severity,
                                metadata={"snippet": line.strip()[:140], "detail": detail[:120]},
                            )
                            count += 1
        except Exception:
            continue

    return count


def scan_python_ast(conn: sqlite3.Connection, root: Path = ROOT) -> int:
    """Scans Python files using native AST parsing for classes, functions, and imports."""
    count = 0
    for py_file in root.rglob("*.py"):
        if any(ignored in py_file.parts for ignored in IGNORE_DIRS):
            continue

        rel_path = str(py_file.relative_to(root)).replace("\\", "/")
        try:
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(py_file))
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [getattr(b, "id", str(b)) for b in node.bases if hasattr(b, "id")]
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                record_episode(
                    conn=conn,
                    event_type="class_detected",
                    file_path=rel_path,
                    symbol_name=node.name,
                    line_number=node.lineno,
                    severity="low",
                    metadata={"bases": bases, "methods_count": len(methods), "methods": methods[:8]},
                )
                count += 1

            elif isinstance(node, ast.FunctionDef):
                # Only record top-level or significant functions
                args = [a.arg for a in node.args.args]
                record_episode(
                    conn=conn,
                    event_type="function_detected",
                    file_path=rel_path,
                    symbol_name=node.name,
                    line_number=node.lineno,
                    severity="low",
                    metadata={"arguments": args, "is_async": False},
                )
                count += 1

            elif isinstance(node, ast.AsyncFunctionDef):
                args = [a.arg for a in node.args.args]
                record_episode(
                    conn=conn,
                    event_type="function_detected",
                    file_path=rel_path,
                    symbol_name=node.name,
                    line_number=node.lineno,
                    severity="low",
                    metadata={"arguments": args, "is_async": True},
                )
                count += 1

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    record_episode(
                        conn=conn,
                        event_type="import_detected",
                        file_path=rel_path,
                        symbol_name=alias.name,
                        line_number=node.lineno,
                        severity="low",
                        metadata={"module": alias.name},
                    )
                    count += 1

            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for alias in node.names:
                    full_name = f"{mod}.{alias.name}" if mod else alias.name
                    record_episode(
                        conn=conn,
                        event_type="import_detected",
                        file_path=rel_path,
                        symbol_name=full_name,
                        line_number=node.lineno,
                        severity="low",
                        metadata={"module": mod, "symbol": alias.name},
                    )
                    count += 1

    return count


def scan_javascript_typescript(conn: sqlite3.Connection, root: Path = ROOT) -> int:
    """Scans JS/JSX/TS/TSX files for functions, classes, and React components."""
    count = 0
    extensions = {".js", ".jsx", ".ts", ".tsx"}

    re_class = re.compile(r"^\s*class\s+([A-Za-z0-9_$]+)", re.MULTILINE)
    re_func = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)", re.MULTILINE)
    re_arrow = re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", re.MULTILINE)
    re_react = re.compile(r"^\s*export\s+default\s+function\s+([A-Za-z0-9_$]+)", re.MULTILINE)
    re_import = re.compile(r"^\s*import\s+(?:\{[^}]*\}|[A-Za-z0-9_$*]+)\s+from\s+['\"]([^'\"]+)['\"]", re.MULTILINE)

    for p in root.rglob("*.*"):
        if any(ignored in p.parts for ignored in IGNORE_DIRS):
            continue
        if p.suffix not in extensions:
            continue

        rel_path = str(p.relative_to(root)).replace("\\", "/")
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            for match in re_class.finditer(content):
                lineno = content[: match.start()].count("\n") + 1
                record_episode(conn, "js_class_detected", rel_path, match.group(1), lineno)
                count += 1

            for match in re_func.finditer(content):
                lineno = content[: match.start()].count("\n") + 1
                record_episode(conn, "js_function_detected", rel_path, match.group(1), lineno)
                count += 1

            for match in re_arrow.finditer(content):
                lineno = content[: match.start()].count("\n") + 1
                record_episode(conn, "js_function_detected", rel_path, match.group(1), lineno)
                count += 1

            for match in re_react.finditer(content):
                lineno = content[: match.start()].count("\n") + 1
                record_episode(conn, "react_component_detected", rel_path, match.group(1), lineno)
                count += 1

            for match in re_import.finditer(content):
                lineno = content[: match.start()].count("\n") + 1
                record_episode(conn, "import_detected", rel_path, match.group(1), lineno)
                count += 1
        except Exception:
            continue

    return count


def scan_with_ast_grep(conn: sqlite3.Connection, root: Path = ROOT) -> int:
    """
    Executes ast-grep (sg) if available on PATH with corrected language-aware patterns.
    Outputs structured JSON directly into SQLite episodes.
    """
    sg_bin = shutil.which("sg")
    if not sg_bin:
        return 0

    count = 0
    # Correct ast-grep pattern definitions with explicit languages
    sg_configs = [
        # Python structural patterns
        {"pattern": "class $NAME: $$$BODY", "lang": "python", "event": "ast_grep_class"},
        {"pattern": "class $NAME($$$BASES): $$$BODY", "lang": "python", "event": "ast_grep_class"},
        {"pattern": "def $FUNC($$$ARGS): $$$BODY", "lang": "python", "event": "ast_grep_function"},
        # JavaScript / TypeScript structural patterns
        {"pattern": "class $NAME { $$$BODY }", "lang": "typescript", "event": "ast_grep_js_class"},
        {"pattern": "function $NAME($$$ARGS) { $$$BODY }", "lang": "typescript", "event": "ast_grep_js_func"},
    ]

    for cfg in sg_configs:
        try:
            cmd = [
                sg_bin,
                "run",
                "--pattern",
                cfg["pattern"],
                "--lang",
                cfg["lang"],
                "--json",
                str(root),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if res.returncode == 0 and res.stdout.strip():
                try:
                    matches = json.loads(res.stdout)
                    for item in matches:
                        file_path = item.get("file", "")
                        if any(ignored in Path(file_path).parts for ignored in IGNORE_DIRS):
                            continue
                        line = item.get("range", {}).get("start", {}).get("line", 1)
                        symbol = item.get("metaVariables", {}).get("single", {}).get("NAME", {}).get("text")
                        if not symbol:
                            symbol = item.get("metaVariables", {}).get("single", {}).get("FUNC", {}).get("text")

                        record_episode(
                            conn=conn,
                            event_type=cfg["event"],
                            file_path=file_path,
                            symbol_name=symbol,
                            line_number=line,
                            severity="low",
                            metadata={"matched_pattern": cfg["pattern"], "text": item.get("text", "")[:100]},
                        )
                        count += 1
                except Exception:
                    pass
        except Exception:
            continue

    return count


def run_ingest(db_path: Path = DB_PATH, root: Path = ROOT) -> Dict[str, Any]:
    """Runs complete ingestion pipeline and returns summary statistics."""
    print("=" * 70)
    print("   IDC COGNITIVE INGEST: REPOSITORY TO EPISODIC SQLITE DATABASE")
    print("=" * 70)

    conn = init_database(db_path)
    before_count = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]

    print(f"-> Base de datos: {db_path} (Registros previos: {before_count})")

    print("-> 1. Escaneando deuda tecnica (TODO / FIXME / HACK / BUG)...")
    debt_count = scan_technical_debt(conn, root)
    print(f"   * Eventos de deuda tecnica procesados: {debt_count}")

    print("-> 2. Escaneando codigo Python con AST nativo...")
    py_count = scan_python_ast(conn, root)
    print(f"   * Componentes Python procesados: {py_count}")

    print("-> 3. Escaneando codigo JavaScript y TypeScript...")
    js_count = scan_javascript_typescript(conn, root)
    print(f"   * Componentes JS/TS procesados: {js_count}")

    sg_bin = shutil.which("sg")
    sg_status = f"DISPONIBLE ({sg_bin})" if sg_bin else "NO DETECTADO (usando fallback AST nativo)"
    print(f"-> 4. Verificando ast-grep (sg): {sg_status}")
    sg_count = scan_with_ast_grep(conn, root)
    if sg_count > 0:
        print(f"   * Coincidencias estructurales ast-grep: {sg_count}")

    conn.commit()

    after_count = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
    total_occurrences = conn.execute("SELECT SUM(occurrences) FROM episodes").fetchone()[0] or 0

    print("\n" + "-" * 70)
    print(f"[IDC INGEST COMPLETADO]:")
    print(f"  • Total episodios unicos en SQLite: {after_count} (+{after_count - before_count} nuevos)")
    print(f"  • Frecuencia total acumulada:        {total_occurrences} observaciones")
    print("=" * 70 + "\n")

    conn.close()

    return {
        "db_path": str(db_path),
        "total_unique_episodes": after_count,
        "total_observations": total_occurrences,
        "debt_events": debt_count,
        "python_events": py_count,
        "js_events": js_count,
        "ast_grep_events": sg_count,
    }


def main():
    run_ingest()


if __name__ == "__main__":
    main()
