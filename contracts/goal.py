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
    deadline: Optional[str] = Field(default=None, description="Optional time constraint or deadline")
    state: str = Field(default="active", description="Lifecycle state: 'active', 'completed', 'rejected', 'paused'")
