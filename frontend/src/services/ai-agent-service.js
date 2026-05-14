/**
 * AI Agent Client Service
 * API client for SmartPort LLM Agents
 */

class AIAgentClientService {
  constructor(baseURL = '/api/v1') {
    this.baseURL = baseURL;
    this.timeout = 30000;
  }

  async queryAgent(message, agentRole = 'operations', portContext = null) {
    try {
      const response = await fetch(`${this.baseURL}/agents/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          agent_role: agentRole,
          port_context: portContext,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Agent query error:', error);
      return {
        role: 'assistant',
        content: `Error: ${error.message}`,
        offline: true,
        agent_role: agentRole,
      };
    }
  }

  async getAvailableAgents() {
    try {
      const response = await fetch(`${this.baseURL}/agents/roles`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Get agents error:', error);
      return { agents: {}, total_agents: 0 };
    }
  }
}

const aiAgentClient = new AIAgentClientService();
