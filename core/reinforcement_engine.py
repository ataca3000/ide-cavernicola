"""
IDC (Inventor Driven Cognition) - Reinforcement Engine (v0.4 Learning)
Calculates reward functions, updates confidence, and optimizes
agent efficiency under finite resource constraints.
Reward = Success + Efficiency + Replication + Purpose Alignment - Energy Cost - Complexity
"""

from typing import Dict, Any


class ReinforcementEngine:
    """
    Evaluates learning feedback and computes rewards
    to reinforce or penalize causal actions.
    """

    def calculate_reward(
        self,
        success: bool,
        efficiency: float,
        replications: int,
        purpose_alignment: float,
        energy_cost: float,
        complexity: float = 1.0
    ) -> float:
        """
        Computes formal IDC reward value:
        Reward = Success + Efficiency + Replication + Purpose Alignment - Energy Cost - Complexity
        """
        success_val = 10.0 if success else -10.0
        efficiency_val = efficiency * 5.0
        replication_val = min(5.0, replications * 0.1)
        alignment_val = purpose_alignment * 5.0
        cost_penalty = energy_cost * 0.5
        complexity_penalty = complexity * 0.5

        raw_reward = (
            success_val
            + efficiency_val
            + replication_val
            + alignment_val
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
        replications: int = 1
    ) -> Dict[str, Any]:
        """Processes an execution episode and produces learning telemetry."""
        is_success = (result.lower() == "success")
        efficiency = 1.0 / max(1.0, energy_used)
        reward = self.calculate_reward(
            success=is_success,
            efficiency=efficiency,
            replications=replications,
            purpose_alignment=purpose_alignment,
            energy_cost=energy_used
        )
        
        return {
            "action": action,
            "success": is_success,
            "reward": reward,
            "adaptation_delta": 0.05 if is_success else -0.10,
            "recommended_action": "REINFORCE" if is_success else "RECORD_IN_TRASH"
        }
