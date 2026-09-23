"""
IDC Core - Failure Autopsy & Morphological Innovation Engine
Transcribes the inventor's diagnostic & redesign sequence:
  - "Mi mente reacciona: ¿qué tiempo funcionó?, ¿qué falló?, ¿por qué?"
  - "¿Pudo haber sido error de carga/esfuerzo, de torque, dureza del material o estabilidad/base de soporte?"
  - "Alternativas: balero de mayor tamaño; barra pesada -> tubo con perforaciones dobladas tipo cuñas sin filo; o dos encontrados girando hacia adentro"
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FailureDiagnosisReport(BaseModel):
    component: str
    operating_hours: float
    detected_cause: str  # 'error_de_carga', 'error_de_torque', 'dureza_insuficiente', 'inestabilidad_bancada'
    evidence: str
    is_scrap_reusable: bool


class MorphologicalAlternative(BaseModel):
    alternative_name: str
    replaces: str
    weight_savings_pct: float
    mechanical_advantage: str
    kinematics: str
    durability_improvement: str


class FailureAutopsyEngine:
    """
    Performs forensic autopsy of past failures and synthesizes
    morphological alternatives (punched folded wedge tubes, dual inward rollers).
    """

    def diagnose_failure(
        self,
        component_name: str,
        operating_hours: float,
        symptoms: List[str]
    ) -> FailureDiagnosisReport:
        sym_text = " ".join(symptoms).lower()

        if any(w in sym_text for w in ["torsion", "retorcido", "torcido", "torque"]):
            cause = "error_de_torque"
            evidence = "Eje o acople deformado por par torsional superior al límite elástico."
            reusable = False
        elif any(w in sym_text for w in ["vibracion", "chueco", "base", "bancada", "desalineado"]):
            cause = "inestabilidad_bancada"
            evidence = "Rigidez insuficiente en el soporte o perfiles base flojos."
            reusable = True  # La pieza sirve, lo que falló fue la estructura de anclaje
        elif any(w in sym_text for w in ["rayado", "desgaste", "limadura", "quebrado"]):
            cause = "dureza_insuficiente"
            evidence = "Material blando sin tratamiento térmico o fricción abrasiva directa."
            reusable = False
        else:
            cause = "error_de_carga"
            evidence = "Fatiga mecánica o sobrecarga estática por encima de especificación."
            reusable = False

        return FailureDiagnosisReport(
            component=component_name,
            operating_hours=operating_hours,
            detected_cause=cause,
            evidence=evidence,
            is_scrap_reusable=reusable
        )

    def generate_morphological_alternatives(
        self,
        component_name: str,
        diagnosis: FailureDiagnosisReport
    ) -> List[MorphologicalAlternative]:
        alternatives: List[MorphologicalAlternative] = []
        comp_lower = component_name.lower()

        # Caso 1: Barra maciza pesada -> Tubo con cuñas dobladas sin filo
        if any(w in comp_lower for w in ["barra", "eje_macizo", "rotor"]):
            alternatives.append(
                MorphologicalAlternative(
                    alternative_name="Tubo cédula con perforaciones troqueladas y dobladas tipo cuñas sin filo",
                    replaces=component_name,
                    weight_savings_pct=65.0,  # Ahorro masivo de peso e inercia rotacional
                    mechanical_advantage="Alivia la carga en rodamientos y desgrana por arrastre sin cortar ni quebrar el grano",
                    kinematics="Rotación aligerada de bajo momento de inercia",
                    durability_improvement="Mayor relación resistencia/peso que una barra maciza"
                )
            )

        # Caso 2: Rendimiento de desgranado o atascos -> Dos rodillos encontrados girando hacia adentro
        if any(w in comp_lower for w in ["rotor", "molino", "desgran", "eje"]):
            alternatives.append(
                MorphologicalAlternative(
                    alternative_name="Doble cilindro sincronizado contrarrotatorio girando hacia adentro",
                    replaces="Rotor simple con cuna fija",
                    weight_savings_pct=15.0,
                    mechanical_advantage="Auto-alimentación continua por tracción simétrica sin empastarse",
                    kinematics="Dos ejes paralelos con engranes 1:1 girando en sentidos opuestos hacia el centro",
                    durability_improvement="Distribuye la carga entre dos ejes, reduciendo a la mitad el torque en cada chumacera"
                )
            )

        # Caso 3: Fallas de rodamientos -> Escalamiento a balero reforzado
        if any(w in comp_lower for w in ["balero", "chumacera", "soporte"]):
            alternatives.append(
                MorphologicalAlternative(
                    alternative_name="Balero de mayor diámetro de carga dinámica o de rodillos oscilantes",
                    replaces=component_name,
                    weight_savings_pct=-20.0,  # Ligeramente más pesado pero indestructible
                    mechanical_advantage="Soporta desalineaciones angulares de hasta 2° sin atascarse",
                    kinematics="Rodadura con alineación auto-compensada",
                    durability_improvement="Vida útil 4x superior ante vibraciones del taller"
                )
            )

        return alternatives
