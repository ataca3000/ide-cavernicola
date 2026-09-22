#!/usr/bin/env python3
"""
IDC CI Failure Hook: Store Failures in Causal Trash & Episodic SQLite
Executed in GitHub Actions (if: failure()) or local test environments
to register failed commands, errors, and test crashes directly into Causal Trash.
Authored by Luis Felipe Durán Salinas (ATACA3000 / Brecha Soluciones DS).
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
_PROJECT_ROOT = str(Path(__file__).parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core.memory_manager import MemoryManager
from scripts.idc_ingest import init_database, record_episode


def capture_failure(goal: str, action: str, error: str, reason: str) -> None:
    print("=" * 70)
    print("   IDC CI FAILURE SENSOR: REGISTRANDO ERROR EN CAUSAL TRASH")
    print("=" * 70)

    # 1. Store in Causal Trash
    memory = MemoryManager()
    trash_entry = memory.record_rejected(
        hypothesis=action,
        reason=f"{reason}: {error}" if error else reason,
        goal=goal,
        metrics={"ci_status": "failed", "error_snippet": error[:200]},
    )

    print(f"-> Fallo registrado en Causal Trash: {trash_entry['id']}")
    print(f"   * Objetivo Afectado: '{goal}'")
    print(f"   * Accion Fallida:    '{action}'")
    print(f"   * Razon / Error:     {trash_entry['reason']}")

    # 2. Store in Episodic SQLite Database
    try:
        db_path = Path("memory/idc.db")
        conn = init_database(db_path)
        record_episode(
            conn=conn,
            event_type="ci_failure_detected",
            file_path=".github/workflows/ci.yml",
            symbol_name=action,
            line_number=0,
            severity="high",
            metadata={
                "goal": goal,
                "failed_action": action,
                "error": error,
                "trash_id": trash_entry["id"],
            },
        )
        conn.commit()
        conn.close()
        print(f"-> Evento de fallo sincronizado en SQLite ({db_path})")
    except Exception as ex:
        print(f"(Aviso: no se pudo escribir en SQLite: {ex})")

    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Capturar errores de ejecucion/CI y registrarlos en Causal Trash"
    )
    parser.add_argument("--goal", default="ci_pipeline_verification", help="Objetivo en ejecucion")
    parser.add_argument("--action", default="pytest tests/", help="Comando o accion que fallo")
    parser.add_argument("--error", default="", help="Detalle o tipo de error (ej. ModuleNotFoundError)")
    parser.add_argument("--reason", default="CI test or execution step failed", help="Motivo del fallo")

    args = parser.parse_args()
    capture_failure(
        goal=args.goal,
        action=args.action,
        error=args.error,
        reason=args.reason,
    )


if __name__ == "__main__":
    main()
