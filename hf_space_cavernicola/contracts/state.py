"""
IDC Contracts - State Contract
Defines the unified state of an IDC Agent at any point during its cognitive lifecycle.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """
    Unified representation of an IDC agent's internal and cognitive state.
    """
    energy: float = Field(..., description="Available energy units (0 to 100)")
    current_goal: str = Field(..., description="Active goal description or identifier")
    active_rules: List[str] = Field(default_factory=list, description="IDs of causal rules actively applied")
    active_context: Dict[str, Any] = Field(default_factory=dict, description="Working environment context")
    uncertainty: float = Field(default=0.0, ge=0.0, le=1.0, description="Calibrated uncertainty score (0.0 to 1.0)")
    version: str = Field(default="0.1.0", description="Schema/agent version")
