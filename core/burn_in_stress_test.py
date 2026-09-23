"""
IDC Core - Burn-in Stress Test Engine (La Prueba de Fuego del Inventor)
Transcribes the inventor's empirical validation axiom:
  - "Todo lleva un tiempo de trabajo por tiempo de descanso, hasta uno"
  - "No puedo futurizar porque depende de mucho más que simple cálculo, puede fallar cualquier cosa"
  - "En masa sería distinto, pero si lo trabajo durante 8 a 12 horas seguidas sin parar estaría con madre: es la prueba de fuego"
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DutyCycleProfile(BaseModel):
    name: str
    work_hours_per_session: float  # e.g., 8.0 a 12.0 horas continuas
    rest_cooling_hours: float       # Tiempo de enfriamiento y descanso térmico
    duty_factor: float              # work / (work + rest)
    anti_futurization_note: str     # Advertencia contra predicciones teóricas en papel


class BurnInStressReport(BaseModel):
    system_name: str
    simulated_or_real_hours: float
    max_sustained_temp_celsius: float
    vibration_bolt_loosening_detected: bool
    jammed_or_stalled: bool
    passed_burn_in: bool
    empirical_verdict: str


class BurnInStressTester:
    """
    Executes and evaluates the 8-12 hour continuous burn-in stress test ('Prueba de Fuego').
    Rejects naive paper-calculation predictions in favor of relentless continuous runtime testing.
    """

    MIN_BURN_IN_HOURS = 8.0
    TARGET_BURN_IN_HOURS = 12.0
    MAX_PERMISSIBLE_TEMP_CELSIUS = 75.0  # Límite térmico seguro de motor/chumaceras

    def create_duty_cycle(
        self,
        work_hours: float = 8.0,
        rest_hours: float = 2.0
    ) -> DutyCycleProfile:
        total = work_hours + rest_hours
        factor = round(work_hours / total, 3) if total > 0 else 1.0

        return DutyCycleProfile(
            name=f"Ciclo_{work_hours}h_trabajo_{rest_hours}h_descanso",
            work_hours_per_session=work_hours,
            rest_cooling_hours=rest_hours,
            duty_factor=factor,
            anti_futurization_note=(
                "Principio del Inventor: No futurizar por simple cálculo en papel. "
                "Cualquier factor no lineal (vibración, impureza, fatiga) puede fallar. "
                "Solo la prueba de fuego empírica valida el sistema."
            )
        )

    def evaluate_burn_in_test(
        self,
        system_name: str,
        actual_continuous_hours: float,
        peak_temp_celsius: float,
        bolts_retained_torque: bool,
        no_jams_occurred: bool
    ) -> BurnInStressReport:
        """
        Evalúa si la máquina o software superó la prueba de fuego (8-12 horas continuas).
        """
        hours_ok = actual_continuous_hours >= self.MIN_BURN_IN_HOURS
        temp_ok = peak_temp_celsius <= self.MAX_PERMISSIBLE_TEMP_CELSIUS
        mechanical_ok = bolts_retained_torque and no_jams_occurred

        passed = hours_ok and temp_ok and mechanical_ok

        if passed:
            verdict = (
                f"PRUEBA_DE_FUEGO_SUPERADA ({actual_continuous_hours:.1f}h continuas sin parar). "
                "Aguantó la jornada completa, tornillos firmes y temperatura estable. ¡ESTÁ CON MADRE!"
            )
        else:
            failures = []
            if not hours_ok:
                failures.append(f"No alcanzó las {self.MIN_BURN_IN_HOURS}h mínimas (corrió {actual_continuous_hours:.1f}h)")
            if not temp_ok:
                failures.append(f"Sobrecalentamiento ({peak_temp_celsius}°C > {self.MAX_PERMISSIBLE_TEMP_CELSIUS}°C)")
            if not bolts_retained_torque:
                failures.append("Tornillos o pernos aflojados por vibración")
            if not no_jams_occurred:
                failures.append("Atasco mecánico o bloqueo de rotor")
            verdict = f"FALLA EN PRUEBA DE FUEGO: {'; '.join(failures)}"

        return BurnInStressReport(
            system_name=system_name,
            simulated_or_real_hours=actual_continuous_hours,
            max_sustained_temp_celsius=peak_temp_celsius,
            vibration_bolt_loosening_detected=not bolts_retained_torque,
            jammed_or_stalled=not no_jams_occurred,
            passed_burn_in=passed,
            empirical_verdict=verdict
        )
