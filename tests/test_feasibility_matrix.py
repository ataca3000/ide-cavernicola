"""
Tests for FeasibilityMatrixEngine:
Verifies the inventor's practical bottleneck equation:
  - Wear calculation: (workload / time) and sacrificial protection (fusible mecánico).
  - Decision pathways: In-shop stock (A), Buy commercial (B1), Custom fabricate (B2), Pivot (C: NUNCA PARAR).
"""

from core.feasibility_matrix import FeasibilityMatrixEngine, DecisionStrategy


def test_wear_calculation_and_sacrificial_part():
    engine = FeasibilityMatrixEngine()

    wear = engine.calculate_wear(
        component="eje_con_dientes",
        workload_cycles=5000.0,
        operating_hours=10.0,
        material_durability_factor=1.0,
        protection_strategy="Tornillos de sacrificio de bajo grado reemplazables"
    )

    assert wear.wear_rate == 500.0  # 5000 / 10
    assert wear.sacrificial_part_used is True
    assert wear.durability_lifespan_hours > 0


def test_decision_option_a_in_shop():
    engine = FeasibilityMatrixEngine()

    verdict = engine.evaluate_feasibility(
        item_name="chumaceras_con_balero",
        in_shop_stock=True,
        commercial_price=40.0,
        fabrication_raw_cost=30.0,
        build_hours=2.0,
        budget_limit=100.0,
        max_time_hours=10.0
    )

    assert verdict.decision == DecisionStrategy.USE_IN_SHOP
    assert verdict.estimated_cost == 0.0


def test_decision_option_b1_buy_commercial_when_cheaper_and_faster():
    engine = FeasibilityMatrixEngine()

    # Reductor 1:30 cuesta $50 comercialmente vs $150 y 12h de fabricarlo a mano
    verdict = engine.evaluate_feasibility(
        item_name="reductor_tornillo_1_30",
        in_shop_stock=False,
        commercial_price=50.0,
        fabrication_raw_cost=60.0,
        build_hours=8.0,  # 8h * $25 = $200 + $60 = $260
        budget_limit=100.0,
        max_time_hours=10.0
    )

    assert verdict.decision == DecisionStrategy.BUY_COMMERCIAL
    assert verdict.estimated_cost == 50.0
    assert "comprarlo" in verdict.rationale.lower()


def test_decision_option_c_pivot_when_budget_time_exceeded():
    engine = FeasibilityMatrixEngine()

    # Inviable fabricar y no hay comercial en presupuesto -> PIVOT A OPCIÓN C
    verdict = engine.evaluate_feasibility(
        item_name="eje_especial_titanio",
        in_shop_stock=False,
        commercial_price=900.0,
        fabrication_raw_cost=400.0,
        build_hours=20.0,
        budget_limit=200.0,
        max_time_hours=5.0
    )

    assert verdict.decision == DecisionStrategy.PIVOT_OPTION_C
    assert "NUNCA PARAR" in verdict.rationale
    assert "Opción C activada" in verdict.next_pivot_plan
