"""
IDC Contracts - Causal Trash Entry Contract
Defines structured negative memory records to prevent repeating failed actions.
"""

import time
from typing import Any, Dict
from pydantic import BaseModel, Field


class CausalTrashEntry(BaseModel):
    """
    Representation of an action rejected by reality, recording the context,
    failure reason, and comparative performance metrics.
    """
    id: str = Field(..., description="Unique trash entry identifier")
    goal: str = Field(..., description="Target objective during failure")
    failed_action: str = Field(..., description="Candidate action that caused the failure or degradation")
    reason: str = Field(..., description="Root cause of failure or performance regression")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Quantitative telemetry (e.g. before/after duration)")
    rejected_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
