"""
Unit tests for IDCAgent cognitive lifecycle
"""

import os
import shutil
import tempfile
import pytest

from contracts import Goal, AgentState
from core import IDCAgent


@pytest.fixture
def temp_agent():
    temp_dir = tempfile.mkdtemp()
    mem_dir = os.path.join(temp_dir, "memory")
    id_dir = os.path.join(mem_dir, "identity")
    os.makedirs(id_dir, exist_ok=True)
    for sub in ["episodic", "causal", "procedural", "trash"]:
        os.makedirs(os.path.join(mem_dir, sub), exist_ok=True)

    id_file = os.path.join(id_dir, "id.json")
    with open(id_file, "w", encoding="utf-8") as f:
        f.write('{"name": "TestAgent", "purpose": "Autonomous learning", "principles": ["Reality First"]}')

    agent = IDCAgent(identity_path=id_file, memory_dir=mem_dir, initial_energy=50.0)
    yield agent
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_agent_initial_state(temp_agent):
    state = temp_agent.state
    assert isinstance(state, AgentState)
    assert state.energy == 50.0
    assert state.current_goal == "idle"
    assert state.uncertainty == 0.0


def test_agent_purpose_rejection(temp_agent):
    # Goal with priority 0.2 should be rejected by purpose filter (< 0.5 threshold)
    low_goal = Goal(id="g_trivial", description="Trivial unaligned task", priority=0.2)
    state = temp_agent.run_step(low_goal, candidate_action="waste_energy")

    assert low_goal.state == "rejected"
    assert state.energy == 50.0  # Zero energy wasted
    assert state.uncertainty == 1.0


def test_agent_successful_step_and_rule_learning(temp_agent):
    goal = Goal(id="g_build", description="Accelerate build time", priority=0.8)
    state = temp_agent.run_step(
        goal=goal,
        candidate_action="enable_parallel_jobs",
        context={"success": True, "expected_effect": "build_time_halved", "estimated_cost": 5.0},
    )

    assert goal.state == "completed"
    assert state.energy < 50.0
    assert len(state.active_rules) == 1
    assert state.uncertainty <= 0.4

    # Verify metrics
    metrics = temp_agent.get_metrics()
    assert metrics.replication_index >= 1.0
    assert metrics.purpose_alignment == 1.0


def test_agent_trash_rejection(temp_agent):
    # First, record a failure so it enters Causal Trash
    fail_goal = Goal(id="g_fail", description="Test bad flag", priority=0.9)
    temp_agent.run_step(
        goal=fail_goal,
        candidate_action="use_broken_compiler_flag",
        context={"success": False, "estimated_cost": 2.0},
    )
    assert fail_goal.state == "failed"

    # Now attempt the exact same bad action again
    retry_goal = Goal(id="g_retry", description="Retry bad flag", priority=0.9)
    energy_before = temp_agent.energy.available()
    state = temp_agent.run_step(
        goal=retry_goal,
        candidate_action="use_broken_compiler_flag",
        context={"estimated_cost": 10.0},
    )

    # Must be rejected without consuming energy
    assert temp_agent.energy.available() == energy_before
    assert state.uncertainty == 0.8
