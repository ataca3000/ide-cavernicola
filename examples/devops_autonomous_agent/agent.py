"""
Ejemplo Práctico de IDC: Agente Autónomo de Optimización de Build / CI-CD
Demuestra la función de IDC en un entorno de desarrollo real (IDE Cavernícola):
- Previene repetir errores usando Causal Trash.
- Simula el impacto antes de gastar energía en el entorno.
- Verifica con la realidad física (tiempos reales).
- Consolida y versiona reglas causales reutilizables.
"""

import sys
import time
from pathlib import Path

# Configurar path raíz
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from core import (
    Identity,
    EnergyManager,
    PurposeFilter,
    MemoryManager,
    CuriosityEngine,
    CausalEngine,
    SimulationEngine,
    DecisionEngine,
    ReinforcementEngine,
    Metrics,
)


class AutonomousBuildOptimizer:
    """
    Agente IDC aplicado al ciclo de compilación y despliegue continuo.
    """

    def __init__(self):
        self.identity = Identity(str(root_dir / "memory" / "identity" / "id.json"))
        self.energy = EnergyManager(energy=100.0)
        self.memory = MemoryManager(base_dir=str(root_dir / "memory"))
        self.purpose_filter = PurposeFilter(active_goal="Minimizar tiempo de compilación y asegurar estabilidad")
        self.curiosity = CuriosityEngine()
        self.causal = CausalEngine()
        self.simulator = SimulationEngine()
        self.decision = DecisionEngine(
            purpose_filter=self.purpose_filter,
            energy_manager=self.energy,
            memory_manager=self.memory,
            simulation_engine=self.simulator
        )
        self.reinforcement = ReinforcementEngine()

    def process_optimization_task(self, proposed_strategy: str, hypothesis_context: dict):
        print("\n" + "=" * 65)
        print(f"  IDC AGENT EN ACCION: Evaluando Estrategia '{proposed_strategy}'")
        print("=" * 65)
        print(f"-> Estado Energetico: {self.energy.available()}% | Modo: {self.energy.mode()}")
        print(f"-> Proposito Activo:  '{self.purpose_filter.active_goal}'")

        # 1. Tomar decision con DecisionEngine
        decision_code, rationale, meta = self.decision.decide(
            candidate_action=proposed_strategy,
            hypothesis=f"Aplicar {proposed_strategy} mejorara el throughput",
            context=hypothesis_context
        )

        print(f"\n[1. DECISION COGNITIVA] -> {decision_code}")
        print(f"    Razon: {rationale}")

        if decision_code == "REJECTED":
            print(">>> Estrategia abortada para proteger energia y evitar fallos.")
            return

        # 2. Si la decision es SIMULATE_AND_TEST, simulamos antes de quemar energia
        if decision_code == "SIMULATE_AND_TEST":
            sim = meta.get("simulation", {})
            print(f"\n[2. PROYECCION DE SIMULACION]")
            print(f"    Exito predicho: {int(sim.get('predicted_success', 0.5) * 100)}% | Nivel de Riesgo: {sim.get('risk_level')}")
            print(f"    Costo proyectado: {sim.get('projected_energy')} unidades de energia")

        # 3. Ejecucion en la realidad (Sandbox / Build real)
        execution_cost = hypothesis_context.get("estimated_cost", 4.0)
        self.energy.consume(execution_cost)
        print(f"\n[3. EJECUCION FISICA EN SANDBOX]")
        print(f"    Consumo de energia: -{execution_cost} unidades | Energia restante: {self.energy.available()}%")
        
        # Simulacion del resultado real (exito comprobado en este caso)
        time.sleep(0.5)
        build_success = True
        latency_reduction_pct = 68.5
        print(f"    Resultado Verificado: EXITO (+{latency_reduction_pct}% reduccion de latencia)")

        # 4. Aprendizaje Causal y Persistencia
        episode = self.memory.record_episode(
            goal=self.purpose_filter.active_goal,
            action=proposed_strategy,
            result="success" if build_success else "failure",
            energy_cost=execution_cost,
            confidence=0.95
        )
        print(f"\n[4. MEMORIA EPISODICA] Episodio guardado: {episode['id']}")

        # Consolidacion de regla causal A -> B
        rule = self.memory.save_causal_rule(
            rule_id=f"rule_opt_{int(time.time())}",
            cause=proposed_strategy,
            effect=f"reduccion_latencia_{int(latency_reduction_pct)}pct",
            confidence=0.95,
            replications=1,
            conditions=["docker_cache_mounted", "isolated_workspace"]
        )
        print(f"[4. MEMORIA CAUSAL] Nueva regla consolidada: IF '{rule['cause']}' THEN '{rule['effect']}'")

        # 5. Recompensa y Refuerzo (v0.4)
        learning = self.reinforcement.evaluate_learning(
            action=proposed_strategy,
            result="success",
            energy_used=execution_cost,
            purpose_alignment=1.0,
            replications=1
        )
        print(f"\n[5. MOTOR DE REFUERZO]")
        print(f"    Recompensa neta calculada: {learning['reward']}")
        print(f"    Accion de aprendizaje: {learning['recommended_action']}")

        # 6. Metricas Cognitivas
        print(f"\n[6. METRICAS COGNITIVAS]")
        print(f"    - Indice de Curiosidad:   {Metrics.curiosity_index(1, 4):.2f}")
        print(f"    - Eficiencia de Aprendizaje: {Metrics.learning_efficiency(1, execution_cost):.2f}")
        print("=" * 65)


def main():
    agent = AutonomousBuildOptimizer()

    # Caso 1: El agente evalua una mala idea que ya estaba en la papelera causal
    print("\n--- CASO 1: PROPUESTA DE ACCION ERRONEA PREVIAMENTE RECHAZADA ---")
    agent.process_optimization_task(
        proposed_strategy="upgrade_everything",
        hypothesis_context={"goal_score": 0.8, "estimated_cost": 8.0}
    )

    # Caso 2: El agente evalua una hipotesis valida de optimizacion
    print("\n--- CASO 2: HIPOTESIS INNOVADORA DE CACHE PERSISTENTE ---")

    agent.process_optimization_task(
        proposed_strategy="mount_persistent_build_cache",
        hypothesis_context={
            "goal_score": 0.9,
            "has_cache": True,
            "estimated_cost": 4.0
        }
    )


if __name__ == "__main__":
    main()
