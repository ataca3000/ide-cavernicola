"""
IDC Contracts - Metrics Contract
Defines the quantitative evaluation vector measuring agent adaptation, curiosity, and efficiency.
"""

from pydantic import BaseModel, Field


class MetricsModel(BaseModel):
    """
    Representation of the IDC cognitive metrics vector.
    """
    curiosity_index: float = Field(default=0.0, ge=0.0, le=1.0, description="IC = Valid Questions / Total Inquiries")
    replication_index: float = Field(default=0.0, ge=0.0, description="IR = Successful Replications")
    adaptation_index: float = Field(default=0.0, ge=0.0, description="IA = Delta Confidence / Required Cycles")
    innovation_index: float = Field(default=0.0, ge=0.0, description="II = Useful Hypotheses / Total Generated")
    purpose_alignment: float = Field(default=1.0, ge=0.0, le=1.0, description="IP = Purpose-Aligned Decisions / Total Actions")
    learning_efficiency: float = Field(default=0.0, ge=0.0, description="LE = Verified Rules / Energy Spent")
