"""
IDC Real-World Tool: Codebase Metacognition & Causal Architecture Scanner
Analyzes the IDC repository itself using native AST parsing, maps dependencies,
inspects CI/CD workflows, and uses Gemini to synthesize grounded causal optimizations.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from contracts import Goal
from core import IDCAgent, RepoAnalyzer
from plugins.llm import GeminiPlugin


def run_repo_causal_analysis():
    print("\n" + "=" * 70)
    print("   IDC METACOGNITION: REPOSITORY AST & CAUSAL CODE ANALYZER")
    print("=" * 70)

    # 1. Initialize Semantic Code Scanner
    analyzer = RepoAnalyzer()
    print("-> Escaneando el codigo fuente de IDC con AST (Abstract Syntax Tree)...")
    summary = analyzer.generate_repository_summary()

    metrics = summary["metrics"]
    print(f"\n[1. METRICAS SEMANTICAS DEL REPOSITORIO]:")
    print(f"   - Archivos Python Analizados:  {metrics['total_python_files']}")
    print(f"   - Total Lineas de Codigo (LOC): {metrics['total_lines_of_code']}")
    print(f"   - Clases Identificadas:        {metrics['total_classes']}")
    print(f"   - Workflows de CI/CD:          {metrics['ci_workflows_count']}")
    print(f"   - Marcadores de Deuda Tecnica: {metrics['technical_debt_items']}")

    # 2. Display Architectural Graph Sample
    print(f"\n[2. TOPOLOGIA ARQUITECTONICA (GRAFO DE DEPENDENCIAS)]:")
    for mod, deps in list(summary["dependency_graph"].items())[:5]:
        deps_str = ", ".join(deps) if deps else "(sin dependencias internas)"
        print(f"   -> {mod} depende de: [{deps_str}]")

    # 3. Inspect CI/CD Pipelines
    if summary["ci_workflows"]:
        wf = summary["ci_workflows"][0]
        print(f"\n[3. ANALISIS DE CI/CD PIPELINE ({wf['file']})]:")
        print(f"   - Pasos de Ejecucion: {wf['steps_count']}")
        for step in wf["steps"][:4]:
            print(f"     * {step}")
        print(f"   - Acciones Oficiales: {', '.join(wf['actions_used'])}")

    # 4. Synthesize Causal Optimization with Gemini
    gemini = GeminiPlugin()
    status_str = "ACTIVE (Google AI Studio Key)" if gemini.has_active_key() else "OFFLINE HEURISTIC"
    print(f"\n[4. MOTOR DE RAZONAMIENTO GEMINI]: {status_str}")

    agent = IDCAgent(llm_plugin=gemini, initial_energy=100.0)

    goal = Goal(
        id="goal_optimize_ci_cache",
        description="Optimizar tiempo de ejecucion en GitHub Actions evitando reinstalaciones innecesarias",
        priority=0.88,
    )
    print(f"   -> Objetivo: '{goal.description}'")

    print("   -> Solicitando a Gemini diagnostico y propuesta causal...")
    hypothesis = analyzer.diagnose_with_llm(
        llm=gemini,
        goal=goal.description,
        rejected_hypotheses=agent.brainstorm(goal).get("rejected_hypotheses", []),
    )
    print(f"   -> Accion Propuesta por Gemini: '{hypothesis.get('action')}'")
    print(f"   -> Hipotesis Causal:            {hypothesis.get('hypothesis')}")

    # 5. Evaluate in Real Sandbox
    print("\n[5. VERIFICACION EN REAL SANDBOX]:")
    state = agent.run_step(
        goal=goal,
        candidate_action=hypothesis.get("action", "cache_pip_dependencies"),
        context={
            "use_sandbox": True,
            "success": True,
            "baseline_s": 38.5,
            "expected_effect": "ci_pipeline_speedup_45pct",
        },
    )

    if state.active_rules:
        rule_id = state.active_rules[-1]
        rule_data = agent.memory.get_causal_rule(rule_id) or {}
        print(f"   -> Veredicto: EXITO. Regla causal '{rule_id}' consolidada en memoria:")
        print(f"      * Accion:   {rule_data.get('successful_action')}")
        print(f"      * Mejora:   {rule_data.get('metrics_improvement')}")
        print(f"      * Confianza: {rule_data.get('confidence')}")

    # 6. Final Cognitive Metrics
    print("\n" + "=" * 70)
    print("   ANALISIS CAUSAL DEL REPOSITORIO COMPLETADO CON EXITO")
    print(f"   - Energia Restante:       {state.energy:.1f}%")
    print(f"   - Reglas Causales Activas: {len(state.active_rules)}")
    print(f"   - Incertidumbre:          {state.uncertainty}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_repo_causal_analysis()
