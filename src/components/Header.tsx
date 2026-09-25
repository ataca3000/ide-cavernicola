import React from 'react';
import { AgentMode } from '../engine/types';

interface HeaderProps {
  mode: AgentMode;
  isRunning: boolean;
  speed: number;
  stepCount: number;
  curiosityIndex: number;
  onTogglePlay: () => void;
  onStep: () => void;
  onSetSpeed: (speed: number) => void;
  onReset: () => void;
  onSpawnFood: () => void;
  onOpenSettings: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  mode,
  isRunning,
  speed,
  stepCount,
  curiosityIndex,
  onTogglePlay,
  onStep,
  onSetSpeed,
  onReset,
  onSpawnFood,
  onOpenSettings,
}) => {
  return (
    <header className="idc-header">
      <div className="header-left">
        <div className="logo-box" title="Centynel — Centro de Inteligencia Operativa">
          <span className="logo-mark" aria-hidden="true">C</span>
        </div>
        <div className="title-group">
          <div className="title-row">
            <h1>CENTYNEL</h1>
            <span className="subtitle-pill">Centro de Inteligencia Operativa</span>
          </div>
          <p className="subtitle-desc">
            Supervisión de agentes, memoria causal y operaciones autónomas en un solo centro de control
          </p>
        </div>
      </div>

      <div className="header-center-metrics">
        {/* Gemini Cloud Indicator */}
        <div className="metric-badge gemini-badge">
          <span className="status-dot green"></span>
          <span>Google Gemini Nube</span>
          <span className="gear-icon">⚙</span>
        </div>

        {/* Health */}
        <div className="metric-badge hp-badge"></div>

        {/* Mode Pill */}
        <div className={`metric-badge mode-badge mode-${mode.toLowerCase()}`} />

        {/* Day/Night */}
        <div className="metric-badge cycle-badge" />

        {/* Step Count */}
        <div className="metric-badge step-badge">
          <span>🔄 Ciclo #{stepCount}</span>
        </div>

        {/* Curiosity Index */}
        <div className="metric-badge curiosity-badge">
          <span>🧠 IC: {curiosityIndex}</span>
        </div>
      </div>

      <div className="header-right-controls">
        <button
          className={`btn-control btn-play ${isRunning ? 'active' : ''}`}
          onClick={onTogglePlay}
        >
          {isRunning ? '⏸ Pausar' : '▶ Reanudar'}
        </button>

        <button className="btn-control" onClick={onStep} disabled={isRunning} title="Avanzar 1 ciclo cognitivo">
          ⏭ Paso
        </button>

        <div className="speed-selector">
          {[1, 2, 5].map((s) => (
            <button
              key={s}
              className={`btn-speed ${speed === s ? 'active' : ''}`}
              onClick={() => onSetSpeed(s)}
            >
              {s}x
            </button>
          ))}
        </div>

        <button className="btn-control btn-spawn" onClick={onSpawnFood} title="Colocar recurso">
          + Recurso
        </button>

        <button className="btn-control btn-reset" onClick={onReset} title="Reiniciar memoria y estado">
          🔄 Reset
        </button>

        <button className="btn-control btn-settings" onClick={onOpenSettings} title="Configurar Servidor y Gemini API">
          ⚙️ Conexión &amp; API
        </button>
      </div>
    </header>
  );
};
