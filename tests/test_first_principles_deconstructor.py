"""
Tests for FirstPrinciplesDeconstructor:
Verifies the inventor's ultimate cognitive axiom:
  "Cuando recuerdo o analizo SIEMPRE SIEMPRE busco por qué y cómo funciona,
   y vuelvo a hacerlo en cada comportamiento que entiendo de ese sistema
   hasta llegar casi a niveles de composición estructural del material aplicado".
"""

from core.first_principles_deconstructor import FirstPrinciplesDeconstructor


def test_recursive_deconstruction_depth():
    deconstructor = FirstPrinciplesDeconstructor()

    # Deconstruct down to material structural level
    tree = deconstructor.analyze_to_material_depth(target_concept="Transmision reductora y rodamientos")

    assert tree.depth_level == 0
    assert "Comportamiento macroscópico" in tree.behavior
    assert len(tree.sub_behaviors) > 0

    level_1 = tree.sub_behaviors[0]
    assert level_1.depth_level == 1
    assert "cinemático" in level_1.behavior.lower() or "desacople" in level_1.behavior.lower()
    assert len(level_1.sub_behaviors) > 0

    level_2 = level_1.sub_behaviors[0]
    assert level_2.depth_level == 2
    assert "fricción" in level_2.behavior.lower() or "rozamiento" in level_2.behavior.lower()
    assert len(level_2.sub_behaviors) > 0

    level_3 = level_2.sub_behaviors[0]
    assert level_3.depth_level == 3
    assert "composición estructural" in level_3.behavior.lower()
    assert len(level_3.material_composition_invariants) >= 3
    assert any("cristalina" in m or "fatiga" in m for m in level_3.material_composition_invariants)


def test_dynamic_empty_inputs_agnostic_tree():
    """Verifies that any custom agnostic system can be deconstructed recursively without hardcoded domains."""
    deconstructor = FirstPrinciplesDeconstructor()

    # Dynamic custom tree
    custom_tree = deconstructor.deconstruct(
        system_behavior="Rotación de eje bajo carga variable",
        how_it_works="Par motor aplicado genera torsión angular a través de acople elástico",
        why_it_works="Tercera ley de Newton y conservación del momento angular",
        sub_layers=[
            {
                "behavior": "Deformación cortante en la superficie exterior del eje",
                "how": "Las fibras exteriores experimentan mayor esfuerzo cortante tau = (T*r)/J",
                "why": "Distribución lineal de deformación radial en sección circular",
                "sub_layers": [
                    {
                        "behavior": "Respuesta a nivel de grano del acero SAE 4140 bonificado",
                        "how": "Dislocaciones en la red cristalina austenítica/martensítica bloqueadas por precipitados de cromo-molibdeno",
                        "why": "Energía de activación de deformación plástica superada sólo bajo esfuerzo de fluencia superior a 650 MPa",
                        "material_basis": [
                            "Estructura martensítica revenida con carburos dispersos",
                            "Tenacidad al impacto Charpy > 40 J",
                            "Módulo de rigidez transversal G = 80 GPa"
                        ]
                    }
                ]
            }
        ]
    )

    assert custom_tree.behavior == "Rotación de eje bajo carga variable"
    assert "torsión" in custom_tree.how_mechanism
    assert len(custom_tree.sub_behaviors) == 1

    sub_1 = custom_tree.sub_behaviors[0]
    assert sub_1.depth_level == 1
    assert "cortante" in sub_1.behavior

    sub_2 = sub_1.sub_behaviors[0]
    assert sub_2.depth_level == 2
    assert "4140" in sub_2.behavior
    assert len(sub_2.material_composition_invariants) == 3
    assert "G = 80 GPa" in sub_2.material_composition_invariants[2]


def test_agent_analyze_first_principles_integration():
    """Verifies IDCAgent can invoke first-principles deconstruction natively during recall/analysis."""
    from core.agent import IDCAgent
    import tempfile
    import shutil

    temp_mem = tempfile.mkdtemp()
    try:
        agent = IDCAgent(memory_dir=temp_mem)
        tree = agent.analyze_first_principles(
            concept_or_behavior="Disipador de calor y aletas térmicas",
            domain_type="termico_y_materiales"
        )
        assert tree is not None
        assert tree.depth_level == 0
        assert len(tree.sub_behaviors) > 0
        # Check deep level
        deepest = tree.sub_behaviors[0].sub_behaviors[0].sub_behaviors[0]
        assert deepest.depth_level == 3
        assert len(deepest.material_composition_invariants) > 0
    finally:
        shutil.rmtree(temp_mem, ignore_errors=True)


