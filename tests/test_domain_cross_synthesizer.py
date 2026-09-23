"""
Tests for DomainCrossSynthesizer:
Verifies the inventor's principle of crossing concepts while respecting physical reality:
  - Discarding absurd crossings (aguacate + motor) in TANGIBLE_FISICO mode unless it's just the name.
  - Allowing synergistic mechanical crossings (cadena de bici + reductor de molino).
  - Enabling free conceptual blending in FICCION_SIMBOLICA mode.
"""

from core.domain_cross_synthesizer import DomainCrossSynthesizer, ImaginationMode


def test_cross_absurd_tangible_rejected():
    synthesizer = DomainCrossSynthesizer()

    result = synthesizer.cross_concepts(
        concept_a="aguacate",
        concept_b="motor de coche",
        mode=ImaginationMode.TANGIBLE_FISICO
    )

    # Physically not viable to cross an avocado with a car engine
    assert result.is_physically_viable is False
    assert result.is_nominal_only is True
    assert "aguacate" in result.warning_or_rationale.lower()
    assert result.functional_hybrid is None


def test_cross_synergistic_mechanical_viable():
    synthesizer = DomainCrossSynthesizer()

    result = synthesizer.cross_concepts(
        concept_a="cadena de bici",
        concept_b="reductor de molino",
        mode=ImaginationMode.TANGIBLE_FISICO
    )

    assert result.is_physically_viable is True
    assert result.is_nominal_only is False
    assert len(result.shared_physical_laws) > 0
    assert "Cinemática rotacional" in result.shared_physical_laws
    assert result.functional_hybrid is not None


def test_cross_raw_material_workload():
    synthesizer = DomainCrossSynthesizer()

    result = synthesizer.cross_concepts(
        concept_a="maiz",
        concept_b="molino desgranador",
        mode=ImaginationMode.TANGIBLE_FISICO
    )

    assert result.is_physically_viable is True
    assert "carga de trabajo" in result.warning_or_rationale


def test_cross_symbolic_fiction_mode():
    synthesizer = DomainCrossSynthesizer()

    result = synthesizer.cross_concepts(
        concept_a="aguacate",
        concept_b="motor cuántico",
        mode=ImaginationMode.FICCION_SIMBOLICA
    )

    assert result.mode == ImaginationMode.FICCION_SIMBOLICA
    assert result.is_nominal_only is True
    assert "Proyecto Aguacate-Motor cuántico" in result.functional_hybrid
