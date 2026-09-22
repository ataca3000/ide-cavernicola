"""
IDC Contracts - Experience Event Contract
Defines atomic episodic records of agent actions and observed outcomes.
"""

from pydantic import BaseModel, Field


class ExperienceEvent(BaseModel):
    """
    Representation of an episodic memory event.
    """
    id: str = Field(..., description="Unique event identifier")
    action: str = Field(..., description="Action undertaken by the agent")
    result: str = Field(..., description="Direct observation or outcome")
    energy_cost: float = Field(default=1.0, ge=0.0, description="Energy consumed during action execution")
    goal: str = Field(..., description="Target goal associated with this action")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence in the outcome assessment")
