import React from 'react';
import { TrashItem } from '../engine/types';

interface CausalTrashPanelProps {
  trashItems: TrashItem[];
}

export const CausalTrashPanel: React.FC<CausalTrashPanelProps> = ({ trashItems }) => {
  return (
    <div className="subpanel-card causal-trash-panel">
      <div className="subpanel-header">
        <span className="subpanel-title">
          <span className="icon">🛡️</span>
          CAUSAL TRASH &amp; TRAUMAS O(1) ({trashItems.length})
        </span>
        <span className="veto-badge">Poda Pre-Ejecución</span>
      </div>

      <div className="subpanel-content">
        {trashItems.length === 0 ? (
          <div className="empty-state">
            Sin cicatrices sistémicas registradas. Si el agente sufre un colapso crítico (ej. atacar lobos con las manos), la acción será proscrita de forma inmediata.
          </div>
        ) : (
          <div className="trash-list">
            {trashItems.map((item) => {
              const severityPercent = Math.round(item.severity * 100);

              return (
                <div key={item.id} className="trash-item">
                  <div className="trash-top">
                    <span className="trash-action">⛔ {item.failedAction}</span>
                    <span className="veto-count" title="Veces que IDC bloqueó esta acción en O(1)">
                      {item.refusalCount} {item.refusalCount === 1 ? 'bloqueo' : 'bloqueos'}
                    </span>
                  </div>
                  <div className="trash-reason">"{item.reason}"</div>
                  <div className="trash-severity-row">
                    <span className="severity-text">Severidad: {severityPercent}%</span>
                    <div className="severity-track">
                      <div
                        className="severity-fill"
                        style={{ width: `${severityPercent}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
