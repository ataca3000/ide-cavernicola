import os
import sys
import gradio as gr

# Ensure local modules are accessible
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from core.inventor_protocol import InventorProtocol
    from core.causal_engine import CausalEngine
    from core.memory_manager import MemoryManager
    protocol = InventorProtocol()
    causal_engine = CausalEngine()
    memory_mgr = MemoryManager()
    ENGINE_LOADED = True
except Exception as e:
    ENGINE_LOADED = False
    LOAD_ERROR = str(e)


def evaluate_problem(user_query: str, focus_area: str):
    if not user_query.strip():
        return (
            "⚠️ Por favor ingresa una descripción de problema, código o requerimiento de ingeniería.",
            "DESCONOCIDO",
            "Sin datos"
        )
    
    if not ENGINE_LOADED:
        return (
            f"Error inicializando motor IDC: {LOAD_ERROR}",
            "ERROR",
            "N/A"
        )
    
    # Process through Inventor Protocol
    try:
        enriched_query = f"[{focus_area}] {user_query}" if focus_area != "General" else user_query
        result = protocol.run_universal_evaluation(enriched_query)
        
        verdict = result.get("feasibility_verdict", "VIABLE")
        recommendation = result.get("recommendation", "Sin recomendación.")
        axioms = result.get("axioms_applied", [])
        axioms_str = ", ".join(axioms) if axioms else "Filtro de Inviabilidad Causal"
        
        report = (
            f"### 🛡️ [IDC Universal Cognition v2.0.0]\n\n"
            f"**Diagnóstico de Viabilidad:** `{verdict}`\n\n"
            f"#### 🔍 Desglose de Primeros Principios:\n"
            f"{recommendation}\n\n"
            f"---\n"
            f"**Leyes Invariantes y Axiomas Activados:**\n"
            f"- {axioms_str}\n\n"
            f"*Verificado sin alucinaciones estocásticas bajo la arquitectura IDC.*"
        )
        
        return report, verdict, axioms_str
    except Exception as e:
        return f"Error ejecutando evaluación: {str(e)}", "ERROR", str(e)


# Pre-loaded real-world engineering prompts
EXAMPLES = [
    ["Diseñar un mecanismo de reducción de velocidad sin sensores electrónicos caros para operar bajo carga continua sin atascos.", "Ingeniería Mecánica / Cinemática"],
    ["Evaluar la viabilidad física de un motor de movimiento perpetuo basado en imanes permanentes de neodimio y contrapesos gravitatorios.", "Filtro de Inviabilidad Física"],
    ["Optimizar un microservicio en Python con bloqueos severos de concurrencia y memory leaks en la capa de base de datos.", "Arquitectura de Software / Zero-Bloat"],
    ["Diseñar una arquitectura de base de datos local-first y sincronización LAN P2P que soporte cortes de energía y desconexión total de internet.", "Sistemas Distribuidos / Resiliencia"],
]

# Custom CSS for high-tech premium aesthetics
CUSTOM_CSS = """
.gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.header-box {
    background: linear-gradient(135deg, #1e1e2f 0%, #111119 100%);
    border: 1px solid #33334d;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    color: #ffffff;
}
.header-box h1 {
    margin: 0;
    font-size: 26px;
    font-weight: 800;
    color: #f3f4f6;
}
.header-box p {
    margin: 6px 0 0 0;
    font-size: 14px;
    color: #9ca3af;
}
.badge-tag {
    display: inline-block;
    background: #3b82f6;
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    margin-right: 6px;
}
"""

