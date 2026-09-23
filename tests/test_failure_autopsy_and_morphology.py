"""
Tests for FailureAutopsyEngine:
Verifies the inventor's forensic diagnostic and morphological redesign sequence:
  - Analyzing failure causes: carga/esfuerzo, torque, dureza, estabilidad base.
  - Generating alternatives:
    * Tubo con perforaciones dobladas tipo cuñas sin filo (en vez de barra maciza pesada).
    * Dos rodillos encontrados girando hacia adentro.
    * Balero de mayor tamaño.
"""

from core.failure_autopsy_and_morphology import FailureAutopsyEngine


def test_failure_diagnosis_torque_and_base():
    engine = FailureAutopsyEngine()

    # Case 1: Torsion failure
    diag_torque = engine.diagnose_failure(
        component_name="Eje de transmision",
        operating_hours=12.0,
        symptoms=["Eje retorcido en el chavetero", "deformacion por torsion"]
    )
    assert diag_torque.detected_cause == "error_de_torque"
    assert diag_torque.is_scrap_reusable is False

    # Case 2: Base instability
    diag_base = engine.diagnose_failure(
        component_name="Chasis estructural",
        operating_hours=5.0,
        symptoms=["Vibracion excesiva", "bancada chueca", "perfiles flojos"]
    )
    assert diag_base.detected_cause == "inestabilidad_bancada"
    assert diag_base.is_scrap_reusable is True  # Pieza rescatable al reforzar la base


def test_morphological_alternatives_punched_tube_and_dual_rollers():
    engine = FailureAutopsyEngine()

    diag = engine.diagnose_failure(
        component_name="Barra maciza de desgranado",
        operating_hours=20.0,
        symptoms=["Sobrecarga y peso excesivo", "grano quebrado"]
    )

    alternatives = engine.generate_morphological_alternatives(
        component_name="Barra maciza de desgranado",
        diagnosis=diag
    )

    assert len(alternatives) >= 2

    # Check 1: Tubo con cuñas dobladas sin filo
    tube_alt = next(a for a in alternatives if "tubo" in a.alternative_name.lower())
    assert tube_alt.weight_savings_pct > 50.0
    assert "cuñas sin filo" in tube_alt.alternative_name.lower()

    # Check 2: Dos encontrados girando hacia adentro
    dual_alt = next(a for a in alternatives if "girando hacia adentro" in a.alternative_name.lower())
    assert "sentidos opuestos" in dual_alt.kinematics.lower() or "paralelos" in dual_alt.kinematics.lower()
