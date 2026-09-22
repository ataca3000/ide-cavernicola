"""
Unit tests for IDC Contracts (Pydantic Models & Interfaces)
"""

import pytest
from pydantic import ValidationError

from contracts import (
    AgentState,
    CausalRule,
    ExperienceEvent,
    Goal,
    MetricsModel,
    PluginInterface,
)


def test_agent_state_contract():
    state = AgentState(
        energy=85.5,
        current_goal="optimize_build",
        active_rules=["rule_001"],
        active_context={"compiler": "gcc"},
        uncertainty=0.15,
        version="0.1.0",
    )
    assert state.energy == 85.5
    assert state.current_goal == "optimize_build"
    assert state.active_rules == ["rule_001"]
    assert state.uncertainty == 0.15

    # Test uncertainty validation (must be between 0.0 and 1.0)
    with pytest.raises(ValidationError):
        AgentState(energy=50.0, current_goal="test", uncertainty=1.5)


def test_causal_rule_contract():
    rule = CausalRule(
        id="rule_cache_01",
        cause="enable_cache",
        effect="build_speedup_50pct",
        confidence=0.92,
        replications=5,
        conditions=["docker", "linux"],
    )
    assert rule.id == "rule_cache_01"
    assert rule.confidence == 0.92
    assert rule.replications == 5
    assert "docker" in rule.conditions

    # Confidence validation
    with pytest.raises(ValidationError):
        CausalRule(id="rule_bad", cause="a", effect="b", confidence=-0.1)


def test_experience_event_contract():
    event = ExperienceEvent(
        id="evt_101",
        action="deploy_staging",
        result="SUCCESS",
        energy_cost=4.5,
        goal="verify_release",
        confidence=0.98,
    )
    dumped = event.model_dump()
    assert dumped["id"] == "evt_101"
    assert dumped["energy_cost"] == 4.5
    assert dumped["result"] == "SUCCESS"


def test_goal_contract():
    goal = Goal(
        id="goal_001",
        description="Reduce CI latency to under 30s",
        priority=0.85,
        deadline="2026-10-01",
        state="active",
    )
    assert goal.priority == 0.85
    assert goal.state == "active"

    # Priority range validation
    with pytest.raises(ValidationError):
        Goal(id="g", description="test", priority=2.0)


def test_metrics_model_contract():
    metrics = MetricsModel(
        curiosity_index=0.8,
        replication_index=4.0,
        adaptation_index=0.45,
        innovation_index=0.7,
        purpose_alignment=0.95,
        learning_efficiency=0.6,
    )
    assert metrics.curiosity_index == 0.8
    assert metrics.purpose_alignment == 0.95


def test_plugin_interface_subclass():
    class CustomPlugin(PluginInterface):
        name = "test_plugin"

        def query(self, request):
            return {"data": request.get("key")}

        def explain(self, request):
            return {"explanation": "simple test"}

        def verify(self, request):
            return {"valid": True}

        def simulate(self, request):
            return {"result": "simulated"}

    plugin = CustomPlugin()
    assert plugin.name == "test_plugin"
    assert plugin.query({"key": "val"}) == {"data": "val"}
    assert plugin.verify({}) == {"valid": True}
