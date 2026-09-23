"""
Tests for InventorReasoner: Verifies the direct algorithmic transcription
of the user's mental cognitive process (Corn Mill Invention Example).
"""

from core.inventor_reasoner import InventorReasoner


def test_inventor_reasoner_corn_mill_synthesis():
    reasoner = InventorReasoner()

    result = reasoner.synthesize_invention("Quiero fabricar un molino de maíz para desgranar")

    # 1. Pitfalls discarded immediately
    assert len(result["discarded_pitfalls"]) >= 2
    assert any("aplastar" in d for d in result["discarded_pitfalls"])
    assert any("triturar" in d for d in result["discarded_pitfalls"])

    # 2. Kinematics: rotational, slow with force
    assert result["kinematics"] == "movimiento_giratorio"
    assert "lento" in result["dynamics"]["speed"]
    assert "alto" in result["dynamics"]["torque"]

    # 3. Transmission: decoupled, 1:30 reduction, pillow blocks/bearings
    assert "1:30" in result["transmission_system"]["speed_reduction"]
    assert any("chumaceras" in s for s in result["transmission_system"]["supports"])

    # 4. Free physics: Gravity feeding
    assert "gravedad" in result["passive_physics_harnessed"]["law"].lower()
    assert result["passive_physics_harnessed"]["energy_cost"] == 0.0

    # 5. Separation: teeth on shaft + 2 ramps
    ramps = result["geometry_and_separation"]["output_separation"]
    assert len(ramps) == 2
    assert any("grano" in r["product"] for r in ramps)
    assert any("olote" in r["product"] for r in ramps)

    # 6. Essential BOM for build start
    tools = result["essential_bom"]["tools_for_build"]
    assert any("soldadora" in t for t in tools)
    assert any("nivel" in t for t in tools)
    assert any("tira líneas" in t for t in tools)

    # 7. Scaled technical drawing with defined dimensions (cotas / dibujo a escala)
    blueprint = result["blueprint_and_scale"]
    assert blueprint["scale_ratio"] == "1:10 (1 cm dibujo = 10 cm realidad)"
    assert blueprint["drawing_status"] == "PLANO_A_ESCALA_COTAS_DEFINIDAS"
    assert "chassis_footprint_cm" in blueprint["dimensions"]
    assert blueprint["dimensions"]["shaft_specs"]["diameter_in"] == 1.0
    assert len(blueprint["critical_tolerances"]) >= 3

    # 8. Spatial Intuition & Bounding Box (Cuartas y cálculo de vistas)
    spatial = result["spatial_intuition"]
    bbox = spatial["bounding_box"]
    assert bbox["shape_type"] == "cubico_con_hueco"
    assert bbox["reference_unit_used"] == "cuarta_humana"
    # 2.5 cuartas * 20 cm = 50 cm
    assert bbox["outer_bounds_cm"]["width_x"] == 50.0
    # 3.5 cuartas * 20 cm = 70 cm
    assert bbox["outer_bounds_cm"]["length_y"] == 70.0
    # 4.5 cuartas * 20 cm = 90 cm
    assert bbox["outer_bounds_cm"]["height_z"] == 90.0

    # Views (Planta, Alzado, Perfil)
    projections = spatial["projections"]
    assert projections["top_view_planta"]["plane"] == "X-Y"
    assert projections["front_view_alzado"]["plane"] == "X-Z"
    assert projections["side_view_perfil"]["plane"] == "Y-Z"
    assert projections["cavity_hollow_ratio"] > 0.0

    assert result["readiness"] >= 0.68


def test_spatial_intuition_screen_pixels():
    from core.spatial_intuition import SpatialIntuitionEngine
    engine = SpatialIntuitionEngine()

    # Delineating in machine space (px)
    box_px = engine.delineate_bounds_from_units(
        shape_type="cubo_virtual",
        units_x=377.95,  # ~10 cm
        units_y=377.95,
        units_z=377.95,
        unit_type="px",
        has_cavity=True,
        cavity_margin_units=37.795
    )
    assert box_px.reference_unit_used == "screen_px"
    assert abs(box_px.outer_bounds_cm["width_x"] - 10.0) < 0.1

    views = engine.calculate_views(box_px)
    assert views.cavity_hollow_ratio > 0.0


def test_sensorless_proximity_evaluation():
    from core.spatial_intuition import SpatialIntuitionEngine
    engine = SpatialIntuitionEngine()

    box = engine.delineate_bounds_from_units(
        shape_type="cubico_con_hueco",
        units_x=2.5,  # 50 cm
        units_y=3.5,  # 70 cm
        units_z=4.5,  # 90 cm
        unit_type="cuarta",
        has_cavity=True,
        cavity_margin_units=0.5  # 10 cm margins
    )

    # Internal rotor mechanism of 20 x 40 x 50 cm
    rotor_dims = {"width_x": 20.0, "length_y": 40.0, "height_z": 50.0}
    eval_result = engine.sensorless_proximity_and_fit(box, rotor_dims)

    assert eval_result["sensorless_perception"] is True
    assert eval_result["physical_sensors_needed"] is False
    assert eval_result["fits_inside_cavity"] is True
    assert eval_result["verdict"] == "HOLGURA_ADECUADA"
