import { TrashItem } from './types';

export class CausalTrash {
  private rejectedActions: Map<string, TrashItem> = new Map();

  record(failedAction: string, hypothesis: string, reason: string, severity: number, step: number): TrashItem {
    const norm = failedAction.toLowerCase().trim();
    const existing = this.rejectedActions.get(norm);

    if (existing) {
      existing.refusalCount += 1;
      existing.severity = Math.min(1.0, existing.severity + 0.1);
      existing.step = step;
      return existing;
    }

    const item: TrashItem = {
      id: `trash_${Math.random().toString(36).substring(2, 9)}`,
      failedAction: norm,
      hypothesis,
      reason,
      severity: Math.max(0.1, Math.min(1.0, severity)),
      step,
      refusalCount: 1,
    };

    this.rejectedActions.set(norm, item);
    return item;
  }

  isRejected(action: string): { rejected: boolean; item?: TrashItem } {
    const norm = action.toLowerCase().trim();
    // Direct O(1) lookup
    if (this.rejectedActions.has(norm)) {
      const item = this.rejectedActions.get(norm)!;
      return { rejected: true, item };
    }

    // Substring lookup for composite actions
    for (const [key, item] of this.rejectedActions.entries()) {
      if (norm.includes(key) || key.includes(norm)) {
        return { rejected: true, item };
      }
    }

    return { rejected: false };
  }

  registerVeto(action: string): void {
    const norm = action.toLowerCase().trim();
    const item = this.rejectedActions.get(norm);
    if (item) {
      item.refusalCount += 1;
    }
  }

  getAll(): TrashItem[] {
    return Array.from(this.rejectedActions.values()).sort((a, b) => b.severity - a.severity);
  }

  count(): number {
    return this.rejectedActions.size;
  }

  clear(): void {
    this.rejectedActions.clear();
  }
}
