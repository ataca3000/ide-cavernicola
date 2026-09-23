"""
IDC Core - Scrap & Manufacturing Selector (Cacería de Chatarra y Selección de Procesos)
Transcribes the inventor's procurement & manufacturing logic:
  - "Siempre voy a la chatarra pero antes ya definí cosas que pueden servirme:"
    (cardán, barra, dos chumaceras de pared o piso, transmisión de coche, motor mínimo 1 HP)
  - "Validar su estabilidad, funcionamiento y estado actual"
  - "Siempre se sabe que es mejor nuevo, pero nunca descartando CNC, 3D, torneado, doblado o corte plasma"
  - "Y qué tantas piezas quieres (tamaño de lote y escala)"
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProcessType(str, Enum):
    SCRAP_RECLAIMED = "SCRAP_RECLAIMED"          # Chatarra/desguace validado in situ
    PLASMA_AND_BENDING = "PLASMA_AND_BENDING"    # Corte plasma + doblado de chapa/perfil
    CONVENTIONAL_LATHE = "CONVENTIONAL_LATHE"    # Torneado tradicional de ejes y bujes
    CNC_MACHINING = "CNC_MACHINING"              # Maquinado CNC para precisión repetible
    ADDITIVE_3D = "ADDITIVE_3D"                  # Impresión 3D para prototipo rápido


class ScrapValidationTest(BaseModel):
    item_category: str
    target_example: str
    inspection_checks: List[str]
    pass_criteria: str


class ManufacturingRecommendation(BaseModel):
    component: str
    batch_quantity: int
    recommended_process: ProcessType
    rationale: str
    estimated_relative_cost: str
    feasibility_notes: str


class ScrapAndManufacturingSelector:
    """
    Selects between targeted scrap hunting and advanced manufacturing
    (CNC, 3D printing, lathe turning, tube bending, plasma cutting)
    driven by batch quantity and required stability.
    """

    def generate_targeted_scrap_checklist(
        self,
        requires_angular_coupling: bool = True,
        min_power_hp: float = 1.0
    ) -> List[ScrapValidationTest]:
        """
        Genera la lista de cosas predefinidas antes de ir al desguace:
        Cardán, barra, chumaceras de piso/pared, transmisión y motor >= 1 HP.
        """
        checklist = [
            ScrapValidationTest(
                item_category="motor_electrico",
                target_example=f"Motor industrial o de lavadora/bomba de mínimo {min_power_hp} HP",
                inspection_checks=[
                    "Sin olor a bobinado recalentado o barniz tostado",
                    "Giro libre del eje con la mano sin rozamiento metálico",
                    "Continuidad de devanados y aislamiento a tierra con multímetro"
                ],
                pass_criteria="Resistencia de aislamiento > 1 MΩ, giro suave sin juego radial perceptible"
            ),
            ScrapValidationTest(
                item_category="chumaceras_soportes",
                target_example="Dos chumaceras de piso o de pared (1 pulgada / 25 mm)",
                inspection_checks=[
                    "Balero gira silencioso sin saltos ni sensación arenosa",
                    "Cuerpo de fundición sin fisuras en las orejas de anclaje",
                    "Prisioneros de sujeción al eje no barridos"
                ],
                pass_criteria="Giro fluido, pista exterior sin juego axial mayor a 0.1 mm"
            ),
            ScrapValidationTest(
                item_category="eje_transmision",
                target_example="Barra de acero calibrado o transmisión de coche (diferencial / engranes)",
                inspection_checks=[
                    "Rodar la barra en una superficie plana para verificar rectitud visual",
                    "Dientes de engranes sin melladuras ni filo en punta",
                    "Estrías o cuñero intacto"
                ],
                pass_criteria="Rectitud con tolerancia < 0.5 mm, engranes sin desportilladuras"
            )
        ]

        if requires_angular_coupling:
            checklist.append(
                ScrapValidationTest(
                    item_category="acople_cardan",
                    target_example="Cruceta o cardán de dirección/transmisión de coche",
                    inspection_checks=[
                        "Cruceta sin holgura excesiva en las 4 agujas de vaso",
                        "Dados de engrase no obturados"
                    ],
                    pass_criteria="Flexión angular suave en ambos ejes sin cabeceo suelto"
                )
            )

        return checklist

    def select_process_by_quantity_and_geometry(
        self,
        part_name: str,
        quantity: int,
        geometry_type: str  # 'placas_tolva', 'eje_cilindrico', 'soporte_complejo', 'prototipo_plastico'
    ) -> ManufacturingRecommendation:
        """
        Decide el proceso considerando: '¿Y qué tantas piezas quieres?'
        1 pieza prototipo vs 10 semiserie vs 100+ producción repetible.
        """
        geom = geometry_type.lower()

        # Placas, tolvas, rampas y costados de chapa
        if any(w in geom for w in ["placa", "tolva", "rampa", "chapa", "costado"]):
            if quantity <= 2:
                proc = ProcessType.PLASMA_AND_BENDING
                rat = "Para 1-2 tolvas: corte por plasma CNC de placas y doblado en prensa o tornillo de banco."
                cost = "Bajo - rápido y sin herramental costoso"
            else:
                proc = ProcessType.PLASMA_AND_BENDING
                rat = f"Para {quantity} piezas: nido de corte plasma automatizado y matriz de doblado repetible."
                cost = "Medio - muy eficiente por economía de escala de chapa"

        # Ejes, flechas, tornillos roscados, bujes de ajuste
        elif any(w in geom for w in ["eje", "cilindro", "flecha", "buje", "torneado"]):
            if quantity <= 5:
                proc = ProcessType.CONVENTIONAL_LATHE
                rat = "Torneado convencional en taller: refrentado, cilindrado de asientos de balero y cuñero."
                cost = "Económico para piezas unitarias"
            else:
                proc = ProcessType.CNC_MACHINING
                rat = f"Para {quantity} ejes: torno CNC para tolerancias h6 idénticas en segundos por pieza."
                cost = "Alto setup inicial, pero costo marginal mínimo por unidad"

        # Piezas complejas, boquillas, guías o prototipado ágil
        elif any(w in geom for w in ["complejo", "plastico", "guia", "boquilla"]):
            if quantity <= 3:
                proc = ProcessType.ADDITIVE_3D
                rat = "Impresión 3D (PETG o Nylon con fibra): validación inmediata sin costos de mecanizado."
                cost = "Mínimo para prototipo"
            else:
                proc = ProcessType.CNC_MACHINING
                rat = f"Para lote de {quantity}: mecanizado CNC en aluminio o polímero técnico."
                cost = "Industrialmente óptimo para resistencia mecánica duradera"

        else:
            proc = ProcessType.SCRAP_RECLAIMED
            rat = "Recuperar de desguace/chatarra validada para prototipo único costo-efectivo."
            cost = "Costo de chatarra por kilo"

        return ManufacturingRecommendation(
            component=part_name,
            batch_quantity=quantity,
            recommended_process=proc,
            rationale=rat,
            estimated_relative_cost=cost,
            feasibility_notes="Siempre es mejor nuevo para serie, pero chatarra o plasma/torno resuelven el prototipo 1"
        )
