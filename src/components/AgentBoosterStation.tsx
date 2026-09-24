import React, { useState, useEffect } from 'react';

interface RepoMetrics {
  total_source_files: number;
  total_python_files: number;
  total_lines_of_code: number;
  total_classes: number;
  technical_debt_items: number;
  ci_workflows_count: number;
  extension_distribution?: Record<string, number>;
}

interface TechnicalDebtItem {
  file: string;
  line: number;
  tag: string;
  detail: string;
}

interface TargetRepoInfo {
  path: string;
  name: string;
  metrics: RepoMetrics;
  debt_preview: TechnicalDebtItem[];
}

interface GuestAgentConfig {
  name: string;
  type: string;
  endpoint_url: string;
  api_key: string;
  model_name: string;
  status: string;
}

interface SuperpowersConfig {
  causal_trash_shield: boolean;
  cybernetic_causal_memory: boolean;
  evolutive_code_engine: boolean;
  low_entropy_curiosity: boolean;
}

interface AgentBoosterStationProps {
  serverUrl: string;
  serverStatus: 'online' | 'offline' | 'checking';
  onExecuteInWorld?: (title: string) => void;
}

export const AgentBoosterStation: React.FC<AgentBoosterStationProps> = ({
  serverUrl,
  serverStatus,
  onExecuteInWorld,
}) => {
  // Station State
  const [targetRepo, setTargetRepo] = useState<TargetRepoInfo | null>(null);
  const [repoPathInput, setRepoPathInput] = useState<string>('');
  const [guestAgent, setGuestAgent] = useState<GuestAgentConfig>({
    name: 'Mi Agente Dev',
    type: 'openai_compatible',
    endpoint_url: 'http://localhost:11434/v1',
    api_key: '',
    model_name: 'llama3:latest',
    status: 'ready',
  });
  const [superpowers, setSuperpowers] = useState<SuperpowersConfig>({
    causal_trash_shield: true,
    cybernetic_causal_memory: true,
    evolutive_code_engine: true,
    low_entropy_curiosity: true,
  });
  const [causalStats, setCausalStats] = useState({ rules: 27, trash: 5 });

  // Mission / Task Execution State
  const [taskInput, setTaskInput] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'console' | 'sdk' | 'debt'>('console');
  const [sdkLanguage, setSdkLanguage] = useState<'python' | 'typescript'>('python');
  const [boostResult, setBoostResult] = useState<any>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const cleanUrl = serverUrl.replace(/\/$/, '');

  // Load Station State
  const fetchStationStatus = async () => {
    try {
      const res = await fetch(`${cleanUrl}/api/station/status`);
      if (res.ok) {
        const data = await res.json();
        setTargetRepo(data.target_repo);
        setRepoPathInput(data.target_repo.path);
        setGuestAgent(data.guest_agent);
        setSuperpowers(data.superpowers);
        setCausalStats({
          rules: data.cognitive_telemetry.causal_rules_count,
          trash: data.cognitive_telemetry.causal_trash_count,
        });
      }
    } catch {
      // Fallback mock if server offline
    }
  };

  useEffect(() => {
    fetchStationStatus();
  }, [serverUrl]);

  // Target Repository Switch
  const handleUpdateRepo = async () => {
    if (!repoPathInput.trim()) return;
    setIsProcessing(true);
    setStatusMessage('Escaneando y vinculando repositorio objetivo...');
    try {
      const res = await fetch(`${cleanUrl}/api/station/target-repo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: repoPathInput }),
      });
      const data = await res.json();
      if (res.ok) {
        setTargetRepo(data.target_repo);
        setStatusMessage(`✅ ${data.message}`);
        setTimeout(() => setStatusMessage(null), 4000);
      } else {
        setStatusMessage(`❌ ${data.error || 'Error al vincular el repositorio'}`);
      }
    } catch (err: any) {
      setStatusMessage(`❌ Error de red: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Connect Guest Agent
  const handleConnectAgent = async () => {
    setIsProcessing(true);
    setStatusMessage('Inyectando superpoderes IDC al agente...');
    try {
      const res = await fetch(`${cleanUrl}/api/station/connect-agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...guestAgent,
          superpowers,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setGuestAgent(data.guest_agent);
        setStatusMessage(`⚡ ${data.message}`);
        setTimeout(() => setStatusMessage(null), 4000);
      }
    } catch (err: any) {
      setStatusMessage(`❌ Error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Toggle Superpower
  const handleToggleSuperpower = (key: keyof SuperpowersConfig) => {
    const updated = { ...superpowers, [key]: !superpowers[key] };
    setSuperpowers(updated);
  };

  // Execute Boosted Task on Target Repo
  const handleBoostTask = async (customPrompt?: string) => {
    const promptToSend = customPrompt || taskInput;
    if (!promptToSend.trim()) return;

    setIsProcessing(true);
    setBoostResult(null);
    if (onExecuteInWorld) onExecuteInWorld(`Superpoderes IDC: ${promptToSend}`);

    try {
      const res = await fetch(`${cleanUrl}/api/station/boost`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task: promptToSend,
          superpowers,
        }),
      });
      const data = await res.json();
      setBoostResult(data);
    } catch (err: any) {
      setBoostResult({
        status: 'error',
        warning: `Error al procesar con el booster: ${err.message}`,
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // Trigger Evolutionary Refactor
  const handleTriggerEvolve = async () => {
    setIsProcessing(true);
    setBoostResult(null);
    if (onExecuteInWorld) onExecuteInWorld('Generando Mutación Evolutiva de Código');

    try {
      const res = await fetch(`${cleanUrl}/api/station/evolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      const data = await res.json();
      setBoostResult({
        status: 'evolution_generated',
        evolution: data,
      });
    } catch (err: any) {
      setBoostResult({
        status: 'error',
        warning: `Error al generar evolución: ${err.message}`,
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="booster-station-container">
      {/* ── Top Hero Banner ────────────────────────────────────────── */}
      <div className="station-hero-banner">
        <div className="hero-left">
          <div className="hero-badge">
            <span className="hero-spark">⚡</span>
            <span>IDC AGENT BOOSTER STATION</span>
            <span className="byoa-tag">BYOA (BRING YOUR OWN AGENT)</span>
          </div>
          <h2>Estación de Superpoderes Cognitivos y Evolutivos</h2>
          <p>
            Conecta <strong>tu propio agente de IA</strong> y <strong>tu repositorio local</strong>. 
            IDC le inyecta <em>Memoria Causal Ciberfísica</em>, <em>Escudo Anti-Bucles Causal Trash O(1)</em> y 
            <em>Síntesis Evolutiva de Código</em> para que resuelva problemas reales sin alucinar ni quemar tokens en vano.
          </p>
        </div>

        <div className="hero-right-metrics">
          <div className="telemetry-pill">
            <span className="pill-label">Reglas Causales Activas</span>
            <span className="pill-value highlight-cyan">🧠 {causalStats.rules}</span>
          </div>
          <div className="telemetry-pill">
            <span className="pill-label">Vetos Causal Trash O(1)</span>
            <span className="pill-value highlight-amber">🛡️ {causalStats.trash}</span>
          </div>
          <div className="telemetry-pill">
            <span className="pill-label">Estado Servidor Puente</span>
            <span className={`pill-value ${serverStatus === 'online' ? 'status-green' : 'status-red'}`}>
              ● {serverStatus === 'online' ? 'Conectado (8000)' : 'Desconectado'}
            </span>
          </div>
        </div>
      </div>

      {statusMessage && (
        <div className="station-status-alert animate-fade-in">
          {statusMessage}
        </div>
      )}

      {/* ── Main Station Configuration Grid ──────────────────────── */}
      <div className="station-config-grid">
        {/* Panel 1: Target Repository Selector */}
        <div className="station-card card-repo">
          <div className="card-header">
            <div className="card-title-wrap">
              <span className="card-icon">📂</span>
              <div>
                <h4>1. Repositorio Objetivo</h4>
                <span className="card-sub">Audita y mejora cualquier carpeta de tu equipo</span>
              </div>
            </div>
            {targetRepo && (
              <span className="repo-name-badge">📦 {targetRepo.name}</span>
            )}
          </div>

          <div className="card-body">
            <div className="input-with-button">
              <input
                type="text"
                className="station-input"
                value={repoPathInput}
                onChange={(e) => setRepoPathInput(e.target.value)}
                placeholder="Ruta absoluta (ej. C:/Users/.../mi-proyecto)"
              />
              <button
                type="button"
                className="btn-station-action"
                onClick={handleUpdateRepo}
                disabled={isProcessing}
              >
                🔍 Escanear Repo
              </button>
            </div>

            {targetRepo && (
              <div className="repo-stats-dashboard">
                <div className="stat-box">
                  <span className="stat-num">{targetRepo.metrics.total_source_files}</span>
                  <span className="stat-desc">Archivos Fuente</span>
                </div>
                <div className="stat-box">
                  <span className="stat-num">{targetRepo.metrics.total_lines_of_code.toLocaleString()}</span>
                  <span className="stat-desc">Líneas de Código</span>
                </div>
                <div className="stat-box">
                  <span className="stat-num highlight-amber">{targetRepo.metrics.technical_debt_items}</span>
                  <span className="stat-desc">Marcadores Deuda</span>
                </div>
                <div className="stat-box">
                  <span className="stat-num highlight-green">{targetRepo.metrics.total_classes}</span>
                  <span className="stat-desc">Clases Detectadas</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Panel 2: Connect Guest Agent */}
        <div className="station-card card-agent">
          <div className="card-header">
            <div className="card-title-wrap">
              <span className="card-icon">🤖</span>
              <div>
                <h4>2. Tu Agente Huésped (BYOA)</h4>
                <span className="card-sub">Configura tu framework o modelo para potenciarlo</span>
              </div>
            </div>
            <span className="agent-status-pill">
              ✨ {guestAgent.status === 'boosted' ? 'POTENCIADO' : 'LISTO'}
            </span>
          </div>

          <div className="card-body">
            <div className="agent-form-row">
              <div className="form-group flex-1">
                <label>Nombre del Agente</label>
                <input
                  type="text"
                  className="station-input"
                  value={guestAgent.name}
                  onChange={(e) => setGuestAgent({ ...guestAgent, name: e.target.value })}
                  placeholder="ej. AutoDev / LangChain Bot"
                />
              </div>

              <div className="form-group flex-1">
                <label>Tipo de Conexión</label>
                <select
                  className="station-select"
                  value={guestAgent.type}
                  onChange={(e) => setGuestAgent({ ...guestAgent, type: e.target.value })}
                >
                  <option value="openai_compatible">⚡ OpenAI Compatible (Local / Cloud)</option>
                  <option value="gemini_sdk">🌐 Google Gemini API</option>
                  <option value="ollama_local">🦙 Ollama Local (Llama 3 / Mistral)</option>
                  <option value="rest_endpoint">🔗 REST Webhook Personalizado</option>
                  <option value="langchain_proxy">🦜🔗 LangChain / CrewAI Wrapper</option>
                </select>
              </div>
            </div>

            <div className="agent-form-row">
              <div className="form-group flex-2">
                <label>Endpoint / URL</label>
                <input
                  type="text"
                  className="station-input font-mono"
                  value={guestAgent.endpoint_url}
                  onChange={(e) => setGuestAgent({ ...guestAgent, endpoint_url: e.target.value })}
                  placeholder="http://localhost:11434/v1 o URL remota"
                />
              </div>

              <div className="form-group flex-1">
                <label>Modelo</label>
                <input
                  type="text"
                  className="station-input font-mono"
                  value={guestAgent.model_name}
                  onChange={(e) => setGuestAgent({ ...guestAgent, model_name: e.target.value })}
                  placeholder="llama3:latest"
                />
              </div>
            </div>

            <button
              type="button"
              className="btn-station-connect"
              onClick={handleConnectAgent}
              disabled={isProcessing}
            >
              ⚡ Inyectar Superpoderes a {guestAgent.name}
            </button>
          </div>
        </div>
      </div>

      {/* ── Superpowers Matrix ─────────────────────────────────────── */}
      <div className="superpowers-section">
        <div className="section-title-row">
          <h3>🧬 Matriz de Superpoderes Cognitivos IDC</h3>
          <span className="section-note">Activa o desactiva las capacidades aumentadas para tu agente</span>
        </div>

        <div className="superpowers-grid">
          {/* Power 1: Causal Trash Shield */}
          <div
            className={`power-card ${superpowers.causal_trash_shield ? 'active' : 'inactive'}`}
            onClick={() => handleToggleSuperpower('causal_trash_shield')}
          >
            <div className="power-card-top">
              <span className="power-icon">🛡️</span>
              <span className="power-state-tag">
                {superpowers.causal_trash_shield ? 'ACTIVO (O(1))' : 'DESACTIVADO'}
              </span>
            </div>
            <div className="power-name">Escudo Anti-Bucles Causal Trash</div>
            <p className="power-desc">
              Veta inmediatamente en <strong>O(1)</strong> cualquier acción o refactorización que haya fallado o causado regresiones en el pasado. Elimina bucles autodestructivos.
            </p>
          </div>

          {/* Power 2: Cybernetic Causal Memory */}
          <div
            className={`power-card ${superpowers.cybernetic_causal_memory ? 'active' : 'inactive'}`}
            onClick={() => handleToggleSuperpower('cybernetic_causal_memory')}
          >
            <div className="power-card-top">
              <span className="power-icon">🧠</span>
              <span className="power-state-tag">
                {superpowers.cybernetic_causal_memory ? 'ACTIVO' : 'DESACTIVADO'}
              </span>
            </div>
            <div className="power-name">Memoria Causal Ciberfísica</div>
            <p className="power-desc">
              Almacena relaciones causa-efecto empíricas de código <code>(A -&gt; B con confianza %)</code> en SQLite persistente para que el agente recuerde entre sesiones.
            </p>
          </div>

          {/* Power 3: Evolutive Code Engine */}
          <div
            className={`power-card ${superpowers.evolutive_code_engine ? 'active' : 'inactive'}`}
            onClick={() => handleToggleSuperpower('evolutive_code_engine')}
          >
            <div className="power-card-top">
              <span className="power-icon">🧬</span>
              <span className="power-state-tag">
                {superpowers.evolutive_code_engine ? 'ACTIVO' : 'DESACTIVADO'}
              </span>
            </div>
            <div className="power-name">Motor de Síntesis Evolutiva</div>
            <p className="power-desc">
              Escanea el AST completo, identifica acoplamientos y marcadores de deuda técnica (TODO, FIXME) y genera parches de refactorización continuos.
            </p>
          </div>

          {/* Power 4: Low Entropy Curiosity */}
          <div
            className={`power-card ${superpowers.low_entropy_curiosity ? 'active' : 'inactive'}`}
            onClick={() => handleToggleSuperpower('low_entropy_curiosity')}
          >
            <div className="power-card-top">
              <span className="power-icon">⚡</span>
              <span className="power-state-tag">
                {superpowers.low_entropy_curiosity ? 'ACTIVO' : 'DESACTIVADO'}
              </span>
            </div>
            <div className="power-name">Curiosidad de Baja Entropía</div>
            <p className="power-desc">
              Formula hipótesis guiadas de mejora arquitectónica sin consumo innecesario de tokens, maximizando el aprendizaje por ciclo metabólico.
            </p>
          </div>
        </div>
      </div>

      {/* ── Operational Cockpit & Missions ──────────────────────────── */}
      <div className="station-operations-card">
        <div className="operations-header-tabs">
          <button
            type="button"
            className={`op-tab-btn ${activeTab === 'console' ? 'active' : ''}`}
            onClick={() => setActiveTab('console')}
          >
            🔬 Consola de Misiones Potenciadas
          </button>
          <button
            type="button"
            className={`op-tab-btn ${activeTab === 'debt' ? 'active' : ''}`}
            onClick={() => setActiveTab('debt')}
          >
            ⚠️ Deuda Técnica del Repo ({targetRepo?.metrics.technical_debt_items || 0})
          </button>
          <button
            type="button"
            className={`op-tab-btn ${activeTab === 'sdk' ? 'active' : ''}`}
            onClick={() => setActiveTab('sdk')}
          >
            🔌 SDK / Código de Integración
          </button>
        </div>

        {/* Tab 1: Console / Missions */}
        {activeTab === 'console' && (
          <div className="operations-console-body">
            <div className="preset-mission-buttons">
              <span className="preset-lbl">Misiones Rápidas para el Repo:</span>
              <button
                type="button"
                className="btn-preset-op"
                onClick={handleTriggerEvolve}
                disabled={isProcessing}
              >
                🧬 Generar Refactor Evolutivo del Repo
              </button>
              <button
                type="button"
                className="btn-preset-op"
                onClick={() => handleBoostTask('Prueba de estrés de Causal Trash con patrón infinite_loop')}
                disabled={isProcessing}
              >
                🛡️ Probar Veto de Bucles en O(1)
              </button>
              <button
                type="button"
                className="btn-preset-op"
                onClick={() => handleBoostTask('Auditar módulos con alta deuda técnica y formular invariantes')}
                disabled={isProcessing}
              >
                🔍 Auditar Invariantes del Código
              </button>
            </div>

            <div className="task-input-row">
              <input
                type="text"
                className="station-input task-input"
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                placeholder="Escribe una misión de mejora para tu repositorio (ej: 'Modularizar dependencias circulares en core')..."
                onKeyDown={(e) => e.key === 'Enter' && handleBoostTask()}
              />
              <button
                type="button"
                className="btn-execute-boost"
                onClick={() => handleBoostTask()}
                disabled={isProcessing || !taskInput.trim()}
              >
                {isProcessing ? '⚡ Procesando...' : '🚀 Ejecutar con Agente Potenciado'}
              </button>
            </div>

            {/* Results Viewer */}
            {boostResult && (
              <div className="boost-result-panel animate-fade-in">
                {boostResult.status === 'blocked_by_causal_trash' ? (
                  <div className="result-blocked-box">
                    <div className="blocked-title">
                      <span className="icon">🛡️</span>
                      <h4>{boostResult.power_triggered}</h4>
                    </div>
                    <p className="blocked-desc">{boostResult.warning}</p>
                    <div className="safe-tip">
                      <strong>Recomendación Segura de IDC:</strong> {boostResult.safe_recommendation}
                    </div>
                  </div>
                ) : boostResult.status === 'evolution_generated' ? (
                  <div className="result-evolution-box">
                    <div className="evolution-header">
                      <span className="badge">🧬 EVOLUCIÓN AUTÓNOMA DE CÓDIGO</span>
                      <span className="target-file">Archivo: {boostResult.evolution.target_file}</span>
                    </div>
                    <div className="evolution-field">
                      <strong>Hipótesis Causal:</strong> {boostResult.evolution.hypothesis}
                    </div>
                    <div className="evolution-field">
                      <strong>Acción Propuesta:</strong> {boostResult.evolution.action}
                    </div>
                    <div className="evolution-field">
                      <strong>Impacto Esperado:</strong> <span className="highlight-green">{boostResult.evolution.impact}</span>
                    </div>

                    <div className="code-patch-block">
                      <span className="code-patch-title">Propuesta de Parche de Código:</span>
                      <pre className="patch-pre">{boostResult.evolution.proposed_patch}</pre>
                    </div>
                  </div>
                ) : (
                  <div className="result-success-box">
                    <div className="result-header">
                      <span className="badge-agent">🤖 {boostResult.agent_name} (Potenciado con IDC)</span>
                      <span className="badge-repo">📁 {boostResult.target_repo}</span>
                    </div>

                    <div className="result-response-text">
                      <pre className="clean-pre">{boostResult.response}</pre>
                    </div>

                    {boostResult.causal_rules_applied && boostResult.causal_rules_applied.length > 0 && (
                      <div className="result-applied-rules">
                        <span className="rules-title">Reglas Causales Inyectadas en el Agente:</span>
                        <ul>
                          {boostResult.causal_rules_applied.map((r: any, idx: number) => (
                            <li key={idx}>
                              <strong>SI [{r.cause}]</strong> ➔ [{r.effect}] <em>(Confianza: {(r.confidence * 100).toFixed(0)}%)</em>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Technical Debt Inventory */}
        {activeTab === 'debt' && (
          <div className="operations-debt-body">
            <h4>Inventario de Deuda Técnica en el Repositorio Objetivo</h4>
            <p className="debt-desc">
              Detectado automáticamente mediante escaneo AST y patrones de código en tiempo real:
            </p>

            {targetRepo?.debt_preview && targetRepo.debt_preview.length > 0 ? (
              <div className="debt-table-wrap">
                <table className="station-table">
                  <thead>
                    <tr>
                      <th>Tipo</th>
                      <th>Archivo</th>
                      <th>Línea</th>
                      <th>Detalle del Marcador</th>
                      <th>Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {targetRepo.debt_preview.map((d, idx) => (
                      <tr key={idx}>
                        <td>
                          <span className={`tag-badge tag-${d.tag.toLowerCase()}`}>{d.tag}</span>
                        </td>
                        <td className="font-mono">{d.file}</td>
                        <td className="font-mono">{d.line}</td>
                        <td className="debt-detail">{d.detail}</td>
                        <td>
                          <button
                            type="button"
                            className="btn-table-action"
                            onClick={() => {
                              setActiveTab('console');
                              handleBoostTask(`Resolver ${d.tag} en ${d.file} línea ${d.line}: ${d.detail}`);
                            }}
                          >
                            ⚡ Resolver
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">No se detectaron marcadores de deuda pendientes. ¡Código limpio!</div>
            )}
          </div>
        )}

        {/* Tab 3: Integration SDK */}
        {activeTab === 'sdk' && (
          <div className="operations-sdk-body">
            <div className="sdk-header-row">
              <div>
                <h4>Usa la Estación de Superpoderes desde tu Propio Código</h4>
                <p>Copia este snippet para envolver tu agente (LangChain, CrewAI, AutoGen o llamadas nativas) con IDC:</p>
              </div>
              <div className="sdk-lang-selector">
                <button
                  type="button"
                  className={`lang-btn ${sdkLanguage === 'python' ? 'active' : ''}`}
                  onClick={() => setSdkLanguage('python')}
                >
                  🐍 Python
                </button>
                <button
                  type="button"
                  className={`lang-btn ${sdkLanguage === 'typescript' ? 'active' : ''}`}
                  onClick={() => setSdkLanguage('typescript')}
                >
                  ⚡ TypeScript
                </button>
              </div>
            </div>

            <div className="sdk-code-box">
              <pre className="sdk-pre">
                {sdkLanguage === 'python' ? (
`# 1. Instala el conector IDC
# pip install idc-agent-booster

from idc_booster import IDCAgentBooster

# 2. Envuelve tu agente con los 4 superpoderes de IDC
booster = IDCAgentBooster(
    station_url="${cleanUrl}",
    target_repo_path="${targetRepo?.path || 'C:/tu-proyecto'}",
    superpowers=["causal_trash", "causal_memory", "evolutive_ast"]
)

# 3. Ejecuta tareas sobre tu código con inmunidad ante bucles
resultado = booster.run("Refactorizar arquitectura de endpoints para eliminar deuda técnica")
print("Respuesta Aumentada:", resultado.response)
print("Reglas Aplicadas:", resultado.causal_rules_applied)`
                ) : (
`// 1. Instala el conector IDC
// npm install @idc/agent-booster

import { IDCAgentBooster } from '@idc/agent-booster';

// 2. Conecta tu agente TypeScript / LangChain.js
const booster = new IDCAgentBooster({
  stationUrl: '${cleanUrl}',
  targetRepoPath: '${targetRepo?.path || './src'}',
  superpowers: ['causal_trash', 'causal_memory', 'evolutive_ast']
});

// 3. Ejecuta misiones protegidas con Causal Trash O(1)
const plan = await booster.boost('Optimizar handlers async en el servidor');
console.log('Prompt Aumentado:', plan.augmentedPrompt);`
                )}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
