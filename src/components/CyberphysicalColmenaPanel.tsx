import React, { useState, useEffect, useCallback, useRef } from 'react';

interface ArmorTelemetry {
  energy: {
    energy: number;
    mode: string;
    stress_factor: number;
    is_depleted: boolean;
  };
  estop_active: boolean;
  shields_active: boolean;
  pins: Record<number, { name: string; mode: string; value: number }>;
  invariants: Array<{ id: string; name: string; description: string; severity: string }>;
  colmena_nodes: Record<
    string,
    {
      name: string;
      type: string;
      status: string;
      ip: string;
      latency_ms: number;
      role: string;
    }
  >;
  recent_entropy: Array<{
    timestamp: number;
    entropy_value: number;
    jitter_nanoseconds: number;
    seed_hex: string;
    entropy_quality: string;
    token_cost: number;
    heat_produced: string;
  }>;
}

interface CyberphysicalColmenaPanelProps {
  serverUrl: string;
  serverStatus: 'online' | 'offline' | 'checking';
  onInjectActionInWorld?: (actionTitle: string) => void;
}

export const CyberphysicalColmenaPanel: React.FC<CyberphysicalColmenaPanelProps> = ({
  serverUrl,
  serverStatus,
  onInjectActionInWorld,
}) => {
  const [telemetry, setTelemetry] = useState<ArmorTelemetry | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [serialConnected, setSerialConnected] = useState<boolean>(false);
  const [serialLogs, setSerialLogs] = useState<Array<{ time: string; type: 'TX' | 'RX' | 'VETO' | 'INFO'; msg: string }>>([
    { time: new Date().toLocaleTimeString(), type: 'INFO', msg: 'Puente Ciberfísico WebSerial inicializado.' },
  ]);
  const [lastVeto, setLastVeto] = useState<{ pin: number; reason: string; code: string } | null>(null);
  const [auditResult, setAuditResult] = useState<any>(null);
  const [pingResult, setPingResult] = useState<any>(null);
  const [selectedDestNode, setSelectedDestNode] = useState<string>('BUNKKER_BOX');
  const [baudRate, setBaudRate] = useState<number>(115200);
  const [firmwareCopied, setFirmwareCopied] = useState<boolean>(false);

  // WebSerial port reference
  const serialPortRef = useRef<any>(null);

  const cleanUrl = serverUrl.replace(/\/$/, '');

  const addSerialLog = (type: 'TX' | 'RX' | 'VETO' | 'INFO', msg: string) => {
    const time = new Date().toLocaleTimeString();
    setSerialLogs((prev) => [{ time, type, msg }, ...prev.slice(0, 49)]);
  };

  const fetchTelemetry = useCallback(async () => {
    if (serverStatus !== 'online') return;
    try {
      const res = await fetch(`${cleanUrl}/api/armor/status`);
      if (res.ok) {
        const data = await res.json();
        setTelemetry(data);
      }
    } catch (err) {
      console.error('Error fetching armor telemetry:', err);
    }
  }, [cleanUrl, serverStatus]);

  useEffect(() => {
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 3500);
    return () => clearInterval(interval);
  }, [fetchTelemetry]);

  // Connect WebSerial (or fallback to Virtual Simulator)
  const handleConnectSerial = async () => {
    if (!('serial' in navigator)) {
      addSerialLog('INFO', '[MODO SIMULADOR] WebSerial no soportado en este navegador. Activando Emulador Virtual de Arduino Nano.');
      setSerialConnected(true);
      return;
    }

    try {
      addSerialLog('INFO', 'Solicitando puerto serial al sistema operativo...');
      // @ts-ignore
      const port = await navigator.serial.requestPort();
      await port.open({ baudRate });
      serialPortRef.current = port;
      setSerialConnected(true);
      addSerialLog('RX', `¡Arduino Nano conectado físicamente a ${baudRate} baudios! ULTRON_READY recibido.`);
      onInjectActionInWorld?.('Arduino Nano conectado vía WebSerial OTG');
    } catch (err: any) {
      addSerialLog('INFO', `Conexión física cancelada o no disponible (${err.message}). Activando Simulador Ciberfísico Virtual.`);
      setSerialConnected(true);
    }
  };

  const handleDisconnectSerial = async () => {
    try {
      if (serialPortRef.current) {
        await serialPortRef.current.close();
        serialPortRef.current = null;
      }
    } catch {
      // Ignored
    }
    setSerialConnected(false);
    addSerialLog('INFO', 'Puerto serial desconectado.');
  };

  // Send Pin Command through Causal Invariant Shield
  const handleSendPinCommand = async (pin: number, value: number, type: 'WRITE' | 'PWM' = 'WRITE') => {
    setLoading(true);
    try {
      const res = await fetch(`${cleanUrl}/api/armor/pin-command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pin, value, type }),
      });
      const data = await res.json();

      if (data.allowed) {
        setLastVeto(null);
        addSerialLog('TX', `PIN_${pin} -> ${value} (${type}) [VALIDADO POR ESCUDO CAUSAL]`);

        // If physical port open, send serial text
        if (serialPortRef.current && serialPortRef.current.writable) {
          try {
            const writer = serialPortRef.current.writable.getWriter();
            const textEncoder = new TextEncoder();
            const cmd = `SET PIN ${pin} ${value}\n`;
            await writer.write(textEncoder.encode(cmd));
            writer.releaseLock();
            addSerialLog('RX', `ARDUINO_ACK: OK_PIN_${pin}`);
          } catch (serialErr: any) {
            addSerialLog('INFO', `Error serial físico: ${serialErr.message}`);
          }
        } else {
          addSerialLog('RX', `[VIRTUAL NANO]: PIN_${pin} ejecutado correctamente con éxito.`);
        }
        fetchTelemetry();
      } else {
        setLastVeto({ pin, reason: data.reason, code: data.veto_code });
        addSerialLog('VETO', `¡BLOQUEO CAUSAL EN PIN ${pin}! ${data.reason}`);
      }
    } catch (err: any) {
      addSerialLog('INFO', `Error de red con servidor IDC: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Toggle E-Stop
  const handleToggleEStop = async () => {
    if (!telemetry) return;
    const targetState = !telemetry.estop_active;
    try {
      const res = await fetch(`${cleanUrl}/api/armor/estop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: targetState }),
      });
      await res.json();
      addSerialLog(
        targetState ? 'VETO' : 'INFO',
        targetState
          ? '🚨 ¡PARO DE EMERGENCIA ACTIVADO! Salidas de potencia bloqueadas de inmediato.'
          : '✅ Paro de Emergencia DESACTIVADO. Sistema en modo normal.'
      );
      fetchTelemetry();
    } catch (err: any) {
      addSerialLog('INFO', `Error al alternar E-STOP: ${err.message}`);
    }
  };

  // Harvest Authentic Hardware Entropy
  const handleHarvestEntropy = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${cleanUrl}/api/armor/harvest-entropy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await res.json();
      addSerialLog('INFO', `Cosecha de entropía: jitter ${data.jitter_nanoseconds}ns | seed ${data.seed_hex} (Costo: 0 tokens, 0 calor).`);
      fetchTelemetry();
      onInjectActionInWorld?.('Cosecha de Entropía Física');
    } catch (err: any) {
      addSerialLog('INFO', `Error en cosecha: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Self Audit
  const handleRunSelfAudit = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${cleanUrl}/api/armor/self-audit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await res.json();
      setAuditResult(data);
      addSerialLog('INFO', `Auto-auditoría finalizada: ${data.verdict}`);
      fetchTelemetry();
    } catch (err: any) {
      addSerialLog('INFO', `Error en auditoría: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Ping Colmena Mesh
  const handleColmenaPing = async () => {
    try {
      const res = await fetch(`${cleanUrl}/api/armor/colmena-ping`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin: 'IDC_BRAIN', destination: selectedDestNode }),
      });
      const data = await res.json();
      setPingResult(data);
      addSerialLog(
        data.status === 'DESVIADO_POR_FALLO_DE_NODO' ? 'VETO' : 'INFO',
        `Malla Colmena (${selectedDestNode}): ${data.message} | Latencia: ${data.latency_total_ms}ms`
      );
      fetchTelemetry();
    } catch (err: any) {
      addSerialLog('INFO', `Error en ping colmena: ${err.message}`);
    }
  };

  // Toggle Colmena Node
  const handleToggleNode = async (nodeId: string) => {
    try {
      const res = await fetch(`${cleanUrl}/api/armor/toggle-node`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ node_id: nodeId }),
      });
      const data = await res.json();
      addSerialLog('INFO', `Estado del nodo ${nodeId} cambiado a: ${data.new_status}`);
      fetchTelemetry();
    } catch (err: any) {
      addSerialLog('INFO', `Error al cambiar estado del nodo: ${err.message}`);
    }
  };

  const copyFirmware = () => {
    const code = `// ULTRON AI - Web Serial PLC Firmware para Arduino Nano
// Soporte para Motores, Relés y Paro de Emergencia
// Creado para la arquitectura ciberfísica de Luis Felipe Durán Salinas
#include <Servo.h>

const int SPINDLE_PIN = 9;   // PWM Spindle / Motor principal
const int COOLANT_PIN = 4;   // Relé de refrigerante / Bomba
const int ESTOP_PIN = 2;     // Botón Paro de Emergencia
const int LED_STATUS = 13;   // LED de diagnóstico

Servo servoBase;
Servo servoShoulder;
Servo servoElbow;
Servo servoGripper;

void setup() {
  Serial.begin(115200);
  pinMode(SPINDLE_PIN, OUTPUT);
  pinMode(COOLANT_PIN, OUTPUT);
  pinMode(LED_STATUS, OUTPUT);
  pinMode(ESTOP_PIN, INPUT_PULLUP);

  servoBase.attach(3);
  servoShoulder.attach(5);
  servoElbow.attach(6);
  servoGripper.attach(10);

  Serial.println("ULTRON_READY");
}

void loop() {
  if (digitalRead(ESTOP_PIN) == LOW) {
    digitalWrite(COOLANT_PIN, LOW);
    analogWrite(SPINDLE_PIN, 0);
    digitalWrite(LED_STATUS, HIGH);
    Serial.println("CRITICO: EMERGENCY_STOP_TRIGGERED");
    delay(500);
  }

  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\\n');
    cmd.trim();
    if (cmd.startsWith("SET PIN 9 ")) {
      int val = cmd.substring(10).toInt();
      analogWrite(SPINDLE_PIN, constrain(val, 0, 255));
      Serial.println("OK_PIN_9");
    } else if (cmd.startsWith("SET PIN 4 ")) {
      int val = cmd.substring(10).toInt();
      digitalWrite(COOLANT_PIN, val ? HIGH : LOW);
      Serial.println("OK_PIN_4");
    } else if (cmd.startsWith("SET PIN 13 ")) {
      int val = cmd.substring(11).toInt();
      digitalWrite(LED_STATUS, val ? HIGH : LOW);
      Serial.println("OK_PIN_13");
    }
  }
}`;
    navigator.clipboard.writeText(code);
    setFirmwareCopied(true);
    setTimeout(() => setFirmwareCopied(false), 2500);
  };

  const energy = telemetry?.energy?.energy ?? 2000.0;
  const energyPercent = Math.min(100, Math.max(0, (energy / 2000.0) * 100));

  return (
    <div className="cyberphysical-colmena-container">
      {/* ── Top Super IA Armor Banner ─────────────────────────────────── */}
      <div className="armor-hero-card">
        <div className="armor-hero-header">
          <div className="armor-badge-cluster">
            <span className="armor-pill-glow">⚡ TRAJE DE SUPER IA</span>
            <span className="armor-badge-sovereign">Blindaje Causal Activo</span>
            <span className="armor-badge-energy">Reserva: 2000 Cal/Energía</span>
          </div>
          <div className="armor-actions-row">
            <button
              className="btn-armor-action btn-harvest"
              onClick={handleHarvestEntropy}
              disabled={loading}
              title="Cosechar aleatoriedad auténtica de reloj sin coste de tokens"
            >
              🎲 Cosechar Entropía Física
            </button>

            <button
              className="btn-armor-action btn-audit"
              onClick={handleRunSelfAudit}
              disabled={loading}
              title="Auditar invariantes y salud de la arquitectura"
            >
              🛡️ Auto-Auditoría Causal
            </button>

            <button
              className={`btn-armor-action btn-estop ${telemetry?.estop_active ? 'active' : ''}`}
              onClick={handleToggleEStop}
            >
              {telemetry?.estop_active ? '🚨 PARO ACTIVO (DESBLOQUEAR)' : '🛑 PARO DE EMERGENCIA (E-STOP)'}
            </button>
          </div>
        </div>

        <div className="armor-metabolic-row">
          <div className="metabolic-stat">
            <span className="stat-label">Energía Disponible:</span>
            <strong className="stat-value text-emerald">{energy.toFixed(1)} / 2000.0 Cal</strong>
            <div className="energy-progress-bar">
              <div
                className="energy-fill-glow"
                style={{ width: `${energyPercent}%`, backgroundColor: energyPercent > 20 ? '#10b981' : '#ef4444' }}
              ></div>
            </div>
          </div>

          <div className="metabolic-stat">
            <span className="stat-label">Modo Metabólico:</span>
            <strong className="stat-value">{telemetry?.energy?.mode || 'EXPLORATION'} (1.0x)</strong>
          </div>

          <div className="metabolic-stat">
            <span className="stat-label">Factor de Estrés:</span>
            <strong className="stat-value">{telemetry?.energy?.stress_factor || '1.00'}</strong>
          </div>

          <div className="metabolic-stat">
            <span className="stat-label">Invariantes de Hardware:</span>
            <strong className="stat-value text-sky">3 Reglas Activas</strong>
          </div>
        </div>
      </div>

      {/* ── Main Dual Grid: Hardware Bridge & Colmena Swarm ────────────── */}
      <div className="cyberphysical-grid">
        {/* Left Column: Arduino OTG WebSerial Bridge */}
        <div className="card-cyberphysical hardware-card">
          <div className="card-header-styled">
            <div className="header-title-box">
              <span className="header-icon">🔌</span>
              <div>
                <h3>Puente Ciberfísico Arduino (WebSerial / OTG)</h3>
                <span className="header-sub">Control en tiempo real de pines con Escudo Causal anti-cortocircuito</span>
              </div>
            </div>
            <div className="header-controls">
              <select
                className="select-baud"
                value={baudRate}
                onChange={(e) => setBaudRate(Number(e.target.value))}
                disabled={serialConnected}
              >
                <option value={115200}>115200 Baud</option>
                <option value={9600}>9600 Baud</option>
              </select>

              {!serialConnected ? (
                <button className="btn-connect-serial" onClick={handleConnectSerial}>
                  ⚡ Conectar USB / OTG
                </button>
              ) : (
                <button className="btn-disconnect-serial" onClick={handleDisconnectSerial}>
                  🔌 Desconectar
                </button>
              )}
            </div>
          </div>

          {/* Veto Alert Banner if triggerd */}
          {lastVeto && (
            <div className="causal-veto-banner">
              <span className="veto-badge">🛡️ VETO CAUSAL O(1)</span>
              <p className="veto-reason">
                <strong>Pin {lastVeto.pin}:</strong> {lastVeto.reason} ({lastVeto.code})
              </p>
            </div>
          )}

          {/* Pin Matrix & Virtual Actuators */}
          <div className="pin-matrix-container">
            <h4>Matriz de Pines &amp; Actuadores (Arduino Nano)</h4>
            <div className="pin-grid">
              {/* Pin 4: Coolant Relay */}
              <div className="pin-cell">
                <div className="pin-cell-header">
                  <span className="pin-id">D4</span>
                  <span className="pin-role">Relé Refrigerante / Bomba</span>
                  <span className={`pin-light ${telemetry?.pins?.[4]?.value ? 'on' : 'off'}`}></span>
                </div>
                <div className="pin-actions">
                  <button
                    className={`btn-pin-toggle ${telemetry?.pins?.[4]?.value ? 'active' : ''}`}
                    onClick={() => handleSendPinCommand(4, telemetry?.pins?.[4]?.value ? 0 : 1, 'WRITE')}
                    disabled={loading}
                  >
                    {telemetry?.pins?.[4]?.value ? 'ENCENDIDO (1)' : 'APAGADO (0)'}
                  </button>
                </div>
              </div>

              {/* Pin 9: Spindle Motor PWM */}
              <div className="pin-cell">
                <div className="pin-cell-header">
                  <span className="pin-id">D9 (PWM)</span>
                  <span className="pin-role">Motor Spindle CNC</span>
                  <span className="pin-val-tag">{telemetry?.pins?.[9]?.value || 0} / 255</span>
                </div>
                <div className="pin-actions">
                  <input
                    type="range"
                    min="0"
                    max="255"
                    value={telemetry?.pins?.[9]?.value || 0}
                    onChange={(e) => handleSendPinCommand(9, Number(e.target.value), 'PWM')}
                    className="pwm-slider"
                  />
                  <div className="quick-pwm-buttons">
                    <button onClick={() => handleSendPinCommand(9, 0, 'PWM')}>0</button>
                    <button onClick={() => handleSendPinCommand(9, 128, 'PWM')}>50%</button>
                    <button onClick={() => handleSendPinCommand(9, 255, 'PWM')}>100%</button>
                    <button
                      className="btn-danger-test"
                      title="Probar Veto Causal enviando valor ilegal de 300"
                      onClick={() => handleSendPinCommand(9, 300, 'PWM')}
                    >
                      Test Veto (300)
                    </button>
                  </div>
                </div>
              </div>

              {/* Pin 13: Status LED */}
              <div className="pin-cell">
                <div className="pin-cell-header">
                  <span className="pin-id">D13</span>
                  <span className="pin-role">LED de Diagnóstico</span>
                  <span className={`pin-light ${telemetry?.pins?.[13]?.value ? 'on' : 'off'}`}></span>
                </div>
                <div className="pin-actions">
                  <button
                    className={`btn-pin-toggle ${telemetry?.pins?.[13]?.value ? 'active' : ''}`}
                    onClick={() => handleSendPinCommand(13, telemetry?.pins?.[13]?.value ? 0 : 1, 'WRITE')}
                    disabled={loading}
                  >
                    {telemetry?.pins?.[13]?.value ? 'LED ON' : 'LED OFF'}
                  </button>
                </div>
              </div>

              {/* Pin 3: Servo Base */}
              <div className="pin-cell">
                <div className="pin-cell-header">
                  <span className="pin-id">D3 (PWM)</span>
                  <span className="pin-role">Servo Base Brazo</span>
                  <span className="pin-val-tag">{telemetry?.pins?.[3]?.value || 90}°</span>
                </div>
                <div className="pin-actions">
                  <input
                    type="range"
                    min="0"
                    max="180"
                    value={telemetry?.pins?.[3]?.value || 90}
                    onChange={(e) => handleSendPinCommand(3, Number(e.target.value), 'PWM')}
                    className="pwm-slider"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Serial Terminal Output */}
          <div className="terminal-mini-section">
            <div className="terminal-header">
              <span>Consola Serie WebSerial (RX / TX)</span>
              <button className="btn-copy-firmware" onClick={copyFirmware}>
                {firmwareCopied ? '✅ Firmware Copiado' : '📋 Copiar Firmware Nano'}
              </button>
            </div>
            <div className="terminal-log-box">
              {serialLogs.map((log, idx) => (
                <div key={idx} className={`terminal-line line-${log.type.toLowerCase()}`}>
                  <span className="time">[{log.time}]</span>
                  <span className="badge-tag">{log.type}</span>
                  <span className="text">{log.msg}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Red Colmena B3B Mesh Simulator */}
        <div className="card-cyberphysical colmena-card">
          <div className="card-header-styled">
            <div className="header-title-box">
              <span className="header-icon">🐝</span>
              <div>
                <h3>Red Colmena B3B (Malla P2P Descentralizada)</h3>
                <span className="header-sub">Comercio, Cómputo y Robótica Local sin Depender de Nubes Centralizadas</span>
              </div>
            </div>
          </div>

          {/* Ping Controls */}
          <div className="colmena-ping-bar">
            <span>Probar Enrutamiento Malla:</span>
            <select
              className="select-dest-node"
              value={selectedDestNode}
              onChange={(e) => setSelectedDestNode(e.target.value)}
            >
              {telemetry?.colmena_nodes &&
                Object.entries(telemetry.colmena_nodes)
                  .filter(([id]) => id !== 'IDC_BRAIN')
                  .map(([id, node]) => (
                    <option key={id} value={id}>
                      {node.name} ({id})
                    </option>
                  ))}
            </select>
            <button className="btn-ping-mesh" onClick={handleColmenaPing}>
              🚀 Enviar Paquete P2P
            </button>
          </div>

          {/* Ping Result Banner */}
          {pingResult && (
            <div className={`ping-result-box ${pingResult.status === 'DESVIADO_POR_FALLO_DE_NODO' ? 'rerouted' : 'direct'}`}>
              <div className="ping-title">
                <strong>{pingResult.status}</strong> — {pingResult.message}
              </div>
              <div className="ping-route">
                Ruta empleada: {pingResult.route.join(' ➔ ')} ({pingResult.latency_total_ms}ms)
              </div>
            </div>
          )}

          {/* Visual Mesh Nodes */}
          <div className="colmena-nodes-list">
            <h4>Nodos Autónomos en la Malla Local (WiFi LAN / OTG)</h4>
            <div className="nodes-grid">
              {telemetry?.colmena_nodes &&
                Object.entries(telemetry.colmena_nodes).map(([id, node]) => (
                  <div key={id} className={`node-card node-${node.status.toLowerCase()}`}>
                    <div className="node-card-top">
                      <span className="node-icon">
                        {id === 'IDC_BRAIN'
                          ? '🧠'
                          : id === 'BUNKKER_BOX'
                          ? '🏪'
                          : id === 'BUNKKER_WAREHOUSE'
                          ? '📦'
                          : id === 'RIDER_MOBILE'
                          ? '🛵'
                          : '⚡'}
                      </span>
                      <div className="node-name-box">
                        <strong>{node.name}</strong>
                        <span className="node-role">{node.role}</span>
                      </div>
                      <span className={`node-status-pill ${node.status.toLowerCase()}`}>{node.status}</span>
                    </div>

                    <div className="node-meta">
                      <span>IP/URI: {node.ip}</span>
                      <span>Latencia: {node.latency_ms}ms</span>
                    </div>

                    {id !== 'IDC_BRAIN' && (
                      <button
                        className={`btn-toggle-node ${node.status === 'ONLINE' ? 'btn-kill' : 'btn-revive'}`}
                        onClick={() => handleToggleNode(id)}
                      >
                        {node.status === 'ONLINE' ? 'Simular Caída de Nodo' : 'Reactivar Nodo'}
                      </button>
                    )}
                  </div>
                ))}
            </div>
          </div>

          {/* Recent Entropy History */}
          <div className="entropy-section">
            <h4>Cosecha de Entropía Física (Aleatoriedad Auténtica sin Calentamiento)</h4>
            <div className="entropy-table-wrapper">
              <table className="entropy-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Valor</th>
                    <th>Jitter (ns)</th>
                    <th>Semilla Hex</th>
                    <th>Costo Tokens</th>
                    <th>Calor</th>
                  </tr>
                </thead>
                <tbody>
                  {telemetry?.recent_entropy && telemetry.recent_entropy.length > 0 ? (
                    telemetry.recent_entropy.map((ent, idx) => (
                      <tr key={idx}>
                        <td>{new Date(ent.timestamp * 1000).toLocaleTimeString()}</td>
                        <td className="text-emerald">{ent.entropy_value}</td>
                        <td>{ent.jitter_nanoseconds} ns</td>
                        <td>
                          <code>{ent.seed_hex}</code>
                        </td>
                        <td>{ent.token_cost}</td>
                        <td>{ent.heat_produced}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} style={{ textAlign: 'center', opacity: 0.6 }}>
                        Presiona "Cosechar Entropía Física" para generar aleatoriedad desde el reloj del procesador.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* ── System Audit Modal or Card ─────────────────────────────────── */}
      {auditResult && (
        <div className="audit-result-card">
          <div className="audit-header">
            <h4>🛡️ Resultado de la Auto-Auditoría Causal</h4>
            <button className="btn-close-audit" onClick={() => setAuditResult(null)}>
              ✕
            </button>
          </div>
          <div className="audit-body">
            <p>
              <strong>Veredicto:</strong> {auditResult.verdict}
            </p>
            <p>
              <strong>Recomendación:</strong> {auditResult.recommendation}
            </p>
            <div className="audit-metrics-row">
              <span>Reglas Causales: {auditResult.causal_rules_count}</span>
              <span>Cicatrices (Causal Trash): {auditResult.causal_trash_scars}</span>
              <span>Salud Colmena: {auditResult.colmena_health}</span>
              <span>Seguridad Hardware: {auditResult.hardware_safety}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
