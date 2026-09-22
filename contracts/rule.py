"""
IDC Contracts - Causal Rule Contract
Defines versioned, verified causal rules derived from experiences and empirical tests.
"""

from typing import List
from pydantic import BaseModel, Field


class CausalRule(BaseModel):
    """
    Representation of an empirical causal rule (Cause -> Effect) with confidence and conditions.
    """
    id: str = Field(..., description="Unique rule identifier")
    version: str = Field(default="1.0.0", description="Semantic rule version")
    cause: str = Field(..., description="Hypothesized or verified trigger/action")
    effect: str = Field(..., description="Observed consequence")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence rating from 0.0 to 1.0")
    replications: int = Field(default=1, ge=0, description="Number of independent successful replications")
    conditions: List[str] = Field(default_factory=list, description="Contextual prerequisites for rule validity")
