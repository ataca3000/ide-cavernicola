"""
IDC Contracts - Goal Contract
Defines goals submitted to or originated within an IDC Agent.
"""

from typing import Optional
from pydantic import BaseModel, Field


class Goal(BaseModel):
    """
    Representation of an intentional objective with priority and lifecycle status.
    """
    id: str = Field(..., description="Unique goal identifier")
    description: str = Field(..., description="Actionable goal statement")
    priority: float = Field(default=0.5, ge=0.0, le=1.0, description="Priority score from 0.0 to 1.0")
    state: str = Field(default="active", description="Lifecycle state: 'active', 'completed', 'rejected', 'paused'")
    target_ideal: float = Field(default=1.0, description="Ideal target benchmark (100% theoretical perfection)")
    stability_threshold: float = Field(
        default=0.68,
        ge=0.5,
        le=1.0,
        description="Empirical reality threshold (65%-70%) to declare goal reached, stable, and safe"
    )

    def is_achieved_and_stable(self, empirical_score: float) -> bool:
        """Evaluates whether an empirical result meets the realistic viability threshold."""
        return empirical_score >= self.stability_threshold

