"""
IDC (Inventor Driven Cognition) CLI
Unified Command-Line Interface for Autonomous Causal Cognitive Architecture.
Authored by Luis Felipe Durán Salinas (ATACA3000 / Brecha Soluciones DS).
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from contracts import Goal
from core.agent import IDCAgent
from core.memory_manager import MemoryManager
from core.repo_analyzer import RepoAnalyzer
from plugins.llm.gemini_plugin import GeminiPlugin
from plugins.llm.ollama_plugin import OllamaPlugin


def print_banner():
    banner = r"""
========================================================================
   ___ ____   ____    ____                 _ _   _            
  |_ _|  _ \ / ___|  / ___|___   __ _ _ __ (_) |_(_)_   _____  
   | || | | | |     | |   / _ \ / _` | '_ \| | __| \ \ / / _ \ 
   | || |_| | |___  | |__| (_) | (_| | | | | | |_| |\ V /  __/ 
  |___|____/ \____|  \____\___/ \__, |_| |_|_|\__|_| \_/ \___| 
                                |___/                          
  INVENTOR DRIVEN COGNITION - Autonomous Causal AI Architecture
  Author: Luis Felipe Durán Salinas (ATACA3000 / Brecha Soluciones DS)
========================================================================
"""
    print(banner)


def cmd_scan(args):
    """Scans the repository AST, technical debt, and CI/CD workflows."""
    print("-> [IDC METACOGNITION] Iniciando escaneo semantico del repositorio...")
    analyzer = RepoAnalyzer(repo_root=args.path)
    summary = analyzer.generate_repository_summary()

    metrics = summary["metrics"]
    print("\n[ESTADISTICAS DE LA BASE DE CODIGO]:")
    print(f"  * Archivos Python:       {metrics['total_python_files']}")
    print(f"  * Lineas de Codigo (LOC): {metrics['total_lines_of_code']}")
    print(f"  * Clases Detectadas:     {metrics['total_classes']}")
    print(f"  * Pipelines CI/CD:       {metrics['ci_workflows_count']}")
    print(f"  * Marcadores de Deuda:   {metrics['technical_debt_items']}")

    if summary["ci_workflows"]:
        print("\n[CI/CD PIPELINES]:")
        for wf in summary["ci_workflows"]:
            print(f"  * {wf['file']} ({wf['steps_count']} pasos, acciones: {', '.join(wf['actions_used'])})")

    if summary["technical_debt"]:
        print(f"\n[DEUDA TECNICA DETECTADA ({len(summary['technical_debt'])} items)]:")
        for item in summary["technical_debt"][:5]:
            print(f"  * [{item['tag']}] {item['file']}:{item['line']} -> {item['detail']}")

    print("\n[MUESTRA DEL GRAFO DE DEPENDENCIAS]:")
    for mod, deps in list(summary["dependency_graph"].items())[:6]:
        deps_str = ", ".join(deps) if deps else "(sin dependencias internas)"
        print(f"  * {mod} -> [{deps_str}]")


def cmd_rules(args):
    """Lists learned causal rules."""
    memory = MemoryManager()
    causal_dir = Path(memory.memory_paths["causal"])
    rules = []
    if causal_dir.exists():
        for rule_file in causal_dir.glob("rule_*.json"):
            try:
                with open(rule_file, "r", encoding="utf-8") as f:
                    rules.append(json.load(f))
            except Exception:
                pass

    print(f"\n[MEMORIA CAUSAL CONSOLIDADA] Total de Reglas: {len(rules)}")
    print("-" * 70)
    if not rules:
        print("  (Aun no hay reglas aprendidas. Ejecuta 'idc think' para generar experiencia.)")
        return

    for r in rules:
        r_id = r.get("id", "desconocido")
        goal = r.get("goal", "N/A")
        action = r.get("successful_action", r.get("cause", "N/A"))
        conf = r.get("confidence", 0.0)
        reps = r.get("replications", 1)
        improvement = r.get("metrics_improvement", {})
        imp_str = f"Mejora: {improvement.get('improvement_pct', 0)}%" if improvement else ""

        print(f"  * [{r_id}] Confianza: {conf:.2f} | Replicaciones: {reps}")
        print(f"    Objetivo: {goal}")
        print(f"    Accion Exitosa: {action}")
        if imp_str:
            print(f"    Metrica: {imp_str}")
        print()


def cmd_trash(args):
    """Lists causal trash entries (rejected hypotheses and failures)."""
    memory = MemoryManager()
    trash_dir = Path(memory.memory_paths["causal_trash"])
    items = []
    if trash_dir.exists():
        for trash_file in trash_dir.glob("trash_*.json"):
            try:
                with open(trash_file, "r", encoding="utf-8") as f:
                    items.append(json.load(f))
            except Exception:
                pass

    print(f"\n[CAUSAL TRASH (MEMORIA NEGATIVA)] Total de Fallos Registrados: {len(items)}")
    print("-" * 70)
    if not items:
        print("  (El basurero causal esta limpio.)")
        return

    for t in items:
        t_id = t.get("id", "desconocido")
        goal = t.get("goal", "N/A")
        action = t.get("failed_action", "N/A")
        reason = t.get("reason", "N/A")
        print(f"  * [{t_id}] Accion Fallida: '{action}'")
        print(f"    Para Objetivo: '{goal}'")
        print(f"    Razon del Descarte: {reason}")
        print()


def cmd_think(args):
    """Runs the cognitive loop with Gemini or Ollama for a given goal."""
    print(f"\n[OBJETIVO RECIBIDO]: '{args.goal}'")

    # Select LLM plugin
    if args.ollama:
        print("-> Conectando con motor local Ollama...")
        llm = OllamaPlugin(model=args.model or "qwen2.5-coder")
    else:
        llm = GeminiPlugin()
        status = "ACTIVO (Google AI Studio Key)" if llm.has_active_key() else "OFFLINE (Heuristico)"
        print(f"-> Conectando con Google Gemini Flash: {status}")

    agent = IDCAgent(llm_plugin=llm, initial_energy=args.energy)

    goal = Goal(
        id=f"goal_cli_{abs(hash(args.goal)) % 10000}",
        description=args.goal,
        priority=args.priority,
    )

    print("\n[PASO 1] Brainstorming y evaluacion contra Causal Trash...")
    brainstorm_res = agent.brainstorm(goal)
    action = brainstorm_res.get("action", "optimize_pipeline")
    hyp = brainstorm_res.get("hypothesis", "N/A")
    print(f"  * Accion Propuesta: '{action}'")
    print(f"  * Hipotesis Causal: {hyp}")

    rejected = brainstorm_res.get("rejected_hypotheses", [])
    if rejected:
        print(f"  * Restricciones de Causal Trash Inyectadas: {len(rejected)}")

    print("\n[PASO 2] Verificando en Real Sandbox / Entorno Empirico...")
    state = agent.run_step(
        goal=goal,
        candidate_action=action,
        context={
            "use_sandbox": True,
            "success": not args.simulate_failure,
            "baseline_s": 40.0,
            "expected_effect": "execution_speedup",
        },
    )

    print("\n[RESULTADO DEL CICLO COGNITIVO]:")
    print(f"  * Energia Restante:       {state.energy:.1f}%")
    print(f"  * Reglas Causales Activas: {len(state.active_rules)}")
    print(f"  * Incertidumbre Cognitiva: {state.uncertainty}")

    if state.active_rules:
        latest_rule_id = state.active_rules[-1]
        rule = agent.memory.get_causal_rule(latest_rule_id) or {}
        print(f"\n[NUEVA REGLA CONSOLIDADA]: {latest_rule_id}")
        print(f"   Accion: {rule.get('successful_action')}")
        print(f"   Confianza: {rule.get('confidence')}")


def main():
    parser = argparse.ArgumentParser(
        prog="idc",
        description="IDC (Inventor Driven Cognition) Autonomous Cognitive Engine",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # scan
    scan_parser = subparsers.add_parser("scan", help="Escanear repositorio mediante AST, CI y deuda tecnica")
    scan_parser.add_argument("--path", default=None, help="Ruta del repositorio a escanear")

    # rules
    subparsers.add_parser("rules", help="Listar reglas causales aprendidas")

    # trash
    subparsers.add_parser("trash", help="Listar acciones descartadas en Causal Trash")

    # think / run
    think_parser = subparsers.add_parser("think", help="Ejecutar ciclo de resolucion causal de un objetivo")
    think_parser.add_argument("goal", help="Descripcion del objetivo a resolver")
    think_parser.add_argument("--ollama", action="store_true", help="Usar Ollama local en vez de Gemini")
    think_parser.add_argument("--model", default=None, help="Nombre del modelo (ej. qwen2.5-coder o gemini-flash)")
    think_parser.add_argument("--energy", type=float, default=100.0, help="Energia inicial del agente")
    think_parser.add_argument("--priority", type=float, default=0.85, help="Prioridad del objetivo (0.0 a 1.0)")
    think_parser.add_argument("--simulate-failure", action="store_true", help="Simular fallo para probar Causal Trash")

    args = parser.parse_args()

    print_banner()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "rules":
        cmd_rules(args)
    elif args.command == "trash":
        cmd_trash(args)
    elif args.command == "think":
        cmd_think(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
