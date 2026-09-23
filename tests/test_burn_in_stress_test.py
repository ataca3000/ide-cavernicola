"""
Tests for BurnInStressTester:
Verifies the inventor's burn-in stress test ("Prueba de fuego") & duty cycle principles:
  - Work duration vs rest/cooling time (duty cycle).
  - Anti-futurization axiom: rejecting paper-only predictions.
  - 8-12 hours continuous stress evaluation: temperature limit, bolt retention, jam-free execution.
"""

from core.burn_in_stress_test import BurnInStressTester


def test_duty_cycle_anti_futurization():
    tester = BurnInStressTester()
    profile = tester.create_duty_cycle(work_hours=8.0, rest_hours=2.0)

    assert profile.work_hours_per_session == 8.0
    assert profile.rest_cooling_hours == 2.0
    assert profile.duty_factor == 0.8
    assert "No futurizar por simple cálculo" in profile.anti_futurization_note


def test_burn_in_stress_success_8_to_12_hours():
    tester = BurnInStressTester()

    # 10 continuous hours, 55°C, bolts tight, no jams
    report = tester.evaluate_burn_in_test(
        system_name="Molino desgranador prototipo 1",
        actual_continuous_hours=10.0,
        peak_temp_celsius=55.0,
        bolts_retained_torque=True,
        no_jams_occurred=True
    )

    assert report.passed_burn_in is True
    assert "PRUEBA_DE_FUEGO_SUPERADA" in report.empirical_verdict
    assert "ESTÁ CON MADRE" in report.empirical_verdict


def test_burn_in_stress_failure_overheating_and_loosening():
    tester = BurnInStressTester()

    # Ran only 4 hours, overheated to 88°C, bolts loosened
    report = tester.evaluate_burn_in_test(
        system_name="Mecanismo con desalineacion",
        actual_continuous_hours=4.0,
        peak_temp_celsius=88.0,
        bolts_retained_torque=False,
        no_jams_occurred=True
    )

    assert report.passed_burn_in is False
    assert "FALLA EN PRUEBA DE FUEGO" in report.empirical_verdict
    assert report.vibration_bolt_loosening_detected is True
