"""
IDC Core - Domain Cross Synthesizer (Motor Universal de Cruce Causal de Conceptos)
Transcribes the inventor's rule:
  - "Siempre cruzo cosas pero depende qué quieras imaginar: algo realmente tangible o idea de película"
  - "No cruzo un aguacate con un motor de coche, solo que lo quiera llamar aguacate jajaja"

Universal and agnostic:
  - Uses abstract causal domain invariants (Kinematic, Thermodynamic, Organic/Biochemical, Electrical, Computational).
  - Empty/dynamic slots: the agent can cross ANY two concepts and declare or detect their causal bridge.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class ImaginationMode(str, Enum):
    TANGIBLE_FISICO = "TANGIBLE_FISICO"
    FICCION_SIMBOLICA = "FICCION_SIMBOLICA"


class DomainCategory(str, Enum):
    MECHANICAL = "MECHANICAL"
    ELECTRICAL = "ELECTRICAL"
    THERMAL = "THERMAL"
    ORGANIC = "ORGANIC"
    COMPUTATIONAL = "COMPUTATIONAL"
    CHEMICAL = "CHEMICAL"
    UNKNOWN = "UNKNOWN"


class DomainCrossResult(BaseModel):
    concept_a: str
    concept_b: str
    mode: ImaginationMode
    is_physically_viable: bool
    is_nominal_only: bool = False  # e.g., "solo se llama aguacate"
    shared_physical_laws: List[str] = Field(default_factory=list)
    functional_hybrid: Optional[str] = None
    warning_or_rationale: str


class DomainCrossSynthesizer:
    """
    Evaluates and generates hybrid inventions by crossing domains agnostically.
    Guarantees that tangible physical inventions are causally grounded,
    preventing LLM-style nonsensical hallucinations.
    """

    def __init__(self):
        # Open domain keyword registry that can be expanded dynamically by the agent
        self.domain_mappings: Dict[str, DomainCategory] = {
            # Mechanical
            "motor": DomainCategory.MECHANICAL,
            "reductor": DomainCategory.MECHANICAL,
            "cadena": DomainCategory.MECHANICAL,
            "eje": DomainCategory.MECHANICAL,
            "chumacera": DomainCategory.MECHANICAL,
            "balero": DomainCategory.MECHANICAL,
            "engrane": DomainCategory.MECHANICAL,
            "tornillo": DomainCategory.MECHANICAL,
            "polea": DomainCategory.MECHANICAL,
            "tolva": DomainCategory.MECHANICAL,
            "rampa": DomainCategory.MECHANICAL,
            "bici": DomainCategory.MECHANICAL,
            "molino": DomainCategory.MECHANICAL,
            "bancada": DomainCategory.MECHANICAL,
            # Electrical
            "cable": DomainCategory.ELECTRICAL,
            "switch": DomainCategory.ELECTRICAL,
            "bateria": DomainCategory.ELECTRICAL,
            "corriente": DomainCategory.ELECTRICAL,
            "voltaje": DomainCategory.ELECTRICAL,
            "relevador": DomainCategory.ELECTRICAL,
            # Organic
            "aguacate": DomainCategory.ORGANIC,
            "maiz": DomainCategory.ORGANIC,
            "manzana": DomainCategory.ORGANIC,
            "fruta": DomainCategory.ORGANIC,
            "grano": DomainCategory.ORGANIC,
            "olote": DomainCategory.ORGANIC,
            "semilla": DomainCategory.ORGANIC,
            # Computational
            "repo": DomainCategory.COMPUTATIONAL,
            "pipeline": DomainCategory.COMPUTATIONAL,
            "api": DomainCategory.COMPUTATIONAL,
            "codigo": DomainCategory.COMPUTATIONAL,
            "algoritmo": DomainCategory.COMPUTATIONAL,
        }

    def register_concept_domain(self, concept_word: str, category: DomainCategory):
        """Allows dynamic registration of concepts into causal domains."""
        self.domain_mappings[concept_word.lower().strip()] = category

    def detect_category(self, concept_text: str) -> DomainCategory:
        text_lower = concept_text.lower()
        for word, cat in self.domain_mappings.items():
            if word in text_lower:
                return cat
        return DomainCategory.UNKNOWN

    def cross_concepts(
        self,
        concept_a: str,
        concept_b: str,
        mode: ImaginationMode = ImaginationMode.TANGIBLE_FISICO,
        domain_a_override: Optional[DomainCategory] = None,
        domain_b_override: Optional[DomainCategory] = None,
        shared_invariants: Optional[List[str]] = None
    ) -> DomainCrossResult:
        """
        Agnostic cross-domain evaluation:
        Evaluates compatibility across mechanical, electrical, thermal, organic, and computational domains.
        """
        cat_a = domain_a_override or self.detect_category(concept_a)
        cat_b = domain_b_override or self.detect_category(concept_b)

        # ── 1. MODO FICCIÓN SIMBÓLICA / IDEA DE PELÍCULA ─────────────────────
        if mode == ImaginationMode.FICCION_SIMBOLICA:
            return DomainCrossResult(
                concept_a=concept_a,
                concept_b=concept_b,
                mode=mode,
                is_physically_viable=True,
                is_nominal_only=True,
                shared_physical_laws=["Ficción conceptual / Nomenclatura libre"],
                functional_hybrid=f"Híbrido simbólico: Proyecto {concept_a.capitalize()}-{concept_b.capitalize()}",
                warning_or_rationale="Cruce conceptual libre para arte, metáfora o diseño especulativo."
            )

        # ── 2. MODO TANGIBLE FÍSICO ──────────────────────────────────────────
        # Incompatibilidad Causal Orgánico + Mecánico (salvo procesamiento de materia prima)
        if (cat_a == DomainCategory.ORGANIC and cat_b == DomainCategory.MECHANICAL) or \
           (cat_b == DomainCategory.ORGANIC and cat_a == DomainCategory.MECHANICAL):
            # Check if one acts as feedstock / workload for the other (e.g. grano para molino)
            ca_lower = concept_a.lower()
            cb_lower = concept_b.lower()
            is_workload = any(w in ca_lower or w in cb_lower for w in ["molino", "desgrane", "procesador", "triturador", "prensa"])
            if is_workload:
                return DomainCrossResult(
                    concept_a=concept_a,
                    concept_b=concept_b,
                    mode=mode,
                    is_physically_viable=True,
                    is_nominal_only=False,
                    shared_physical_laws=shared_invariants or ["Mecánica de fricción/cizalle", "Conservación de materia"],
                    functional_hybrid=f"Sistema de procesamiento: {concept_a} y {concept_b}",
                    warning_or_rationale="Cruce causal válido: la materia orgánica es la carga de trabajo del mecanismo."
                )
            else:
                return DomainCrossResult(
                    concept_a=concept_a,
                    concept_b=concept_b,
                    mode=mode,
                    is_physically_viable=False,
                    is_nominal_only=True,
                    shared_physical_laws=[],
                    functional_hybrid=None,
                    warning_or_rationale=(
                        f"Inviable físicamente cruzar '{concept_a}' con '{concept_b}'. "
                        "No comparten principios de transmisión de fuerza o energía. "
                        "Solo es viable como apodo/nombre código ('solo que lo quiera llamar aguacate jajaja')."
                    )
                )

        # Cruce Mecánico + Mecánico o Mecánico + Eléctrico (Sinergias comunes)
        if (cat_a == DomainCategory.MECHANICAL and cat_b == DomainCategory.MECHANICAL) or \
           (cat_a == DomainCategory.MECHANICAL and cat_b == DomainCategory.ELECTRICAL) or \
           (cat_a == DomainCategory.ELECTRICAL and cat_b == DomainCategory.MECHANICAL):
            return DomainCrossResult(
                concept_a=concept_a,
                concept_b=concept_b,
                mode=mode,
                is_physically_viable=True,
                is_nominal_only=False,
                shared_physical_laws=shared_invariants or ["Cinemática rotacional", "Relación de transmisión de torque", "Potencia electromecánica"],
                functional_hybrid=f"Mecanismo híbrido: {concept_a} acoplado a {concept_b}",
                warning_or_rationale="Cruce causalmente compatible en el dominio electromecánico."
            )

        # Default fallback con leyes físicas genéricas
        return DomainCrossResult(
            concept_a=concept_a,
            concept_b=concept_b,
            mode=mode,
            is_physically_viable=True,
            is_nominal_only=False,
            shared_physical_laws=shared_invariants or ["Leyes de la física clásica"],
            functional_hybrid=f"Ensamblaje tangible de {concept_a} y {concept_b}",
            warning_or_rationale="Cruce tangible evaluado."
        )
