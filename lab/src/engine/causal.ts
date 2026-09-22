import { CausalRule } from './types';

export class CausalEngine {
  private rules: Map<string, CausalRule> = new Map();

  private makeKey(cause: string, effect: string): string {
    return `${cause}->${effect}`;
  }

  learn(cause: string, effect: string, isSuccess: boolean, currentStep: number): CausalRule {
    const key = this.makeKey(cause, effect);
    const existing = this.rules.get(key);

    if (existing) {
      if (isSuccess) {
        existing.successes += 1;
        // Bayesian progressive reinforcement towards 0.99
        existing.confidence = Math.min(
          0.99,
          existing.confidence + 0.15 * (1.0 - existing.confidence)
        );
      } else {
        existing.failures += 1;
        // Faster penalization on failures
        existing.confidence = Math.max(
          0.05,
          existing.confidence - 0.25 * existing.confidence
        );
      }
      existing.lastUsedStep = currentStep;
      return existing;
    }

    const newRule: CausalRule = {
      id: `rule_${Math.random().toString(36).substring(2, 9)}`,
      cause,
      effect,
      confidence: isSuccess ? 0.65 : 0.25,
      successes: isSuccess ? 1 : 0,
      failures: isSuccess ? 0 : 1,
      lastUsedStep: currentStep,
    };

    this.rules.set(key, newRule);
    return newRule;
  }

  infer(cause: string): CausalRule[] {
    const matched: CausalRule[] = [];
    for (const rule of this.rules.values()) {
      if (rule.cause === cause || cause.includes(rule.cause) || rule.cause.includes(cause)) {
        matched.push(rule);
      }
    }
    return matched.sort((a, b) => b.confidence - a.confidence);
  }

  getBestEffect(cause: string): { effect: string; confidence: number } | null {
    const matched = this.infer(cause);
    if (matched.length > 0 && matched[0].confidence >= 0.4) {
      return { effect: matched[0].effect, confidence: matched[0].confidence };
    }
    return null;
  }

  getAllRules(): CausalRule[] {
    return Array.from(this.rules.values()).sort((a, b) => b.confidence - a.confidence);
  }

  clear(): void {
    this.rules.clear();
  }
}
