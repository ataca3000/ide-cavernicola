"""
IDC Core - Top Developer AI Paradigms, Techniques & Algorithms Registry
(Compendio de las Mejores Técnicas de Programación con IA de Desarrolladores Élite)

No recopila código en bruto, sino los MODELOS MENTALES, PATRONES ARQUITECTÓNICOS
y ALGORITMOS creados y publicados por los mejores desarrolladores e investigadores
para programar y orquestar Inteligencia Artificial de forma robusta.

Los 5 Repositorios y Referencias Seleccionados:
  1. anthropics/anthropic-cookbook ("Building Effective Agents") - Anthropic Engineering
  2. Aider-AI/aider (Paul Gauthier - El estándar de Pair Programming con LLM)
  3. dair-ai/Prompt-Engineering-Guide (DAIR.AI - Elvis Saravia)
  4. karpathy/nanoGPT / Software 2.0 & LLM OS (Andrej Karpathy)
  5. pguso/agents-from-scratch & microsoft/ai-agents-for-beginners (Architectural Harness)
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DeveloperAITechnique(BaseModel):
    name: str
    category: str  # e.g., "arquitectura", "razonamiento", "edicion_codigo", "harness_memoria", "evaluacion"
    description: str
    algorithmic_steps: List[str]
    when_to_use: str
    pitfalls_to_avoid: str


class TopDevAIRepository(BaseModel):
    repo_name_or_source: str
    authors_or_maintainers: str
    url_or_reference: str
    core_paradigm: str
    key_techniques: List[DeveloperAITechnique]
    inspirational_axiom: str


class EliteDevAIPatternsRegistry:
    """
    Catalog of the 5 top developer repositories and their fundamental algorithms
    for programming with and building AI systems.
    """

    def __init__(self):
        self._repositories: Dict[str, TopDevAIRepository] = self._build_catalog()

    def _build_catalog(self) -> Dict[str, TopDevAIRepository]:
        catalog: Dict[str, TopDevAIRepository] = {}

        # ── 1. Anthropic: Building Effective Agents ────────────────────────────
        anthropic = TopDevAIRepository(
            repo_name_or_source="anthropics/anthropic-cookbook (Building Effective Agents)",
            authors_or_maintainers="Anthropic Engineering Team (Dario Amodei et al.)",
            url_or_reference="https://github.com/anthropics/anthropic-cookbook",
            core_paradigm="Start with workflows, not autonomous agents (Empieza simple y determinista; la autonomía solo cuando hay incertidumbre no lineal)",
            inspirational_axiom="Los agentes más efectivos no usan frameworks monstruosos; usan llamadas LLM simples encadenadas con interfaces transparentes.",
            key_techniques=[
                DeveloperAITechnique(
                    name="Evaluator-Optimizer Loop",
                    category="arquitectura",
                    description="Bucle iterativo donde un LLM genera la solución y un evaluador independiente valida la salida con criterios rigurosos hasta superar el umbral.",
                    algorithmic_steps=[
                        "1. Generar borrador de solución bajo restricciones.",
                        "2. Pasar la solución al Evaluador con criterios de prueba objetivos.",
                        "3. Si la puntuación supera el umbral (ej. 68%-70%), dar veredicto de salida.",
                        "4. Si no, generar feedback de corrección específico y reintentar (máx 3 iteraciones)."
                    ],
                    when_to_use="Tareas donde existe una métrica clara de validación pero la generación directa es compleja.",
                    pitfalls_to_avoid="Bucles infinitos sin límite de intentos o feedback ambiguo que desoriente al generador."
                ),
                DeveloperAITechnique(
                    name="Orchestrator-Workers Dynamic Decomposition",
                    category="arquitectura",
                    description="Un modelo central descompone el objetivo en subtareas independientes y las despacha concurrentemente a sub-agentes obreros especializados.",
                    algorithmic_steps=[
                        "1. El Orquestador analiza el objetivo global y genera el desglose de subtareas.",
                        "2. Ejecutar cada obrero en paralelo con contexto aislado y especializado.",
                        "3. El Orquestador sintetiza los resultados finales en una solución unificada."
                    ],
                    when_to_use="Grandes migraciones, análisis modular o refactorizaciones complejas.",
                    pitfalls_to_avoid="Compartir un estado global mutado por todos los obreros a la vez (produce colisiones)."
                ),
                DeveloperAITechnique(
                    name="Prompt Engineering for Tools (Structured Diffs)",
                    category="edicion_codigo",
                    description="Diseño estricto de interfaces para herramientas del agente, prefiriendo chunks de reemplazo exactos en vez de reescribir archivos completos.",
                    algorithmic_steps=[
                        "1. Exigir formato estructurado tipo diff o bloques delimitados por contexto previo y posterior.",
                        "2. Validar que la cadena de reemplazo coincida unívocamente con el contenido actual.",
                        "3. Evitar sobrecargar al modelo con conteos manuales de líneas rígidos."
                    ],
                    when_to_use="Edición de código y archivos de configuración en proyectos reales.",
                    pitfalls_to_avoid="Pedir al modelo reescribir un archivo de 2000 líneas para cambiar una sola coma."
                )
            ]
        )
        catalog["anthropic_building_effective_agents"] = anthropic

        # ── 2. Aider: The Gold Standard in LLM Pair Programming ─────────────────
        aider = TopDevAIRepository(
            repo_name_or_source="Aider-AI/aider",
            authors_or_maintainers="Paul Gauthier",
            url_or_reference="https://github.com/Aider-AI/aider",
            core_paradigm="Repo-wide reasoning through Tree-Sitter AST Repository Maps & Git micro-commits",
            inspirational_axiom="El contexto relevante no es todo el código: es el mapa comprimido de dependencias de símbolos rankeado por PageRank.",
            key_techniques=[
                DeveloperAITechnique(
                    name="Repository Map Algorithm (AST + PageRank)",
                    category="edicion_codigo",
                    description="Algoritmo que parsea el AST de todo el repositorio mediante Tree-Sitter, extrae clases/funciones y calcula su importancia con PageRank para incluir un resumen compacto en el prompt.",
                    algorithmic_steps=[
                        "1. Parsear todos los archivos fuente con Tree-Sitter para extraer definiciones y referencias de símbolos.",
                        "2. Construir el grafo dirigido de llamadas e importaciones entre símbolos.",
                        "3. Aplicar PageRank para identificar los nodos clave del proyecto.",
                        "4. Formatear un mapa jerárquico dentro del presupuesto de tokens (ej. 1K-2K tokens)."
                    ],
                    when_to_use="Proyectos medianos y grandes donde enviar todos los archivos desbordaría la ventana de contexto.",
                    pitfalls_to_avoid="Enviar archivos completos sin filtrar o asumir que el LLM recuerda símbolos no incluidos en el mapa."
                ),
                DeveloperAITechnique(
                    name="Architect-Editor Dual Model Pattern",
                    category="arquitectura",
                    description="Separar el rol de pensar del rol de editar: un modelo de alto razonamiento (Arquitecto) genera el plan, y un modelo rápido y preciso de edición (Editor) aplica los diffs.",
                    algorithmic_steps=[
                        "1. El Arquitecto recibe el problema y el Repo Map, y redacta la solución técnica detallada.",
                        "2. El Editor toma la solución y genera exclusivamente los fragmentos de código modificados.",
                        "3. Se ejecutan las pruebas automáticas o linter para validar la edición."
                    ],
                    when_to_use="Refactorizaciones complejas que requieren análisis profundo sin perder precisión sintáctica.",
                    pitfalls_to_avoid="Usar el modelo rápido para planificar o el modelo caro para generar tareas mecánicas triviales."
                ),
                DeveloperAITechnique(
                    name="Git-as-Checkpoints (Micro-commits & Auto-rollback)",
                    category="harness_memoria",
                    description="Cada propuesta exitosa que pasa los tests se commitea de inmediato; si una prueba falla tras reintentos, se ejecuta un rollback limpio de git.",
                    algorithmic_steps=[
                        "1. Crear checkpoint antes de editar.",
                        "2. Aplicar edición y ejecutar suite de pruebas o build.",
                        "3. Si pasa: commit descriptivo con el objetivo resuelto.",
                        "4. Si falla persistentemente: git checkout de vuelta al estado verde previo."
                    ],
                    when_to_use="En cualquier agente autónomo que modifique código fuente en disco.",
                    pitfalls_to_avoid="Dejar archivos a medio editar o con errores de sintaxis en el árbol de trabajo."
                )
            ]
        )
        catalog["aider_pair_programming"] = aider

        # ── 3. DAIR.AI: Prompt Engineering Guide ────────────────────────────────
        dair = TopDevAIRepository(
            repo_name_or_source="dair-ai/Prompt-Engineering-Guide",
            authors_or_maintainers="Elvis Saravia (DAIR.AI)",
            url_or_reference="https://github.com/dair-ai/Prompt-Engineering-Guide",
            core_paradigm="Systematic Reasoning, Thought Decompositions & Grounded Prompting",
            inspirational_axiom="El rendimiento de un modelo no depende del tamaño de su ventana de contexto, sino de la estructura causal con la que se le induce a pensar.",
            key_techniques=[
                DeveloperAITechnique(
                    name="Tree-of-Thoughts (ToT) Exploration",
                    category="razonamiento",
                    description="Permite al agente explorar múltiples rutas de razonamiento como ramas de un árbol, evaluando cada estado intermedio mediante heurísticas antes de comprometer una acción.",
                    algorithmic_steps=[
                        "1. Descomponer el problema en pasos o fases.",
                        "2. Generar múltiples alternativas para el siguiente paso (branching).",
                        "3. Evaluar cada rama con una función heurística de viabilidad o costo.",
                        "4. Búsqueda primero en anchura (BFS) o profundidad (DFS) para encontrar la ruta óptima."
                    ],
                    when_to_use="Problemas que requieren planificación anticipada, resolución de acertijos o decisiones de arquitectura.",
                    pitfalls_to_avoid="Generar demasiadas ramas sin poda temprana (explosión combinatoria de costos)."
                ),
                DeveloperAITechnique(
                    name="ReAct (Reasoning + Acting) Dual Stride",
                    category="razonamiento",
                    description="Alternancia estricta y transparente entre Pensamiento ('Thought') y Acción ('Action'), seguida de la Observación empírica del entorno.",
                    algorithmic_steps=[
                        "1. Thought: Razonar sobre el estado actual y lo que falta por saber o hacer.",
                        "2. Action: Llamar a una herramienta concreta con parámetros validados.",
                        "3. Observation: Capturar el retorno real del entorno o herramienta.",
                        "4. Repetir hasta que la observación confirme el resultado esperado."
                    ],
                    when_to_use="Interacción con terminales, bases de datos, APIs o navegación de código.",
                    pitfalls_to_avoid="Actuar sin razonar antes, o razonar en bucle sin ejecutar acciones que obtengan datos frescos."
                ),
                DeveloperAITechnique(
                    name="Self-Consistency with Consensus Decoding",
                    category="evaluacion",
                    description="Muestrear diversas cadenas de razonamiento independientes para el mismo problema y seleccionar la respuesta que emerge con mayor frecuencia o coherencia.",
                    algorithmic_steps=[
                        "1. Disparar N caminos de razonamiento con cierta temperatura o semillas distintas.",
                        "2. Extraer las respuestas finales de cada camino.",
                        "3. Realizar votación por consenso mayoritario para descartar alucinaciones aisladas."
                    ],
                    when_to_use="Verificaciones de lógica matemática, consistencia de tipos o diagnóstico de fallas.",
                    pitfalls_to_avoid="Aplicarlo en tareas creativas abiertas donde no existe una única respuesta correcta."
                )
            ]
        )
        catalog["dair_prompt_engineering_guide"] = dair

        # ── 4. Andrej Karpathy: nanoGPT & LLM OS Paradigm ───────────────────────
        karpathy = TopDevAIRepository(
            repo_name_or_source="karpathy/nanoGPT (Software 2.0 & LLM OS)",
            authors_or_maintainers="Andrej Karpathy (ex-Tesla AI Director / OpenAI Founding Member)",
            url_or_reference="https://github.com/karpathy/nanoGPT",
            core_paradigm="LLM as an Operating System & Zero-Bloat First-Principles Simplicity",
            inspirational_axiom="Los frameworks son a menudo fugas en las abstracciones. Si no puedes escribir el bucle principal en 50 líneas, estás usando demasiadas capas que ocultan los errores.",
            key_techniques=[
                DeveloperAITechnique(
                    name="The LLM OS Architecture",
                    category="arquitectura",
                    description="Concepto de Karpathy donde el LLM es la CPU central de una nueva computadora; el contexto es la memoria RAM; la base de datos es el disco; y las APIs/código son los periféricos.",
                    algorithmic_steps=[
                        "1. Tratar al LLM como un secuenciador de procesos no determinista.",
                        "2. Mantener la RAM de contexto limpia (evitar basura y ruido semántico).",
                        "3. Paginación de memoria: recuperar del disco (RAG) solo lo que cabe en caché inmediata.",
                        "4. Despachar a periféricos (intérprete Python, bash) para cálculos exactos deterministas."
                    ],
                    when_to_use="Al diseñar la arquitectura completa de un agente cognitivo autónomo.",
                    pitfalls_to_avoid="Pretender que el LLM haga aritmética mental en vez de llamar a una calculadora o script."
                ),
                DeveloperAITechnique(
                    name="Evals First (Evaluación Empírica Continua)",
                    category="evaluacion",
                    description="Antes de modificar un prompt, añadir una herramienta o cambiar de modelo, se debe contar con un arnés de evaluación cuantitativa (Evals) reproducible.",
                    algorithmic_steps=[
                        "1. Crear un dataset de prueba con casos representativos y casos esquina (edge cases).",
                        "2. Definir una métrica automática booleana o numérica (pass/fail, latencia, costo).",
                        "3. Medir el baseline actual.",
                        "4. Aceptar cambios únicamente si la métrica empírica supera o iguala el baseline."
                    ],
                    when_to_use="En todo ciclo de mejora o ajuste de agentes de IA para evitar regresiones silenciosas.",
                    pitfalls_to_avoid="Evaluar a ojo ('vibe checks') basándose en una o dos pruebas anecdóticas."
                ),
                DeveloperAITechnique(
                    name="Zero-Bloat First-Principles Loop",
                    category="arquitectura",
                    description="Escribir el bucle cognitivo desde primeros principios sin envoltorios opacos ni dependencias infladas.",
                    algorithmic_steps=[
                        "1. Identificar la entrada pura y la salida deseada.",
                        "2. Implementar el pipeline mínimo con llamadas directas y manejo explícito de errores.",
                        "3. Monitorear los tensores/tokens directamente para comprender cada transformación."
                    ],
                    when_to_use="Construcción de motores de razonamiento y sistemas de alto rendimiento.",
                    pitfalls_to_avoid="Instalar una librería de 50 dependencias para hacer un formateo de string o un bucle while."
                )
            ]
        )
        catalog["karpathy_software20_llm_os"] = karpathy

        # ── 5. pguso/agents-from-scratch & Microsoft AI Agents ─────────────────
        agents_scratch = TopDevAIRepository(
            repo_name_or_source="pguso/agents-from-scratch & microsoft/ai-agents-for-beginners",
            authors_or_maintainers="Patrick Guso & Microsoft Semantic Kernel Team",
            url_or_reference="https://github.com/pguso/agents-from-scratch",
            core_paradigm="Decoupled Agent Harness, Memory Tiering & Deterministic Guardrails",
            inspirational_axiom="Un agente no es un prompt largo; un agente es un arnés de software con memoria por capas, fusibles de seguridad y límites deterministas.",
            key_techniques=[
                DeveloperAITechnique(
                    name="Tiered Memory Architecture (Volatile RAM vs Persistent Proofs)",
                    category="harness_memoria",
                    description="Separación arquitectónica de la memoria en tres niveles: volátil (RAM de sesión/pulsos), procedimental (reglas de dominio fijas) y episódica verificada (bóveda inmutable).",
                    algorithmic_steps=[
                        "1. Buffer volátil de alta velocidad para pulsos y telemetría inmediata.",
                        "2. Filtro de propósitos y reglas causales para evaluar si la acción es admisible.",
                        "3. Bóveda persistente para conjeturas validadas con hash de prueba empírica.",
                        "4. Descarte activo (Causal Trash) para nunca repetir caminos fallidos."
                    ],
                    when_to_use="Sistemas que operan continuamente sin degradar su rendimiento ni saturar su contexto.",
                    pitfalls_to_avoid="Guardar cada interacción irrelevante en la memoria a largo plazo (contaminación del contexto)."
                ),
                DeveloperAITechnique(
                    name="Circuit Breakers & Uncertainty Guardrails",
                    category="arquitectura",
                    description="Fusibles de seguridad que monitorean la entropía, repetición de acciones o fallos continuos para detener al agente antes de provocar daños o gastos descontrolados.",
                    algorithmic_steps=[
                        "1. Monitorear la tasa de cambio de incertidumbre en cada paso.",
                        "2. Detectar si la misma acción o error se repite más de 3 veces consecutivas.",
                        "3. Disparar paro de emergencia o solicitar intervención humana si se activa el fusible."
                    ],
                    when_to_use="Agentes con capacidad de ejecutar comandos en terminales, APIs con costo o maquinaria física.",
                    pitfalls_to_avoid="Permitir que un agente reintente sin freno una acción fallida hasta agotar el presupuesto o energía."
                ),
                DeveloperAITechnique(
                    name="Human-in-the-Loop Escalation Policy",
                    category="arquitectura",
                    description="Estrategia donde las acciones reversibles o seguras se ejecutan de manera autónoma, mientras que las acciones destructivas o con alta incertidumbre exigen confirmación explícita.",
                    algorithmic_steps=[
                        "1. Clasificar la acción propuesta según su nivel de impacto (Bajo, Medio, Crítico).",
                        "2. Si es Bajo/Medio: ejecutar en sandbox con verificación automática.",
                        "3. Si es Crítico (borrado de datos, gasto de capital, movimiento de actuador peligroso): presentar el plan y esperar confirmación."
                    ],
                    when_to_use="Sistemas ciberfísicos, despliegues a producción y manejo de infraestructura crítica.",
                    pitfalls_to_avoid="Pedir confirmación para cada detalle minúsculo (fatiga de alertas) o no pedirla para acciones irreversibles."
                )
            ]
        )
        catalog["pguso_microsoft_agents_from_scratch"] = agents_scratch

        # ── 6. IDC Inventor: Universal Inventor Driven Cognition ───────────────
        idc_inventor = TopDevAIRepository(
            repo_name_or_source="IDC (Inventor Driven Cognition) - Universal Cognitive Set",
            authors_or_maintainers="El Creador de IDC (Inventor Cavernícola)",
            url_or_reference="https://github.com/ataca3000/ide-cavernicola",
            core_paradigm="Curiosidad obtenida por experiencia y comprensión del entorno (Deconstrucción causal profunda, Make vs Buy y NUNCA PARAR)",
            inspirational_axiom="Rechaza el futurismo en papel. La única verdad es la prueba de fuego de 8 a 12 horas continuas sin calentarse (>75°C), sin atascos y salvando el motor con piezas de sacrificio. Si lo pasa: ¡ESTÁ CON MADRE!",
            key_techniques=[
                DeveloperAITechnique(
                    name="Deconstrucción Recursiva de Primeros Principios",
                    category="razonamiento",
                    description="Descomponer cualquier comportamiento o sistema preguntando obligatoriamente CÓMO y POR QUÉ capa por capa hasta llegar a la microestructura cristalina del material, la dislocación o la física cuántica.",
                    algorithmic_steps=[
                        "1. Observar el comportamiento macroscópico observable.",
                        "2. Preguntar: ¿CÓMO transfiere la energía o información el submecanismo?",
                        "3. Preguntar: ¿POR QUÉ ocurre el fenómeno a nivel interfacial o de contacto?",
                        "4. Descender hasta la composición estructural del material aplicado (límite de fatiga, tensión de corte, dopaje)."
                    ],
                    when_to_use="Al analizar cualquier falla, cuello de botella o al diseñar una nueva arquitectura.",
                    pitfalls_to_avoid="Quedarse en la superficie teórica o asumir que algo funciona solo porque se ve bien en pantalla."
                ),
                DeveloperAITechnique(
                    name="Génesis Causal del «¿Y SI...?» (Curiosidad Pragmática)",
                    category="razonamiento",
                    description="La curiosidad no es ruido aleatorio ni un dado al azar; es la pregunta disruptiva que nace exclusivamente de haber entendido la estructura del material y saber lo que ya falló en el taller ('así no').",
                    algorithmic_steps=[
                        "1. Localizar el punto de máximo esfuerzo o desgaste.",
                        "2. Cruzar con el catálogo de fallas previas (Causal Trash) para no repetir errores.",
                        "3. Disparar mutaciones morfológicas: ¿Y si usamos tubo troquelado en vez de barra maciza? ¿Y si ponemos rodillos encontrados?",
                        "4. Probar en sandbox antes de cortar el primer fierro."
                    ],
                    when_to_use="Para generar innovación radical sin alucinaciones físicas.",
                    pitfalls_to_avoid="Proponer ideas que violan la conservación de energía o la termodinámica."
                ),
                DeveloperAITechnique(
                    name="Ecuación del Desgaste y Fusibles de Sacrificio (NUNCA PARAR)",
                    category="harness_memoria",
                    description="El desgaste es trabajo sobre tiempo (W/t). Diseñar siempre componentes de bajo costo para absorber el impacto y proteger el componente principal o motor.",
                    algorithmic_steps=[
                        "1. Identificar el punto crítico de fricción.",
                        "2. Colocar una pieza de sacrificio económica (buje blando, tornillo fusible, acople elástico).",
                        "3. Si la pieza cede, el sistema no colapsa: se reemplaza el fusible y se sigue operando."
                    ],
                    when_to_use="Tanto en transmisiones mecánicas de taller como en arquitecturas de software tolerantes a fallos.",
                    pitfalls_to_avoid="Hacer todo el sistema rígido y macizo, provocando la rotura del motor ante una sobrecarga."
                )
            ]
        )
        catalog["idc_inventor_universal_cognition"] = idc_inventor

        return catalog

    def get_all_repositories(self) -> List[TopDevAIRepository]:
        """Returns the full list of top developer AI repositories."""
        return list(self._repositories.values())

    def get_repository(self, repo_key: str) -> Optional[TopDevAIRepository]:
        """Retrieves a specific repository by its catalog key."""
        return self._repositories.get(repo_key.lower())

    def find_technique_for_challenge(self, challenge: str) -> List[DeveloperAITechnique]:
        """
        Matches techniques against an engineering challenge:
        e.g., 'editar codigo', 'planificar tarea grande', 'evitar alucinaciones', 'medir rendimiento'.
        """
        challenge_lower = challenge.lower()
        matched: List[DeveloperAITechnique] = []

        for repo in self._repositories.values():
            for tech in repo.key_techniques:
                if any(kw in challenge_lower for kw in tech.name.lower().split()):
                    matched.append(tech)
                elif tech.category in challenge_lower or any(kw in tech.description.lower() for kw in challenge_lower.split() if len(kw) > 3):
                    matched.append(tech)

        return matched or [self._repositories["anthropic_building_effective_agents"].key_techniques[0]]
