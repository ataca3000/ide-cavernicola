import React from 'react';
import { CausalRule } from '../engine/types';

interface CausalGraphPanelProps {
  rules: CausalRule[];
}

export const CausalGraphPanel: React.FC<CausalGraphPanelProps> = ({ rules }) => {
  return (
    <div className="subpanel-card causal-graph-panel">
      <div className="subpanel-header">
        <span className="subpanel-title">
          <span className="icon">🔮</span>
          REGLAS CAUSALES APRENDIDAS ({rules.length})
        </span>
        <span className="bayes-badge">Bayesian Updating</span>
      </div>

      <div className="subpanel-content">
        {rules.length === 0 ? (
          <div className="empty-state">
            El agente aún no ha consolidado reglas causales en este entorno. Se generarán al experimentar y evaluar consecuencias.
          </div>
        ) : (
          <div className="rules-list">
            {rules.map((rule) => {
              const confidencePercent = Math.round(rule.confidence * 100);
              const barColor =
                confidencePercent >= 70
                  ? '#10b981'
                  : confidencePercent >= 40
                  ? '#f59e0b'
                  : '#ef4444';

              return (
                <div key={rule.id} className="rule-item">
                  <div className="rule-top">
                    <span className="rule-cause">{rule.cause}</span>
                    <span className="rule-arrow">➔</span>
                    <span className="rule-effect">{rule.effect}</span>
                  </div>
                  <div className="rule-metrics">
                    <div className="confidence-track">
                      <div
                        className="confidence-fill"
                        style={{
                          width: `${confidencePercent}%`,
                          backgroundColor: barColor,
                        }}
                      ></div>
                    </div>
                    <span className="confidence-label" style={{ color: barColor }}>
                      {confidencePercent}% conf
                    </span>
                    <span className="usage-stats">
                      ✓{rule.successes} ✗{rule.failures}
                    </span>
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
