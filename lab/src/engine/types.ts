export type EntityType =
  | 'caveman'
  | 'mammoth'
  | 'wolf'
  | 'fire'
  | 'food'
  | 'bones'
  | 'rock'
  | 'tree';

export interface Entity {
  id: string;
  x: number;
  y: number;
  type: EntityType;
  hp?: number;
  maxHp?: number;
  label?: string;
}

export type ActionType =
  | 'explore'
  | 'reach_fire'
  | 'approach_food'
  | 'flee_wolf'
  | 'attack_wolf'
  | 'rest'
  | 'curious_experiment';

export interface Memory {
  id: string;
  step: number;
  event: string;
  action: string;
  result: 'success' | 'failure';
  energyDelta: number;
  damageDelta: number;
  context?: string;
}

export interface CausalRule {
  id: string;
  cause: string;
  effect: string;
  confidence: number;
  successes: number;
  failures: number;
  lastUsedStep: number;
}

export interface TrashItem {
  id: string;
  failedAction: string;
  hypothesis: string;
  reason: string;
  severity: number; // 0.0 - 1.0
  step: number;
  refusalCount: number;
}

export type LogTag =
  | 'PERCEPTION'
  | 'MEMORIA'
  | 'CAUSAL'
  | 'TRASH_VETO'
  | 'SIMULATION'
  | 'ACTION'
  | 'LEARNING'
  | 'TRAUMA';

export interface ThoughtLog {
  id: string;
  step: number;
  tag: LogTag;
  message: string;
  highlight?: boolean;
}

export interface Goal {
  name: string;
  targetType?: EntityType;
}

export type AgentMode = 'EXPLORATION' | 'OPTIMIZATION' | 'SURVIVAL';

export interface AgentState {
  energy: number;
  maxEnergy: number;
  hp: number;
  maxHp: number;
  mode: AgentMode;
  currentGoal: Goal;
  totalSteps: number;
  curiosityIndex: number;
  lastAction: ActionType;
  avatar: 'caveman' | 'mammoth';
}

export interface FloatingText {
  id: string;
  x: number;
  y: number;
  text: string;
  color: string;
  createdAt: number;
}
