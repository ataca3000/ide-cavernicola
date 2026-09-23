"""
IDC Core - Stress Point & Tribology/Thermal Engine (Puntos de Trabajo Fuerte y Reacción Térmica)
Transcribes the inventor's rule:
  - "Primero veo dónde llevarán los puntos de trabajo fuerte (ejes y transmisión)"
  - "Qué desgaste generan y qué soluciones hay como fluidos, viscosidad y reacción térmica"
  - "Para disminuir la pérdida de energía o reducir el ruido y desgaste por fricción"
  - "Más el ambiente en el que está operando (polvo, intemperie, calor)"
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StressPointReport(BaseModel):
    point_name: str
    component_type: str  # 'eje', 'transmision_tornillo', 'chumacera_balero', 'engrane'
    load_severity: str  # 'ALTA', 'MEDIA', 'EXTREMA'
    friction_coefficient_dry: float
    friction_coefficient_lubricated: float
    energy_loss_reduction_pct: float
    noise_reduction_db: float
    thermal_reaction_celsius: float
    recommended_fluid: str  # e.g. "Grasa de litio NLGI 2 EP", "Aceite para engranajes SAE 90 / ISO VG 320"
    viscosity_spec: str
    environmental_protection: str  # e.g. "Retén de doble labio 2RS contra polvo de maíz"


class StressPointAnalyzer:
    """
    Analyzes mechanical and computational stress points, friction loss,
    thermal dissipation, and operating environment constraints.
    """

    def analyze_assembly_stress_points(
        self,
        components: List[str],
        operating_environment: str = "taller_con_polvo_y_grano"
    ) -> List[StressPointReport]:
        """
        Identifica puntos de trabajo fuerte y genera la solución tribológica y térmica.
        """
        reports: List[StressPointReport] = []
        env_lower = operating_environment.lower()
        has_dust = any(w in env_lower for w in ["polvo", "grano", "maiz", "polvillo", "tierra"])

        for comp in components:
            c_lower = comp.lower()

            if any(w in c_lower for w in ["reductor", "tornillo sin fin", "transmision", "cadena"]):
                # Transmisión: alto roce por deslizamiento y calentamiento
                reports.append(
                    StressPointReport(
                        point_name=comp,
                        component_type="transmision_reductor",
                        load_severity="ALTA",
                        friction_coefficient_dry=0.35,
                        friction_coefficient_lubricated=0.06,
                        energy_loss_reduction_pct=82.8,
                        noise_reduction_db=14.5,
                        thermal_reaction_celsius=48.0,  # Calentamiento mitigado por baño
                        recommended_fluid="Aceite sintético para reductores tornillo sin fin ISO VG 320 (SAE 90/140)",
                        viscosity_spec="Alta viscosidad cinemática (320 cSt a 40°C) para película de choque",
                        environmental_protection="Cárter cerrado estanco con tapón respiradero con filtro para polvo"
                        if has_dust else "Cárter cerrado estándar"
                    )
                )

            elif any(w in c_lower for w in ["eje", "chumacera", "balero", "rodamiento"]):
                # Ejes y soportes de giro
                reports.append(
                    StressPointReport(
                        point_name=comp,
                        component_type="eje_y_chumaceras",
                        load_severity="MEDIA-ALTA",
                        friction_coefficient_dry=0.20,
                        friction_coefficient_lubricated=0.015,
                        energy_loss_reduction_pct=92.5,
                        noise_reduction_db=18.0,
                        thermal_reaction_celsius=35.0,
                        recommended_fluid="Grasa consistente con jabón de litio y aditivos extrema presión (EP 2)",
                        viscosity_spec="Consistencia NLGI 2 con base mineral de 150-220 cSt",
                        environmental_protection="Sellos de caucho de contacto 2RS + engrasador alemite para purga de polvo"
                        if has_dust else "Sellos metálicos tipo ZZ"
                    )
                )

            elif any(w in c_lower for w in ["dientes", "rotor", "desgrane", "corte", "cizalle", "martillo", "herramienta"]):
                # Zona de impacto, cizalle o corte directo
                reports.append(
                    StressPointReport(
                        point_name=comp,
                        component_type="impacto_mecanico",
                        load_severity="EXTREMA",
                        friction_coefficient_dry=0.45,
                        friction_coefficient_lubricated=0.25,
                        energy_loss_reduction_pct=44.4,
                        noise_reduction_db=8.0,
                        thermal_reaction_celsius=42.0,
                        recommended_fluid="Sin fluido químico (contacto alimentario con grano) - Lubricación sólida por fricción seca",
                        viscosity_spec="N/A (Superficie pulida o endurecida por temple)",
                        environmental_protection="Deflectores de chapa para evacuar el polvo hacia la tolva"
                    )
                )

        return reports
