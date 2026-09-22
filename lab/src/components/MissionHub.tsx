import React, { useState } from 'react';

interface MissionHubProps {
  serverStatus: 'online' | 'offline' | 'checking';
  isRunningMission: boolean;
  onExecuteMission: (type: 'scan' | 'memory' | 'causal_stress' | 'custom', prompt?: string) => void;
  onOpenSettings: () => void;
}

export const MissionHub: React.FC<MissionHubProps> = ({
  serverStatus,
  isRunningMission,
  onExecuteMission,
  onOpenSettings,
}) => {
  const [customPrompt, setCustomPrompt] = useState('');

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customPrompt.trim()) {
      onExecuteMission('custom', customPrompt.trim());
    }
  };

  return (
    <div className="mission-hub-card">
      <div className="mission-hub-header">
        <div className="hub-title-row">
          <span className="hub-icon">🚀</span>
          <div>
            <h4>CENTRO DE MISIONES Y PRUEBAS REALES IDC</h4>
            <span className="hub-sub">
              El juego 2D refleja la simulación mientras IDC ejecuta la tarea real en tu máquina.
            </span>
          </div>
        </div>

        <div className="hub-header-actions">
          <button
            className={`server-status-pill ${serverStatus}`}
            onClick={onOpenSettings}
            title="Clic para configurar servidor o API Key"
          >
            <span className="status-dot"></span>
            {serverStatus === 'online' ? 'Servidor Local Conectado' : 'Modo Standalone / Desconectado'}
          </button>
        </div>
      </div>

      {isRunningMission && (
        <div className="mission-progress-banner">
          <div className="spinner"></div>
          <span>Agente IDC ejecutando misión real en segundo plano... Observa el juego y la terminal.</span>
        </div>
      )}

      {/* Preset Missions Grid */}
      <div className="missions-presets-grid">
        <button
          className="mission-card-btn"
          onClick={() => onExecuteMission('scan')}
          disabled={isRunningMission}
        >
          <span className="mission-icon">🔍</span>
          <div className="mission-info">
            <strong>Escanear Repositorio Real</strong>
            <span>Extrae AST nativo, deuda técnica y workflows CI/CD</span>
          </div>
        </button>

        <button
          className="mission-card-btn"
          onClick={() => onExecuteMission('memory')}
          disabled={isRunningMission}
        >
          <span className="mission-icon">🧠</span>
          <div className="mission-info">
            <strong>Auditar Memoria SQLite</strong>
            <span>Consulta idc.db, reglas causales y traumas ciberfísicos</span>
          </div>
        </button>

        <button
          className="mission-card-btn"
          onClick={() => onExecuteMission('causal_stress')}
          disabled={isRunningMission}
        >
          <span className="mission-icon">🛡️</span>
          <div className="mission-info">
            <strong>Prueba de Estrés Causal Trash</strong>
            <span>Inyecta acción catastrófica y prueba veto O(1)</span>
          </div>
        </button>
      </div>

      {/* Custom Mission User Prompt */}
      <form onSubmit={handleCustomSubmit} className="custom-mission-form">
        <div className="custom-input-label">
          <span>💬 MISIÓN A PETICIÓN DEL USUARIO:</span>
        </div>
        <div className="custom-input-row">
          <input
            type="text"
            className="custom-mission-input"
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="Ej: 'Optimizar el cache de dependencias y evitar bucles en CI' o cualquier objetivo..."
            disabled={isRunningMission}
          />
          <button
            type="submit"
            className="btn-launch-mission"
            disabled={isRunningMission || !customPrompt.trim()}
          >
            {isRunningMission ? 'Ejecutando...' : 'Lanzar a IDC ➔'}
          </button>
        </div>
      </form>
    </div>
  );
};
