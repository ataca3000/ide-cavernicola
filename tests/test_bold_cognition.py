"""
Unit tests for IDC Bold Cognition:
Energy Manager dynamics, mode-aware RL rewards, Innovation Index (II),
and On-Demand Systemic Trauma Recall ("Dejar de temer a la muerte").
"""

from core.agent import IDCAgent
from core.energy_manager import EnergyManager
from core.memory_manager import MemoryManager
from core.metrics import Metrics
from core.reinforcement_engine import ReinforcementEngine
from plugins.llm.base import BaseLLMPlugin


class CaptureHypothesisLLM(BaseLLMPlugin):
    def __init__(self):
        self.last_rejected = []

    def query(self, prompt: str, **kwargs) -> str:
        return "response"

    def explain(self, context: str, decision: str) -> str:
        return "explanation"

    def verify(self, rule_hypothesis: str, evidence: dict) -> bool:
        return True

    def simulate(self, action: str, current_state: dict) -> dict:
        return {}

    def extract_causal_rule(self, episode: dict) -> dict:
        return {}

    def generate_hypothesis(self, goal, context=None, rejected_hypotheses=None):
        self.last_rejected = list(rejected_hypotheses or [])
        return {"action": "bold_action_proposal", "hypothesis": "creative_breakthrough"}


def test_energy_manager_production():
    em = EnergyManager(energy=100.0)
    assert em.mode() == "EXPLORATION"
    assert em.stress_factor() == 1.0

    # Consume in exploration
    em.consume_action(base_cost=10.0, complexity=1.0)
    assert em.available() == 90.0

    # Drop to optimization mode
    em.consume(75.0)
    assert em.available() == 15.0
    assert em.mode() == "OPTIMIZATION"
    assert em.stress_factor() > 2.0

    # Drop to survival mode
    em.consume(12.0)
    assert em.available() == 3.0
    assert em.mode() == "SURVIVAL"

    # Recharge
    em.recharge(50.0)
    assert em.available() == 53.0
    assert em.mode() == "EXPLORATION"


def test_reinforcement_mode_aware_rewards():
    re = ReinforcementEngine()

    # Exploration rewards innovation and is gentle on energy cost
    reward_exp = re.calculate_reward(
        success=True,
        efficiency=1.0,
        replications=1,
        purpose_alignment=1.0,
        energy_cost=4.0,
        complexity=1.0,
        mode="EXPLORATION",
        innovation_index=2.5,
    )

    # Survival mode severely penalizes energy waste and rewards state preservation
    reward_surv_fail = re.calculate_reward(
        success=False,
        efficiency=0.1,
        replications=1,
        purpose_alignment=0.5,
        energy_cost=4.0,
        complexity=2.0,
        mode="SURVIVAL",
        innovation_index=1.0,
    )

    assert reward_exp > 20.0
    assert reward_surv_fail < -20.0


def test_innovation_index():
    # When agent explores 10 actions with 5 constraints, II is high
    ii = Metrics.innovation_index(unique_actions_explored=10, rejected_constraints=5)
    assert ii == 3.0

    # When no constraints, base II is 1.0
    assert Metrics.innovation_index(1, 0) == 1.0


def test_on_demand_trauma_memory(tmp_path):
    mem = MemoryManager(base_dir=str(tmp_path / "memory"))

    # Record a catastrophic collapse
    mem.record_systemic_trauma(
        trauma_id="trauma_hardware_lockdown_001",
        trigger_goal="Acelerar compilacion de contenedores",
        environment_verdict="HARDWARE_LOCKDOWN",
        fatal_actions=["force_kernel_panic", "dma_kernel_bypass"],
        reason="Total hardware blockade",
    )

    # 1. DEFAULT BEHAVIOR: "Dejar de temer a la muerte"
    # By default, past trauma is dormant to allow bold exploration!
    dormant = mem.recall_systemic_traumas(on_demand=False)
    assert dormant == []

    # 2. ON-DEMAND BEHAVIOR: explicitly requested
    recalled = mem.recall_systemic_traumas(on_demand=True)
    assert len(recalled) == 1
    assert recalled[0]["environment_verdict"] == "HARDWARE_LOCKDOWN"


def test_agent_bold_vs_cautious_trauma(tmp_path):
    mem_dir = str(tmp_path / "memory")
    mem = MemoryManager(base_dir=mem_dir)
    mem.record_systemic_trauma(
        trauma_id="trauma_001",
        trigger_goal="extreme_test",
        environment_verdict="FATAL",
        fatal_actions=["fatal_action_a", "fatal_action_b"],
        reason="crash",
    )

    llm = CaptureHypothesisLLM()

    # Case A: Default agent ("Sin miedo a la muerte") -> does not restrict trauma actions
    agent_bold = IDCAgent(llm_plugin=llm, memory_dir=mem_dir, recall_trauma=False)
    from contracts import Goal
    agent_bold.brainstorm(Goal(id="g1", description="new_bold_goal", priority=0.8), force_llm=True)
    assert "fatal_action_a" not in llm.last_rejected

    # Case B: On-Demand Trauma Recall -> restricts fatal actions
    agent_cautious = IDCAgent(llm_plugin=llm, memory_dir=mem_dir, recall_trauma=True)
    agent_cautious.brainstorm(Goal(id="g2", description="new_bold_goal", priority=0.8), force_llm=True)
    assert "fatal_action_a" in llm.last_rejected
    assert "fatal_action_b" in llm.last_rejected
