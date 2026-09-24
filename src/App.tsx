import React, { useState, useEffect, useRef, useCallback } from 'react';
import { World } from './engine/world';
import { CavemanAgent } from './engine/agent';
import { Header } from './components/Header';
import { WorldCanvas } from './components/WorldCanvas';
import { CognitiveTerminal } from './components/CognitiveTerminal';
import { CausalGraphPanel } from './components/CausalGraphPanel';
import { CausalTrashPanel } from './components/CausalTrashPanel';
import { GoalController } from './components/GoalController';
import { ConnectionModal } from './components/ConnectionModal';
import { MissionHub } from './components/MissionHub';
import { RealResultsViewer } from './components/RealResultsViewer';
import { CognitiveChatBar } from './components/CognitiveChatBar';
import { AgentBoosterStation } from './components/AgentBoosterStation';
import { CyberphysicalColmenaPanel } from './components/CyberphysicalColmenaPanel';

export const App: React.FC = () => {
  // Engines instances kept across renders
  const worldRef = useRef<World>(new World());
  const agentRef = useRef<CavemanAgent>(new CavemanAgent());

  // Simulation execution state
  const [isRunning, setIsRunning] = useState<boolean>(true);
  const [speed, setSpeed] = useState<number>(1);
  const [activeTab, setActiveTab] = useState<'sim' | 'booster' | 'cyberphysical' | 'translation'>('sim');

  // Server & API Configuration State
  const [serverUrl, setServerUrl] = useState<string>(() => {
    const saved = localStorage.getItem('idc_server_url');
    if (saved) return saved;
    if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;
    if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      return '';
    }
    return 'http://127.0.0.1:8000';
  });
  const [geminiKey, setGeminiKey] = useState<string>('');
  const [serverStatus, setServerStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [serverDetails, setServerDetails] = useState<any>(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  // Mission Execution & Real Results State
  const [isRunningMission, setIsRunningMission] = useState<boolean>(false);
  const [activeMissionResult, setActiveMissionResult] = useState<any>(null);

  // Trigger UI state re-renders on engine ticks
  const [, setTick] = useState<number>(0);

  const world = worldRef.current;
  const agent = agentRef.current;

  // Check connection to local Python server
  const checkServerConnection = useCallback(async (customUrl?: string) => {
    const targetUrl = (customUrl || serverUrl).replace(/\/$/, '');
    setServerStatus('checking');
    try {
      const res = await fetch(`${targetUrl}/api/status`, { method: 'GET' });
      if (res.ok) {
        const data = await res.json();
        setServerStatus('online');
        setServerDetails(data);
        agent.addLog(
          'LEARNING',
          `Conexión establecida con el Servidor Local IDC (${targetUrl}). Base de datos SQLite idc.db activa.`,
          true
        );
      } else {
        setServerStatus('offline');
      }
    } catch {
      setServerStatus('offline');
    }
  }, [serverUrl, agent]);

  // Initial connection check on mount
  useEffect(() => {
    checkServerConnection();
  }, [checkServerConnection]);

  const performStep = useCallback(() => {
    agent.step(world);
    setTick((t) => t + 1);
  }, [agent, world]);

  // Main game tick loop
  useEffect(() => {
    if (!isRunning) return;

    // Base interval is 1200ms at 1x, faster with higher speeds
    const intervalTime = Math.max(200, Math.floor(1200 / speed));
    const timer = setInterval(() => {
      performStep();
    }, intervalTime);

    return () => clearInterval(timer);
  }, [isRunning, speed, performStep]);

  const handleReset = () => {
    world.reset();
    agent.reset();
    setTick((t) => t + 1);
  };

  const handleSpawnWolf = () => {
    world.spawnPredator();
    agent.addLog('PERCEPTION', '¡Un nuevo lobo acechador ha aparecido en el glaciar!', true);
    setTick((t) => t + 1);
  };

  const handleSpawnFood = () => {
    world.spawnFood();
    agent.addLog('PERCEPTION', '¡Una fuente de bayas/carne ha caído en el terreno!', true);
    setTick((t) => t + 1);
  };

  // Execute real mission via local IDC Server
  const handleExecuteMission = async (
    type: 'scan' | 'memory' | 'causal_stress' | 'custom',
    prompt?: string
  ) => {
    if (serverStatus !== 'online') {
      // Offline fallback: simulate in browser
      agent.addLog('PERCEPTION', `[MODO STANDALONE] Servidor local desconectado. Ejecutando misión simulada: ${type}`);
      agent.setGoal(prompt || `Misión Autónoma: ${type}`);
      agent.addFloatingText(world.getAgent().x, world.getAgent().y, 'Misión Local', '#38bdf8');
      setTick((t) => t + 1);
      return;
    }

    setIsRunningMission(true);
    const targetUrl = serverUrl.replace(/\/$/, '');

    const missionTitles: Record<string, string> = {
      scan: 'Escaneo AST de Repositorio & Deuda Técnica',
      memory: 'Auditoría de Memoria Ciberfísica SQLite',
      causal_stress: 'Prueba de Estrés Causal Trash O(1)',
      custom: prompt || 'Misión Personalizada',
    };

    const missionTitle = missionTitles[type] || type;

    // Visual synchronization in the 2D world
    agent.setGoal(`[MISIÓN REAL] ${missionTitle}`);
    agent.addLog('ACTION', `>>> INICIANDO MISIÓN REAL EN SERVIDOR IDC: "${missionTitle}" <<<`, true);
    const agentEntity = world.getAgent();
    agent.addFloatingText(agentEntity.x, agentEntity.y, 'Ejecutando IDC...', '#f59e0b');
    setTick((t) => t + 1);

    try {
      const response = await fetch(`${targetUrl}/api/mission`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, prompt }),
      });

      if (!response.ok) {
        throw new Error(`Error en el servidor: HTTP ${response.status}`);
      }

      const result = await response.json();

      // Mission completed successfully
      agent.addFloatingText(agentEntity.x, agentEntity.y, '¡Misión Completada!', '#10b981');
      agent.addLog(
        'LEARNING',
        `MISIÓN REAL COMPLETADA: ${result.summary}`,
        true
      );

      // Refresh server metrics
      checkServerConnection();

      // Open real results modal
      setActiveMissionResult(result);
    } catch (err: any) {
      agent.addLog('TRAUMA', `Error al ejecutar la misión real: ${err.message}`, true);
      agent.addFloatingText(agentEntity.x, agentEntity.y, 'Fallo de Red', '#ef4444');
    } finally {
      setIsRunningMission(false);
      setTick((t) => t + 1);
    }
  };

  const handleSaveConfig = async (newUrl: string, newKey: string, newMode: string) => {
    const cleanUrl = newUrl.replace(/\/$/, '');
    setServerUrl(cleanUrl);
    localStorage.setItem('idc_server_url', cleanUrl);
    setGeminiKey(newKey);
    const targetUrl = cleanUrl;

    try {
      await fetch(`${targetUrl}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gemini_api_key: newKey, mode: newMode }),
      });
      checkServerConnection(targetUrl);
    } catch {
      // Ignored if offline
    }
  };

  const agentState = agent.getState();
  const agentEntity = world.getAgent();

  return (
    <div className="idc-lab-app">
      {/* ── Top Header ────────────────────────────────────────── */}
      <Header
        energy={agentState.energy}
        hp={agentState.hp}
        mode={agentState.mode}
        isRunning={isRunning}
        speed={speed}
        dayCycle={world.dayCycle}
        stepCount={agent.stepCount}
        curiosityIndex={agentState.curiosityIndex}
        onTogglePlay={() => setIsRunning(!isRunning)}
        onStep={performStep}
        onSetSpeed={(s) => setSpeed(s)}
        onReset={handleReset}
        onSpawnWolf={handleSpawnWolf}
        onSpawnFood={handleSpawnFood}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* ── Subheader Navigation Tabs (Matching Image) ────────── */}
      <div className="tab-navigation-bar">
        <button
          className={`tab-nav-btn ${activeTab === 'sim' ? 'active' : ''}`}
          onClick={() => setActiveTab('sim')}
        >
          <span className="tab-icon">🧔</span>
          <span>SIMULACIÓN DEL CAVERNÍCOLA IDC</span>
        </button>

        <button
          className={`tab-nav-btn ${activeTab === 'booster' ? 'active' : ''}`}
          onClick={() => setActiveTab('booster')}
        >
          <span className="tab-icon">⚡</span>
          <span>ESTACIÓN DE SUPERPODERES (BYOA)</span>
        </button>

        <button
          className={`tab-nav-btn ${activeTab === 'cyberphysical' ? 'active' : ''}`}
          onClick={() => setActiveTab('cyberphysical')}
        >
          <span className="tab-icon">🔌</span>
          <span>CIBERFÍSICO & COLMENA B3B</span>
        </button>

        <button
          className={`tab-nav-btn ${activeTab === 'translation' ? 'active' : ''}`}
          onClick={() => setActiveTab('translation')}
        >
          <span className="tab-icon">📖</span>
          <span>TRADUCCIÓN COGNITIVA IDC</span>
        </button>

        <div className="tab-spacer"></div>

        <button
          className="tab-settings-quick"
          onClick={() => setIsSettingsOpen(true)}
          title="Configurar conexión del Agente / API Key"
        >
          ⚙️ Servidor: <strong style={{ color: serverStatus === 'online' ? '#10b981' : '#ef4444' }}>
            {serverStatus === 'online' ? 'Online' : 'Offline'}
          </strong>
        </button>
      </div>

      {/* ── Main Cockpit Area (Split Screen) ──────────────────── */}
      <main className="cockpit-container">
        {activeTab === 'sim' ? (
          <div className="cockpit-grid">
            {/* Left Column: Physical World Grid, Mission Hub & Goal Controller */}
            <div className="cockpit-col cockpit-left">
              <WorldCanvas
                world={world}
                agentEntity={agentEntity}
                floatingTexts={agent.floatingTexts}
                onCellClick={(x, y) => {
                  agent.addLog('PERCEPTION', `Inspeccionando coordenadas terrestres (${x}, ${y}).`);
                  setTick((t) => t + 1);
                }}
              />

              <MissionHub
                serverStatus={serverStatus}
                isRunningMission={isRunningMission}
                onExecuteMission={handleExecuteMission}
                onOpenSettings={() => setIsSettingsOpen(true)}
              />

              <GoalController
                currentGoal={agent.goal.name}
                onSetGoal={(goalStr) => {
                  agent.setGoal(goalStr);
                  setTick((t) => t + 1);
                }}
              />
            </div>

            {/* Right Column: Conversational Agent Chat, Mental Telemetry & Dual Subpanels */}
            <div className="cockpit-col cockpit-right">
              <CognitiveChatBar
                serverUrl={serverUrl}
                serverStatus={serverStatus}
                geminiKey={geminiKey}
                onLaunchMission={(prompt) => handleExecuteMission('custom', prompt)}
                onOpenSettings={() => setIsSettingsOpen(true)}
              />

              <CognitiveTerminal
                logs={agent.logs}
                currentGoal={agent.goal.name}
                stepCount={agent.stepCount}
              />

              <div className="dual-subpanels-row">
                <CausalGraphPanel rules={agent.causal.getAllRules()} />
                <CausalTrashPanel trashItems={agent.trash.getAll()} />
              </div>
            </div>
          </div>
        ) : activeTab === 'booster' ? (
          <AgentBoosterStation
            serverUrl={serverUrl}
            serverStatus={serverStatus}
            onExecuteInWorld={(title) => {
              agent.setGoal(`[SUPERPODER] ${title}`);
              agent.addLog('ACTION', `Inyectando superpoder cognitivo al agente huésped: ${title}`, true);
              const ag = world.getAgent();
              agent.addFloatingText(ag.x, ag.y, 'Superpoder IDC ⚡', '#38bdf8');
              setTick((t) => t + 1);
            }}
          />
        ) : activeTab === 'cyberphysical' ? (
          <CyberphysicalColmenaPanel
            serverUrl={serverUrl}
            serverStatus={serverStatus}
            onInjectActionInWorld={(actionTitle) => {
              agent.setGoal(`[HARDWARE] ${actionTitle}`);
              agent.addLog('ACTION', `Interacción ciberfísica enviada: ${actionTitle}`, true);
              const ag = world.getAgent();
              agent.addFloatingText(ag.x, ag.y, 'Ciberfísico 🔌', '#10b981');
              setTick((t) => t + 1);
            }}
          />
        ) : (
          /* Translation / Architectural View */
          <div className="translation-view-card">
            <h2>Mapeo de Capas Cognitivas de IDC en el Laboratorio</h2>
            <div className="translation-grid">
              <div className="trans-card">
                <h3>Tipo 1: Memoria Episódica</h3>
                <p>
                  Registra cada evento <code>(Lobo, Alimento, Fuego)</code>, la acción ejecutada y el resultado binario de supervivencia.
                </p>
                <div className="metric-preview">Registros actuales: {agent.memories.count()}</div>
              </div>

              <div className="trans-card">
                <h3>Tipo 2: Filtro de Propósito</h3>
                <p>
                  Determina si el agente prioriza supervivencia o curiosidad según su nivel metabólico (Energía y Salud).
                </p>
                <div className="metric-preview">Modo activo: {agent.mode}</div>
              </div>

              <div className="trans-card">
                <h3>Tipo 3: Simulación Causal</h3>
                <p>
                  Proyecta las consecuencias antes de actuar: si una regla causal indica que huir tiene alta confianza, no gasta energía en experimentar.
                </p>
                <div className="metric-preview">Reglas activas: {agent.causal.getAllRules().length}</div>
              </div>

              <div className="trans-card">
                <h3>Tipo 4: Curiosidad Dirigida</h3>
                <p>
                  Genera hipótesis exploratorias de baja entropía sin costo de tokens, ampliando el repertorio de supervivencia del agente.
                </p>
                <div className="metric-preview">Índice IC: {agentState.curiosityIndex}</div>
              </div>

              <div className="trans-card">
                <h3>Tipo 5: Causal Trash &amp; Cicatrices</h3>
                <p>
                  Poda en $O(1)$ las ramas de acción que produjeron colapsos de salud previos, evitando que el agente caiga en bucles autodestructivos.
                </p>
                <div className="metric-preview">Acciones vetadas: {agent.trash.count()}</div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ── Modals ───────────────────────────────────────────── */}
      <ConnectionModal
        isOpen={isSettingsOpen}
        serverUrl={serverUrl}
        geminiKey={geminiKey}
        serverStatus={serverStatus}
        serverDetails={serverDetails}
        onClose={() => setIsSettingsOpen(false)}
        onSave={handleSaveConfig}
        onTestConnection={() => checkServerConnection()}
      />

      <RealResultsViewer
        result={activeMissionResult}
        onClose={() => setActiveMissionResult(null)}
      />

      {/* ── Footer Matching Reference Image ──────────────────── */}
      <footer className="idc-footer">
        <span className="footer-left">
          IDC Cavernícola • <em>"Cognición Causal y Evolución de Código"</em>
        </span>
        <span className="footer-right">
          Creado por <strong className="author-name">Luis Felipe Durán Salinas</strong> (ATACA3000 / Brecha Soluciones DS)
        </span>
      </footer>
    </div>
  );
};
