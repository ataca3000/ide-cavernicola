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

  return (
    <div className="cognitive-terminal-container">
      <div className="terminal-header">
        <div className="terminal-title">
          <span className="terminal-icon">🧠</span>
          <span>TELEMETRÍA COGNITIVA IDC • MONÓLOGO INTERNO</span>
        </div>
        <div className="terminal-controls">
          <select
            className="filter-select"
            value={filterTag}
            onChange={(e) => setFilterTag(e.target.value)}
          >
            <option value="ALL">Todos los Tags</option>
            <option value="TRASH_VETO">Veto Causal O(1)</option>
            <option value="CAUSAL">Reglas Causales</option>
            <option value="TRAUMA">Traumas</option>
            <option value="LEARNING">Aprendizaje</option>
            <option value="SIMULATION">Simulación</option>
          </select>
          <span className="step-counter">CICLO #{stepCount}</span>
        </div>
      </div>

      <div className="terminal-goal-banner">
        <span className="goal-label">🎯 OBJETIVO EN MEMORIA DE TRABAJO:</span>
        <span className="goal-text">"{currentGoal}"</span>
      </div>

      <div className="terminal-stream">
        {filteredLogs.map((log) => {
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
    </div>
  );
};
