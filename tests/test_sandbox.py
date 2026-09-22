"""
Unit tests for RealSandbox and Causal Trash Contract
"""

from contracts.trash import CausalTrashEntry
from contracts.rule import CausalRule
from core.sandbox import RealSandbox


def test_causal_trash_contract():
    trash = CausalTrashEntry(
        id="trash_001",
        goal="optimize_build",
        failed_action="use_broken_flag",
        reason="Exit code 1",
        metrics={"baseline_s": 45.0, "duration_s": 56.2, "delta_s": 11.2},
    )
    dumped = trash.model_dump()
    assert dumped["failed_action"] == "use_broken_flag"
    assert dumped["metrics"]["baseline_s"] == 45.0


def test_causal_rule_cumulative_contract():
    rule = CausalRule(
        id="rule_999",
        goal="optimize_build",
        cause="mount_cache",
        effect="faster_build",
        successful_action="mount_cache",
        failed_actions_superseded=["use_broken_flag", "no_cache_flag"],
        confidence=0.96,
        replications=2,
        reuses=5,
        metrics_improvement={"baseline_s": 45.0, "achieved_s": 12.0, "improvement_pct": 73.3},
    )
    dumped = rule.model_dump()
    assert "use_broken_flag" in dumped["failed_actions_superseded"]
    assert dumped["reuses"] == 5
    assert dumped["metrics_improvement"]["improvement_pct"] == 73.3


def test_real_sandbox_strategy_evaluation():
    sandbox = RealSandbox(default_baseline_s=50.0)

    # Test degraded / failing strategy
    bad_res = sandbox.evaluate_strategy("optimize_something", is_known_bad=True)
    assert bad_res["success"] is False
    assert bad_res["duration_s"] > bad_res["baseline_s"]

    # Test successful strategy
    good_res = sandbox.evaluate_strategy("enable_docker_caching", is_known_bad=False)
    assert good_res["success"] is True
    assert good_res["duration_s"] < good_res["baseline_s"]
    assert good_res["improvement_pct"] > 0
    assert good_res["energy_cost"] < bad_res["energy_cost"]


def test_real_sandbox_command_execution():
    sandbox = RealSandbox()
    # Execute simple command
    res = sandbox.execute_command("echo IDC_SANDBOX_TEST")
    assert res["success"] is True
    assert "IDC_SANDBOX_TEST" in res["stdout"]
    assert res["duration_s"] >= 0.0