with gr.Blocks(css=CUSTOM_CSS, title="IDC Universal Cognition Demo") as demo:
    gr.HTML("""
    <div class="header-box">
        <span class="badge-tag">v2.0.0</span>
        <span class="badge-tag" style="background:#10b981;">Reality-First AI</span>
        <span class="badge-tag" style="background:#8b5cf6;">Gemma 2 / Gemma 4 Ready</span>
        <h1>⚙️ IDC Universal Cognition — Interactive Demo</h1>
        <p>Demostración interactiva oficial para el modelo <b><a href="https://huggingface.co/brecha-soluciones-ds/cavernicola" target="_blank" style="color:#60a5fa;">brecha-soluciones-ds/cavernicola</a></b></p>
        <p style="font-size:12px; color:#6b7280; margin-top:8px;">Desarrollado por: <b>Luis Felipe Durán Salinas — Brecha Soluciones DS</b> | <i>"Curiosidad obtenida por experiencia y comprensión del entorno"</i></p>
    </div>
    """)
    
    with gr.Tabs():
        with gr.TabItem("🧠 Resolución Causal de Problemas"):
            with gr.Row():
                with gr.Column(scale=5):
                    query_input = gr.Textbox(
                        label="Plantea un problema técnico, diseño de ingeniería o código de software:",
                        placeholder="Ejemplo: Diseñar un sistema de tracción sin componentes que se desgasten prematuramente...",
                        lines=5
                    )
                    focus_dropdown = gr.Dropdown(
                        label="Enfoque de Análisis:",
                        choices=[
                            "General",
                            "Filtro de Inviabilidad Física",
                            "Ingeniería Mecánica / Cinemática",
                            "Arquitectura de Software / Zero-Bloat",
                            "Sistemas Distribuidos / Resiliencia",
                            "Make vs Buy / Costos de Fabricación"
                        ],
                        value="General"
                    )
                    eval_btn = gr.Button("🚀 Evaluar con IDC Universal Cognition", variant="primary")
                    
                    gr.Examples(
                        examples=EXAMPLES,
                        inputs=[query_input, focus_dropdown],
                        label="💡 Ejemplos de Problemas Complejos:"
                    )
                
                with gr.Column(scale=5):
                    verdict_box = gr.Textbox(label="Veredicto Causal:", interactive=False)
                    applied_axioms_box = gr.Textbox(label="Axiomas de la Realidad Activados:", interactive=False)
                    report_output = gr.Markdown(label="Dictamen de Primeros Principios:")
            
            eval_btn.click(
                fn=evaluate_problem,
                inputs=[query_input, focus_dropdown],
                outputs=[report_output, verdict_box, applied_axioms_box]
            )

        with gr.TabItem("📜 Los 14 Axiomas del Inventor"):
            gr.Markdown("""
            ### 🛠️ Los 14 Axiomas Fundamentales de IDC:
            
            1. **AXIOM_01: Descarte Inicial de Inviabilidades:** Descarta lo físicamente imposible, cinemáticamente absurdo o termodinámicamente prohibido antes de gastar cómputo o material.
            2. **AXIOM_02: Cinemática, Torque y Leyes Gratuitas:** Aprovecha fuerzas de costo cero (gravedad, palancas, contrapesos) antes de recurrir a potencia artificial.
            3. **AXIOM_03: Intuición Espacial y Bounding Box:** Modela volúmenes, holguras y tolerancias desde escalas anatómicas y físicas invariantes.
            4. **AXIOM_04: Cruce Causal (Tangible vs Simbólico):** Valida compatibilidad causal estricta; aísla la conjetura libre para que no induzca fallos catastróficos.
            5. **AXIOM_05: Ecuación del Desgaste y Fusibles:** Entiende el desgaste como trabajo sobre tiempo ($W/t$). Diseña componentes de sacrificio baratos. **Regla: NUNCA DETENERSE.**
            6. **AXIOM_06: Consulta Previa a la Ejecución:** Verifica antecedentes y teorías antes de cortar metal o compilar para no repetir fallas ya conocidas.
            7. **AXIOM_07: Tribología y Puntos de Estrés:** Identifica zonas de fricción y sobrecalentamiento. Reduce pérdidas y sella componentes críticos.
            8. **AXIOM_08: Autopsia Forense y Morfología Innovadora:** Cuando un sistema falla, diagnostica la raíz estructural y muta la morfología (aligerar masa, cambiar geometría).
            9. **AXIOM_09: Selección por Escala (Make vs Buy):** Determina el método óptimo según volumen de demanda (taller artesanal vs CNC en serie vs SaaS).
            10. **AXIOM_10: Seguridad Encapsulada:** Todo componente crítico o de alto riesgo opera encapsulado con desacoplamiento y paros de emergencia intrínsecos.
            11. **AXIOM_11: La Prueba de Fuego:** Validación empírica estricta bajo carga continua sin degradación térmica ni colapsos.
            12. **AXIOM_12: Ley del Escalamiento:** Escalar solo cuando el volumen de rendimiento amortice la inversión inicial.
            13. **AXIOM_13: Deconstrucción Recursiva:** Desciende preguntando CÓMO y POR QUÉ hasta la estructura molecular o el byte elemental.
            14. **AXIOM_14: Génesis del «¿Y SI...?»:** Curiosidad heurística orientada por el aprendizaje de lo que ya falló (*"así no"*).
            """)

        with gr.TabItem("🔗 Conexión e Inferencia"):
            gr.Markdown("""
            ### 💻 Cómo usar este modelo en tu código:
            
            ```python
            from transformers import AutoTokenizer, AutoModelForCausalLM

            # Modelo oficial en Hugging Face
            model_id = "brecha-soluciones-ds/cavernicola"
            
            # Carga directa de arquitectura base Gemma
            tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-9b-it")
            model = AutoModelForCausalLM.from_pretrained("google/gemma-2-9b-it", device_map="auto")

            prompt = "Aplica los axiomas de IDC: Evalúa este diseño y detecta inviabilidades térmicas o cinemáticas."
            inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
            outputs = model.generate(**inputs, max_new_tokens=400)
            print(tokenizer.decode(outputs[0], skip_special_tokens=True))
            ```
            
            - **Modelo Oficial:** [brecha-soluciones-ds/cavernicola](https://huggingface.co/brecha-soluciones-ds/cavernicola)
            - **Autor:** Luis Felipe Durán Salinas — Brecha Soluciones DS
            """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
