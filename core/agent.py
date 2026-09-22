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
from core.sandbox import RealSandbox
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
        sandbox: Optional[RealSandbox] = None,
        recall_trauma: bool = False,
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
        self.sandbox = sandbox or RealSandbox()
        self.recall_trauma = recall_trauma

        self.decision = DecisionEngine(
            purpose_filter=self.purpose,
            energy_manager=self.energy,
            memory_manager=self.memory,
            simulation_engine=self.simulation,
        )

        self._active_rules: List[str] = []
        self._total_actions: int = 0
        self._aligned_actions: int = 0
        self._failed_actions_history: Dict[str, List[str]] = {}
        self._last_rl_feedback: Optional[Dict[str, Any]] = None

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

        # 5. Execute Action (Deduct Energy with Mode Stress)
        complexity = context.get("complexity", 1.0)
        consumed = self.energy.consume_action(action_cost, complexity=complexity)

        # Determine success and metrics (either from RealSandbox or from context)
        if context.get("use_sandbox"):
            sandbox_res = self.sandbox.evaluate_strategy(
                action=candidate_action,
                baseline_s=context.get("baseline_s", 45.0),
                is_known_bad=not context.get("success", True),
            )
            is_success = sandbox_res["success"]
            action_cost = sandbox_res["energy_cost"]
            metrics = {
                "baseline_s": sandbox_res["baseline_s"],
                "duration_s": sandbox_res["duration_s"],
                "improvement_pct": sandbox_res["improvement_pct"],
            }
            reason = sandbox_res["reason"]
        else:
            is_success = context.get("success", True)
            metrics = context.get("metrics", {})
            reason = context.get("reason", f"Execution outcome under {goal.description}")

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
            superseded = list(self._failed_actions_history.get(goal.description, []))
            rule = CausalRule(
                id=rule_id,
                goal=goal.description,
                cause=candidate_action,
                effect=context.get("expected_effect", "goal_achieved"),
                successful_action=candidate_action,
                failed_actions_superseded=superseded,
                confidence=0.95,
                replications=1,
                reuses=1,
                conditions=[goal.description],
                metrics_improvement=metrics,
            )
            self.memory.save_causal_rule(
                rule_id=rule.id,
                cause=rule.cause,
                effect=rule.effect,
                confidence=rule.confidence,
                replications=rule.replications,
                conditions=rule.conditions,
                goal=rule.goal,
                successful_action=rule.successful_action,
                failed_actions_superseded=rule.failed_actions_superseded,
                metrics_improvement=rule.metrics_improvement,
                reuses=rule.reuses,
            )
            if rule_id not in self._active_rules:
                self._active_rules.append(rule_id)
            goal.state = "completed"
        else:
            if goal.description not in self._failed_actions_history:
                self._failed_actions_history[goal.description] = []
            if candidate_action not in self._failed_actions_history[goal.description]:
                self._failed_actions_history[goal.description].append(candidate_action)

            # Register in Causal Trash to prevent repeating failure
            self.memory.record_rejected(
                hypothesis=candidate_action,
                reason=reason,
                goal=goal.description,
                metrics=metrics,
            )
            goal.state = "failed"

        # 7. Reinforcement Learning Evaluation & Adaptive Feedback
        innovation_index = Metrics.innovation_index(
            unique_actions_explored=self._total_actions,
            rejected_constraints=len(self._failed_actions_history.get(goal.description, [])),
        )
        self._last_rl_feedback = self.reinforcement.evaluate_learning(
            action=candidate_action,
            result=result_str,
            energy_used=consumed,
            purpose_alignment=self._aligned_actions / max(1, self._total_actions),
            replications=1,
            mode=self.energy.mode(),
            complexity=complexity,
            innovation_index=innovation_index,
        )

        return self._sync_state()

    def brainstorm(
        self,
        goal: Goal,
        context: Optional[Dict[str, Any]] = None,
        force_llm: bool = False,
        recall_trauma: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes or retrieves an action hypothesis for the given goal.
        Follows IDC's Core Principle:
          1. CAUSAL MEMORY FIRST: If a proven empirical rule exists (confidence >= 0.7),
             return it directly. Zero tokens, zero LLM calls, zero hallucinations.
          2. LLM BRAINSTORMING SECOND: If novel, query Gemini/Ollama with Causal Trash constraints.
          3. ON-DEMAND TRAUMA RECALL ("Dejar de temer a la muerte"):
             By default, systemic existential trauma is dormant. Only recalled on explicit demand.
        """
        context = context or {}
        should_recall_trauma = self.recall_trauma if recall_trauma is None else recall_trauma

        # 1. Causal Memory Short-Circuit (Zero Token Retrieval)
        if not force_llm:
            proven_rule = self.memory.find_proven_rule_for_goal(goal.description)
            if proven_rule:
                action = proven_rule.get("successful_action") or proven_rule.get("cause")
                rule_id = proven_rule.get("id", "causal_rule")
                return {
                    "action": action,
                    "hypothesis": f"Reusing verified causal rule '{rule_id}': {proven_rule.get('cause')}",
                    "from_causal_memory": True,
                    "rule_id": rule_id,
                    "confidence": proven_rule.get("confidence", 0.95),
                    "tokens_saved": True,
                    "rejected_hypotheses": [],
                }

        # 2. LLM Brainstorming with Causal Trash negative constraints
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

        # 3. Dual Trauma Trigger: On-Demand OR Autonomic Metabolic Stress Reflex
        # By default, systemic trauma is dormant ("dejar de temer a la muerte").
        # However, if metabolic stress exceeds critical threshold (stress_factor >= 2.2 or SURVIVAL mode),
        # the agent automatically triggers an involuntary trauma flashback to preserve survival.
        stress_critical = (self.energy.stress_factor() >= 2.2) or (self.energy.mode() == "SURVIVAL")
        active_trauma_recall = should_recall_trauma or stress_critical

        if active_trauma_recall:
            traumas = self.memory.recall_systemic_traumas(on_demand=True)
            for t in traumas:
                chain = t.get("fatal_actions_chain") or t.get("fatal_actions") or []
                for fatal in chain:
                    if fatal not in rejected:
                        rejected.append(fatal)
                last_mutation = t.get("survival_mutation")
                if last_mutation and last_mutation not in rejected:
                    rejected.append(last_mutation)

        res = self.llm.generate_hypothesis(
            goal=goal.description,
            context=context,
            rejected_hypotheses=rejected,
        )
        res["from_causal_memory"] = False
        res["tokens_saved"] = False
        return res

    def get_metrics(self) -> MetricsModel:
        """Computes and returns the formal IDC cognitive metrics vector."""
        total = max(1, self._total_actions)
        alignment = self._aligned_actions / total
        rules_count = len(self._active_rules)
        energy_spent = max(1.0, 100.0 - self.energy.available())
        efficiency = Metrics.learning_efficiency(rules_count, energy_spent)
        total_failed_constraints = sum(len(v) for v in self._failed_actions_history.values())
        innov_index = Metrics.innovation_index(self._total_actions, total_failed_constraints)

        return MetricsModel(
            curiosity_index=0.75,
            replication_index=float(rules_count),
            adaptation_index=Metrics.adaptation_index(0.8, 2),
            innovation_index=innov_index,
            purpose_alignment=round(alignment, 2),
            learning_efficiency=round(efficiency, 2),
        )

    def recharge(self, amount: float = 100.0) -> None:
        """Restores agent energy reserves."""
        self.energy.recharge(amount)
        self.state.energy = self.energy.available()

    def _sync_state(self) -> AgentState:
        """Synchronizes internal agent state attributes with AgentState contract."""
        self.state.energy = self.energy.available()
        self.state.active_rules = list(self._active_rules)
        return self.state