def test_quantum_atomic_observer_spacetime_deconstruction():
    """
    Verifies deconstruction down to:
    Atomic orbitals, quantum superposition, observer frequency tuning,
    dark matter, and spacetime curvature modulating light frequencies and particles.
    """
    deconstructor = FirstPrinciplesDeconstructor()
    tree = deconstructor.analyze_to_atomic_and_quantum_depth(
        target_concept="Emisión y propagación de pulsos láser en fibra dopada"
    )

    assert tree.depth_level == 0
    # Level 1: Interfacial / macro transferencia
    level_1 = tree.sub_behaviors[0]
    assert level_1.depth_level == 1

    # Level 2: Red del material
    level_2 = level_1.sub_behaviors[0]
    assert level_2.depth_level == 2

    # Level 3: Atómico / orbitales
    level_3 = level_2.sub_behaviors[0]
    assert level_3.depth_level == 3
    assert "atómico" in level_3.behavior.lower() or "orbitales" in level_3.behavior.lower()

    # Level 4: Cuántico / Superposición / Observador / Espaciotiempo
    quantum_node = level_3.sub_behaviors[0]
    assert quantum_node.depth_level == 4
    assert "cuántico" in quantum_node.behavior.lower()
    assert "observador" in quantum_node.behavior.lower()
    assert len(quantum_node.atomic_quantum_invariants) >= 4
    assert any("superposición" in inv.lower() for inv in quantum_node.atomic_quantum_invariants)
    assert any("observador" in inv.lower() for inv in quantum_node.atomic_quantum_invariants)
    assert any("materia oscura" in inv.lower() for inv in quantum_node.atomic_quantum_invariants)
    assert any("luz" in inv.lower() or "fotones" in inv.lower() for inv in quantum_node.atomic_quantum_invariants)

    assert quantum_node.spacetime_properties.get("light_speed_c") == 299792458.0
    assert quantum_node.spacetime_properties.get("observer_tuning_active") is True


def test_agent_reach_quantum_first_principles():
    """Verifies IDCAgent can invoke reach_quantum=True and load quantum domain laws."""
    from core.agent import IDCAgent
    from contracts.reality import DomainType
    import tempfile
    import shutil

    temp_mem = tempfile.mkdtemp()
    try:
        agent = IDCAgent(memory_dir=temp_mem)
        agent.mount_reality(DomainType.QUANTUM)

        # Validate quantum action compliance
        valid, err = agent.reality.validate_action("analizar_estado_superposicion_con_observador")
        assert valid is True
        assert err is None

        # Violation check
        invalid, err_msg = agent.reality.validate_action("superluminal_photon_vacuum")
        assert invalid is False
        assert "Spacetime Curvature" in err_msg

        # Agent first principles drill down to quantum
        tree = agent.analyze_first_principles(
            concept_or_behavior="Refracción y difracción de luz en interferómetro",
            reach_quantum=True
        )
        assert tree is not None
        # Drill down to bottom
        bottom = tree.sub_behaviors[0].sub_behaviors[0].sub_behaviors[0].sub_behaviors[0]
        assert "cuántico" in bottom.behavior.lower()
        assert bottom.spacetime_properties["observer_tuning_active"] is True
    finally:
        shutil.rmtree(temp_mem, ignore_errors=True)


def test_birth_of_what_if_from_deep_material_understanding():
    """
    Verifies the inventor's axiom:
    'Y de este entendimiento profundo hasta la estructura del material...
     ES DEL QUE NACE EL ¿Y SI...?'
    """
    deconstructor = FirstPrinciplesDeconstructor()
    tree = deconstructor.analyze_to_material_depth(target_concept="Transmision reductora bajo fatiga severa")

    # Harvest what-if hypotheses born from structural deconstruction
    what_ifs = deconstructor.spawn_what_if_innovations(tree)

    assert len(what_ifs) > 0
    assert any("¿y si" in w.lower() for w in what_ifs)
    assert any("morfología" in w.lower() or "hueca" in w.lower() or "perforada" in w.lower() for w in what_ifs)
    assert any("fusible de sacrificio" in w.lower() or "desacoplando" in w.lower() for w in what_ifs)
    assert any("dos ejes o rodillos encontrados" in w.lower() for w in what_ifs)


def test_curiosity_obtained_by_experience_and_environment_understanding():
    """
    Verifies:
    'CURIOSIDAD OBTENIDA POR EXPERIENCIA Y COMPRENSIÓN DE TU ENTORNO'
    The agent's curiosity is grounded in past workshop lessons, physical surroundings,
    and structural deconstruction.
    """
    from core.curiosity_engine import CuriosityEngine
    engine = CuriosityEngine()

    experience = ["Barra maciza de 2 pulgadas falló por sobrepeso y sobrecarga en baleros"]
    environment = {"gravedad_gratuita": True, "chatarra_disponible": ["tubo", "chumaceras", "cardan"]}

    curiosities = engine.generate_inventor_curiosity(
        experience_lessons=experience,
        environment_understanding=environment,
        system_bottleneck="Eje central de desgranado"
    )

    assert len(curiosities) == 3
    assert engine.novel_question_count() == 3
    assert any("¿y si aliviamos el esfuerzo" in q.lower() for q in curiosities)
    assert any("fusible de sacrificio" in q.lower() for q in curiosities)
    assert any("dos rodillos o ejes encontrados" in q.lower() for q in curiosities)
