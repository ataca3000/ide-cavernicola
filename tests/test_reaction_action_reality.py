"""
Unit and Integration Tests for Bio-Physical Reaction-Action Engine,
Pluggable Reality Domains, and Citable Memory Vault.
"""

import os
import shutil
import tempfile
import pytest

from contracts.pulse import ReactionPulse, PulseReactionRule
from contracts.reality import DomainType
from contracts.goal import Goal
from core.pulse_reaction_engine import PulseReactionEngine
from core.reality_loader import RealityLoader
from core.citable_memory_vault import CitableMemoryVault
from core.mutant_action_engine import MutantActionEngine
from core.agent import IDCAgent


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


# ── 1. Pulse Reaction Engine Tests ──────────────────────────────────────────

def test_pulse_reaction_under_threshold():
    engine = PulseReactionEngine()
    pulse = ReactionPulse(channel="voltage_rail", amplitude=12.0)
    response = engine.receive_pulse(pulse)

    assert not response.triggered
    assert response.latency_ms < 5.0
    assert engine.stats["total_pulses_received"] == 1
    assert engine.stats["total_reflexes_fired"] == 0


def test_pulse_reaction_critical_spike():
    engine = PulseReactionEngine()
    # Lethal voltage spike: 13.5V > 12.8V threshold
    pulse = ReactionPulse(channel="voltage_rail", amplitude=13.5)
    response = engine.receive_pulse(pulse)

    assert response.triggered
    assert response.action == "trip_breaker_and_isolate_rail"
    assert response.latency_ms < 5.0
    assert response.energy_cost > 0.0
    assert engine.stats["total_reflexes_fired"] == 1


def test_pulse_buffer_clearing():
    engine = PulseReactionEngine(buffer_size=10)
    for i in range(15):
        engine.receive_pulse(ReactionPulse(channel="voltage_rail", amplitude=11.0 + (i * 0.1)))

    assert engine.stats["buffered_pulses_count"] == 10
    engine.clear_volatile_buffer()
    assert engine.stats["buffered_pulses_count"] == 0


# ── 2. Pluggable Reality Loader Tests ────────────────────────────────────────

def test_pluggable_reality_cyberphysical_guard():
    loader = RealityLoader()
    loader.mount(DomainType.CYBERPHYSICAL)

    # Valid action
    valid, _ = loader.validate_action("allocate_aligned_cache_buffer")
    assert valid

    # Forbidden pattern
    invalid, reason = loader.validate_action("trigger_buffer_overflow_exploit")
    assert not invalid
    assert "buffer_overflow" in reason


def test_pluggable_reality_thermodynamics_temperature_invariant():
    loader = RealityLoader()
    loader.mount(DomainType.THERMODYNAMICS)

    # Valid positive Kelvin
    valid, _ = loader.validate_action("cool_chamber", parameters={"min_temperature_kelvin": 4.2})
    assert valid

    # Forbidden negative Kelvin
    invalid, reason = loader.validate_action("freeze_system", parameters={"min_temperature_kelvin": -10.0})
    assert not invalid
    assert "below absolute zero" in reason


def test_pluggable_reality_domain_isolation():
    loader = RealityLoader()
    # Mount cyberphysical only — thermodynamics is NOT mounted
    loader.mount(DomainType.CYBERPHYSICAL)

    # Action that would violate thermodynamics passes because agent is operating purely in cyberphysical domain
    valid, _ = loader.validate_action("freeze_system", parameters={"min_temperature_kelvin": -10.0})
    assert valid
    assert DomainType.THERMODYNAMICS not in loader.mounted_domains


def test_pluggable_reality_physics_speed_of_light():
    loader = RealityLoader()
    loader.mount(DomainType.CLASSICAL_PHYSICS)

    invalid, reason = loader.validate_action("faster_than_light_propulsion_drive")
    assert not invalid
    assert "Universal Speed Limit" in reason


# ── 3. Citable Memory Vault & Mutant Action Engine Tests ─────────────────────

