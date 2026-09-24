"""
IDC (Inventor Driven Cognition) - Decision Engine (v0.3 Reasoning)
Coordinates Purpose, Energy constraints, Memory checks, and Simulations
to make executive decisions for the agent.
"""

from typing import Dict, Any, Tuple, Optional
from core.purpose_filter import PurposeFilter
from core.energy_manager import EnergyManager
from core.memory_manager import MemoryManager
from core.simulation_engine import SimulationEngine


class DecisionEngine:
    """
    Executive arbiter of IDC actions.
    Decides whether an action should be:
      - EXECUTED_DIRECTLY: Pattern already proven with high confidence
      - SIMULATE_AND_TEST: Novel hypothesis worth exploring within energy limits
      - REJECTED: Unaligned with purpose, known failure in trash, or energy exhausted
    """

    def __init__(
        self,
        purpose_filter: PurposeFilter,
        energy_manager: EnergyManager,
        memory_manager: MemoryManager,
        simulation_engine: Optional[SimulationEngine] = None
    ):
        self.purpose_filter = purpose_filter
        self.energy_manager = energy_manager
        self.memory_manager = memory_manager
        self.simulation_engine = simulation_engine or SimulationEngine()

    def decide(
        self,
        candidate_action: str,
        hypothesis: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Evaluates a candidate action and returns:
            (decision_code: str, rationale: str, metadata: dict)
        """
        context = context or {}

        # 1. Purpose Filter Check
        goal_score = context.get("goal_score", 0.7)
        if not self.purpose_filter.evaluate(goal_score):
            return "REJECTED", "Action rejected: not aligned with current purpose.", {"filter": "purpose"}

        # 2. Causal Trash Check (Avoid repeated mistakes)
        if self.memory_manager.is_rejected(candidate_action) or (hypothesis and self.memory_manager.is_rejected(hypothesis)):
            return "REJECTED", "Action rejected: matches known failure in Causal Trash.", {"filter": "trash"}

        # 3. Energy Affordability Check
        cost = context.get("estimated_cost", 3.0)
        if not self.energy_manager.can_afford(cost):
            return "REJECTED", f"Action rejected: insufficient energy (cost {cost} > available {self.energy_manager.available()}).", {"filter": "energy"}

        # 4. Pattern Recognition in Causal Memory
        proven_rules = self.memory_manager.find_rules_by_cause(candidate_action)
        if proven_rules:
            best_rule = max(proven_rules, key=lambda r: r.get("confidence", 0.0))
            if best_rule.get("confidence", 0.0) >= 0.85:
                return "EXECUTE_DIRECT", f"Action accepted: matched proven causal rule '{best_rule['id']}'.", {
                    "rule": best_rule,
                    "mode": self.energy_manager.mode()
                }

        # 5. Simulation projection for exploratory / novel actions
        sim = self.simulation_engine.simulate(hypothesis, candidate_action, context)
        if sim["risk_level"] == "HIGH" and self.energy_manager.mode() == "SURVIVAL":
            return "REJECTED", "Action rejected: high risk in Survival Mode.", {"simulation": sim}

        return "SIMULATE_AND_TEST", f"Action accepted for empirical validation (projected success: {sim['predicted_success']}).", {
            "simulation": sim,
            "mode": self.energy_manager.mode()
        }
