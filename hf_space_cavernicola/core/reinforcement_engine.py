"""
IDC (Inventor Driven Cognition) - Reinforcement Engine (v0.5 Production RL)
Calculates reward functions, updates confidence, and adapts agent behavior
under finite energy constraints across operational modes (Exploration, Optimization, Survival).
Authored by Luis Felipe Durán Salinas (ATACA3000 / Brecha Soluciones DS).
"""

from typing import Any, Dict


class ReinforcementEngine:
    """
    Evaluates learning feedback and computes rewards to reinforce or penalize causal actions.
    Adapts dynamic weights based on operational mode:
      - EXPLORATION: Rewards bold innovation and curiosity ("sin miedo a la muerte").
      - OPTIMIZATION: Rewards pragmatic cost reduction and pipeline acceleration.
      - SURVIVAL: Severely penalizes complexity and energy waste; rewards state preservation.
    """

    def calculate_reward(
        self,
        success: bool,
        efficiency: float,
        replications: int,
        purpose_alignment: float,
        energy_cost: float,
        complexity: float = 1.0,
        mode: str = "EXPLORATION",
        innovation_index: float = 1.0,
    ) -> float:
        """
        Computes mode-aware IDC reward value:
        Reward = Success + Efficiency + Replication + Purpose Alignment + Innovation Bonus - Mode Cost Penalty - Complexity
        """
        # 1. Base Success / Failure Score
        if success:
            success_val = 15.0 if mode == "SURVIVAL" else 10.0
        else:
            success_val = -20.0 if mode == "SURVIVAL" else -10.0

        # 2. Efficiency & Replications
        efficiency_val = efficiency * 5.0
        replication_val = min(5.0, replications * 0.2)
        alignment_val = purpose_alignment * 5.0

        # 3. Innovation Bonus ("Sin miedo a la muerte")
        # In Exploration mode, bold divergence from Causal Trash is heavily rewarded
        if mode == "EXPLORATION":
            innovation_bonus = innovation_index * 3.0
            cost_penalty = energy_cost * 0.3
            complexity_penalty = complexity * 0.4
        elif mode == "OPTIMIZATION":
            innovation_bonus = innovation_index * 1.5
            cost_penalty = energy_cost * 1.0
            complexity_penalty = complexity * 1.2
        else:  # SURVIVAL MODE
            # In Survival mode, unnecessary complexity is lethal
            innovation_bonus = innovation_index * 0.5
            cost_penalty = energy_cost * 2.5
            complexity_penalty = complexity * 2.5

        raw_reward = (
            success_val
            + efficiency_val
            + replication_val
            + alignment_val
            + innovation_bonus
            - cost_penalty
            - complexity_penalty
        )
        return round(raw_reward, 2)

    def evaluate_learning(
        self,
        action: str,
        result: str,
        energy_used: float,
        purpose_alignment: float = 1.0,
        replications: int = 1,
        mode: str = "EXPLORATION",
        complexity: float = 1.0,
        innovation_index: float = 1.0,
    ) -> Dict[str, Any]:
        """Processes an execution episode and produces learning telemetry and adaptation delta."""
        is_success = (result.upper() == "SUCCESS")
        efficiency = 1.0 / max(0.5, energy_used)

        reward = self.calculate_reward(
            success=is_success,
            efficiency=efficiency,
            replications=replications,
            purpose_alignment=purpose_alignment,
            energy_cost=energy_used,
            complexity=complexity,
            mode=mode,
            innovation_index=innovation_index,
        )

        # Dynamic adaptation delta based on mode and outcome
        if is_success:
            delta = 0.08 if mode == "EXPLORATION" else 0.05
        else:
            delta = -0.20 if mode == "SURVIVAL" else (-0.12 if mode == "OPTIMIZATION" else -0.06)

        return {
            "action": action,
            "success": is_success,
            "mode": mode,
            "reward": reward,
            "innovation_index": innovation_index,
            "adaptation_delta": round(delta, 2),
            "recommended_action": "REINFORCE" if is_success else "RECORD_IN_TRASH",
        }
