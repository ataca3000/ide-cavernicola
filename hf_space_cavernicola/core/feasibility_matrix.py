"""
IDC Core - Feasibility & Bottleneck Matrix (Matriz de Viabilidad, Desgaste y Opciones A/B/C)
Transcribes the inventor's pragmatic equation:
  - "El verdadero cuello sale entre lo que tienes, lo que ya existe, el presupuesto, qué es viable y qué no"
  - "Calculas el desgaste por trabajo entre el tiempo"
  - "Lo que ya existe vs lo que tendrías que inventar entre el tiempo que te llevará construirlo"
  - "Si no valida o es mejor comprar uno que ya venden -> Opción B, o de ahí sale C: NUNCA PARAR"
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DecisionStrategy(str, Enum):
    USE_IN_SHOP = "USE_IN_SHOP"              # Opción A: Reutilizar lo que ya tienes a mano
    BUY_COMMERCIAL = "BUY_COMMERCIAL"        # Opción B1: Mejor comprar lo que ya venden hecho
    FABRICATE_CUSTOM = "FABRICATE_CUSTOM"    # Opción B2: Fabricar/inventar a medida
    PIVOT_OPTION_C = "PIVOT_OPTION_C"        # Opción C: Mutar diseño o método alternativo (Nunca parar)


class WearAndProtectionAnalysis(BaseModel):
    component: str
    workload_joules_or_cycles: float
    operating_hours: float
    wear_rate: float  # (workload / time)
    durability_lifespan_hours: float
    protection_measure: str  # e.g., "fusible mecánico", "tornillo de sacrificio", "engrase"
    sacrificial_part_used: bool  # Protege componentes caros con piezas baratas reemplazables


class FeasibilityVerdict(BaseModel):
    item_or_subsystem: str
    decision: DecisionStrategy
    rationale: str
    estimated_cost: float
    estimated_hours: float
    wear_analysis: WearAndProtectionAnalysis
    next_pivot_plan: Optional[str] = None  # Plan C para "nunca parar"


class FeasibilityMatrixEngine:
    """
    Evaluates physical durability, workshop inventory, make vs buy feasibility,
    and fallback mutation options (A -> B -> C) to never stall development.
    """

    def __init__(self, hourly_shop_rate: float = 25.0):
        self.hourly_shop_rate = hourly_shop_rate

    def calculate_wear(
        self,
        component: str,
        workload_cycles: float,
        operating_hours: float,
        material_durability_factor: float = 1.0,
        protection_strategy: str = "Tornillos de grado bajo como fusibles de sacrificio"
    ) -> WearAndProtectionAnalysis:
        """
        Calcula el desgaste = trabajo / tiempo.
        Evalúa si usa partes de sacrificio baratas para salvar piezas caras (motor/reductor).
        """
        effective_hours = max(1.0, operating_hours)
        base_wear_rate = round(workload_cycles / (effective_hours * material_durability_factor), 2)
        lifespan_hours = round((10000.0 * material_durability_factor) / max(0.1, base_wear_rate), 1)

        is_sacrificial = any(w in protection_strategy.lower() for w in ["sacrificio", "fusible", "tornillo", "barato"])

        return WearAndProtectionAnalysis(
            component=component,
            workload_joules_or_cycles=workload_cycles,
            operating_hours=operating_hours,
            wear_rate=base_wear_rate,
            durability_lifespan_hours=lifespan_hours,
            protection_measure=protection_strategy,
            sacrificial_part_used=is_sacrificial
        )

    def evaluate_feasibility(
        self,
        item_name: str,
        in_shop_stock: bool,
        commercial_price: Optional[float],
        fabrication_raw_cost: float,
        build_hours: float,
        budget_limit: float,
        max_time_hours: float,
        workload_cycles: float = 1000.0,
        operating_hours: float = 50.0
    ) -> FeasibilityVerdict:
        """
        Ejecuta el árbol de decisión del inventor:
        1. ¿Lo tienes a mano? -> Opción A: Úsalo ya.
        2. ¿Existe en venta, es más barato/rápido que construirlo y entra en presupuesto? -> Opción B1: Cómpralo hecho.
        3. ¿Fabricarlo es viable en tiempo y dinero? -> Opción B2: Fabrícalo a mano.
        4. Si no valida ninguna -> Opción C: Rediseñar con otra idea y ¡NUNCA PARAR!
        """
        wear = self.calculate_wear(
            component=item_name,
            workload_cycles=workload_cycles,
            operating_hours=operating_hours
        )

        # 1. Opción A: En inventario del taller
        if in_shop_stock:
            return FeasibilityVerdict(
                item_or_subsystem=item_name,
                decision=DecisionStrategy.USE_IN_SHOP,
                rationale=f"Ya lo tienes en taller a costo $0 inmediato. Proceder directo.",
                estimated_cost=0.0,
                estimated_hours=0.5,
                wear_analysis=wear,
                next_pivot_plan=None
            )

        total_fabricate_cost = fabrication_raw_cost + (build_hours * self.hourly_shop_rate)

        # 2. Opción B1: Comprar comercial existente si es más eficiente
        if commercial_price is not None and commercial_price <= budget_limit:
            if commercial_price < total_fabricate_cost or build_hours > max_time_hours:
                return FeasibilityVerdict(
                    item_or_subsystem=item_name,
                    decision=DecisionStrategy.BUY_COMMERCIAL,
                    rationale=(
                        f"Ya existe en el mercado por ${commercial_price}, que es menor o más rápido "
                        f"que fabricarlo por ${total_fabricate_cost} en {build_hours}h. Mejor comprarlo."
                    ),
                    estimated_cost=commercial_price,
                    estimated_hours=1.0,  # Tiempo de adquisición
                    wear_analysis=wear,
                    next_pivot_plan="Si no hay stock en tienda -> pasar a Opción B2 (fabricar a medida)"
                )

        # 3. Opción B2: Fabricar a mano en taller
        if total_fabricate_cost <= budget_limit and build_hours <= max_time_hours:
            return FeasibilityVerdict(
                item_or_subsystem=item_name,
                decision=DecisionStrategy.FABRICATE_CUSTOM,
                rationale=(
                    f"Fabricación propia viable: costo material ${fabrication_raw_cost} + {build_hours}h trabajo "
                    f"dentro del presupuesto de ${budget_limit}."
                ),
                estimated_cost=total_fabricate_cost,
                estimated_hours=build_hours,
                wear_analysis=wear,
                next_pivot_plan="Si falla la soldadura o temple -> pasar a Opción C (reutilizar otra pieza)"
            )

        # 4. Opción C: Ninguna de las dos valida -> Mutar diseño, ¡NUNCA PARAR!
        return FeasibilityVerdict(
            item_or_subsystem=item_name,
            decision=DecisionStrategy.PIVOT_OPTION_C,
            rationale=(
                f"El costo (${total_fabricate_cost}) o tiempo ({build_hours}h) excede límites (${budget_limit}, {max_time_hours}h). "
                f"Activando Opción C: rediseñar mecanismo con materiales de desguace o geometría más simple. ¡NUNCA PARAR!"
            ),
            estimated_cost=fabrication_raw_cost * 0.4,
            estimated_hours=build_hours * 0.5,
            wear_analysis=wear,
            next_pivot_plan="Opción C activada: pivote a transmisión por polea en V o engranaje recuperado."
        )
