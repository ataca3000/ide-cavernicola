"""
IDC Core - Tenacity Loop (Bucle de Tenacidad Autónoma)
Implements the human inventor persistence cycle:
  1. Hypothesis: '¿Y si lo hago así?' -> HypotheticalMemory
  2. Reality trial: Sandbox or physical actuation
  3. Learning on failure: 'Ah okey, entonces así no' -> CausalTrash (never repeated)
  4. External consultation: Query observer/ConceptNet if uncertainty persists
  5. Mutation: Adaptive parameter adjustment
  6. Persistence: Never stops until empirical victory is achieved
  7. Success: Promotes winning strategy into CitableLogicalMemory with SHA256 proof
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from contracts.goal import Goal
from contracts.memory_library import CitableLogicalMemory, HypotheticalMemory
from core.agent import IDCAgent
from core.commonsense_engine import CommonsenseEngine


class TenacityResolver:
    """
    Autonomous goal resolver governed by tenacious trial, failure categorization,
    observer consultation, and causal memory consolidation.
    """

    def __init__(
        self,
        agent: IDCAgent,
        commonsense: Optional[CommonsenseEngine] = None,
        max_attempts: int = 15,
    ):
        self.agent = agent
        self.commonsense = commonsense or CommonsenseEngine(vault=agent.vault, reality=agent.reality)
        self.max_attempts = max_attempts

        self.history: List[Dict[str, Any]] = []

    def solve(
        self,
        goal: Goal,
        environment_actuator: Callable[[str, Dict[str, Any]], Tuple[bool, str, Dict[str, Any]]],
        initial_context: Optional[Dict[str, Any]] = None,
        observer_oracle: Optional[Callable[[str, str], str]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the tenacity resolution loop.
        environment_actuator(action, context) -> (success: bool, outcome_log: str, telemetry: dict)
        """
        context = dict(initial_context or {})
        attempts = 0
        failed_lessons: List[str] = []

        while attempts < self.max_attempts:
            attempts += 1

            # 1. Sensory Perception & Common Sense Check
            vision_detections = context.get("vision_detections", [])
            telemetry = context.get("telemetry", {})
            scene_analysis = self.commonsense.interpret_sensory_scene(vision_detections, telemetry)

            # Auto-mount recommended reality domains based on scene common sense
            for domain_str in scene_analysis["recommended_domains"]:
                try:
                    from contracts.reality import DomainType
                    self.agent.mount_reality(DomainType(domain_str))
                except Exception:
                    pass

            # 2. Formulate Hypothesis: '¿Y si lo hago así?'
            mutant_proposal = self.agent.generate_mutant_action(goal, context)
            candidate_action = mutant_proposal["action"]
            hypo_id = mutant_proposal.get("hypothetical_id")

            # Check if proposal is blocked by common sense restrictions or reality laws
            if not mutant_proposal["valid_reality"]:
                # 'Ah okey, entonces así no': record law violation into Causal Trash
                self.agent.memory.record_rejected(
                    hypothesis=f"Action '{candidate_action}' violates reality law: {mutant_proposal.get('violation_reason')}",
                    reason="Reality Law Invariant Breach",
                    goal=goal.description,
                    metrics=context,
                )
                failed_lessons.append(f"Intento {attempts} [Fallo Ley]: {mutant_proposal.get('violation_reason')}")
                continue

            # 3. Reality Trial: Execute candidate action in environment
            trial_res = environment_actuator(candidate_action, context)
            if isinstance(trial_res, tuple) and len(trial_res) == 3:
                outcome, outcome_log, telemetry_feedback = trial_res
            else:
                outcome, outcome_log, telemetry_feedback = trial_res[0], trial_res[1], {}

            context["telemetry"] = telemetry_feedback

            # Determine empirical score (supports float score or bool)
            if isinstance(outcome, bool):
                empirical_score = 0.75 if outcome else 0.30
                is_viable = outcome
            else:
                empirical_score = float(outcome)
                is_viable = goal.is_achieved_and_stable(empirical_score)

            # 4. Evaluation of Outcome: Reached, Stable and Safe (65% - 70%)
            if is_viable:
                goal.state = "completed"
                citable = self.agent.promote_hypothesis_to_citable(
                    hypothetical_id=hypo_id,
                    claim=f"Action '{candidate_action}' achieves goal '{goal.description}' with empirical score {empirical_score}",
                    domain=self.agent.reality.mounted_domains[0].value if self.agent.reality.mounted_domains else "general",
                    citation_source=f"tenacity_loop_attempt_{attempts}",
                    empirical_log=f"{outcome_log} [score={empirical_score}]",
                    conditions=list(context.keys()),
                )
                self.agent.mutant_engine.reinforce_mutation(hypo_id, success=True, reward=empirical_score)

                return {
                    "solved": True,
                    "status": "ALCANZADO_ESTABLE_Y_SEGURO",
                    "empirical_score": empirical_score,
                    "stability_threshold": goal.stability_threshold,
                    "ideal_target": goal.target_ideal,
                    "attempts": attempts,
                    "winning_action": candidate_action,
                    "citable_memory_id": citable.id,
                    "proof_hash": citable.proof_hash,
                    "failed_attempts_overcome": failed_lessons,
                    "scene_analysis": scene_analysis,
                }
            else:
                # 'Ah okey, entonces así no': catalog failure in Causal Trash
                self.agent.memory.record_rejected(
                    hypothesis=f"Action '{candidate_action}' under context {context}",
                    reason=f"Environment failure (score {empirical_score} < {goal.stability_threshold}): {outcome_log}",
                    goal=goal.description,
                    metrics=context,
                )
                failed_lessons.append(f"Intento {attempts} [Fallo Ejecución]: {candidate_action} -> {outcome_log}")
                self.agent.mutant_engine.reinforce_mutation(hypo_id, success=False, reward=-0.5)

                # 5. External Observer Consultation (if available)
                if observer_oracle:
                    advice = observer_oracle(candidate_action, outcome_log)
                    context["observer_advice"] = advice
                    context["target_subsystem"] = f"adapted_{attempts}"

        return {
            "solved": False,
            "attempts": attempts,
            "failed_attempts": failed_lessons,
            "reason": "Exceeded maximum tenacity attempts without empirical success",
        }
