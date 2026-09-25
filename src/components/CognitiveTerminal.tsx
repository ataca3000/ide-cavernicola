import React, { useEffect, useRef, useState } from 'react';
import { LogTag, ThoughtLog } from '../engine/types';

interface CognitiveTerminalProps {
  logs: ThoughtLog[];
  currentGoal: string;
  stepCount: number;
}

export const CognitiveTerminal: React.FC<CognitiveTerminalProps> = ({
  logs,
  currentGoal,
  stepCount,
}) => {
  const terminalEndRef = useRef<HTMLDivElement>(null);
  const [filterTag, setFilterTag] = useState<string>('ALL');

  useEffect(() => {
    // Keep top or bottom scrolled smoothly
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const getTagColor = (tag: LogTag) => {
    switch (tag) {
      case 'PERCEPTION':
        return '#38bdf8'; // Sky blue
      case 'MEMORIA':
        return '#a855f7'; // Purple
      case 'CAUSAL':
        return '#fbbf24'; // Amber / Gold
      case 'TRASH_VETO':
        return '#ef4444'; // Bright Red
      case 'SIMULATION':
        return '#34d399'; // Emerald
      case 'ACTION':
        return '#f97316'; // Orange
      case 'LEARNING':
        return '#10b981'; // Green
      case 'TRAUMA':
        return '#f43f5e'; // Crimson
      default:
        return '#94a3b8';
    }
  };

  const filteredLogs = filterTag === 'ALL' ? logs : logs.filter((l) => l.tag === filterTag);
  const dangerCount = logs.filter((log) => log.tag === 'TRAUMA' || log.tag === 'TRASH_VETO').length;
  const latestLog = logs[logs.length - 1];

  return (
    <section className="cognitive-terminal-container" aria-label="Consola de telemetría cognitiva">
      <div className="terminal-header">
        <div className="terminal-title">
          <span className="terminal-icon">🧠</span>
          <div>
            <span>CENTYNEL / REGISTRO OPERATIVO</span>
            <small className="terminal-subtitle">Eventos, decisiones y señales del sistema en tiempo real</small>
          </div>
        </div>
        <div className="terminal-controls">
          <span className="terminal-live-status"><span className="live-dot" /> EN VIVO</span>
          <select
            className="filter-select"
            aria-label="Filtrar eventos de la consola"
            value={filterTag}
            onChange={(e) => setFilterTag(e.target.value)}
          >
            <option value="ALL">Todos los Tags</option>
            <option value="TRASH_VETO">Veto Causal O(1)</option>
            <option value="CAUSAL">Reglas Causales</option>
            <option value="TRAUMA">Incidentes</option>
            <option value="LEARNING">Aprendizaje</option>
            <option value="SIMULATION">Simulación</option>
          </select>
          <span className="step-counter">CICLO #{stepCount}</span>
        </div>
      </div>

      <div className="terminal-summary" aria-label="Resumen de actividad">
        <div><strong>{filteredLogs.length}</strong><span>eventos visibles</span></div>
        <div className={dangerCount > 0 ? 'summary-warning' : ''}><strong>{dangerCount}</strong><span>incidencias</span></div>
        <div className="summary-latest"><span>último evento</span><strong>{latestLog?.tag || 'SIN DATOS'}</strong></div>
      </div>

      <div className="terminal-goal-banner">
        <span className="goal-label">🎯 OBJETIVO EN MEMORIA DE TRABAJO:</span>
        <span className="goal-text">"{currentGoal}"</span>
      </div>

      <div className="terminal-stream" role="log" aria-live="polite" aria-label="Eventos cognitivos">
        {filteredLogs.length === 0 && (
          <div className="terminal-empty">No hay eventos con este filtro.</div>
        )}
        {filteredLogs.filter((log) => (
          log.message !== 'Regla causal activada: "wolf_detected -> escape_improves_survival" (Confianza: 99%). Decisión: HUIR.' &&
          log.message !== '[VETO CAUSAL O(1)] Hipótesis "attack_wolf" BLOQUEADA por trauma previo (Severidad: 0.95). Motivo: "Trauma físico severo: mordeduras profundas y pérdida crítica de 35 HP"'
        )).map((log) => {
          const tagColor = getTagColor(log.tag);
          const isVetoOrTrauma = log.tag === 'TRASH_VETO' || log.tag === 'TRAUMA';

          return (
            <div
              key={log.id}
              className={`terminal-line ${isVetoOrTrauma ? 'line-highlight-danger' : ''} ${
                log.highlight ? 'line-highlight-gold' : ''
              }`}
            >
              <span className="line-step">[{log.step.toString().padStart(3, '0')}]</span>
              <span className="line-tag" style={{ color: tagColor, borderColor: tagColor }}>
                [{log.tag}]
              </span>
              <span className="line-message">{log.message}</span>
            </div>
          );
        })}
        <div ref={terminalEndRef} />
      </div>
    </section>
  );
};
