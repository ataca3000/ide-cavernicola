"""
Tests for ScrapAndManufacturingSelector:
Verifies the inventor's targeted scrap hunting & manufacturing method:
  - Checklist of defined scrap components: cardan, shaft, pillow blocks, motor >= 1 HP.
  - In-situ validation criteria (stability, wear, radial play).
  - Scalability decision driven by batch quantity (1 piece vs 10 vs 100+ -> Scrap, Plasma/Bending, Lathe, CNC, 3D).
"""

from core.scrap_and_manufacturing_selector import ScrapAndManufacturingSelector, ProcessType


def test_targeted_scrap_checklist():
    selector = ScrapAndManufacturingSelector()
    checklist = selector.generate_targeted_scrap_checklist(requires_angular_coupling=True, min_power_hp=1.0)

    assert len(checklist) >= 4
    categories = [item.item_category for item in checklist]
    assert "motor_electrico" in categories
    assert "chumaceras_soportes" in categories
    assert "eje_transmision" in categories
    assert "acople_cardan" in categories


def test_process_selection_by_quantity_and_geometry():
    selector = ScrapAndManufacturingSelector()

    # 1. Tolva (placas y doblado) para 1 unidad -> Plasma & Bending
    rec_hopper = selector.select_process_by_quantity_and_geometry(
        part_name="Tolva de alimentacion conica",
        quantity=1,
        geometry_type="placas_tolva_chapa"
    )
    assert rec_hopper.recommended_process == ProcessType.PLASMA_AND_BENDING

    # 2. Eje torneado unitario -> Conventional Lathe
    rec_shaft = selector.select_process_by_quantity_and_geometry(
        part_name="Eje calibrado de 1 pulgada",
        quantity=1,
        geometry_type="eje_cilindrico_con_chaveteros"
    )
    assert rec_shaft.recommended_process == ProcessType.CONVENTIONAL_LATHE

    # 3. Lote grande de 50 ejes -> CNC Machining
    rec_cnc_shaft = selector.select_process_by_quantity_and_geometry(
        part_name="Eje calibrado en serie",
        quantity=50,
        geometry_type="eje_cilindrico_con_chaveteros"
    )
    assert rec_cnc_shaft.recommended_process == ProcessType.CNC_MACHINING

    # 4. Prototipo rápido de boquilla -> Impresión 3D
    rec_3d = selector.select_process_by_quantity_and_geometry(
        part_name="Boquilla de desahogo ergonomica",
        quantity=1,
        geometry_type="boquilla_plastico_complejo"
    )
    assert rec_3d.recommended_process == ProcessType.ADDITIVE_3D
