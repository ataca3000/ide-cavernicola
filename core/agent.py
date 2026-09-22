"""
IDC (Inventor Driven Cognition) - IDCAgent
Unified cognitive agent orchestrating Identity, Energy, Purpose, Memory,
Curiosity, Causal Reasoning, Simulation, and Reinforcement under finite resources.
"""

import os
from typing import Any, Dict, List, Optional

from contracts.event import ExperienceEvent
from contracts.goal import Goal
from contracts.metrics import MetricsModel
from contracts.rule import CausalRule
from contracts.state import AgentState

from core.causal_engine import CausalEngine
from core.curiosity_engine import CuriosityEngine
from core.decision_engine import DecisionEngine
from core.energy_manager import EnergyManager
from core.identity import Identity
from core.memory_manager import MemoryManager
from core.metrics import Metrics
from core.purpose_filter import PurposeFilter
from core.reinforcement_engine import ReinforcementEngine
from core.simulation_engine import SimulationEngine
from plugins.llm import BaseLLMPlugin, GeminiPlugin


class IDCAgent:
    """
    Autonomous cognitive agent operating under finite resources and empirical verification.
    """

    def __init__(
        self,
        identity_path: Optional[str] = None,
        memory_dir: Optional[str] = None,
        initial_energy: float = 100.0,
        llm_plugin: Optional[BaseLLMPlugin] = None,
    ):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        id_path = identity_path or os.path.join(base_dir, "memory", "identity", "id.json")
        mem_path = memory_dir or os.path.join(base_dir, "memory")

        self.identity = Identity(id_path)
        self.energy = EnergyManager(energy=initial_energy)
        self.purpose = PurposeFilter()
        self.memory = MemoryManager(mem_path)
        self.curiosity = CuriosityEngine()
        self.causal = CausalEngine()
        self.simulation = SimulationEngine()
        self.reinforcement = ReinforcementEngine()
        self.llm = llm_plugin or GeminiPlugin()

        self.decision = DecisionEngine(
            purpose_filter=self.purpose,
            energy_manager=self.energy,
            memory_manager=self.memory,
            simulation_engine=self.simulation,
        )

        self._active_rules: List[str] = []
        self._total_actions: int = 0
        self._aligned_actions: int = 0

        self.state = AgentState(
            energy=self.energy.available(),
            current_goal="idle",
            active_rules=[],
            active_context={},
            uncertainty=0.0,
            version="0.1.0",
        )

    def run_step(
        self,
        goal: Goal,
        candidate_action: str,
        hypothesis: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentState:
        """
        Executes one full cognitive cycle for a given goal and candidate action.
        Returns the updated AgentState contract.
        """
        context = context or {}
        self._total_actions += 1

        # 1. Update State with Current Goal
        self.state.current_goal = goal.description
        self.state.active_context = context

        # 2. Purpose Filter Check
        if not self.purpose.evaluate(goal.priority):
            goal.state = "rejected"
            self.state.uncertainty = 1.0
            return self._sync_state()

        self._aligned_actions += 1

        # 3. Consult Decision Engine (Evaluates Causal Trash, Proven Rules, and Energy)
        decision_code, rationale, meta = self.decision.decide(
            candidate_action=candidate_action,
            hypothesis=hypothesis,
            context={**context, "goal_score": goal.priority},
        )

        action_cost = meta.get("cost", 2.0)
        uncertainty = 0.1 if decision_code == "EXECUTED_DIRECTLY" else (0.8 if decision_code == "REJECTED" else 0.4)
        self.state.uncertainty = uncertainty

        # 4. Handle Execution / Rejection
        if decision_code == "REJECTED":
            # Record rejection event
            event = ExperienceEvent(
                id=f"event_{self._total_actions:04d}",
                action=candidate_action,
                result=f"REJECTED: {rationale}",
                energy_cost=0.0,
                goal=goal.description,
                confidence=0.0,
            )
            self.memory.record_episode(
                goal=event.goal,
                action=event.action,
                result=event.result,
                energy_cost=event.energy_cost,
                confidence=event.confidence,
                episode_id=event.id,
            )
            return self._sync_state()

        # 5. Execute Action (Deduct Energy)
        self.energy.consume(action_cost)

        # Determine success from context or simulate verified execution
        is_success = context.get("success", True)
        result_str = "SUCCESS" if is_success else "FAILURE"

        # 6. Memory & Learning Consolidation
        event = ExperienceEvent(
            id=f"event_{self._total_actions:04d}",
            action=candidate_action,
            result=result_str,
            energy_cost=action_cost,
            goal=goal.description,
            confidence=0.95 if is_success else 0.1,
        )
        self.memory.record_episode(
            goal=event.goal,
            action=event.action,
            result=event.result,
            energy_cost=event.energy_cost,
            confidence=event.confidence,
            episode_id=event.id,
        )

        if is_success:
            rule_id = f"rule_{abs(hash(candidate_action)) % 10000:04d}"
            rule = CausalRule(
                id=rule_id,
                cause=candidate_action,
                effect=context.get("expected_effect", "goal_achieved"),
                confidence=0.90,
                replications=1,
                conditions=[goal.description],
            )
            self.memory.save_causal_rule(
                rule_id=rule.id,
                cause=rule.cause,
                effect=rule.effect,
                confidence=rule.confidence,
                replications=rule.replications,
                conditions=rule.conditions,
            )
            if rule_id not in self._active_rules:
                self._active_rules.append(rule_id)
            goal.state = "completed"
        else:
            # Register in Causal Trash to prevent repeating failure
            self.memory.record_rejected(
                hypothesis=candidate_action,
                reason=f"Execution failed under {goal.description}",
            )
            goal.state = "failed"

        return self._sync_state()

    def brainstorm(self, goal: Goal, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Uses the connected LLM plugin (Gemini/Ollama) to brainstorm a candidate hypothesis,
        automatically enforcing Causal Trash negative constraints.
        """
        context = context or {}
        rejected = []
        for file in self.memory.trash_dir.glob("*.json"):
            try:
                import json
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "hypothesis" in data:
                        rejected.append(data["hypothesis"])
            except Exception:
                continue

        return self.llm.generate_hypothesis(
            goal=goal.description,
            context=context,
            rejected_hypotheses=rejected,
        )

    def get_metrics(self) -> MetricsModel:
        """Computes and returns the formal IDC cognitive metrics vector."""
        total = max(1, self._total_actions)
        alignment = self._aligned_actions / total
        rules_count = len(self._active_rules)
        energy_spent = max(1.0, 100.0 - self.energy.available())
        efficiency = Metrics.learning_efficiency(rules_count, energy_spent)

        return MetricsModel(
            curiosity_index=0.75,
            replication_index=float(rules_count),
            adaptation_index=Metrics.adaptation_index(0.8, 2),
            innovation_index=0.6,
            purpose_alignment=round(alignment, 2),
            learning_efficiency=round(efficiency, 2),
        )

    def recharge(self, amount: float = 100.0) -> None:
        """Restores agent energy reserves."""
        self.energy.energy = min(100.0, self.energy.energy + amount)
        self.state.energy = self.energy.available()

    def _sync_state(self) -> AgentState:
        """Synchronizes internal agent state attributes with AgentState contract."""
        self.state.energy = self.energy.available()
        self.state.active_rules = list(self._active_rules)
        return self.state
