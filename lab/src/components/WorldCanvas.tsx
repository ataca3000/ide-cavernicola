import React, { useState } from 'react';
import { Entity, FloatingText } from '../engine/types';
import { World, MAP_SIZE } from '../engine/world';

interface WorldCanvasProps {
  world: World;
  agentEntity: Entity;
  floatingTexts: FloatingText[];
  onCellClick?: (x: number, y: number) => void;
}

export const WorldCanvas: React.FC<WorldCanvasProps> = ({
  world,
  agentEntity,
  floatingTexts,
  onCellClick,
}) => {
  const [fogEnabled, setFogEnabled] = useState(true);

  const getEntityIcon = (type: Entity['type']) => {
    switch (type) {
      case 'caveman':
      case 'mammoth':
        return '🧔';
      case 'wolf':
        return '🐺';
      case 'fire':
        return '🔥';
      case 'food':
        return '🍖';
      case 'bones':
        return '🦴';
      case 'rock':
        return '🪨';
      case 'tree':
        return '🌲';
      default:
        return '❓';
    }
  };

  return (
    <div className="world-canvas-container">
      <div className="world-header-toolbar">
        <div className="world-title">
          <span className="tab-pill active">🏔️ GLACIAR 20x20</span>
          <span className="coords-info">
            Posición: ({agentEntity.x}, {agentEntity.y})
          </span>
        </div>
        <div className="world-actions">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={fogEnabled}
              onChange={(e) => setFogEnabled(e.target.checked)}
            />
            Niebla de Guerra
          </label>
        </div>
      </div>

      <div className={`world-grid-frame cycle-${world.dayCycle}`}>
        {/* Floating Combat / Heal Texts */}
        {floatingTexts.map((ft) => (
          <div
            key={ft.id}
            className="floating-text-badge"
            style={{
              left: `${(ft.x / MAP_SIZE) * 100}%`,
              top: `${(ft.y / MAP_SIZE) * 100}%`,
              color: ft.color,
            }}
          >
            {ft.text}
          </div>
        ))}

        {/* 20x20 Grid Display */}
        <div className="world-grid">
          {Array.from({ length: MAP_SIZE }).map((_, y) => (
            <div key={`row_${y}`} className="grid-row">
              {Array.from({ length: MAP_SIZE }).map((_, x) => {
                const isDiscovered = world.discoveredTiles[y][x];
                const isHiddenByFog = fogEnabled && !isDiscovered;
                const isAgentHere = agentEntity.x === x && agentEntity.y === y;
                const cellEntities = world.getEntitiesAt(x, y);

                let cellClass = 'grid-cell';
                if (isHiddenByFog) cellClass += ' cell-fog';
                if (isAgentHere) cellClass += ' cell-agent';

                return (
                  <div
                    key={`cell_${x}_${y}`}
                    className={cellClass}
                    onClick={() => onCellClick && onCellClick(x, y)}
                    title={`(${x}, ${y}) ${
                      cellEntities.map((e) => e.label || e.type).join(', ')
                    }`}
                  >
                    {!isHiddenByFog ? (
                      <div className="cell-content">
                        {isAgentHere && (
                          <div className="entity-icon entity-agent animate-pulse">
                            {getEntityIcon('caveman')}
                          </div>
                        )}
                        {!isAgentHere && cellEntities.length > 0 && (
                          <div
                            className={`entity-icon entity-${cellEntities[0].type} ${
                              cellEntities[0].type === 'fire' ? 'entity-glow-fire' : ''
                            } ${
                              cellEntities[0].type === 'wolf' ? 'entity-glow-wolf' : ''
                            }`}
                          >
                            {getEntityIcon(cellEntities[0].type)}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="fog-shroud">·</div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      <div className="world-legend">
        <span>🧔 El Cavernícola (Agente IDC)</span>
        <span>🐺 Lobo (Peligro)</span>
        <span>🔥 Hoguera (Sanación)</span>
        <span>🍖 Alimento (+Energía)</span>
        <span>🦴 Restos (Trauma)</span>
        <span>🪨 Rocas / 🌲 Árboles</span>
      </div>
    </div>
  );
};
