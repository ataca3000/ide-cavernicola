import React, { useState } from 'react';

interface ConnectionModalProps {
  isOpen: boolean;
  serverUrl: string;
  geminiKey: string;
  serverStatus: 'online' | 'offline' | 'checking';
  serverDetails: any;
  onClose: () => void;
  onSave: (url: string, key: string, mode: string) => void;
  onTestConnection: () => void;
}

export const ConnectionModal: React.FC<ConnectionModalProps> = ({
  isOpen,
  serverUrl,
  geminiKey,
  serverStatus,
  serverDetails,
  onClose,
  onSave,
  onTestConnection,
}) => {
  const [url, setUrl] = useState(serverUrl);
  const [key, setKey] = useState(geminiKey);
  const [mode, setMode] = useState('local_idc');
  const [showKey, setShowKey] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(url, key, mode);
    onClose();
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <span className="modal-icon">⚙️</span>
            <h3>Configuración de Conexión y Servidor IDC</h3>
          </div>
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          {/* Status Banner */}
          <div className={`status-banner status-${serverStatus}`}>
            <span className={`status-light ${serverStatus}`}></span>
            <div className="status-text">
              <strong>
                {serverStatus === 'online'
                  ? '🟢 Servidor Local IDC Conectado (localhost:8000)'
                  : serverStatus === 'checking'
                  ? '🟡 Verificando Conexión...'
                  : '🔴 Servidor Local Desconectado (Modo Standalone)'}
              </strong>
              {serverDetails?.sqlite_db && (
                <div className="status-sub">
                  SQLite idc.db: {serverDetails.sqlite_db.causal_rules} reglas,{' '}
                  {serverDetails.sqlite_db.causal_trash_items} vetos en trash.
                </div>
              )}
            </div>
            <button
              type="button"
              className="btn-ping"
              onClick={onTestConnection}
              disabled={serverStatus === 'checking'}
            >
              Probar Ping
            </button>
          </div>

          {/* Mode Selector */}
          <div className="form-group">
            <label className="form-label">Modo de Ejecución del Agente:</label>
            <div className="mode-options">
              <label className={`mode-option ${mode === 'local_idc' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="execMode"
                  value="local_idc"
                  checked={mode === 'local_idc'}
                  onChange={() => setMode('local_idc')}
                />
                <div className="option-info">
                  <strong>🖥️ Agente Local Python (IDC Core)</strong>
                  <span>Ejecuta AST, SQLite idc.db y CausalEngine localmente</span>
                </div>
              </label>

              <label className={`mode-option ${mode === 'gemini_cloud' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="execMode"
                  value="gemini_cloud"
                  checked={mode === 'gemini_cloud'}
                  onChange={() => setMode('gemini_cloud')}
                />
                <div className="option-info">
                  <strong>🌐 Google Gemini Nube (API)</strong>
                  <span>Razonamiento multimodal y síntesis profunda con LLM</span>
                </div>
              </label>
            </div>
          </div>

          {/* Server URL Input */}
          <div className="form-group">
            <label className="form-label">URL del Servidor Local IDC:</label>
            <input
              type="text"
              className="form-input"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="http://127.0.0.1:8000"
            />
            <span className="input-hint">
              Servidor backend Python (<code>uv run python server.py</code>).
            </span>
          </div>

          {/* Gemini API Key Input */}
          <div className="form-group">
            <label className="form-label">Google Gemini API Key (Opcional):</label>
            <div className="key-input-row">
              <input
                type={showKey ? 'text' : 'password'}
                className="form-input"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="AIzaSy..."
              />
              <button
                type="button"
                className="btn-toggle-key"
                onClick={() => setShowKey(!showKey)}
              >
                {showKey ? 'Ocultar' : 'Ver'}
              </button>
            </div>
            <span className="input-hint">
              Si se provee, el agente local usará el plugin Gemini para misiones complejas.
            </span>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="btn-primary">
              Guardar y Conectar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
