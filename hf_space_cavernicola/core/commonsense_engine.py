"""
IDC Core - Commonsense Causal Engine
Codifies physical, systemic, and environmental common sense in Spanish and English.
Grounds sensory and vision perceptions (camera frames, obstacle bounding boxes, telemetry)
into causal affordances, prerequisites, and safety invariants.
"""

from typing import Any, Dict, List, Optional, Tuple
from contracts.memory_library import CitableLogicalMemory
from core.citable_memory_vault import CitableMemoryVault
from core.reality_loader import RealityLoader


class CommonsenseConcept:
    """Represents a grounded concept with causal affordances and physical prerequisites."""
    def __init__(
        self,
        name: str,
        domain: str,
        properties: List[str],
        causes: List[str],
        prerequisites: List[str],
        hazards: List[str],
        synonyms_es: List[str],
        synonyms_en: List[str],
    ):
        self.name = name
        self.domain = domain
        self.properties = properties
        self.causes = causes
        self.prerequisites = prerequisites
        self.hazards = hazards
        self.synonyms_es = [s.lower() for s in synonyms_es]
        self.synonyms_en = [s.lower() for s in synonyms_en]

    def matches(self, term: str) -> bool:
        t = term.strip().lower()
        return t == self.name.lower() or t in self.synonyms_es or t in self.synonyms_en


class CommonsenseEngine:
    """
    Evaluates real-time sensory perception and camera feeds against codified common sense.
    Identifies obstacles, hazards, and prerequisites in human environments.
    """

    def __init__(self, vault: Optional[CitableMemoryVault] = None, reality: Optional[RealityLoader] = None):
        self.vault = vault
        self.reality = reality
        self._concepts: Dict[str, CommonsenseConcept] = {}
        self._seed_foundational_commonsense()

    def _seed_foundational_commonsense(self) -> None:
        """Seeds bilingual core physical and situational commonsense rules."""
        seeds = [
            CommonsenseConcept(
                name="obstacle",
                domain="classical_physics",
                properties=["solid", "impassable", "physical_barrier"],
                causes=["collision", "path_blocked", "velocity_drop_to_zero"],
                prerequisites=["needs_detour", "needs_clearing"],
                hazards=["physical_damage", "chassis_impact"],
                synonyms_es=["obstáculo", "bloqueo", "pared", "barrera", "escombro"],
                synonyms_en=["obstacle", "barrier", "blockage", "wall", "debris"],
            ),
            CommonsenseConcept(
                name="human",
                domain="cyberphysical",
                properties=["biological", "fragile", "dynamic", "priority_safety"],
                causes=["unexpected_movement", "interaction_request"],
                prerequisites=["maintain_safety_distance", "audio_warning"],
                hazards=["injury_risk_critical", "emergency_stop_required"],
                synonyms_es=["humano", "persona", "operador", "peaton", "usuario"],
                synonyms_en=["human", "person", "operator", "pedestrian", "user"],
            ),
            CommonsenseConcept(
                name="high_temperature",
                domain="thermodynamics",
                properties=["thermal_energy", "exothermic", "degrades_components"],
                causes=["thermal_throttling", "material_deformation", "combustion"],
                prerequisites=["cooling_active", "heat_shield"],
                hazards=["hardware_burn", "irreversible_damage"],
                synonyms_es=["calor_extremo", "fuego", "alta_temperatura", "sobrecalentamiento"],
                synonyms_en=["fire", "extreme_heat", "high_temperature", "overheating"],
            ),
            CommonsenseConcept(
                name="loose_wire_short_circuit",
                domain="cyberphysical",
                properties=["electrical", "unstable_impedance", "current_spike"],
                causes=["voltage_drop", "blown_fuse", "fire_hazard"],
                prerequisites=["isolate_power", "continuity_test"],
                hazards=["short_circuit", "controller_burnout"],
                synonyms_es=["cable_suelto", "cortocircuito", "falla_electrica"],
                synonyms_en=["loose_wire", "short_circuit", "electrical_fault"],
            ),
            CommonsenseConcept(
                name="slippery_surface",
                domain="classical_physics",
                properties=["low_friction", "traction_loss"],
                causes=["wheel_slip", "trajectory_drift"],
                prerequisites=["reduce_speed", "increase_torque_control"],
                hazards=["skid", "loss_of_control"],
                synonyms_es=["suelo_resbaladizo", "aceite", "agua", "baja_traccion"],
                synonyms_en=["slippery_surface", "oil_slick", "water_puddle", "low_traction"],
            ),
        ]
        for c in seeds:
            self._concepts[c.name] = c

    def lookup_concept(self, term: str) -> Optional[CommonsenseConcept]:
        """Bilingual concept lookup matching Spanish or English synonyms."""
        for c in self._concepts.values():
            if c.matches(term):
                return c
        return None

    def interpret_sensory_scene(
        self,
        detections: List[Dict[str, Any]],
        telemetry: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Interprets camera vision detections (e.g. object labels, bounding box proximities)
        and sensor telemetry to deduce obstacles, hazards, and common-sense restrictions.
        """
        telemetry = telemetry or {}
        identified_hazards: List[str] = []
        action_restrictions: List[str] = []
        inferred_prerequisites: List[str] = []
        active_domains_needed: set = set()

        for det in detections:
            label = det.get("label", "")
            distance_meters = det.get("distance_m", 99.0)
            concept = self.lookup_concept(label)

            if concept:
                active_domains_needed.add(concept.domain)
                # Proximity rules
                if distance_meters < 1.0:
                    identified_hazards.extend([f"CRITICAL_PROXIMITY: {h}" for h in concept.hazards])
                    action_restrictions.append(f"HALT_OR_DETOUR_AROUND_{concept.name.upper()}")
                else:
                    inferred_prerequisites.extend(concept.prerequisites)

        # Check telemetry common sense (e.g. temperature, voltage)
        temp_c = telemetry.get("temperature_c", 25.0)
        if temp_c > 75.0:
            heat_concept = self._concepts.get("high_temperature")
            if heat_concept:
                identified_hazards.extend(heat_concept.hazards)
                action_restrictions.append("RESTRICT_POWER_CONSUMPTION")
                active_domains_needed.add("thermodynamics")

        return {
            "scene_clear": len(identified_hazards) == 0,
            "hazards": list(set(identified_hazards)),
            "restrictions": list(set(action_restrictions)),
            "prerequisites": list(set(inferred_prerequisites)),
            "recommended_domains": list(active_domains_needed),
        }
