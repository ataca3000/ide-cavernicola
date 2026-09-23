"""
Tests for ScaleThroughputEngine:
Verifies the inventor's dual scaling & cost axiom:
  "Si es pequeño... si nos vamos a lo grande podemos hacer más con menos tiempo, PERO A MAYOR COSTO".
"""

from core.scale_throughput_engine import ScaleThroughputEngine


def test_scale_advantage_high_volume_justified():
    engine = ScaleThroughputEngine()

    # Large target volume: 15,000 kg
    comp = engine.calculate_scale_advantage(
        target_workload_units=15000.0,
        small_scale_capacity_per_hr=100.0,
        large_scale_capacity_per_hr=1500.0,
        small_scale_cost=300.0,
        large_scale_cost=2500.0
    )

    assert comp.throughput_multiplier == 15.0
    assert comp.time_saved_hours > 100.0
    assert comp.is_large_scale_justified is True
    assert "AMORTIZA EL MAYOR COSTO" in comp.scalability_verdict


def test_scale_disadvantage_low_volume_rejected_due_to_higher_cost():
    engine = ScaleThroughputEngine()

    # Low volume: only 500 kg
    comp = engine.calculate_scale_advantage(
        target_workload_units=500.0,
        small_scale_capacity_per_hr=100.0,
        large_scale_capacity_per_hr=1500.0,
        small_scale_cost=300.0,
        large_scale_cost=2800.0
    )

    assert comp.cost_increase_factor > 8.0
    assert comp.is_large_scale_justified is False
    assert "PERO A MAYOR COSTO" in comp.scalability_verdict
    assert "NO SE JUSTIFICA EL GASTO" in comp.scalability_verdict
