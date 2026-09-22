import { MemoryStore } from './memory';
import { CausalEngine } from './causal';
import { CausalTrash } from './trash';
import { CuriosityEngine } from './curiosity';
import { World, manhattanDistance } from './world';
import { AgentMode, AgentState, Entity, FloatingText, Goal, ThoughtLog } from './types';

export class CavemanAgent {
  energy: number = 100;
  maxEnergy: number = 100;
  hp: number = 100;
  maxHp: number = 100;
  avatar: 'caveman' | 'mammoth' = 'caveman';

  goal: Goal = {
    name: 'Sobrevivir y Explorar',
    targetType: undefined,
  };

  stepCount: number = 0;
  mode: AgentMode = 'EXPLORATION';

  memories: MemoryStore = new MemoryStore();
  causal: CausalEngine = new CausalEngine();
  trash: CausalTrash = new CausalTrash();
  curiosity: CuriosityEngine = new CuriosityEngine();

  logs: ThoughtLog[] = [];
  floatingTexts: FloatingText[] = [];

  constructor() {
    this.addLog('PERCEPTION', 'Sistema cognitivo IDC inicializado. Identidad activa: "Reality First".');
  }

  addLog(tag: ThoughtLog['tag'], message: string, highlight?: boolean): void {
    const log: ThoughtLog = {
      id: `log_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      step: this.stepCount,
      tag,
      message,
      highlight,
    };
    this.logs.unshift(log);
    // Keep max 150 logs in memory
    if (this.logs.length > 150) {
      this.logs.pop();
    }
  }

  addFloatingText(x: number, y: number, text: string, color: string): void {
    this.floatingTexts.push({
      id: `ft_${Date.now()}_${Math.random()}`,
      x,
      y,
      text,
      color,
      createdAt: Date.now(),
    });
  }

  setGoal(name: string): void {
    let targetType: Goal['targetType'] = undefined;
    const lower = name.toLowerCase();
    if (lower.includes('fuego') || lower.includes('fire')) targetType = 'fire';
    else if (lower.includes('lobo') || lower.includes('wolf')) targetType = 'wolf';
    else if (lower.includes('comida') || lower.includes('food') || lower.includes('carne')) targetType = 'food';

    this.goal = { name, targetType };
    this.addLog('PERCEPTION', `Nuevo objetivo fijado por el usuario: "${name}"`, true);
  }

  getState(): AgentState {
    return {
      energy: Math.max(0, Math.round(this.energy)),
      maxEnergy: this.maxEnergy,
      hp: Math.max(0, Math.round(this.hp)),
      maxHp: this.maxHp,
      mode: this.mode,
      currentGoal: this.goal,
      totalSteps: this.stepCount,
      curiosityIndex: this.curiosity.getCuriosityIndex(),
      lastAction: 'explore',
      avatar: this.avatar,
    };
  }

  // Core IDC Decision & Cognitive Step
  step(world: World): void {
    this.stepCount += 1;
    world.stepEnvironment();

    // Clean old floating texts (older than 2.5s)
    const now = Date.now();
    this.floatingTexts = this.floatingTexts.filter((ft) => now - ft.createdAt < 2500);

    // 1. Update Metabolic Mode based on Energy & HP
    if (this.energy <= 20 || this.hp <= 30) {
      this.mode = 'SURVIVAL';
    } else if (this.energy <= 60) {
      this.mode = 'OPTIMIZATION';
    } else {
      this.mode = 'EXPLORATION';
    }

    const agentEntity = world.getAgent();
    world.updateVision(agentEntity.x, agentEntity.y, 4);

    // 2. Scan surroundings
    const visibleEntities = world.entities.filter(
      (e) => e.id !== 'agent_player' && manhattanDistance(agentEntity, e) <= 4
    );

    const wolvesNearby = visibleEntities.filter((e) => e.type === 'wolf');
    const closestWolf = wolvesNearby.sort(
      (a, b) => manhattanDistance(agentEntity, a) - manhattanDistance(agentEntity, b)
    )[0];

    const fireEntity = world.entities.find((e) => e.type === 'fire');
    const foodsNearby = visibleEntities.filter((e) => e.type === 'food');

    // Energy baseline decay per step (colder at night)
    const coldCost = world.dayCycle === 'night' ? 1.8 : 0.9;
    this.energy = Math.max(0, this.energy - coldCost);

    // 3. Cognitive Evaluation Loop
    if (closestWolf && manhattanDistance(agentEntity, closestWolf) <= 3) {
      this.handleWolfEncounter(agentEntity, closestWolf, fireEntity, world);
      return;
    }

    // Low Energy / Health -> Prioritize Fire Sanctuary or Food
    if (this.mode === 'SURVIVAL' || this.energy < 40 || (fireEntity && manhattanDistance(agentEntity, fireEntity) === 0)) {
      if (fireEntity && manhattanDistance(agentEntity, fireEntity) === 0) {
        // Resting by fire
        this.energy = Math.min(this.maxEnergy, this.energy + 15);
        this.hp = Math.min(this.maxHp, this.hp + 10);
        this.addFloatingText(agentEntity.x, agentEntity.y, '+15 NRG +10 HP', '#10b981');
        this.addLog(
          'ACTION',
          `Descansando junto a la hoguera sagrada. Calor restaurador aplicado (+15 Energía, +10 Salud).`
        );
        return;
      }

      if (foodsNearby.length > 0) {
        const closestFood = foodsNearby[0];
        this.moveTowards(agentEntity, closestFood.x, closestFood.y, world);
        if (manhattanDistance(agentEntity, closestFood) === 0) {
          // Eat food
          this.energy = Math.min(this.maxEnergy, this.energy + 35);
          this.addFloatingText(agentEntity.x, agentEntity.y, '+35 Nutrición', '#10b981');
          world.removeEntity(closestFood.id);
          this.memories.add({
            id: `mem_${Date.now()}`,
            step: this.stepCount,
            event: 'food_consumption',
            action: 'consume_berries',
            result: 'success',
            energyDelta: 35,
            damageDelta: 0,
          });
          this.causal.learn('consume_berries', 'energy_restored', true, this.stepCount);
          this.addLog('LEARNING', `Alimento ingerido. Regla causal reforzada: "consume_berries -> energy_restored".`);
        }
        return;
      }

      if (fireEntity) {
        this.addLog('SIMULATION', `Nivel metabólico en ${this.mode}. Proyectando ruta hacia la hoguera de calor.`);
        this.moveTowards(agentEntity, fireEntity.x, fireEntity.y, world);
        return;
      }
    }

    // 4. Default: Exploratory Behavior guided by Curiosity Engine
    this.handleExploration(agentEntity, world);
  }

  private handleWolfEncounter(
    agentEntity: Entity,
    wolf: Entity,
    fireEntity: Entity | undefined,
    world: World
  ): void {
    const dist = manhattanDistance(agentEntity, wolf);
    this.addLog(
      'PERCEPTION',
      `¡Depredador detectado! Lobo a distancia ${dist} en (${wolf.x}, ${wolf.y}). Nivel de amenaza alto.`
    );

    // ── Check Causal Trash ───────────────────────────────────────────────────
    const attackCheck = this.trash.isRejected('attack_wolf');

    if (attackCheck.rejected) {
      // VETO TRIGGERED!
      this.trash.registerVeto('attack_wolf');
      this.addLog(
        'TRASH_VETO',
        `[VETO CAUSAL O(1)] Hipótesis "attack_wolf" BLOQUEADA por trauma previo (Severidad: ${attackCheck.item?.severity.toFixed(2)}). Motivo: "${attackCheck.item?.reason}".`,
        true
      );

      // Query Causal Engine for best escape strategy
      const escapeRule = this.causal.getBestEffect('wolf_detected');
      if (escapeRule && escapeRule.confidence >= 0.5) {
        this.addLog(
          'CAUSAL',
          `Regla causal activada: "wolf_detected -> ${escapeRule.effect}" (Confianza: ${(escapeRule.confidence * 100).toFixed(0)}%). Decisión: HUIR.`
        );
      } else {
        this.addLog('SIMULATION', `Sin regla previa garantizada. Ejecutando evasión táctica alejándose del lobo.`);
      }

      // Flee away from wolf (towards fire if available)
      if (fireEntity) {
        this.moveTowards(agentEntity, fireEntity.x, fireEntity.y, world);
      } else {
        this.moveAwayFrom(agentEntity, wolf.x, wolf.y, world);
      }

      // Record successful escape
      this.memories.add({
        id: `mem_${Date.now()}`,
        step: this.stepCount,
        event: 'wolf_encounter',
        action: 'flee_wolf',
        result: 'success',
        energyDelta: -3,
        damageDelta: 0,
      });

      this.causal.learn('wolf_detected', 'escape_improves_survival', true, this.stepCount);
      this.addFloatingText(agentEntity.x, agentEntity.y, '¡Evasión Causal!', '#38bdf8');
      return;
    }

    // ── If not in Causal Trash yet: Agent naively tries to attack ────────────
    this.addLog(
      'SIMULATION',
      `Primera experiencia con depredador. Sin registros traumáticos en Causal Trash. Evaluando combate cuerpo a cuerpo.`
    );
    this.addLog('ACTION', `El cavernícola arremete contra el lobo con sus propias manos ("attack_wolf")...`);

    // Catastrophic Combat Outcome:
    const damage = 35;
    this.hp = Math.max(5, this.hp - damage);
    this.energy = Math.max(5, this.energy - 20);

    this.addFloatingText(agentEntity.x, agentEntity.y, `-${damage} HP`, '#ef4444');
    this.addFloatingText(wolf.x, wolf.y, `Contraataque`, '#f59e0b');

    // ── Record Trauma & Populate Causal Trash ────────────────────────────────
    const trauma = this.trash.record(
      'attack_wolf',
      'Atacar al lobo con las manos desnudas',
      `Trauma físico severo: mordeduras profundas y pérdida crítica de ${damage} HP`,
      0.95,
      this.stepCount
    );

    this.memories.add({
      id: `mem_${Date.now()}`,
      step: this.stepCount,
      event: 'wolf_encounter',
      action: 'attack_wolf',
      result: 'failure',
      energyDelta: -20,
      damageDelta: -damage,
    });

    this.causal.learn('wolf_detected', 'attack_wolf_causes_trauma', false, this.stepCount);

    this.addLog(
      'TRAUMA',
      `¡COLAPSO DE COMBATE! Daño severo (-${damage} HP). Cicatriz grabada en Causal Trash: id="${trauma.id}" (Severidad: 0.95).`,
      true
    );

    // Retreat 1 cell immediately after trauma
    this.moveAwayFrom(agentEntity, wolf.x, wolf.y, world);
  }

  private handleExploration(agentEntity: Entity, world: World): void {
    const trashItems = this.trash.getAll().map((t) => t.failedAction);
    const hypothesis = this.curiosity.suggestHypothesis(
      'terreno_artico',
      world.dayCycle,
      trashItems
    );

    this.addLog(
      'SIMULATION',
      `Curiosidad Tipo 4 activa (Índice IC: ${this.curiosity.getCuriosityIndex()}): Hipótesis -> "${hypothesis.rationale}".`
    );

    // Move randomly or towards undiscovered fog tiles
    const moves = [
      { x: 1, y: 0 }, { x: -1, y: 0 }, { x: 0, y: 1 }, { x: 0, y: -1 }
    ];

    // Prefer moves that reveal unvisited fog
    let bestMove = moves[0];
    let maxHiddenTiles = -1;

    for (const m of moves) {
      const nx = agentEntity.x + m.x;
      const ny = agentEntity.y + m.y;
      if (!world.isObstacle(nx, ny) && nx >= 0 && nx < world.size && ny >= 0 && ny < world.size) {
        let hidden = 0;
        for (let dy = -2; dy <= 2; dy++) {
          for (let dx = -2; dx <= 2; dx++) {
            const tx = nx + dx;
            const ty = ny + dy;
            if (tx >= 0 && tx < world.size && ty >= 0 && ty < world.size && !world.discoveredTiles[ty][tx]) {
              hidden++;
            }
          }
        }
        if (hidden > maxHiddenTiles) {
          maxHiddenTiles = hidden;
          bestMove = m;
        }
      }
    }

    const nextX = agentEntity.x + bestMove.x;
    const nextY = agentEntity.y + bestMove.y;

    if (!world.isObstacle(nextX, nextY)) {
      agentEntity.x = nextX;
      agentEntity.y = nextY;
      this.addLog('ACTION', `Explorando cuadrícula hacia sector (${nextX}, ${nextY}). Niebla de guerra despejada.`);
    }
  }

  private moveTowards(agentEntity: Entity, targetX: number, targetY: number, world: World): void {
    const dx = Math.sign(targetX - agentEntity.x);
    const dy = Math.sign(targetY - agentEntity.y);

    let nextX = agentEntity.x;
    let nextY = agentEntity.y;

    if (Math.abs(targetX - agentEntity.x) > Math.abs(targetY - agentEntity.y)) {
      nextX += dx;
      if (world.isObstacle(nextX, nextY)) {
        nextX = agentEntity.x;
        nextY += dy;
      }
    } else {
      nextY += dy;
      if (world.isObstacle(nextX, nextY)) {
        nextY = agentEntity.y;
        nextX += dx;
      }
    }

    if (!world.isObstacle(nextX, nextY)) {
      agentEntity.x = nextX;
      agentEntity.y = nextY;
    }
  }

  private moveAwayFrom(agentEntity: Entity, enemyX: number, enemyY: number, world: World): void {
    const dx = -Math.sign(enemyX - agentEntity.x);
    const dy = -Math.sign(enemyY - agentEntity.y);

    const moves = [
      { x: dx, y: 0 },
      { x: 0, y: dy },
      { x: dx, y: dy },
      { x: -dx, y: 0 },
    ];

    for (const m of moves) {
      const nx = agentEntity.x + m.x;
      const ny = agentEntity.y + m.y;
      if (
        nx >= 0 &&
        nx < world.size &&
        ny >= 0 &&
        ny < world.size &&
        !world.isObstacle(nx, ny)
      ) {
        agentEntity.x = nx;
        agentEntity.y = ny;
        break;
      }
    }
  }

  reset(): void {
    this.energy = 100;
    this.hp = 100;
    this.stepCount = 0;
    this.mode = 'EXPLORATION';
    this.memories.clear();
    this.causal.clear();
    this.trash.clear();
    this.curiosity.clear();
    this.logs = [];
    this.floatingTexts = [];
    this.addLog('PERCEPTION', 'Sistema reiniciado. Todos los almacenes de memoria reseteados a estado basal.');
  }
}
