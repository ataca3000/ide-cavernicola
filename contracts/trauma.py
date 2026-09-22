"""
IDC Contracts - Systemic Trauma & Existential Collapse Model
Strict Pydantic contract capturing fatal cascades, hardware lockdowns,
and metabolic energy collapse telemetry.
Authored by Luis Felipe Durán Salinas (ATACA3000 / Brecha Soluciones DS).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HardwareTelemetry(BaseModel):
    """Snapshot of execution environment and hardware state during crisis."""
    os_name: str = Field(default="unknown")
    python_version: str = Field(default="unknown")
    memory_stress: Optional[float] = Field(default=None, description="Memory pressure or stress factor")
    hardware_lockdown: bool = Field(default=True, description="Indicates whether physical constraints blocked execution")
    cpu_cores: Optional[int] = Field(default=None)


class SystemicTrauma(BaseModel):
    """
    Formal contract for a catastrophic existential failure or hardware lockdown.
    Preserved in memory/identity/systemic_traumas.json and recalled only on demand
    or when metabolic stress exceeds critical survival thresholds.
    """
    trauma_id: str = Field(..., description="Unique identifier for the systemic failure")
    timestamp: str = Field(..., description="ISO UTC timestamp of the collapse")
    trigger_goal: str = Field(..., description="The objective being pursued when collapse occurred")
    environment_verdict: str = Field(default="HARDWARE_LOCKDOWN", description="Verdict that terminated the agent")
    fatal_actions_chain: List[str] = Field(default_factory=list, description="Ordered sequence of failed actions in the cascade")
    survival_mutation: Optional[str] = Field(default=None, description="Last emergency action attempted before system blackout")
    stress_factor: float = Field(default=3.0, description="Metabolic stress factor at the moment of collapse")
    energy_depleted: float = Field(default=100.0, description="Total energy drained during the crisis")
    hardware_telemetry: HardwareTelemetry = Field(default_factory=HardwareTelemetry)
    metadata: Dict[str, Any] = Field(default_factory=dict)
