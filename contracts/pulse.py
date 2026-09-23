"""
IDC Contracts - Pulse & Reaction Contract
Defines bio-physical electrical/current pulses, real-time telemetry signals,
and fast-path pre-cached reflex reaction rules.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import time
import uuid


class ReactionPulse(BaseModel):
    """
    Bio-physical current or real-time telemetry pulse signal.
    Processed in volatile RAM cache without disk persistence.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel: str = Field(..., description="Sensor or bus channel name (e.g. 'voltage_rail', 'thermal_spike', 'network_io')")
    amplitude: float = Field(..., description="Magnitude of the signal/pulse")
    frequency: float = Field(default=1.0, description="Pulse frequency in Hz")
    gradient: float = Field(default=0.0, description="Rate of change (first derivative) of the signal")
    timestamp: float = Field(default_factory=time.time, description="High-resolution epoch timestamp")
    criticality: float = Field(default=0.0, ge=0.0, le=1.0, description="Calculated urgency/threat level")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw sensory telemetry payload")


class PulseReactionRule(BaseModel):
    """
    Pre-cached condition-to-reflex mapping held in volatile RAM for O(1) response.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel: str = Field(..., description="Target channel to monitor")
    threshold_amplitude: float = Field(..., description="Threshold beyond which reflex triggers")
    trigger_condition: str = Field(default="gt", description="Condition: 'gt', 'lt', 'gradient_spike'")
    reflex_action: str = Field(..., description="Deterministic reflex action to trigger immediately")
    cooldown_ms: float = Field(default=50.0, description="Cooldown between triggers in milliseconds")
    energy_cost: float = Field(default=0.05, description="Low energetic cost of involuntary reaction")
    active: bool = Field(default=True, description="Whether rule is currently pre-cached in RAM")


class ReflexResponse(BaseModel):
    """
    Immediate involuntary output produced by the PulseReactionEngine.
    """
    triggered: bool = Field(default=False)
    rule_id: Optional[str] = Field(default=None)
    action: Optional[str] = Field(default=None)
    latency_ms: float = Field(default=0.0, description="Execution latency in milliseconds (target < 2ms)")
    energy_cost: float = Field(default=0.0)
    triggering_pulse_id: Optional[str] = Field(default=None)
    reason: Optional[str] = Field(default=None)
