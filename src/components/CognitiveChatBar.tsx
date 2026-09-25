import React, { useState, useRef, useEffect } from 'react';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'cavernicola';
  text: string;
  time: string;
  proposal?: {
    title: string;
    type: 'internal_refactor' | 'ecosystem_integration';
    project_to_integrate: string;
    hypothesis: string;
    action: string;
    impact: string;
  };
  missionPrompt?: string;
}

interface CognitiveChatBarProps {
  serverUrl: string;
  serverStatus: 'online' | 'offline' | 'checking';
  geminiKey: string;
  onLaunchMission: (prompt: string) => void;
  onOpenSettings: () => void;
}

export const CognitiveChatBar: React.FC<CognitiveChatBarProps> = ({
  serverUrl,
  serverStatus,
  geminiKey,
  onLaunchMission,
  onOpenSettings,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'cavernicola',
      text: 'Soy Centynel, tu centro de inteligencia operativa. Puedo explicar la arquitectura del repositorio, detectar deuda técnica y recomendar integraciones con trazabilidad.',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [chatMode, setChatMode] = useState<'local_idc' | 'gemini_cloud'>(
    geminiKey ? 'gemini_cloud' : 'local_idc'
  );
  const [isMinimized, setIsMinimized] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const quickPrompts = [
    '¿Qué herramientas o proyectos externos recomiendas conectar con IDC?',
    'Analiza la deuda técnica del repo y propón una mejora',
    'Propón una evolución para el Causal Trash',
    '¿Cómo podemos optimizar el consumo de energía en el ciclo cognitivo?',
  ];

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim();
    if (!text || isSending) return;

    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsSending(true);

    try {
      const res = await fetch(`${serverUrl.replace(/\/$/, '')}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          mode: chatMode,
          gemini_api_key: geminiKey,
        }),
      });

      if (!res.ok) {
        throw new Error(`Error en servidor: HTTP ${res.status}`);
      }

      const data = await res.json();

      const botMsg: ChatMessage = {
        id: `cav_${Date.now()}`,
        sender: 'cavernicola',
        text: data.reply || 'He procesado tu consulta pero no formulé una respuesta textual.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        proposal: data.evolutive_proposal,
        missionPrompt: data.mission_prompt,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: 'cavernicola',
        text: `Gruñido de error: No pude procesar tu petición a través del servidor (${err.message}). Asegúrate de que server.py esté activo.`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className={`cognitive-chat-container ${isMinimized ? 'chat-minimized' : ''}`}>
      {/* ── Chat Header ────────────────────────────────────────── */}
      <div className="chat-header" onClick={() => setIsMinimized(!isMinimized)}>
        <div className="chat-title-group">
          <span className="chat-avatar-icon">🧔</span>
          <div>
            <h5>CENTRO DE CONSULTA CENTYNEL</h5>
            <span className="chat-sub">Mente Artificial &amp; Propuestas Evolutivas de Código</span>
          </div>
        </div>

        <div className="chat-header-actions" onClick={(e) => e.stopPropagation()}>
          <span className={`chat-status-pill ${serverStatus}`} title={`Servidor IDC: ${serverStatus}`}>
            ● {serverStatus === 'online' ? 'Online' : 'Offline'}
          </span>

          <select
            className="chat-mode-select"
            value={chatMode}
            onChange={(e) => setChatMode(e.target.value as any)}
            title="Seleccionar motor de conversación"
          >
            <option value="local_idc">🖥️ Local IDC Core</option>
            <option value="gemini_cloud">🌐 Gemini Nube API</option>
          </select>

          <button
            type="button"
            className="chat-toggle-btn"
            onClick={onOpenSettings}
            title="Configurar conexión del Agente / API Key"
          >
            ⚙️
          </button>

          <button
            type="button"
            className="chat-toggle-btn"
            onClick={() => setIsMinimized(!isMinimized)}
            title={isMinimized ? 'Expandir chat' : 'Minimizar chat'}
          >
            {isMinimized ? '▲ Expandir' : '▼ Minimizar'}
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* ── Chat Messages Thread ───────────────────────────────── */}
          <div className="chat-messages-thread">
            {messages.map((m) => (
              <div key={m.id} className={`chat-bubble-row sender-${m.sender}`}>
                <div className="bubble-avatar">
                  {m.sender === 'cavernicola' ? '🧔' : '🧑‍💻'}
                </div>
                <div className="bubble-content-wrap">
                  <div className="bubble-meta">
                    <span className="bubble-author">
                      {m.sender === 'cavernicola' ? 'Cavernícola IDC' : 'Tú'}
                    </span>
                    <span className="bubble-time">{m.time}</span>
                  </div>

                  <div className="bubble-text">{m.text}</div>

                  {/* ── Evolutive Proposal / External Integration Card ── */}
                  {m.proposal && (
                    <div className={`proposal-card type-${m.proposal.type}`}>
                      <div className="proposal-header">
                        <span className="proposal-badge">
                          {m.proposal.type === 'ecosystem_integration'
                            ? '🌐 INTEGRACIÓN DE ECOSISTEMA'
                            : '🧬 MEJORA EVOLUTIVA INTERNA'}
                        </span>
                        <span className="proposal-project">
                          📦 {m.proposal.project_to_integrate}
                        </span>
                      </div>

                      <div className="proposal-title">{m.proposal.title}</div>

                      <div className="proposal-details">
                        <div className="proposal-field">
                          <span className="field-lbl">Hipótesis Causal:</span>
                          <span className="field-val">{m.proposal.hypothesis}</span>
                        </div>
                        <div className="proposal-field">
                          <span className="field-lbl">Acción Recomendada:</span>
                          <span className="field-val">{m.proposal.action}</span>
                        </div>
                        <div className="proposal-field">
                          <span className="field-lbl">Impacto Esperado:</span>
                          <span className="field-val highlight-green">{m.proposal.impact}</span>
                        </div>
                      </div>

                      {m.missionPrompt && (
                        <div className="proposal-action-row">
                          <button
                            type="button"
                            className="btn-convert-mission"
                            onClick={() => onLaunchMission(m.missionPrompt!)}
                            title="Lanza esta mejora directamente al bucle del agente y el juego"
                          >
                            🚀 Convertir en Misión Real
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isSending && (
              <div className="chat-bubble-row sender-cavernicola">
                <div className="bubble-avatar">🧔</div>
                <div className="bubble-content-wrap">
                  <div className="bubble-typing">
                    <span></span><span></span><span></span>
                    <em>Centynel está analizando la topología del repositorio y sintetizando una respuesta...</em>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* ── Quick Prompt Chips ─────────────────────────────────── */}
          <div className="chat-quick-chips">
            {quickPrompts.map((qp, idx) => (
              <button
                key={idx}
                type="button"
                className="quick-chip-btn"
                onClick={() => handleSend(qp)}
                disabled={isSending}
              >
                {qp}
              </button>
            ))}
          </div>

          {/* ── Chat Input Row ─────────────────────────────────────── */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="chat-input-bar"
          >
            <input
              type="text"
              className="chat-text-input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Consulta a Centynel (ej: '¿Qué riesgos y mejoras recomiendas para este repositorio?')..."
              disabled={isSending}
            />
            <button
              type="submit"
              className="chat-send-btn"
              disabled={isSending || !inputText.trim()}
            >
              Enviar ➔
            </button>
          </form>
        </>
      )}
    </div>
  );
};
