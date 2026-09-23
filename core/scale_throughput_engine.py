"""
IDC Core - Scale & Throughput Engine (Ley del Escalamiento: Hacer Más en Menos Tiempo, Pero a Mayor Costo)
Transcribes the inventor's dual economic scaling axiom:
  - "Si es pequeño... si nos vamos a lo grande, pues podemos hacer más con menos tiempo"
  - "PERO MAYOR COSTO": El contrapeso indispensable de la realidad.
  - La inversión de capital inicial (CAPEX) vs el tiempo de operación ahorrado (OPEX) y el punto de equilibrio.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ScaleComparison(BaseModel):
    small_scale_throughput_units_per_hr: float
    large_scale_throughput_units_per_hr: float
    throughput_multiplier: float
    time_to_process_target_hours_small: float
    time_to_process_target_hours_large: float
    time_saved_hours: float
    time_efficiency_gain_pct: float
    small_scale_cost: float
    large_scale_cost: float
    cost_increase_factor: float
    break_even_units: float  # Unidades necesarias para que el ahorro de tiempo compense el mayor costo
    is_large_scale_justified: bool
    scalability_verdict: str


class ScaleThroughputEngine:
    """
    Evaluates mechanical, physical, and algorithmic scaling:
    Balances the massive time savings of large-scale throughput against its higher initial capital cost ('Mayor Costo').
    """

    def calculate_scale_advantage(
        self,
        target_workload_units: float,  # e.g., 6,000 kg de maíz o jobs de cómputo
        small_scale_capacity_per_hr: float = 100.0,
        large_scale_capacity_per_hr: float = 1500.0,
        small_scale_cost: float = 300.0,    # e.g., $300 dólares (chatarra/taller unitario)
        large_scale_cost: float = 2800.0,   # e.g., $2800 dólares (industrial, tolva grande, motor 10 HP)
        hourly_operator_labor_value: float = 25.0
    ) -> ScaleComparison:
        time_small = round(target_workload_units / max(1.0, small_scale_capacity_per_hr), 2)
        time_large = round(target_workload_units / max(1.0, large_scale_capacity_per_hr), 2)

        time_saved = round(time_small - time_large, 2)
        multiplier = round(large_scale_capacity_per_hr / max(1.0, small_scale_capacity_per_hr), 1)
        efficiency_gain = round(((time_small - time_large) / time_small) * 100.0, 1) if time_small > 0 else 0.0

        delta_cost = max(0.0, large_scale_cost - small_scale_cost)
        cost_increase_factor = round(large_scale_cost / max(1.0, small_scale_cost), 1)

        # Ahorro de tiempo en valor monetario
        # Ahorro por unidad: (1/capacity_small - 1/capacity_large) * hourly_rate
        time_saving_per_unit_hrs = (1.0 / small_scale_capacity_per_hr) - (1.0 / large_scale_capacity_per_hr)
        money_saved_per_unit = time_saving_per_unit_hrs * hourly_operator_labor_value

        break_even_units = round(delta_cost / max(0.001, money_saved_per_unit), 1) if money_saved_per_unit > 0 else 999999.0
        is_justified = target_workload_units >= break_even_units

        if is_justified:
            verdict = (
                f"A gran escala produces {multiplier}x más rápido (ahorras {time_saved}h). "
                f"Tiene mayor costo inicial (${large_scale_cost} vs ${small_scale_cost}), "
                f"pero el volumen ({target_workload_units} unidades) supera el punto de equilibrio ({break_even_units} unidades). "
                "¡JUSTIFICADO: HACER MÁS EN MENOS TIEMPO AMORTIZA EL MAYOR COSTO!"
            )
        else:
            verdict = (
                f"A gran escala ahorras tiempo ({time_saved}h), PERO A MAYOR COSTO (${large_scale_cost} vs ${small_scale_cost}). "
                f"Para un volumen bajo de {target_workload_units} unidades (debajo de {break_even_units} unidades de equilibrio), "
                "NO SE JUSTIFICA EL GASTO: El prototipo pequeño de bajo costo es la decisión inteligente."
            )

        return ScaleComparison(
            small_scale_throughput_units_per_hr=small_scale_capacity_per_hr,
            large_scale_throughput_units_per_hr=large_scale_capacity_per_hr,
            throughput_multiplier=multiplier,
            time_to_process_target_hours_small=time_small,
            time_to_process_target_hours_large=time_large,
            time_saved_hours=time_saved,
            time_efficiency_gain_pct=efficiency_gain,
            small_scale_cost=small_scale_cost,
            large_scale_cost=large_scale_cost,
            cost_increase_factor=cost_increase_factor,
            break_even_units=break_even_units,
            is_large_scale_justified=is_justified,
            scalability_verdict=verdict
        )
