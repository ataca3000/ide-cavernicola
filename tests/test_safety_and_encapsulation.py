"""
Tests for SafetyEncapsulationEngine:
Verifies the inventor's safety & enclosure architecture:
  - Enclosure style like a plotter with top hopper ("como un plotter con tolva arriba").
  - Everything dangerous encapsulated with covers/flanges.
  - Minimal pinch clearance line.
  - Multi-level size trap preventing children/hands from reaching rotating parts.
  - Emergency stop & informed hazard disclosure.
"""

from core.safety_and_encapsulation import SafetyEncapsulationEngine


def test_safety_enclosure_plotter_style():
    engine = SafetyEncapsulationEngine()

    spec = engine.generate_safety_enclosure(
        rotor_diameter_mm=120.0,
        transmission_components=["Motor 1 HP", "Reductor 1:30", "Chumaceras de piso", "Cadena y estrellas"]
    )

    assert spec.architecture_style == "plotter_industrial_con_tolva_superior"
    assert spec.is_fully_encapsulated is True
    # All rotating transmission parts must be encapsulated
    assert any("reductor" in h.lower() for h in spec.enclosed_hazards)
    assert any("cadena" in h.lower() for h in spec.enclosed_hazards)
    assert any("rotor" in h.lower() for h in spec.enclosed_hazards)

    # Minimal pinch line
    assert spec.pinch_clearance_mm <= 3.0

    # Multi-level size trap
    trap = spec.size_trap_specs
    assert trap["entry_aperture_limit_mm"] == 65.0  # Fit corn cob, reject human limbs
    assert trap["hopper_neck_depth_mm"] >= 450.0   # Beyond child arm reach
    assert trap["child_protection_rating"] == "APROBADO_ANTI_ALCANCE_MANO"
    assert "hongo" in spec.emergency_stop_mechanism.lower()
