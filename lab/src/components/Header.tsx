import React from 'react';
import { AgentMode } from '../engine/types';

interface HeaderProps {
  energy: number;
  hp: number;
  mode: AgentMode;
  isRunning: boolean;
  speed: number;
  dayCycle: 'day' | 'dusk' | 'night';
  stepCount: number;
  curiosityIndex: number;
  avatar: 'caveman' | 'mammoth';
  onTogglePlay: () => void;
  onStep: () => void;
  onSetSpeed: (speed: number) => void;
  onReset: () => void;
  onToggleAvatar: () => void;
  onSpawnWolf: () => void;
  onSpawnFood: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  energy,
  hp,
  mode,
  isRunning,
  speed,
  dayCycle,
  stepCount,
  curiosityIndex,
  avatar,
  onTogglePlay,
  onStep,
  onSetSpeed,
  onReset,
  onToggleAvatar,
  onSpawnWolf,
  onSpawnFood,
}) => {
  const getEnergyColor = (val: number) => {
    if (val > 60) return '#10b981';
    if (val > 25) return '#f59e0b';
    return '#ef4444';
  };

  const getDayIcon = () => {
    if (dayCycle === 'day') return '☀️ Día';
    if (dayCycle === 'dusk') return '🌅 Atardecer';
    return '🌙 Noche Helada';
  };

  return (
    <header className="idc-header">
      <div className="header-left">
        <div className="logo-box" onClick={onToggleAvatar} title="Clic para alternar Mamut / Cavernícola">
          <span className="logo-icon">{avatar === 'mammoth' ? '🦣' : '🧔'}</span>
        </div>
        <div className="title-group">
          <div className="title-row">
            <h1>IDC cavernícola</h1>
            <span className="subtitle-pill">Watch a Mammoth Learn to Survive</span>
          </div>
          <p className="subtitle-desc">
            Simulador del Agente IDC en la Era Glaciar • Memoria Causal &amp; Supervivencia Autónoma
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

        {/* Metabolic Energy Bar */}
        <div className="metric-badge energy-badge" style={{ borderColor: getEnergyColor(energy) }}>
          <span className="energy-icon">⚡</span>
          <div className="energy-info">
            <span className="energy-label">Energía:</span>
            <span className="energy-value" style={{ color: getEnergyColor(energy) }}>
              {energy}%
            </span>
          </div>
          <div className="energy-track">
            <div
              className="energy-fill"
              style={{
                width: `${energy}%`,
                backgroundColor: getEnergyColor(energy),
              }}
            ></div>
          </div>
        </div>

        {/* Health */}
        <div className="metric-badge hp-badge">
          <span>❤️ Salud: {hp}%</span>
        </div>

        {/* Mode Pill */}
        <div className={`metric-badge mode-badge mode-${mode.toLowerCase()}`}>
          <span className="mode-dot"></span>
          <span>Modo: {mode}</span>
        </div>

        {/* Day/Night */}
        <div className="metric-badge cycle-badge">
          <span>{getDayIcon()}</span>
        </div>

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

        <button className="btn-control btn-spawn" onClick={onSpawnWolf} title="Inyectar amenaza">
          +🐺 Lobo
        </button>

        <button className="btn-control btn-spawn" onClick={onSpawnFood} title="Colocar recurso">
          +🍖 Comida
        </button>

        <button className="btn-control btn-reset" onClick={onReset} title="Reiniciar memoria y estado">
          🔄 Reset
        </button>
      </div>
    </header>
  );
};
