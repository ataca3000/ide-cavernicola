export interface ExperimentHypothesis {
  action: string;
  rationale: string;
  novelty: number;
}

export class CuriosityEngine {
  private askedQuestions: Set<string> = new Set();
  private totalInquiries: number = 0;

  suggestHypothesis(
    subject: string,
    environmentContext: string,
    failedActions: string[]
  ): ExperimentHypothesis {
    this.totalInquiries += 1;
    const cleanSubject = subject.toLowerCase();

    const candidateTemplates = [
      {
        action: `flank_and_circle_${cleanSubject}`,
        rationale: `Probar aproximación lateral para evaluar campo visual y ángulo ciego`,
        novelty: 0.85,
      },
      {
        action: `use_torch_against_${cleanSubject}`,
        rationale: `Comprobar hipótesis: fuego y antorchas intimidan a los depredadores`,
        novelty: 0.92,
      },
      {
        action: `lure_${cleanSubject}_into_bones_obstacle`,
        rationale: `Usar el terreno rocoso y restos óseos como trampa de desaceleración`,
        novelty: 0.78,
      },
      {
        action: `retreat_to_fire_sanctuary`,
        rationale: `Mantener posición defensiva cerca del calor para optimizar energía`,
        novelty: 0.65,
      },
      {
        action: `scout_foraging_perimeter`,
        rationale: `Inspeccionar terreno adyacente para localizar bayas y fuentes calóricas`,
        novelty: 0.7,
      },
    ];

    // Filter out actions already vetoed by Causal Trash
    const normalizedFails = failedActions.map((f) => f.toLowerCase());
    const viable = candidateTemplates.filter(
      (c) => !normalizedFails.some((fail) => c.action.includes(fail) || fail.includes(c.action))
    );

    const chosen = viable.length > 0 ? viable[Math.floor(Math.random() * viable.length)] : candidateTemplates[0];

    const question = `¿Qué ocurre al aplicar ${chosen.action} frente a ${cleanSubject} en ${environmentContext}?`;
    this.askedQuestions.add(question);

    return chosen;
  }

  getCuriosityIndex(): number {
    if (this.totalInquiries === 0) return 1.0;
    return Math.min(1.0, parseFloat((this.askedQuestions.size / Math.max(this.totalInquiries, 1)).toFixed(2)));
  }

  getQuestionsCount(): number {
    return this.askedQuestions.size;
  }

  clear(): void {
    this.askedQuestions.clear();
    this.totalInquiries = 0;
  }
}