def test_citable_memory_promotion_lifecycle(temp_dir):
    vault = CitableMemoryVault(base_dir=temp_dir)

    # 1. Record volatile hypothetical
    hypo = vault.record_hypothetical(
        conjecture="Preheating cache reduces thread contention by 40%",
        mutant_parameters={"thread_count": 8, "cache_prefetch": True}
    )
    assert hypo.id is not None
    assert not hypo.promoted_to_citable

    # 2. Promote after empirical verification
    citable = vault.promote_to_citable(
        hypothetical_id=hypo.id,
        claim="Preheating L1 cache cuts lock wait times by 40% under 8 threads",
        domain="cyberphysical",
        citation_source="benchmark_run_x86_64",
        empirical_log="trial_1=42ms, trial_2=41ms, baseline=70ms",
        conditions=["architecture == x86_64", "threads >= 4"],
        axioms=["Cache coherence protocol MESI"],
    )

    assert citable.proof_hash is not None
    assert len(citable.proof_hash) == 64  # SHA256 length
    assert vault.total_citable_count == 1

    # Hypothetical is linked and marked promoted
    updated_hypo = vault.get_hypothetical(hypo.id)
    assert updated_hypo.promoted_to_citable
    assert updated_hypo.citable_memory_id == citable.id

    # Citation test
    citation = vault.cite_memory(citable.id)
    assert f"id={citable.id}" in citation
    assert citable.reusable_count == 1


def test_mutant_action_engine_evolution(temp_dir):
    vault = CitableMemoryVault(base_dir=temp_dir)
    reality = RealityLoader()
    reality.mount(DomainType.CYBERPHYSICAL)

    engine = MutantActionEngine(vault=vault, reality_loader=reality, base_mutation_rate=0.5)
    goal = Goal(id="g1", description="optimize throughput", priority=0.9)

    action_res = engine.generate_mutant_action(goal, context={"target_subsystem": "io_scheduler"})
    assert action_res["valid_reality"]
    assert "hypothetical_id" in action_res
    assert action_res["generation"] == 1

    # Reinforce successful mutation
    initial_genome = dict(engine.policy_genome)
    engine.reinforce_mutation(action_res["hypothetical_id"], success=True, reward=1.0)
    assert engine.stats["successful_mutations"] == 1


# ── 4. Full IDCAgent Bio-Physical Integration Tests ─────────────────────────

def test_idc_agent_pulse_reflex_and_reality(temp_dir):
    mem_dir = os.path.join(temp_dir, "memory")
    agent = IDCAgent(memory_dir=mem_dir, initial_energy=100.0)

    # Test 1: Immediate reflex to thermal spike
    thermal_pulse = ReactionPulse(channel="thermal_spike", amplitude=92.0)
    reflex = agent.process_pulse(thermal_pulse)

    assert reflex.triggered
    assert reflex.action == "throttle_clock_and_divert_load"
    assert agent.energy.available() < 100.0  # Involuntary reflex consumed small energy

    # Test 2: Mount Classical Physics reality
    agent.mount_reality(DomainType.CLASSICAL_PHYSICS)
    assert agent.reality.is_mounted(DomainType.CLASSICAL_PHYSICS)

    # Test 3: Generate mutant action complying with reality
    goal = Goal(id="g_mech", description="balance kinetic load", priority=0.8)
    mutant_res = agent.generate_mutant_action(goal, context={"target_subsystem": "motor_pivots"})

    assert mutant_res["valid_reality"]
    assert "explore" in mutant_res["action"] or "exploit" in mutant_res["action"]

    # Test 4: Promote empirical hypothesis to citable memory directly via agent
    citable = agent.promote_hypothesis_to_citable(
        hypothetical_id=mutant_res["hypothetical_id"],
        claim="Torque distribution follows lever arm equation",
        domain="classical_physics",
        citation_source="sensor_run_77",
        empirical_log="F1*d1 == F2*d2 validated",
    )
    assert citable.claim == "Torque distribution follows lever arm equation"
    assert agent.vault.total_citable_count >= 1
