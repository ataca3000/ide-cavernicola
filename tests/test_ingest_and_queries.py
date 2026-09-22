"""
Unit tests for IDC Ingest, SQLite Deduplication, Architectural Queries, and Causal Short-Circuit.
"""

import sqlite3
from pathlib import Path
from unittest.mock import patch

from contracts import Goal
from core.agent import IDCAgent
from core.memory_manager import MemoryManager
from plugins.llm.base import BaseLLMPlugin
from scripts.idc_ingest import init_database, record_episode, scan_python_ast, scan_technical_debt
from scripts.idc_queries import IDCAnalytics
from scripts.store_failure import capture_failure


class DummyLLM(BaseLLMPlugin):
    def generate_hypothesis(self, goal, context=None, rejected_hypotheses=None):
        return {"action": "dummy_action", "hypothesis": "dummy_hypothesis"}


def test_sqlite_deduplication(tmp_path):
    test_db = tmp_path / "test_idc.db"
    conn = init_database(test_db)

    # Insert initial episode
    record_episode(
        conn=conn,
        event_type="todo_detected",
        file_path="core/test.py",
        symbol_name="",
        line_number=42,
        severity="medium",
        metadata={"detail": "refactor this"},
    )
    conn.commit()

    count1 = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
    occ1 = conn.execute("SELECT occurrences FROM episodes WHERE line_number = 42").fetchone()[0]
    assert count1 == 1
    assert occ1 == 1

    # Insert identical episode (same event_type, file_path, line_number, symbol_name)
    record_episode(
        conn=conn,
        event_type="todo_detected",
        file_path="core/test.py",
        symbol_name="",
        line_number=42,
        severity="medium",
        metadata={"detail": "refactor this updated"},
    )
    conn.commit()

    count2 = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
    occ2 = conn.execute("SELECT occurrences FROM episodes WHERE line_number = 42").fetchone()[0]

    # Unique rows must remain 1, while occurrences must be incremented to 2
    assert count2 == 1
    assert occ2 == 2
    conn.close()


def test_scan_technical_debt(tmp_path):
    sample_file = tmp_path / "sample.py"
    sample_file.write_text(
        "# TODO: implement feature\n# FIXME: critical bug\n# HACK: temporary workaround\n",
        encoding="utf-8",
    )
    test_db = tmp_path / "test_debt.db"
    conn = init_database(test_db)

    count = scan_technical_debt(conn, root=tmp_path)
    conn.commit()

    assert count == 3
    rows = conn.execute("SELECT event_type FROM episodes").fetchall()
    types = [r[0] for r in rows]
    assert "todo_detected" in types
    assert "fixme_detected" in types
    assert "hack_detected" in types
    conn.close()


def test_idc_analytics_queries(tmp_path):
    test_db = tmp_path / "test_analytics.db"
    conn = init_database(test_db)
    record_episode(conn, "class_detected", "core/agent.py", "IDCAgent", 10)
    record_episode(conn, "function_detected", "core/agent.py", "run_step", 25)
    record_episode(conn, "import_detected", "core/agent.py", "core.MemoryManager", 5)
    record_episode(conn, "todo_detected", "core/agent.py", "", 30, severity="medium")
    conn.commit()
    conn.close()

    analytics = IDCAnalytics(db_path=test_db)
    summary = analytics.get_inventory_summary()
    assert summary["classes"] == 1
    assert summary["functions"] == 1
    assert summary["imports"] == 1
    assert summary["tech_debt"] == 1

    complex_mods = analytics.get_most_complex_modules(5)
    assert len(complex_mods) == 1
    assert complex_mods[0]["file_path"] == "core/agent.py"

    hubs = analytics.get_most_imported_internal_symbols(5)
    assert len(hubs) == 1
    assert hubs[0]["symbol_name"] == "core.MemoryManager"

    analytics.close()


def test_capture_failure_hook(tmp_path):
    with patch("core.memory_manager.Path") as mock_path:
        capture_failure(
            goal="unit_test_goal",
            action="pytest tests/broken_test.py",
            error="AssertionError: 1 != 2",
            reason="Test failed",
        )
    # Check trash entry in actual memory manager
    mem = MemoryManager()
    assert mem.is_rejected("pytest tests/broken_test.py")


def test_causal_memory_short_circuit(tmp_path):
    mem = MemoryManager(base_dir=str(tmp_path / "memory"))
    mem.save_causal_rule(
        rule_id="rule_test_cache",
        cause="docker_layer_caching",
        effect="faster_builds",
        confidence=0.95,
        goal="acelerar compilacion de contenedores",
        successful_action="enable_docker_layer_cache",
    )

    agent = IDCAgent(llm_plugin=DummyLLM(), memory_path=str(tmp_path / "memory"))

    goal = Goal(id="g1", description="acelerar compilacion de contenedores docker", priority=0.9)
    res = agent.brainstorm(goal)

    # Must be retrieved from Causal Memory, not LLM!
    assert res.get("from_causal_memory") is True
    assert res.get("tokens_saved") is True
    assert res.get("action") == "enable_docker_layer_cache"
    assert "rule_test_cache" in res.get("hypothesis")
