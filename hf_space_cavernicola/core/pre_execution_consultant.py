"""
IDC Core - Pre-Execution Consultant (Consultor Previo Agnóstico Universal)
Transcribes the inventor's golden rule:
  - "La consulta SIEMPRE se hace ANTES de llevarlo a cabo"
  - "Te cercioras de tus teorías físicas como de materiales y aplicación para obtener el mejor resultado"
  - "Por otros que ya han hecho algo similar (en tu caso los repositorios)"

Agnostic architecture:
  - All input slots (theories, materials, prior art sources) are open and dynamic.
  - Can be registered dynamically by the agent for ANY domain (mechanics, biotech, software, robotics).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PriorArtReference(BaseModel):
    source_name_or_repo: str
    solution_approach: str
    known_failure_points: List[str] = Field(default_factory=list)  # Errores que otros ya cometieron
    proven_best_practices: List[str] = Field(default_factory=list)  # Lo que sí funciona en la realidad


class PreExecutionValidationResult(BaseModel):
    goal_or_task: str
    physical_theory_validated: bool
    materials_application_verified: bool
    prior_art_consulted: List[PriorArtReference]
    critical_adjustments_recommended: List[str]
    ready_to_build: bool
    status: str = "CONSULTA_PREVIA_COMPLETADA"


class PreExecutionConsultant:
    """
    Executes mandatory pre-flight consultation before any fabrication, build,
    or execution step is carried out.
    Agnostic to problem domain: open registry and dynamic slots.
    """

    def __init__(self):
        self.prior_art_registry: Dict[str, PriorArtReference] = {}
        self._load_elite_dev_patterns()

    def _load_elite_dev_patterns(self):
        """Loads the top 5 developer AI programming repositories into the prior art registry."""
        try:
            from core.elite_dev_ai_patterns import EliteDevAIPatternsRegistry
            registry = EliteDevAIPatternsRegistry()
            for key, repo in registry._repositories.items():
                self.prior_art_registry[key] = PriorArtReference(
                    source_name_or_repo=repo.repo_name_or_source,
                    solution_approach=f"Paradigma: {repo.core_paradigm}",
                    known_failure_points=[t.pitfalls_to_avoid for t in repo.key_techniques],
                    proven_best_practices=[f"{t.name}: {t.description}" for t in repo.key_techniques]
                )
        except Exception:
            pass

    def register_prior_art(self, category_key: str, reference: PriorArtReference):
        """Allows the agent to dynamically register prior art for any topic."""
        self.prior_art_registry[category_key.lower()] = reference

    def consult_before_execution(
        self,
        domain_or_goal: str,
        material_or_runtime_specs: Optional[Dict[str, Any]] = None,
        external_similar_repos: Optional[List[str]] = None,
        custom_prior_art: Optional[List[PriorArtReference]] = None
    ) -> PreExecutionValidationResult:
        """
        Ejecuta la consulta previa obligatoria con slots dinámicos:
        Cerciora la física, los materiales y extrae las lecciones de otros antes de fabricar o compilar.
        """
        specs = material_or_runtime_specs or {"power_adequate": True, "material_adequate": True}
        goal_lower = domain_or_goal.lower()

        prior_art_matches: List[PriorArtReference] = []
        adjustments: List[str] = []

        # 1. Consultar antecedentes personalizados inyectados por el agente
        if custom_prior_art:
            prior_art_matches.extend(custom_prior_art)

        # 2. Consultar si hay registros coincidentes en la base dinámica
        for key, ref in self.prior_art_registry.items():
            if key in goal_lower:
                prior_art_matches.append(ref)

        # 3. Consultar repositorios o referencias externas similares
        if external_similar_repos:
            for repo in external_similar_repos:
                prior_art_matches.append(
                    PriorArtReference(
                        source_name_or_repo=repo,
                        solution_approach=f"Patrón extraído de referencia previa: {repo}",
                        known_failure_points=["Fallas por desalineación de interfaces o toolchains incompatibles"],
                        proven_best_practices=["Compatibilidad modular por interfaces limpias y desacopladas"]
                    )
                )

        # Si aún no hay referencias, generar slot dinámico de consulta previa
        if not prior_art_matches:
            prior_art_matches.append(
                PriorArtReference(
                    source_name_or_repo=f"prior_art_search({domain_or_goal})",
                    solution_approach="Validación de antecedentes previa en repositorios similares",
                    known_failure_points=[
                        "Trabajo sin fusibles de protección o aislamiento térmico",
                        "Sobreesfuerzo por ignorar la resistencia real de los materiales"
                    ],
                    proven_best_practices=[
                        "Implementar desacople modular y partes de sacrificio",
                        "Verificar tolerancias de holgura antes del ensamblaje definitivo"
                    ]
                )
            )

        # Extraer puntos críticos detectados
        for ref in prior_art_matches:
            for fp in ref.known_failure_points:
                adjustments.append(f"Atención a falla previa en '{ref.source_name_or_repo}': {fp}")

        # 4. Cerciorarse de teorías físicas y de materiales (dinámico)
        physics_ok = specs.get("power_adequate", True)
        if not physics_ok:
            adjustments.append("Alerta física: Par motor o potencia insuficiente para la carga prevista.")

        materials_ok = specs.get("material_adequate", True)
        if not materials_ok:
            adjustments.append("Alerta material: Espesor, dureza o resistencia insuficiente para el régimen de trabajo.")

        ready = physics_ok and materials_ok

        return PreExecutionValidationResult(
            goal_or_task=domain_or_goal,
            physical_theory_validated=physics_ok,
            materials_application_verified=materials_ok,
            prior_art_consulted=prior_art_matches,
            critical_adjustments_recommended=adjustments,
            ready_to_build=ready,
            status="CONSULTA_PREVIA_VALIDADA_CON_EXITO" if ready else "AJUSTE_PREVIO_REQUERIDO"
        )
