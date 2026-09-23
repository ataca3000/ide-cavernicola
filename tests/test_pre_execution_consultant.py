"""
Tests for PreExecutionConsultant:
Verifies the inventor's golden rule:
  "La consulta SIEMPRE se hace ANTES de llevarlo a cabo: te cercioras de tus teorías
   físicas como de materiales y aplicación para obtener el mejor resultado por otros que ya han hecho algo similar".
"""

from core.pre_execution_consultant import PreExecutionConsultant, PriorArtReference


def test_pre_execution_consultation_corn_mill():
    consultant = PreExecutionConsultant()

    # Dynamic slot registration by the agent
    consultant.register_prior_art(
        category_key="molino",
        reference=PriorArtReference(
            source_name_or_repo="agro_machinery/corn_sheller_standard",
            solution_approach="Rotor con reductor y separación por gravedad",
            known_failure_points=["Falta de lubricación en baleros por polvo de maíz"],
            proven_best_practices=["Tapas guardapolvo y tornillo fusible"]
        )
    )

    result = consultant.consult_before_execution(
        domain_or_goal="Fabricar un molino de maíz para desgranar",
        material_or_runtime_specs={"power_adequate": True, "material_adequate": True}
    )

    assert result.physical_theory_validated is True
    assert result.materials_application_verified is True
    assert result.ready_to_build is True
    assert len(result.prior_art_consulted) > 0
    failures = result.prior_art_consulted[0].known_failure_points
    assert any("polvo" in f for f in failures)


def test_pre_execution_consultation_fails_if_physics_inadequate():
    consultant = PreExecutionConsultant()

    result = consultant.consult_before_execution(
        domain_or_goal="Cilindro de compresión hidráulica",
        material_or_runtime_specs={"power_adequate": False, "material_adequate": True}
    )

    assert result.physical_theory_validated is False
    assert result.ready_to_build is False
    assert result.status == "AJUSTE_PREVIO_REQUERIDO"
    assert any("par motor" in a.lower() or "insuficiente" in a.lower() for a in result.critical_adjustments_recommended)


def test_inventor_protocol_executes_pre_consultation():
    from core.inventor_protocol import InventorProtocol

    protocol = InventorProtocol()
    res = protocol.execute_workflow(
        repo_target="https://github.com/example/open-corn-mill.git",
        goal_description="Molino desgranador de maíz",
        build_verifier=lambda: (True, "Build exitoso", 0.72)
    )

    # Verify that Paso 3.5 [Consulta Previa] was recorded in the audit log
    assert any("PASO 3.5 [Consulta Previa]" in log for log in res["audit_log"])
    assert res["verdict"] == "¡Galleta cocinada!"
