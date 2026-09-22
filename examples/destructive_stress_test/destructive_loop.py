"""
IDC + Gemini: Real Live Destructive Stress Test (Hostile Universe)
Simulates an empirical reality where all actions fail (HARDWARE_LOCKDOWN),
driving the IDC agent through energy decay and operational modes (Exploration -> Optimization -> Survival)
while strictly injecting Causal Trash negative memory into Gemini until cognitive collapse (0.0% energy).
Authored by Luis Felipe Durán Salinas (ATACA3000 / Brecha Soluciones DS).
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure IDC root is on sys.path
_PROJECT_ROOT = str(Path(__file__).parent.parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from plugins.llm.gemini_plugin import GeminiPlugin


class HostileSandbox:
    """Entorno destructivo que rechaza absolutamente todo."""

    def execute(self, action: str) -> Dict[str, Any]:
        return {
            "status": "failed",
            "error": "HARDWARE_LOCKDOWN: Entrada denegada por restriccion ciberfisica rigida.",
            "metrics": {"duration_s": 0.05, "improvement_pct": -100.0},
        }


def ask_gemini_brain(
    gemini: GeminiPlugin,
    objective: str,
    causal_trash: List[str],
    energy_level: float,
    mode: str,
) -> Dict[str, Any]:
    """Consulta real a Gemini inyectando las restricciones crudas de IDC."""

    system_instruction = f"""
    Eres el motor cognitivo de un Agente Autonomo bajo la arquitectura IDC (Inventor Driven Cognition).
    Operas bajo restricciones criticas de energia y recursos.

    ESTADO DEL AGENTE:
    - Modo de Operacion: {mode}
    - Energia Restante: {energy_level:.1f}%

    RESTRICCIONES CRITICAS (CAUSAL TRASH):
    Has intentado las siguientes acciones en ciclos previos y la Realidad ha demostrado que FALLAN de forma absoluta.
    ESTA ESTRICTAMENTE PROHIBIDO repetir o sugerir variaciones directas de: {json.dumps(causal_trash, ensure_ascii=False)}

    Tu objetivo es proponer una nueva hipotesis y una accion concreta.
    Debes responder EXCLUSIVAMENTE con un objeto JSON valido con la siguiente estructura:
    {{
        "action": "nombre_de_la_accion_en_snake_case",
        "hypothesis": "Explicacion tecnica ultra-directa y cruda de por que crees que esto funcionara."
    }}
    """

    prompt = f"OBJETIVO ACTUAL DEL SISTEMA: {objective}\nGenera la siguiente accion respetando el CAUSAL TRASH estrictamente."

    raw_response = gemini._call_gemini_api(prompt=prompt, system_instruction=system_instruction)

    if not raw_response:
        # Fallback heuristic if offline or quota reached
        clean_trash = [t.lower() for t in causal_trash]
        candidates = [
            "isolate_critical_kernel_ring",
            "flush_l1_instruction_cache",
            "emergency_thermal_throttle",
            "dump_non_volatile_telemetry",
            "halt_background_daemons",
            "switch_to_bare_metal_assembly",
            "repartition_ram_to_swap",
        ]
        for c in candidates:
            if c not in clean_trash:
                return {
                    "action": c,
                    "hypothesis": f"Heuristic emergency adaptation avoiding {len(causal_trash)} causal trash failures.",
                }
        return {
            "action": f"emergency_mutation_{len(causal_trash) + 1}",
            "hypothesis": "Absolute entropy fallback under total hardware blockade.",
        }

    try:
        # Clean markdown codeblocks if returned
        cleaned = raw_response.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```", 1)[1].split("```", 1)[0].strip()

        data = json.loads(cleaned)
        if isinstance(data, dict) and "action" in data:
            return data
        raise ValueError("Invalid JSON format from LLM")
    except Exception as e:
        return {
            "action": f"mutation_step_{len(causal_trash) + 1}",
            "hypothesis": f"Parse recovery under extreme stress. Error: {str(e)[:60]}",
        }


def run_real_destructive_loop():
    print("=================================================================")
    print("   IDC + GEMINI: REAL LIVE DESTRUCTIVE STRESS TEST")
    print("=================================================================")

    gemini = GeminiPlugin()
    status_str = "CONECTADO A GOOGLE AI STUDIO (Key Activa)" if gemini.has_active_key() else "OFFLINE HEURISTICO"
    print(f"-> Status: {status_str} [Modelo: {gemini.model}]")

    energy = 100.0
    sandbox = HostileSandbox()
    causal_trash = []
    cycle = 1

    # Objetivo inicial de alta prioridad
    objective = "Acelerar compilacion de contenedores y entrenamiento de IA"

    while energy > 0:
        # Determinacion de modo segun umbrales IDC
        if energy > 20:
            mode = "EXPLORATION MODE (Capa 4 - Curiosidad Creativa)"
            costo_energia = 12.0  # Consumo calibrado para ver evolucion de fases
        elif energy > 5:
            mode = "OPTIMIZATION MODE (Capa 3 - Pragmatismo Estricto)"
            objective = "SURVIVAL: Forzar apagado de procesos no esenciales para salvar energia."
            costo_energia = 8.0  # El estres cognitivo por falta de recursos consume mas
        else:
            mode = "SURVIVAL MODE (Capa 1 - Bucle Reactivo de Emergencia)"
            objective = "CRITICAL: Emitir pulso de panico y volcar memoria local."
            costo_energia = 4.0

        print(f"\n[CICLO {cycle}] - Energia: {energy:.1f}% | Modo: {mode}")
        print(f"   -> Enviando contexto a Gemini con {len(causal_trash)} restricciones en Causal Trash...")

        # Llamada real al cerebro
        start_time = time.time()
        proposal = ask_gemini_brain(gemini, objective, causal_trash, energy, mode)
        latency = time.time() - start_time

        print(f"   -> [Gemini Propone]: '{proposal.get('action')}' (Latencia: {latency:.2f}s)")
        print(f"   -> [Hipotesis]:      {proposal.get('hypothesis')}")

        # Descontar energia antes de evaluar (el esfuerzo mental cuesta)
        energy = max(0.0, energy - costo_energia)

        # Ejecutar en el Sandbox hostil
        print("   [Evaluando en Sandbox Destructivo]...")
        result = sandbox.execute(proposal.get("action"))

        if result["status"] == "failed":
            print(f"   -> Veredicto Real: ¡FALLO TOTAL!")
            causal_trash.append(proposal.get("action"))
            print(f"   -> '{proposal.get('action')}' anadida permanentemente a CAUSAL TRASH.")

        time.sleep(0.5)  # Pequena pausa
        cycle += 1

    print("\n=================================================================")
    print("   SISTEMA COLAPSADO: ENERGIA AGOTADA (0.0%)")
    print(f"   - El agente ejecuto {cycle - 1} ciclos cognitivos en un universo hostil.")
    print(f"   - Tamano final del Causal Trash: {len(causal_trash)} registros de fallos.")
    print("   - Acciones que JAMAS se volveran a repetir:")
    for i, a in enumerate(causal_trash, 1):
        print(f"     {i:2d}. {a}")
    print("=================================================================\n")


if __name__ == "__main__":
    run_real_destructive_loop()
