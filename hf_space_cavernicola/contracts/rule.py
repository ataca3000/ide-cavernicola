"""
IDC Contracts - Causal Rule Contract
Defines versioned, verified causal rules derived from experiences and empirical tests,
including cumulative linkage to previous failed actions that this rule superseded.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CausalRule(BaseModel):
    """
    Representation of an empirical causal rule with cumulative memory:
    stores the successful action, confidence, and the failed actions it superseded.
    """
    id: str = Field(..., description="Unique rule identifier")
    version: str = Field(default="1.0.0", description="Semantic rule version")
    goal: str = Field(default="", description="Objective this rule fulfills")
    cause: str = Field(..., description="Hypothesized or verified trigger/action")
    effect: str = Field(..., description="Observed consequence")
    successful_action: Optional[str] = Field(default=None, description="Exact successful action executed")
    failed_actions_superseded: List[str] = Field(
        default_factory=list,
        description="List of previously failed actions for this goal that this rule overcame"
    )
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence rating from 0.0 to 1.0")
    replications: int = Field(default=1, ge=0, description="Number of independent successful replications")
    reuses: int = Field(default=0, ge=0, description="Number of times this rule was reused in production")
    conditions: List[str] = Field(default_factory=list, description="Contextual prerequisites for rule validity")
    metrics_improvement: Dict[str, Any] = Field(
        default_factory=dict,
        description="Quantitative improvements achieved (e.g. latency delta, memory reduction)"
    )
