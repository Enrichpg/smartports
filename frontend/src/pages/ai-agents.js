/**
 * AI Agents Page — Interactive chat with LLM agents
 * Allows users to query specialized port operations agents
 */

export class AIAgentsPage {
  constructor() {
    this.pageId = 'ai-agents';
    this.conversation = [];
    this.currentAgent = 'operations';
    this.isLoading = false;
    this.agents = {};
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Load available agents
    const agentsInfo = await aiAgentClient.getAvailableAgents();
    this.agents = agentsInfo.agents || {};
    console.log('[AIAgentsPage] Available agents:', Object.keys(this.agents));

    container.innerHTML = this._render();
    this._attachEventListeners();
  }

  _render() {
    return `
      <div class="ai-agents-container">
        <div class="ai-agents-header">
          <div class="header-content">
            <h1>🤖 Asistente IA SmartPort</h1>
            <p>Consulta sobre operaciones portuarias, predicciones y alertas</p>
          </div>
        </div>

        <div class="ai-agents-main">
          <div class="chat-area">
            <div class="agent-selector">
              <label>Selecciona un agente especializado:</label>
              <div class="agent-buttons">
                ${this._renderAgentButtons()}
              </div>
            </div>

            <div class="chat-messages" id="chatMessages">
              <div class="message message-system">
                <div class="message-content">
                  <p><strong>Bienvenido al Asistente IA SmartPort</strong></p>
                  <p>Puedes hacer preguntas sobre:</p>
                  <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>✅ Disponibilidad de atraques y ocupación</li>
                    <li>📊 Predicciones de ocupación</li>
                    <li>🚨 Alertas y mantenimiento</li>
                    <li>⚖️ Normativa y seguridad</li>
                    <li>🔔 Gestión de incidentes</li>
                  </ul>
                  <p style="margin-top: 10px; font-size: 0.9em; color: #666;">Escribe tu pregunta abajo y presiona Enter o haz click en Enviar</p>
                </div>
              </div>
            </div>

            <div class="chat-input-area">
              <textarea 
                id="messageInput" 
                class="message-input" 
                placeholder="Escribe tu pregunta... (ej: ¿Cuántos atraques libres hay en Vigo?)"
                rows="3"
              ></textarea>
              <div class="input-buttons">
                <button id="sendBtn" class="btn btn-primary">📤 Enviar</button>
                <button id="clearBtn" class="btn btn-secondary">🗑️ Limpiar</button>
              </div>
            </div>

            <div class="agent-info">
              <div id="agentStatus" class="status-box">
                <p><strong>Agente Activo:</strong> <span id="activeAgentName">Operaciones</span></p>
                <p><strong>Herramientas Disponibles:</strong> <span id="toolsCount">8+</span></p>
              </div>
            </div>
          </div>

          <div class="agents-sidebar">
            <h3>📚 Agentes Disponibles</h3>
            <div id="agentsList" class="agents-list">
              ${this._renderAgentsList()}
            </div>

            <hr style="margin: 20px 0;">

            <h3>💡 Ejemplos</h3>
            <div class="examples-list" id="examplesList">
              ${this._renderExamples()}
            </div>

            <hr style="margin: 20px 0;">

            <div class="quick-actions">
              <h3>⚡ Acciones Rápidas</h3>
              <button class="quick-action-btn" id="occupancyBtn">📊 Ocupación</button>
              <button class="quick-action-btn" id="alertsBtn">🚨 Alertas</button>
              <button class="quick-action-btn" id="forecastBtn">📈 Predicción</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  _renderAgentButtons() {
    const agents = {
      operations: { icon: '🏢', label: 'Operaciones' },
      forecasting: { icon: '📊', label: 'Predicciones' },
      maintenance: { icon: '🔧', label: 'Mantenimiento' },
      compliance: { icon: '⚖️', label: 'Cumplimiento' },
      incident: { icon: '🚨', label: 'Incidentes' },
    };

    return Object.entries(agents)
      .map(([key, { icon, label }]) => `
        <button 
          class="agent-btn ${key === this.currentAgent ? 'active' : ''}" 
          data-agent="${key}"
        >
          ${icon} ${label}
        </button>
      `)
      .join('');
  }

  _renderAgentsList() {
    return Object.entries(this.agents)
      .map(([role, info]) => `
        <div class="agent-item">
          <div class="agent-header">${info.name || role}</div>
          <p class="agent-desc">${info.description || 'Sin descripción'}</p>
          <div class="agent-tools">Herramientas: ${info.tools?.length || 0}</div>
        </div>
      `)
      .join('');
  }

  _renderExamples() {
    const examples = {
      operations: [
        '¿Cuántos atraques libres hay?',
        '¿Cuál es la ocupación actual?',
        '¿Qué buques están atracados?',
      ],
      forecasting: [
        '¿Ocupación en 48 horas?',
        'Tendencia próxima semana',
        '¿Riesgo de congestión?',
      ],
      maintenance: [
        '¿Alertas de mantenimiento?',
        '¿Próximo mantenimiento?',
      ],
      compliance: [
        '¿Requisitos de seguridad?',
        '¿Estado documentación?',
      ],
      incident: [
        'Resumen de alertas',
        '¿Incidentes activos?',
      ],
    };

    const currentExamples = examples[this.currentAgent] || examples.operations;

    return currentExamples
      .map((example) => `
        <button class="example-btn" data-example="${example}">
          ${example}
        </button>
      `)
      .join('');
  }

  _attachEventListeners() {
    // Send button
    document.getElementById('sendBtn')?.addEventListener('click', () => this._sendMessage());

    // Clear button
    document.getElementById('clearBtn')?.addEventListener('click', () => this._clearChat());

    // Message input
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
      messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this._sendMessage();
        }
      });
    }

    // Agent buttons
    document.querySelectorAll('.agent-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.agent-btn').forEach((b) => b.classList.remove('active'));
        e.target.classList.add('active');
        this.currentAgent = e.target.dataset.agent;
        this._updateAgentInfo();
        this._updateExamples();
      });
    });

    // Example buttons
    this._attachExampleListeners();

    // Quick actions
    document.getElementById('occupancyBtn')?.addEventListener('click', () => {
      document.getElementById('messageInput').value = '¿Cuál es la ocupación actual de todos los puertos?';
      this._sendMessage();
    });

    document.getElementById('alertsBtn')?.addEventListener('click', () => {
      this.currentAgent = 'incident';
      document.querySelector('[data-agent="incident"]').click();
      document.getElementById('messageInput').value = '¿Cuáles son las alertas críticas activas?';
      this._sendMessage();
    });

    document.getElementById('forecastBtn')?.addEventListener('click', () => {
      this.currentAgent = 'forecasting';
      document.querySelector('[data-agent="forecasting"]').click();
      document.getElementById('messageInput').value = '¿Cuál será la ocupación en las próximas 48 horas?';
      this._sendMessage();
    });
  }

  _attachExampleListeners() {
    document.querySelectorAll('.example-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const example = e.target.dataset.example;
        document.getElementById('messageInput').value = example;
        this._sendMessage();
      });
    });
  }

  async _sendMessage() {
    if (this.isLoading) return;

    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    this.conversation.push({ role: 'user', content: message });
    input.value = '';
    this._addMessageToUI('user', message);

    this.isLoading = true;
    this._showLoadingIndicator();

    try {
      const response = await aiAgentClient.queryAgent(message, this.currentAgent);
      this.conversation.push({ role: 'assistant', content: response.content });
      this._addMessageToUI('assistant', response.content, response.offline);
    } catch (error) {
      console.error('Error:', error);
      this._addMessageToUI('assistant', 'Error: No se pudo procesar tu pregunta.', true);
    } finally {
      this.isLoading = false;
      this._removeLoadingIndicator();
    }
  }

  _addMessageToUI(role, content, offline = false) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageEl = document.createElement('div');
    messageEl.className = `message message-${role}`;
    if (offline) messageEl.classList.add('offline');

    const contentEl = document.createElement('div');
    contentEl.className = 'message-content';
    contentEl.innerHTML = `<p>${content.replace(/\n/g, '<br>')}</p>`;

    messageEl.appendChild(contentEl);
    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  _showLoadingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const loadingEl = document.createElement('div');
    loadingEl.id = 'loadingIndicator';
    loadingEl.className = 'message message-system';
    loadingEl.innerHTML = `
      <div class="message-content">
        <div class="typing-animation">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
    chatMessages.appendChild(loadingEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  _removeLoadingIndicator() {
    document.getElementById('loadingIndicator')?.remove();
  }

  _updateAgentInfo() {
    const agentName = document.getElementById('activeAgentName');
    if (agentName && this.agents[this.currentAgent]) {
      agentName.textContent = this.agents[this.currentAgent].name || this.currentAgent;
    }
  }

  _updateExamples() {
    const examplesList = document.getElementById('examplesList');
    if (examplesList) {
      examplesList.innerHTML = this._renderExamples();
      this._attachExampleListeners();
    }
  }

  _clearChat() {
    this.conversation = [];
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
      chatMessages.innerHTML = `
        <div class="message message-system">
          <div class="message-content">
            <p><strong>Chat limpiado</strong></p>
            <p>Puedes comenzar una nueva conversación.</p>
          </div>
        </div>
      `;
    }
  }

  unmount() {
    console.log('[AIAgentsPage] Unmounting...');
  }
}
