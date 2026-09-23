"""
IDC Core - Mutant Action Engine
Adaptive decision-making engine:
Generates mutating action strategies influenced by reinforcement feedback.
Blends active 'Recuerdos Lógicos Citables' and 'Recuerdos Hipotéticos'
under the strict invariants enforced by mounted 'Librerías de Realidad'.
"""

import random
from typing import Any, Dict, List, Optional
from contracts.goal import Goal
from contracts.memory_library import CitableLogicalMemory, HypotheticalMemory
from core.citable_memory_vault import CitableMemoryVault
from core.reality_loader import RealityLoader


class MutantActionEngine:
    """
    Mutant Decision Engine.
    Evolves candidate action policies through parameter mutation,
    cross-breeding citable logical memories with hypothetical conjectures,
    strictly bounded by active reality laws.
    """

    def __init__(
        self,
        vault: CitableMemoryVault,
        reality_loader: RealityLoader,
        base_mutation_rate: float = 0.2,
    ):
        self.vault = vault
        self.reality = reality_loader
        self.mutation_rate = base_mutation_rate

        # Evolving decision genome: adaptive heuristic hyperparameters
        self.policy_genome: Dict[str, float] = {
            "exploration_drive": 0.4,
            "risk_tolerance": 0.3,
            "energy_conservation": 0.7,
            "citable_prior_bias": 0.8,
        }

        self._generation: int = 0
        self._successful_mutations: int = 0
        self._rejected_mutations: int = 0

    def generate_mutant_action(
        self,
        goal: Goal,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes a candidate action by mutating policy hyperparameters,
        citing verified logical memories, and validating against mounted reality laws.
        """
        context = context or {}
        self._generation += 1

        # 1. Select relevant citable memories based on active mounted domains
        cited_memories: List[CitableLogicalMemory] = []
        for domain in self.reality.mounted_domains:
            cited_memories.extend(self.vault.query_citable_by_domain(domain.value))

        citations = [self.vault.cite_memory(m.id) for m in cited_memories[:3]]

        # 2. Mutate policy genome based on current mutation rate
        mutated_genome = self._mutate_genome()

        # 3. Formulate a mutant action candidate
        action_name = self._formulate_action_name(goal, mutated_genome, context)

        # 4. Reality Law Gate: Validate action against mounted domains
        is_valid, violation_reason = self.reality.validate_action(
            action_name,
            parameters=context
        )

        if not is_valid:
            self._rejected_mutations += 1
            # Adjust mutation away from violation
            self.policy_genome["risk_tolerance"] = max(0.05, self.policy_genome["risk_tolerance"] - 0.05)
            return {
                "action": "fallback_safe_observation",
                "valid_reality": False,
                "violation_reason": violation_reason,
                "mutated_genome": mutated_genome,
                "generation": self._generation,
                "citations": citations,
            }

        # 5. Record the exploratory action as a Hypothetical Memory
        hypo = self.vault.record_hypothetical(
            conjecture=f"Action '{action_name}' achieves goal '{goal.description}' with genome {mutated_genome}",
            derived_from_rules=[m.id for m in cited_memories[:3]],
            mutant_parameters=mutated_genome,
            plausibility_score=round(1.0 - (mutated_genome["risk_tolerance"] * 0.5), 2),
        )

        return {
            "action": action_name,
            "valid_reality": True,
            "hypothetical_id": hypo.id,
            "mutated_genome": mutated_genome,
            "generation": self._generation,
            "citations": [c for c in citations if c],
        }

    def _mutate_genome(self) -> Dict[str, float]:
        """Applies stochastic mutation within bounds [0.05, 0.95]."""
        new_genome = {}
        for k, v in self.policy_genome.items():
            if random.random() < self.mutation_rate:
                delta = random.uniform(-0.1, 0.1)
                new_genome[k] = round(max(0.05, min(0.95, v + delta)), 3)
            else:
                new_genome[k] = v
        return new_genome

    def _formulate_action_name(
        self,
        goal: Goal,
        genome: Dict[str, float],
        context: Dict[str, Any],
    ) -> str:
        """Formulates the candidate action identifier reflecting mutated parameters."""
        prefix = "exploit" if genome["exploration_drive"] < 0.5 else "explore"
        focus = context.get("target_subsystem", "system_state")
        return f"{prefix}_{focus}_under_{goal.description.replace(' ', '_')}"

    def reinforce_mutation(self, hypothetical_id: str, success: bool, reward: float) -> None:
        """
        Feedback loop: learning modifies the genome.
        Successful mutations consolidate; unsuccessful mutations push genome toward caution.
        """
        hypo = self.vault.get_hypothetical(hypothetical_id)
        if not hypo:
            return

        if success:
            self._successful_mutations += 1
            # Reinforce successful genome
            for k, v in hypo.mutant_parameters.items():
                self.policy_genome[k] = round(0.8 * self.policy_genome[k] + 0.2 * v, 3)
            # Increase confidence
            hypo.sandbox_success_rate = min(1.0, hypo.sandbox_success_rate + 0.2)
        else:
            self._rejected_mutations += 1
            # Decrease risk tolerance on failure
            self.policy_genome["risk_tolerance"] = max(0.05, round(self.policy_genome["risk_tolerance"] * 0.9, 3))
            self.policy_genome["energy_conservation"] = min(0.95, round(self.policy_genome["energy_conservation"] * 1.1, 3))

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "generation": self._generation,
            "successful_mutations": self._successful_mutations,
            "rejected_mutations": self._rejected_mutations,
            "current_genome": self.policy_genome,
            "mutation_rate": self.mutation_rate,
        }
