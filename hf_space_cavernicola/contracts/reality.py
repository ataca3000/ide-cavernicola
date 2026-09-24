"""
IDC Contracts - Pluggable Reality Libraries
Defines laws, constraints, and invariants that govern distinct physical and systemic realities
(e.g., Classical Mechanics, Thermodynamics/Chemistry, Quantum, Cyberphysical/Software).
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class DomainType(str, Enum):
    CYBERPHYSICAL = "cyberphysical"       # Operating systems, memory, networking, algorithms
    CLASSICAL_PHYSICS = "classical_physics" # Kinematics, Newtonian dynamics, gravity, mechanics
    THERMODYNAMICS = "thermodynamics"     # Entropy, temperature (Kelvin), heat transfer
    CHEMISTRY = "chemistry"               # Stoichiometry, reaction kinetics, molecular stability
    QUANTUM = "quantum"                   # Superposition, state vectors, decoherence bounds


class RealityLaw(BaseModel):
    """
    An inviolable principle within a specific reality domain.
    Actions violating these laws are blocked before execution to conserve energy and avoid damage.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Name of the physical/systemic law (e.g. 'Conservation of Energy')")
    domain: DomainType = Field(..., description="Target domain this law belongs to")
    description: str = Field(..., description="Human and machine readable explanation")
    forbidden_patterns: List[str] = Field(
        default_factory=list,
        description="Substrings or regex patterns in candidate actions that directly violate this law"
    )
    invariants: Dict[str, Any] = Field(
        default_factory=dict,
        description="Numerical invariants (e.g. {'min_temperature_kelvin': 0.0, 'max_velocity_c': 1.0})"
    )


class RealityDomain(BaseModel):
    """
    A pluggable, cohesive set of laws representing a domain of reality.
    Only domains needed for the agent's current mission are mounted.
    """
    domain: DomainType
    version: str = Field(default="1.0.0")
    laws: List[RealityLaw] = Field(default_factory=list)
    constants: Dict[str, float] = Field(default_factory=dict)
    active: bool = Field(default=True)
