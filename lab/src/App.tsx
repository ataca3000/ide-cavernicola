import React, { useState, useEffect, useRef, useCallback } from 'react';
import { World } from './engine/world';
import { CavemanAgent } from './engine/agent';
import { Header } from './components/Header';
import { WorldCanvas } from './components/WorldCanvas';
import { CognitiveTerminal } from './components/CognitiveTerminal';
import { CausalGraphPanel } from './components/CausalGraphPanel';
import { CausalTrashPanel } from './components/CausalTrashPanel';
import { GoalController } from './components/GoalController';

export const App: React.FC = () => {
  // Engines instances kept across renders
  const worldRef = useRef<World>(new World());
  const agentRef = useRef<CavemanAgent>(new CavemanAgent());

  // Simulation execution state
  const [isRunning, setIsRunning] = useState<boolean>(true);
  const [speed, setSpeed] = useState<number>(1);
  const [activeTab, setActiveTab] = useState<'sim' | 'translation'>('sim');

  // Trigger UI state re-renders on engine ticks
  const [, setTick] = useState<number>(0);

  const world = worldRef.current;
  const agent = agentRef.current;

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

  const handleToggleAvatar = () => {
    agent.avatar = agent.avatar === 'caveman' ? 'mammoth' : 'caveman';
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
        avatar={agent.avatar}
        onTogglePlay={() => setIsRunning(!isRunning)}
        onStep={performStep}
        onSetSpeed={(s) => setSpeed(s)}
        onReset={handleReset}
        onToggleAvatar={handleToggleAvatar}
        onSpawnWolf={handleSpawnWolf}
        onSpawnFood={handleSpawnFood}
      />

      {/* ── Subheader Navigation Tabs (Matching Image) ────────── */}
      <div className="tab-navigation-bar">
        <button
          className={`tab-nav-btn ${activeTab === 'sim' ? 'active' : ''}`}
          onClick={() => setActiveTab('sim')}
        >
          <span className="tab-icon">🦣</span>
          <span>SIMULACIÓN DEL MAMUT / CAVERNÍCOLA</span>
        </button>

        <button
          className={`tab-nav-btn ${activeTab === 'translation' ? 'active' : ''}`}
          onClick={() => setActiveTab('translation')}
        >
          <span className="tab-icon">📖</span>
          <span>TRADUCCIÓN COGNITIVA IDC</span>
        </button>

        <div className="tab-spacer"></div>
      </div>

      {/* ── Main Cockpit Area (Split Screen) ──────────────────── */}
      <main className="cockpit-container">
        {activeTab === 'sim' ? (
          <div className="cockpit-grid">
            {/* Left Column: Physical World Grid & Goal Controller */}
            <div className="cockpit-col cockpit-left">
              <WorldCanvas
                world={world}
                agentEntity={agentEntity}
                avatar={agent.avatar}
                floatingTexts={agent.floatingTexts}
                onCellClick={(x, y) => {
                  agent.addLog('PERCEPTION', `Inspeccionando coordenadas terrestres (${x}, ${y}).`);
                  setTick((t) => t + 1);
                }}
              />

              <GoalController
                currentGoal={agent.goal.name}
                onSetGoal={(goalStr) => {
                  agent.setGoal(goalStr);
                  setTick((t) => t + 1);
                }}
              />
            </div>

            {/* Right Column: Mental Telemetry & Dual Subpanels */}
            <div className="cockpit-col cockpit-right">
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

      {/* ── Footer Matching Reference Image ──────────────────── */}
      <footer className="idc-footer">
        <span className="footer-left">
          IDC Cavernícola • <em>"Watch a Mammoth Learn to Survive"</em>
        </span>
        <span className="footer-right">
          Creado por <strong className="author-name">Luis Felipe Durán Salinas</strong> (ATACA3000 / Brecha Soluciones DS)
        </span>
      </footer>
    </div>
  );
};
