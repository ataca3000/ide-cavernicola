import React, { useState } from 'react';

interface RealResultsViewerProps {
  result: any;
  onClose: () => void;
}

export const RealResultsViewer: React.FC<RealResultsViewerProps> = ({ result, onClose }) => {
  const [showRaw, setShowRaw] = useState(false);

  if (!result) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card results-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <span className="modal-icon">🏆</span>
            <div>
              <h3>Resultado Real de la Misión IDC</h3>
              <span className="results-subtitle">{result.title}</span>
            </div>
          </div>
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body results-body">
          {/* Summary Banner */}
          <div className="mission-summary-banner">
            <div className="summary-status-badge">✓ MISIÓN COMPLETADA</div>
            <p className="summary-text">{result.summary}</p>
          </div>

          {/* Metrics Grid */}
          {result.metrics && (
            <div className="results-metrics-grid">
              {Object.entries(result.metrics).map(([key, value]) => (
                <div key={key} className="result-metric-card">
                  <span className="metric-title">{key.replace(/_/g, ' ')}</span>
                  <span className="metric-val">{String(value)}</span>
                </div>
              ))}
            </div>
          )}

          {/* Cognitive Timeline */}
          {result.timeline && (
            <div className="timeline-section">
              <h4>Línea de Tiempo Cognitiva (Ejecutada por IDC)</h4>
              <div className="timeline-list">
                {result.timeline.map((step: any, idx: number) => (
                  <div key={idx} className="timeline-item">
                    <span className="timeline-step">Paso {step.step}</span>
                    <span className="timeline-action">[{step.action}]</span>
                    <span className="timeline-detail">{step.detail}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Raw Output Toggle */}
          <div className="raw-output-section">
            <button
              type="button"
              className="btn-toggle-raw"
              onClick={() => setShowRaw(!showRaw)}
            >
              {showRaw ? '▼ Ocultar Datos Crudos' : '▶ Ver Salida Completa JSON (AST / idc.db)'}
            </button>

            {showRaw && (
              <pre className="raw-output-pre">
                {JSON.stringify(result.raw_output, null, 2)}
              </pre>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button
            type="button"
            className="btn-secondary"
            onClick={() => {
              navigator.clipboard.writeText(JSON.stringify(result, null, 2));
              alert('Resultado copiado al portapapeles.');
            }}
          >
            📋 Copiar JSON
          </button>
          <button type="button" className="btn-primary" onClick={onClose}>
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
};
