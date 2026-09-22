import { Entity, EntityType } from './types';

export const MAP_SIZE = 20;

export function manhattanDistance(a: { x: number; y: number }, b: { x: number; y: number }): number {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}

export function euclideanDistance(a: { x: number; y: number }, b: { x: number; y: number }): number {
  return Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2));
}

export class World {
  size: number = MAP_SIZE;
  entities: Entity[] = [];
  discoveredTiles: boolean[][];
  dayCycle: 'day' | 'dusk' | 'night' = 'day';
  stepCount: number = 0;

  constructor() {
    this.discoveredTiles = Array.from({ length: MAP_SIZE }, () => Array(MAP_SIZE).fill(false));
    this.reset();
  }

  reset(): void {
    this.entities = [];
    this.discoveredTiles = Array.from({ length: MAP_SIZE }, () => Array(MAP_SIZE).fill(false));
    this.stepCount = 0;
    this.dayCycle = 'day';

    // 1. Agent starting position (Mammoth / Caveman at 5, 12)
    this.addEntity({ id: 'agent_player', x: 5, y: 12, type: 'caveman', hp: 100, maxHp: 100, label: 'Mamut / Cavernícola' });

    // 2. Fire (sanctuary at 4, 4)
    this.addEntity({ id: 'fire_sanctuary', x: 4, y: 4, type: 'fire', label: 'Hoguera Sagrada' });

    // 3. Predators (Wolves roaming around 14, 8 and 16, 14)
    this.addEntity({ id: 'wolf_alpha', x: 14, y: 8, type: 'wolf', hp: 45, maxHp: 45, label: 'Lobo Alfa' });
    this.addEntity({ id: 'wolf_beta', x: 16, y: 14, type: 'wolf', hp: 35, maxHp: 35, label: 'Lobo Ártico' });

    // 4. Food / Berries (Sanctuary nutrition at 7, 3 and 12, 16)
    this.addEntity({ id: 'food_1', x: 7, y: 3, type: 'food', label: 'Bayas Silvestres' });
    this.addEntity({ id: 'food_2', x: 12, y: 16, type: 'food', label: 'Carne Seca' });

    // 5. Bones / Fossils (Trauma zones at 13, 9 and 8, 15)
    this.addEntity({ id: 'bones_1', x: 13, y: 9, type: 'bones', label: 'Huesos de Caza Pasada' });
    this.addEntity({ id: 'bones_2', x: 8, y: 15, type: 'bones', label: 'Fósil Ancestral' });

    // 6. Terrain Obstacles (Rocks and Frozen Trees)
    const rocks = [
      { x: 9, y: 7 }, { x: 10, y: 7 }, { x: 10, y: 8 },
      { x: 3, y: 9 }, { x: 15, y: 5 }, { x: 11, y: 12 }
    ];
    rocks.forEach((r, idx) => {
      this.addEntity({ id: `rock_${idx}`, x: r.x, y: r.y, type: 'rock', label: 'Roca Glaciar' });
    });

    const trees = [
      { x: 2, y: 2 }, { x: 3, y: 3 }, { x: 17, y: 2 }, { x: 18, y: 3 },
      { x: 6, y: 17 }, { x: 14, y: 17 }
    ];
    trees.forEach((t, idx) => {
      this.addEntity({ id: `tree_${idx}`, x: t.x, y: t.y, type: 'tree', label: 'Pino Congelado' });
    });

    // Reveal initial vision around agent (radius 4)
    this.updateVision(5, 12, 4);
  }

  addEntity(entity: Entity): void {
    this.entities.push(entity);
  }

  removeEntity(id: string): void {
    this.entities = this.entities.filter((e) => e.id !== id);
  }

  getAgent(): Entity {
    return this.entities.find((e) => e.id === 'agent_player') || this.entities[0];
  }

  getEntitiesAt(x: number, y: number): Entity[] {
    return this.entities.filter((e) => e.x === x && e.y === y);
  }

  isOccupied(x: number, y: number, ignoreTypes: EntityType[] = []): boolean {
    return this.entities.some(
      (e) => e.x === x && e.y === y && !ignoreTypes.includes(e.type)
    );
  }

  isObstacle(x: number, y: number): boolean {
    if (x < 0 || x >= this.size || y < 0 || y >= this.size) return true;
    return this.entities.some((e) => e.x === x && e.y === y && (e.type === 'rock' || e.type === 'tree'));
  }

  updateVision(agentX: number, agentY: number, radius: number = 4): void {
    for (let dy = -radius; dy <= radius; dy++) {
      for (let dx = -radius; dx <= radius; dx++) {
        const nx = agentX + dx;
        const ny = agentY + dy;
        if (nx >= 0 && nx < this.size && ny >= 0 && ny < this.size) {
          if (Math.abs(dx) + Math.abs(dy) <= radius + 1) {
            this.discoveredTiles[ny][nx] = true;
          }
        }
      }
    }
  }

  stepEnvironment(): void {
    this.stepCount += 1;
    // Day cycle rotates every 30 steps
    const cycleIndex = Math.floor(this.stepCount / 25) % 3;
    this.dayCycle = cycleIndex === 0 ? 'day' : cycleIndex === 1 ? 'dusk' : 'night';

    // Move wolves slightly towards agent if within scent distance (manhattan < 6)
    const agent = this.getAgent();
    this.entities.forEach((e) => {
      if (e.type === 'wolf') {
        const dist = manhattanDistance(e, agent);
        if (dist <= 6 && dist > 1) {
          const dx = Math.sign(agent.x - e.x);
          const dy = Math.sign(agent.y - e.y);

          // Wolves move 50% of the time, more aggressive at night
          const moveChance = this.dayCycle === 'night' ? 0.8 : 0.45;
          if (Math.random() < moveChance) {
            let nextX = e.x;
            let nextY = e.y;
            if (Math.abs(agent.x - e.x) > Math.abs(agent.y - e.y)) {
              nextX += dx;
            } else {
              nextY += dy;
            }
            if (!this.isObstacle(nextX, nextY) && !(nextX === agent.x && nextY === agent.y)) {
              e.x = nextX;
              e.y = nextY;
            }
          }
        } else if (dist > 6 && Math.random() < 0.25) {
          // Patrol randomly
          const moves = [
            { x: 1, y: 0 }, { x: -1, y: 0 }, { x: 0, y: 1 }, { x: 0, y: -1 }
          ];
          const m = moves[Math.floor(Math.random() * moves.length)];
          const nx = e.x + m.x;
          const ny = e.y + m.y;
          if (!this.isObstacle(nx, ny) && nx >= 0 && nx < this.size && ny >= 0 && ny < this.size) {
            e.x = nx;
            e.y = ny;
          }
        }
      }
    });
  }

  spawnPredator(): void {
    const x = Math.floor(Math.random() * (this.size - 4)) + 2;
    const y = Math.floor(Math.random() * (this.size - 4)) + 2;
    if (!this.isObstacle(x, y)) {
      this.addEntity({
        id: `wolf_${Date.now()}`,
        x,
        y,
        type: 'wolf',
        hp: 40,
        maxHp: 40,
        label: 'Lobo Feroz',
      });
    }
  }

  spawnFood(): void {
    const x = Math.floor(Math.random() * (this.size - 4)) + 2;
    const y = Math.floor(Math.random() * (this.size - 4)) + 2;
    if (!this.isObstacle(x, y)) {
      this.addEntity({
        id: `food_${Date.now()}`,
        x,
        y,
        type: 'food',
        label: 'Carne Fresca',
      });
    }
  }
}
