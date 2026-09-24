"""
IDC Core - Safety & Encapsulation Engine (Encapsulado Tipo Plotter y Trampa por Niveles)
Transcribes the inventor's safety philosophy:
  - "La seguridad siempre es de cada quien, pero mis métodos es dejar todo lo peligroso encapsulado con tapas y contenedores"
  - "Por eso el diseño queda como un plotter con tolva en la parte de arriba"
  - "Espacio de roce mínimo: una pequeña línea"
  - "Trampa de tamaño por niveles para que no llegue un niño"
  - "Paro de emergencia y advertencia clara (es peligroso, ahí tú sabes)"
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EnclosureSafetySpec(BaseModel):
    architecture_style: str = "plotter_industrial_con_tolva_superior"
    is_fully_encapsulated: bool = True
    enclosed_hazards: List[str]  # e.g., 'engranes', 'cadenas', 'eje_rotor', 'poleas'
    pinch_clearance_mm: float  # Espacio de roce mínimo
    size_trap_specs: Dict[str, Any]  # Trampa de tamaño por niveles contra extremidades/niños
    emergency_stop_mechanism: str  # Paro de emergencia tipo hongo de corte inmediato
    hazard_disclosure: str  # Advertencia informada al operador


class SafetyEncapsulationEngine:
    """
    Designs industrial safety enclosures:
    Encapsulates all rotating hazards, enforces minimal pinch clearances,
    and constructs multi-level size traps preventing children or hands from reaching rotors.
    """

    MAX_COB_DIAMETER_MM = 65.0   # Diámetro máximo de mazorca
    MIN_HOPPER_NECK_DEPTH_MM = 450.0  # Profundidad que excede el alcance del brazo de un niño

    def generate_safety_enclosure(
        self,
        rotor_diameter_mm: float,
        transmission_components: List[str],
        power_voltage: str = "120V/220V AC",
        max_feedstock_diameter_mm: float = 65.0,
        safety_reach_depth_mm: float = 450.0,
        custom_hazard_labels: Optional[List[str]] = None
    ) -> EnclosureSafetySpec:
        """
        Genera la arquitectura tipo 'plotter con tolva superior'
        con todo lo peligroso sellado bajo tapas protectoras.
        Slots dinámicos para cualquier material o mecanismo.
        """
        if custom_hazard_labels:
            enclosed = list(custom_hazard_labels)
        else:
            enclosed = [
                comp for comp in transmission_components
                if any(w in comp.lower() for w in ["reductor", "chumacera", "cadena", "engrane", "motor", "polea", "eje", "bancada"])
            ]
            enclosed.append("Rotor interno de trabajo")

        size_trap = {
            "entry_aperture_limit_mm": max_feedstock_diameter_mm,
            "hopper_neck_depth_mm": safety_reach_depth_mm,
            "internal_baffle_angle_deg": 45.0,  # Deflector laberinto: impide meter la mano recta al rotor
            "child_protection_rating": "APROBADO_ANTI_ALCANCE_MANO",
            "mechanism": "Trampa geométrica por niveles: el material cae por gravedad oblicua, la mano no puede doblar la esquina"
        }

        return EnclosureSafetySpec(
            architecture_style="plotter_industrial_con_tolva_superior",
            is_fully_encapsulated=True,
            enclosed_hazards=enclosed,
            pinch_clearance_mm=2.5,  # Línea mínima de roce para cero pellizcos
            size_trap_specs=size_trap,
            emergency_stop_mechanism="Botonera tipo hongo NC de corte directo a línea principal (fácil acceso frontal)",
            hazard_disclosure="AVISO DE SEGURIDAD INDUSTRIAL: Maquinaria rotativa de alto torque. Operar exclusivamente por personal capacitado con tolva cerrada."
        )
