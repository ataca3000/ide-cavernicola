"""
IDC Contracts - Selective Memory Libraries
Defines 'Recuerdos Lógicos Citables' (Immutable, verifiable empirical facts with cryptographic proof)
and 'Recuerdos Hipotéticos' (Volatile, counterfactual sandbox inferences).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class CitableLogicalMemory(BaseModel):
    """
    Recuerdo Lógico Citable:
    Empirically verified, immutable knowledge backed by citations,
    reproducible proof hashes, and formal conditions.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    claim: str = Field(..., description="The verified statement or empirical fact (e.g. 'Ohm: V = I * R')")
    domain: str = Field(..., description="Domain of applicability (e.g. 'physics', 'cyberphysical')")
    citation_source: str = Field(..., description="Authoritative origin, theorem name, or sandbox run ID")
    proof_hash: str = Field(..., description="Cryptographic SHA256 of the verification log or reproducible experiment")
    axioms: List[str] = Field(default_factory=list, description="Underlying mathematical/physical axioms")
    conditions: List[str] = Field(default_factory=list, description="Boundary conditions where this claim holds")
    empirical_confirmations: int = Field(default=1, ge=1, description="Number of times confirmed in real runs")
    created_at: float = Field(default_factory=time.time)
    reusable_count: int = Field(default=0, description="Times cited by mutant action decisions")


class HypotheticalMemory(BaseModel):
    """
    Recuerdo Hipotético:
    Volatile counterfactual conjecture ('What-if' models) generated during
    mutation or sandbox simulation. Unproven until verified empirically.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conjecture: str = Field(..., description="Unverified hypothesis or novel action-effect proposal")
    derived_from_rules: List[str] = Field(default_factory=list, description="IDs of citable memories or causal rules blended")
    mutant_parameters: Dict[str, Any] = Field(default_factory=dict, description="Genetic/mutant parameter mutations applied")
    plausibility_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Heuristic plausibility prior to execution")
    simulation_runs: int = Field(default=0, description="Number of sandbox trial runs evaluated")
    sandbox_success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    promoted_to_citable: bool = Field(default=False, description="True once empirically verified in real environment")
    citable_memory_id: Optional[str] = Field(default=None, description="Linked CitableLogicalMemory ID upon promotion")
    created_at: float = Field(default_factory=time.time)
