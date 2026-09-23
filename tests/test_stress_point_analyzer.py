"""
Tests for StressPointAnalyzer:
Verifies the inventor's tribological & thermal stress point principle:
  - Identifying heavy-duty points (shafts, transmission).
  - Calculating wear, friction reduction via fluids & viscosity.
  - Mitigating thermal reaction and noise.
  - Defending against operating environment (polvo de maíz, abrasivos).
"""

from core.stress_point_analyzer import StressPointAnalyzer


def test_stress_point_transmission_analysis():
    analyzer = StressPointAnalyzer()

    reports = analyzer.analyze_assembly_stress_points(
        components=["Reductor tornillo sin fin 1:30", "Eje calibrado con dos chumaceras"],
        operating_environment="taller_con_polvo_y_maiz"
    )

    assert len(reports) == 2

    # 1. Transmission report
    trans = next(r for r in reports if "reductor" in r.point_name.lower())
    assert trans.component_type == "transmision_reductor"
    assert trans.energy_loss_reduction_pct > 80.0
    assert trans.noise_reduction_db > 10.0
    assert "ISO VG 320" in trans.recommended_fluid or "SAE" in trans.recommended_fluid
    assert "polvo" in trans.environmental_protection.lower()

    # 2. Shaft & Pillow blocks report
    shaft = next(r for r in reports if "chumacera" in r.point_name.lower())
    assert shaft.component_type == "eje_y_chumaceras"
    assert "litio" in shaft.recommended_fluid.lower()
    assert "2RS" in shaft.environmental_protection or "alemite" in shaft.environmental_protection
