"""
Tests for Commonsense Causal Engine and Tenacity Resolution Loop.
"""

import os
import shutil
import tempfile
import pytest

from contracts.goal import Goal
from contracts.reality import DomainType
from core.agent import IDCAgent
from core.commonsense_engine import CommonsenseEngine
from core.tenacity_loop import TenacityResolver


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def test_commonsense_bilingual_lookup():
    engine = CommonsenseEngine()

    # Spanish lookup
    c_es = engine.lookup_concept("obstáculo")
    assert c_es is not None
    assert c_es.name == "obstacle"
    assert "collision" in c_es.causes

    # English lookup
    c_en = engine.lookup_concept("slippery_surface")
    assert c_en is not None
    assert "skid" in c_en.hazards

    # Human priority safety lookup
    c_human = engine.lookup_concept("persona")
    assert c_human is not None
    assert "emergency_stop_required" in c_human.hazards


def test_commonsense_scene_interpretation():
    engine = CommonsenseEngine()

    # Camera detections: obstacle at 0.4 meters (critical proximity)
    detections = [
        {"label": "obstáculo", "distance_m": 0.4},
        {"label": "humano", "distance_m": 3.5},
    ]
    telemetry = {"temperature_c": 82.0}

    analysis = engine.interpret_sensory_scene(detections, telemetry)

    assert not analysis["scene_clear"]
    assert any("CRITICAL_PROXIMITY" in h for h in analysis["hazards"])
    assert "thermodynamics" in analysis["recommended_domains"]
    assert "classical_physics" in analysis["recommended_domains"]


def test_tenacity_resolver_obstacle_overcoming(temp_dir):
    mem_dir = os.path.join(temp_dir, "memory")
    agent = IDCAgent(memory_dir=mem_dir)
    tenacity = TenacityResolver(agent=agent, max_attempts=5)

    goal = Goal(id="g_nav", description="reach target beacon through corridor", priority=0.9)

    call_count = 0

    # Simulated environment actuator with initial failures (obstacle blockage)
    def mock_environment(action: str, context: dict):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return False, "Blocked by heavy pallet: forward path obstructed", {"obstacle_cleared": False}
        elif call_count == 2:
            return False, "Traction loss on surface: wheel slip detected", {"obstacle_cleared": False}
        else:
            return True, "Trajectory verified: beacon reached with 0 collisions", {"obstacle_cleared": True}

    def mock_observer(failed_action: str, reason: str):
        return f"Advice: detour around left flank to avoid traction loss on {failed_action}"

    initial_context = {
        "vision_detections": [{"label": "obstáculo", "distance_m": 0.8}],
        "telemetry": {"temperature_c": 35.0},
    }

    result = tenacity.solve(
        goal=goal,
        environment_actuator=mock_environment,
        initial_context=initial_context,
        observer_oracle=mock_observer,
    )

    # Verifications
    assert result["solved"]
    assert result["attempts"] == 3
    assert len(result["failed_attempts_overcome"]) == 2
    assert "citable_memory_id" in result
    assert len(result["proof_hash"]) == 64

    # Causal trash recorded the failures
    assert len(agent.memory.get_rejected_list()) >= 2
    # Citable logical memory vault contains the empirical victory
    assert agent.vault.total_citable_count == 1
    assert result["status"] == "ALCANZADO_ESTABLE_Y_SEGURO"


def test_tenacity_numerical_viability_threshold(temp_dir):
    mem_dir = os.path.join(temp_dir, "memory")
    agent = IDCAgent(memory_dir=mem_dir)
    tenacity = TenacityResolver(agent=agent, max_attempts=5)

    # Goal with ideal target 1.0 (100%), but stability threshold 0.68 (68%)
    goal = Goal(id="g_motor", description="calibrate motor torque efficiency", priority=0.8, stability_threshold=0.68)

    attempt = 0
    def motor_environment(action: str, context: dict):
        nonlocal attempt
        attempt += 1
        if attempt == 1:
            # 52% efficiency: below 68% threshold -> considered unstable
            return 0.52, "Efficiency 52% with high thermal loss", {}
        else:
            # 70% efficiency: meets viability threshold (65%-70%) -> ALCANZADO_ESTABLE_Y_SEGURO
            return 0.70, "Efficiency 70% reached under physical friction limits", {}

    res = tenacity.solve(goal=goal, environment_actuator=motor_environment)

    assert res["solved"]
    assert res["status"] == "ALCANZADO_ESTABLE_Y_SEGURO"
    assert res["empirical_score"] == 0.70
    assert res["stability_threshold"] == 0.68
    assert res["ideal_target"] == 1.0
    assert goal.state == "completed"

