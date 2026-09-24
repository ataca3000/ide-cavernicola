"""
IDC (Inventor Driven Cognition) - Production Energy Manager
Coordinates dynamic resource allocation, metabolic stress scaling across operational modes
(Exploration, Optimization, Survival), and finite battery depletion.
Authored by Luis Felipe Durán Salinas (ATACA3000 / Brecha Soluciones DS).
"""

from typing import Any, Dict


class EnergyManager:
    """
    Manages energy reserves and operational thresholds:
      - EXPLORATION (> 20%): Baseline cost (1.0x). High curiosity and creative divergence.
      - OPTIMIZATION (5% - 20%): Stress multiplier (1.25x). Severe penalty for complexity.
      - SURVIVAL (<= 5%): Emergency burnout (1.5x). State preservation and panic pulse.
    """

    def __init__(self, energy: float = 100.0, max_energy: float = 100.0):
        self.max_energy = float(max_energy)
        self.energy = float(min(self.max_energy, energy))

    def consume(self, amount: float) -> float:
        """Original direct consumption method."""
        consumed = min(self.energy, max(0.0, float(amount)))
        self.energy = max(0.0, self.energy - consumed)
        return consumed

    def consume_action(self, base_cost: float, complexity: float = 1.0) -> float:
        """
        Consumes energy taking into account operational mode and cognitive stress.
        Under low energy, panic and friction consume more metabolic burn.
        """
        mode = self.mode()
        if mode == "SURVIVAL":
            mode_mult = 1.5
        elif mode == "OPTIMIZATION":
            mode_mult = 1.25
        else:
            mode_mult = 1.0

        effective_cost = base_cost * mode_mult * max(0.5, complexity)
        return self.consume(effective_cost)

    def recharge(self, amount: float = 100.0) -> float:
        """Restores energy up to max_energy."""
        old = self.energy
        self.energy = min(self.max_energy, self.energy + float(amount))
        return self.energy - old

    def available(self) -> float:
        """Returns available energy percentage/units."""
        return round(self.energy, 2)

    def can_afford(self, amount: float) -> bool:
        """Checks if agent can afford an action."""
        return self.energy >= amount

    def is_depleted(self) -> bool:
        """Returns True if energy is 0.0 (system collapse)."""
        return self.energy <= 0.0

    def stress_factor(self) -> float:
        """
        Computes dynamic stress factor from 1.0 (calm at 100%) to 3.0 (desperate near 0%).
        """
        burnout = (self.max_energy - self.energy) / max(1.0, self.max_energy)
        return round(1.0 + burnout * 2.0, 2)

    def mode(self) -> str:
        """
        Returns operational mode based on thermodynamic thresholds:
          - SURVIVAL: <= 5%
          - OPTIMIZATION: <= 20%
          - EXPLORATION: > 20%
        """
        if self.energy <= 5.0:
            return "SURVIVAL"
        if self.energy <= 20.0:
            return "OPTIMIZATION"
        return "EXPLORATION"

    def telemetry(self) -> Dict[str, Any]:
        """Produces real-time energy telemetry."""
        return {
            "energy": self.available(),
            "mode": self.mode(),
            "stress_factor": self.stress_factor(),
            "is_depleted": self.is_depleted(),
        }
