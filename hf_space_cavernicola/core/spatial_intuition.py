"""
IDC Core - Spatial Intuition Engine (Intuición Espacial y Delineado Mental)
Transcribes the human inventor's intuitive volumetric delimitation:
  - "Delinear límites sin medir con regla al inicio (Bounding Box Mental)"
  - "Unidad de referencia biológica (1 cuarta = aprox 20 cm) vs Digital (px / voxels)"
  - "Cálculo de vistas (Planta, Alzado, Perfil, Corte) y huecos/cavidades volumétricas"
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class SpatialBoundingBox(BaseModel):
    """Mental enclosure box delineated without prior caliper measurements."""
    shape_type: str = "cuboid_with_cavity"  # e.g., cuboid, cylinder, prism
    outer_bounds_cm: Dict[str, float]  # width_x, length_y, height_z
    inner_cavity_cm: Optional[Dict[str, float]] = None  # hollow core for mechanisms
    reference_unit_used: str = "cuarta_humana"  # 'cuarta_humana' (20cm) or 'screen_px'
    reference_unit_value: float = 20.0  # cm per unit
    unit_count: Dict[str, float] = Field(default_factory=dict)  # bounds in units (e.g. 2.5 cuartas)


class MultiViewProjection(BaseModel):
    """Derived 2D/3D projections from the intuitive mental bounding limits."""
    top_view_planta: Dict[str, Any]
    front_view_alzado: Dict[str, Any]
    side_view_perfil: Dict[str, Any]
    cavity_hollow_ratio: float  # Percentage of internal open space (0.0 to 1.0)


class SpatialIntuitionEngine:
    """
    Simulates the mental drafting ability of an inventor:
    Takes high-level shapes, delineates bounding limits using body-centric or pixel units,
    and calculates structural views and hollow tolerances before detailed CAD/cutting.
    """

    HUMAN_SPAN_CM = 20.0  # 1 cuarta = ~20 cm
    DEFAULT_PX_PER_CM = 37.795  # Standard 96 DPI screen (approx 38 px = 1 cm)

    def __init__(self, human_span_cm: float = 20.0, px_per_cm: float = 37.795):
        self.human_span_cm = human_span_cm
        self.px_per_cm = px_per_cm

    def delineate_bounds_from_units(
        self,
        shape_type: str,
        units_x: float,
        units_y: float,
        units_z: float,
        unit_type: str = "cuarta",
        has_cavity: bool = True,
        cavity_margin_units: float = 0.5
    ) -> SpatialBoundingBox:
        """
        Delineates the outer boundaries and inner cavity using intuitive units
        (such as "cuartas" or "px") before touching a physical tape measure.
        """
        if unit_type == "cuarta":
            scale_cm = self.human_span_cm
            unit_name = "cuarta_humana"
        elif unit_type in ["px", "pixel"]:
            scale_cm = 1.0 / self.px_per_cm
            unit_name = "screen_px"
        else:
            scale_cm = 1.0  # Default cm
            unit_name = "metric_cm"

        outer_x_cm = round(units_x * scale_cm, 2)
        outer_y_cm = round(units_y * scale_cm, 2)
        outer_z_cm = round(units_z * scale_cm, 2)

        cavity_cm = None
        if has_cavity:
            margin_cm = round(cavity_margin_units * scale_cm, 2)
            cavity_cm = {
                "cavity_width_x": max(0.0, round(outer_x_cm - (2 * margin_cm), 2)),
                "cavity_length_y": max(0.0, round(outer_y_cm - (2 * margin_cm), 2)),
                "cavity_depth_z": max(0.0, round(outer_z_cm - margin_cm, 2)),
            }

        return SpatialBoundingBox(
            shape_type=shape_type,
            outer_bounds_cm={
                "width_x": outer_x_cm,
                "length_y": outer_y_cm,
                "height_z": outer_z_cm
            },
            inner_cavity_cm=cavity_cm,
            reference_unit_used=unit_name,
            reference_unit_value=scale_cm,
            unit_count={"units_x": units_x, "units_y": units_y, "units_z": units_z}
        )

    def calculate_views(self, box: SpatialBoundingBox) -> MultiViewProjection:
        """
        Calculates the orthogonal technical views (Planta, Alzado, Perfil)
        and the structural cavity-to-solid ratio.
        """
        bounds = box.outer_bounds_cm
        cavity = box.inner_cavity_cm

        outer_vol = bounds["width_x"] * bounds["length_y"] * bounds["height_z"]
        cavity_vol = 0.0
        if cavity:
            cavity_vol = (
                cavity["cavity_width_x"]
                * cavity["cavity_length_y"]
                * cavity["cavity_depth_z"]
            )

        hollow_ratio = round(cavity_vol / outer_vol, 3) if outer_vol > 0 else 0.0

        top_view = {
            "view_name": "Vista Superior (Planta)",
            "plane": "X-Y",
            "width_x_cm": bounds["width_x"],
            "length_y_cm": bounds["length_y"],
            "features": "Abertura de tolva / entrada superior y sujeción de bastidor"
        }

        front_view = {
            "view_name": "Vista Frontal (Alzado)",
            "plane": "X-Z",
            "width_x_cm": bounds["width_x"],
            "height_z_cm": bounds["height_z"],
            "features": "Eje rotacional, chumaceras de piso, bancada y salida inferior"
        }

        side_view = {
            "view_name": "Vista Lateral (Perfil)",
            "plane": "Y-Z",
            "length_y_cm": bounds["length_y"],
            "height_z_cm": bounds["height_z"],
            "features": "Ángulo de inclinación de tolva, reductor y rampa de desahogo"
        }

        return MultiViewProjection(
            top_view_planta=top_view,
            front_view_alzado=front_view,
            side_view_perfil=side_view,
            cavity_hollow_ratio=hollow_ratio
        )

    def sensorless_proximity_and_fit(
        self,
        box: SpatialBoundingBox,
        internal_object_cm: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Evaluates mechanical fit and boundaries WITHOUT physical proximity sensors (LiDAR/sonar/IR).
        "SIN NECESIDAD DE SENSOR DE PROXIMIDAD O SIMILAR":
        Pure intrinsic geometric projection from the mental bounding box.
        """
        cavity = box.inner_cavity_cm or box.outer_bounds_cm

        obj_w = internal_object_cm.get("width_x", 0.0)
        obj_l = internal_object_cm.get("length_y", 0.0)
        obj_h = internal_object_cm.get("height_z", 0.0)

        clearance_x = round(cavity.get("cavity_width_x", cavity.get("width_x", 0.0)) - obj_w, 2)
        clearance_y = round(cavity.get("cavity_length_y", cavity.get("length_y", 0.0)) - obj_l, 2)
        clearance_z = round(cavity.get("cavity_depth_z", cavity.get("height_z", 0.0)) - obj_h, 2)

        fits_inside = clearance_x >= 0 and clearance_y >= 0 and clearance_z >= 0
        min_clearance = min(clearance_x, clearance_y, clearance_z)

        return {
            "sensorless_perception": True,
            "physical_sensors_needed": False,  # Cero sensores de proximidad / LiDAR / Ultrasonido
            "method": "Proyección geométrica intrínseca (referencia mental en cuartas/px)",
            "fits_inside_cavity": fits_inside,
            "clearance_margins_cm": {
                "clearance_x": clearance_x,
                "clearance_y": clearance_y,
                "clearance_z": clearance_z,
            },
            "minimum_clearance_cm": min_clearance,
            "verdict": (
                "HOLGURA_ADECUADA" if min_clearance > 1.0 else (
                    "AJUSTE_JUSTO_RIESGO_ROCE" if fits_inside else "COLISION_DETECTADA_AMPLIAR_HUECO"
                )
            ),
        }
