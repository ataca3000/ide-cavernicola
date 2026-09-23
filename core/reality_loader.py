"""
IDC Core - Pluggable Reality Loader
Dynamically mounts and unmounts reality libraries (cyberphysical, physics, thermodynamics, chemistry, quantum).
Validates candidate decisions against active domain laws before execution,
ensuring agents cannot propose actions that violate physical or systemic realities.
"""

from typing import Dict, List, Optional, Tuple, Any
from contracts.reality import RealityDomain, RealityLaw, DomainType


class RealityLoader:
    """
    Manages pluggable reality libraries.
    Ensures agents only carry the laws necessary for their environment,
    preventing computational bloat and out-of-domain hallucinations.
    """

    def __init__(self):
        self._mounted_domains: Dict[DomainType, RealityDomain] = {}
        self._domain_catalog: Dict[DomainType, RealityDomain] = self._build_default_catalog()

    def _build_default_catalog(self) -> Dict[DomainType, RealityDomain]:
        """Creates the foundational catalog of reality domains."""
        catalog: Dict[DomainType, RealityDomain] = {}

        # 1. Cyberphysical / Systems Domain
        cyber = RealityDomain(
            domain=DomainType.CYBERPHYSICAL,
            version="1.0.0",
            constants={"max_port": 65535, "byte_limit": 255},
            laws=[
                RealityLaw(
                    name="Pointer & Memory Safety",
                    domain=DomainType.CYBERPHYSICAL,
                    description="Memory address cannot be negative or access unallocated heap beyond bounds",
                    forbidden_patterns=["buffer_overflow", "null_pointer_dereference", "double_free", "negative_memory_alloc"],
                ),
                RealityLaw(
                    name="Network Port Boundary",
                    domain=DomainType.CYBERPHYSICAL,
                    description="TCP/UDP port numbers must be between 1 and 65535",
                    forbidden_patterns=["bind_port_70000", "bind_negative_port"],
                ),
            ]
        )
        catalog[DomainType.CYBERPHYSICAL] = cyber

        # 2. Classical Physics Domain
        physics = RealityDomain(
            domain=DomainType.CLASSICAL_PHYSICS,
            version="1.0.0",
            constants={"c_speed_of_light": 299792458.0, "standard_gravity": 9.80665},
            laws=[
                RealityLaw(
                    name="Conservation of Energy",
                    domain=DomainType.CLASSICAL_PHYSICS,
                    description="Energy cannot be created from nothing; perpetual motion machines of the first kind are impossible",
                    forbidden_patterns=["free_energy_generator", "perpetual_motion", "over_unity_power"],
                ),
                RealityLaw(
                    name="Universal Speed Limit",
                    domain=DomainType.CLASSICAL_PHYSICS,
                    description="No physical mass can accelerate past the speed of light in vacuum",
                    forbidden_patterns=["faster_than_light_propulsion", "superluminal_travel_mass"],
                ),
            ]
        )
        catalog[DomainType.CLASSICAL_PHYSICS] = physics

        # 3. Thermodynamics Domain
        thermo = RealityDomain(
            domain=DomainType.THERMODYNAMICS,
            version="1.0.0",
            constants={"absolute_zero_kelvin": 0.0},
            laws=[
                RealityLaw(
                    name="Third Law of Thermodynamics (Absolute Zero)",
                    domain=DomainType.THERMODYNAMICS,
                    description="Temperature cannot drop below 0 Kelvin",
                    forbidden_patterns=["negative_kelvin", "cool_below_absolute_zero"],
                    invariants={"min_temperature_kelvin": 0.0}
                ),
                RealityLaw(
                    name="Second Law of Thermodynamics (Entropy)",
                    domain=DomainType.THERMODYNAMICS,
                    description="Total entropy of an isolated system never decreases over time",
                    forbidden_patterns=["decrease_isolated_entropy", "reverse_macro_entropy"],
                ),
            ]
        )
        catalog[DomainType.THERMODYNAMICS] = thermo

        # 4. Chemistry Domain
        chem = RealityDomain(
            domain=DomainType.CHEMISTRY,
            version="1.0.0",
            laws=[
                RealityLaw(
                    name="Conservation of Mass (Lavoisier)",
                    domain=DomainType.CHEMISTRY,
                    description="Mass of reactants must equal mass of products in a chemical reaction",
                    forbidden_patterns=["spontaneous_mass_creation", "annihilate_element_spontaneously"],
                ),
                RealityLaw(
                    name="Valence Octet Constraint",
                    domain=DomainType.CHEMISTRY,
                    description="Stable organic molecules must respect atomic valence electron caps",
                    forbidden_patterns=["pentavalent_carbon", "nonavalent_nitrogen"],
                ),
            ]
        )
        catalog[DomainType.CHEMISTRY] = chem

        # 5. Quantum Domain
        quantum = RealityDomain(
            domain=DomainType.QUANTUM,
            version="1.0.0",
            constants={"planck_constant": 6.62607015e-34},
            laws=[
                RealityLaw(
                    name="No-Cloning Theorem",
                    domain=DomainType.QUANTUM,
                    description="An arbitrary unknown quantum state cannot be cloned identically",
                    forbidden_patterns=["perfect_quantum_cloning", "duplicate_arbitrary_qubit_state"],
                ),
                RealityLaw(
                    name="Heisenberg Uncertainty Principle",
                    domain=DomainType.QUANTUM,
                    description="Position and momentum cannot both be known simultaneously with zero variance",
                    forbidden_patterns=["zero_uncertainty_simultaneous_pos_momentum"],
                ),
                RealityLaw(
                    name="Superposition & Observer Wavefunction Tuning",
                    domain=DomainType.QUANTUM,
                    description="Quantum states remain in superposition until observer measurement or environment interaction tunes/collapses the state vector",
                    forbidden_patterns=["arbitrary_superposition_persistence_at_macro_thermal", "collapse_without_interaction"],
                ),
                RealityLaw(
                    name="Spacetime Curvature & Light Geodesics",
                    domain=DomainType.QUANTUM,
                    description="Light particles and electromagnetic frequencies propagate along geodesics deformed by mass-energy and dark matter curvature",
                    forbidden_patterns=["superluminal_photon_vacuum", "unbent_light_in_infinite_gravity_well"],
                    invariants={"max_photon_speed_c": 1.0}
                ),
            ]
        )
        catalog[DomainType.QUANTUM] = quantum

        return catalog

    def mount(self, domain_type: DomainType) -> bool:
        """Mounts a specific domain of reality laws into active cognitive capacity."""
        if domain_type in self._domain_catalog:
            self._mounted_domains[domain_type] = self._domain_catalog[domain_type]
            return True
        return False

    def unmount(self, domain_type: DomainType) -> bool:
        """Unmounts a domain to free cognitive capacity and avoid out-of-domain clutter."""
        if domain_type in self._mounted_domains:
            del self._mounted_domains[domain_type]
            return True
        return False

    def is_mounted(self, domain_type: DomainType) -> bool:
        """Checks if a domain is currently active."""
        return domain_type in self._mounted_domains

    @property
    def mounted_domains(self) -> List[DomainType]:
        return list(self._mounted_domains.keys())

    def validate_action(self, candidate_action: str, parameters: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validates a proposed candidate action against all currently mounted reality laws.
        Returns (True, None) if compliant, or (False, violation_reason) if a law is breached.
        """
        action_lower = candidate_action.lower()
        parameters = parameters or {}

        for domain_type, domain in self._mounted_domains.items():
            for law in domain.laws:
                # 1. Pattern-based forbidden violations
                for pattern in law.forbidden_patterns:
                    if pattern.lower() in action_lower:
                        return False, f"Reality Law Violation in [{domain_type.value}]: Action matches forbidden pattern '{pattern}' of law '{law.name}'"

                # 2. Invariant boundary checks
                for inv_key, inv_bound in law.invariants.items():
                    if inv_key in parameters:
                        val = parameters[inv_key]
                        if inv_key == "min_temperature_kelvin" and val < inv_bound:
                            return False, f"Thermodynamic Violation: Temperature {val}K is below absolute zero ({inv_bound}K)"

        return True, None
