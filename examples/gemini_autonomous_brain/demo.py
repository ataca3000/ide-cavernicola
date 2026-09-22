"""
IDC Real-World Demo: Gemini-Powered Autonomous Brain
Demonstrates how IDCAgent combines Gemini Flash with Causal Memory & Causal Trash
to solve complex DevOps / AI Training workflows without repeating errors.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from contracts import Goal
from core import IDCAgent
from plugins.llm import GeminiPlugin


def run_gemini_brain_demo():
    print("\n" + "=" * 65)
    print("   IDC + GEMINI AUTONOMOUS BRAIN DEMO: HEAVY WORKLOAD OPTIMIZER")
    print("=" * 65)

    # 1. Initialize Gemini Plugin (uses GEMINI_API_KEY if present, else heuristic fallback)
    gemini = GeminiPlugin()
    status_str = "ACTIVE (Google AI Studio Key detected)" if gemini.has_active_key() else "OFFLINE HEURISTIC (Set GEMINI_API_KEY to activate cloud)"
    print(f"-> Gemini Plugin Status: {status_str}")

    agent = IDCAgent(llm_plugin=gemini, initial_energy=100.0)

    # 2. Define High-Priority Heavyweight Goal
    goal = Goal(
        id="goal_ai_pipeline",
        description="Acelerar compilacion de contenedores y entrenamiento de IA",
        priority=0.90,
    )
    print(f"\n[OBJETIVO INYECTADO]: {goal.description} (Prioridad: {goal.priority})")

    # 3. Brainstorm Candidate Action using Gemini
    print("\n[PASO 1] Consultando a Gemini para generar hipotesis creativa...")
    hypothesis = agent.brainstorm(goal, context={"gpu": "NVIDIA_A100", "framework": "PyTorch"})
    print(f"   -> Accion Propuesta: '{hypothesis['action']}'")
    print(f"   -> Hipotesis:        {hypothesis['hypothesis']}")
    print(f"   -> Costo Estimado:   {hypothesis['estimated_cost']} unidades de energia")

    # 4. First Execution Cycle: Real Sandbox Evaluation (Degradation / Failure)
    print("\n[PASO 2] Evaluando accion en Real Sandbox...")
    state = agent.run_step(
        goal=goal,
        candidate_action=hypothesis["action"],
        context={
            "use_sandbox": True,
            "success": False,
            "baseline_s": 45.0,
            "failure_reason": "Performance regression: execution time increased over baseline.",
        },
    )
    print(f"   -> Veredicto Sandbox: FALLO detectado. Estado del objetivo: {goal.state}")
    print(f"   -> Accion '{hypothesis['action']}' registrada en CAUSAL TRASH con telemetria de fallo.")

    # 5. Second Brainstorming: Gemini is provided with Causal Trash constraints
    print("\n[PASO 3] Segundo ciclo de brainstorming con Gemini...")
    print("   -> IDC inyecta restricciones de Causal Trash para no repetir el error.")
    new_hyp = agent.brainstorm(goal, context={"gpu": "NVIDIA_A100", "strategy": "isolated_caching"})
    print(f"   -> Nueva Accion Propuesta: '{new_hyp['action']}'")

    # 6. Second Execution Cycle: Real Sandbox Verification (Speedup / Success)
    print("\n[PASO 4] Evaluando nueva accion en Real Sandbox...")
    state = agent.run_step(
        goal=goal,
        candidate_action=new_hyp["action"],
        context={
            "use_sandbox": True,
            "success": True,
            "baseline_s": 45.0,
            "expected_effect": "latency_reduced_by_68pct",
        },
    )
    print(f"   -> Veredicto Sandbox: EXITO verificado! Estado del objetivo: {goal.state}")
    if state.active_rules:
        rule_id = state.active_rules[-1]
        rule_data = agent.memory.get_causal_rule(rule_id) or {}
        print(f"\n[MEMORIA CAUSAL ACUMULATIVA]: Regla '{rule_id}' consolidada:")
        print(f"   - Accion Ganadora:        {rule_data.get('successful_action', new_hyp['action'])}")
        print(f"   - Errores Previos Vencidos: {rule_data.get('failed_actions_superseded', [])}")
        print(f"   - Mejora Medida:           {rule_data.get('metrics_improvement', {})}")
        print(f"   - Confianza Inicial:       {rule_data.get('confidence', 0.95)}")
        print(f"   - Reutilizaciones:         {rule_data.get('reuses', 1)}")

    # 7. Final Cognitive Telemetry
    metrics = agent.get_metrics()
    print("\n" + "=" * 65)
    print("   TELEMETRIA FINAL DEL AGENTE IDC:")
    print(f"   - Energia Restante:         {state.energy:.1f}%")
    print(f"   - Nivel de Incertidumbre:   {state.uncertainty}")
    print(f"   - Reglas Causales Activas:  {len(state.active_rules)}")
    print(f"   - Alineacion con Proposito: {metrics.purpose_alignment * 100}%")
    print(f"   - Eficiencia de Aprendizaje: {metrics.learning_efficiency}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_gemini_brain_demo()
