import { Memory } from './types';

export class MemoryStore {
  private memories: Memory[] = [];
  private eventIndex: Map<string, Memory[]> = new Map();
  private actionIndex: Map<string, Memory[]> = new Map();

  add(memory: Memory): void {
    this.memories.push(memory);

    // Index by event
    const eventList = this.eventIndex.get(memory.event) || [];
    eventList.push(memory);
    this.eventIndex.set(memory.event, eventList);

    // Index by action
    const actionList = this.actionIndex.get(memory.action) || [];
    actionList.push(memory);
    this.actionIndex.set(memory.action, actionList);
  }

  find(event: string): Memory[] {
    return this.eventIndex.get(event) || [];
  }

  findByAction(action: string): Memory[] {
    return this.actionIndex.get(action) || [];
  }

  getFailures(event?: string): Memory[] {
    const list = event ? this.find(event) : this.memories;
    return list.filter((m) => m.result === 'failure');
  }

  getSuccesses(event?: string): Memory[] {
    const list = event ? this.find(event) : this.memories;
    return list.filter((m) => m.result === 'success');
  }

  getAll(): Memory[] {
    return [...this.memories];
  }

  count(): number {
    return this.memories.length;
  }

  clear(): void {
    this.memories = [];
    this.eventIndex.clear();
    this.actionIndex.clear();
  }
}
