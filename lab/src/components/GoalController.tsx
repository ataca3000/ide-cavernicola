import React, { useState } from 'react';

interface GoalControllerProps {
  currentGoal: string;
  onSetGoal: (goal: string) => void;
}

export const GoalController: React.FC<GoalControllerProps> = ({ currentGoal, onSetGoal }) => {
  const [inputValue, setInputValue] = useState(currentGoal);

  const presets = [
    { label: '🔥 Alcanzar Fuego', value: 'Alcanzar la hoguera sagrada' },
    { label: '🐺 Evadir Lobos', value: 'Evadir depredadores árticos' },
    { label: '🍖 Buscar Comida', value: 'Recolectar bayas y carne' },
    { label: '🏔️ Explorar Glaciar', value: 'Explorar cuadrícula y despejar niebla' },
    { label: '🦴 Investigar Fósiles', value: 'Examinar restos óseos ancestrales' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSetGoal(inputValue.trim());
    }
  };

  return (
    <div className="goal-controller-card">
      <div className="goal-header">
        <span className="goal-title">🎯 CONTROLADOR DE PROPÓSITO (IDC PURPOSE FILTER)</span>
        <span className="info-chip">Reconfiguración en Caliente</span>
      </div>

      <form onSubmit={handleSubmit} className="goal-input-row">
        <input
          type="text"
          className="goal-input"
          placeholder="Escribe un objetivo para el cavernícola (ej: 'Construir Refugio')..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <button type="submit" className="btn-set-goal">
          Fijar Propósito
        </button>
      </form>

      <div className="goal-presets">
        <span className="presets-label">Objetivos sugeridos:</span>
        <div className="preset-chips">
          {presets.map((p) => (
            <button
              key={p.value}
              type="button"
              className={`chip-btn ${currentGoal === p.value ? 'active' : ''}`}
              onClick={() => {
                setInputValue(p.value);
                onSetGoal(p.value);
              }}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
