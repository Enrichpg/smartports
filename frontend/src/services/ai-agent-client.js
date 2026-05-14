/**
 * AI Agent Client - Communicates with SmartPort LLM Agents API
 * Handles queries to different specialized agents
 */

class AIAgentClient {
  constructor(baseURL = '/api/v1') {
    this.baseURL = baseURL;
    this.timeout = 30000; // 30 seconds
  }

  /**
   * Send a message to an agent
   * @param {string} message - User message
   * @param {string} agentRole - Agent role (operations, forecasting, maintenance, compliance, incident)
   * @param {object} portContext - Optional context data
   * @returns {Promise<object>} Agent response
   */
  async queryAgent(message, agentRole = 'operations', portContext = null) {
    const payload = {
      message,
      agent_role: agentRole,
      port_context: portContext,
    };

    try {
      const response = await fetch(`${this.baseURL}/agents/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

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

  /**
   * Get available agent roles and their capabilities
   * @returns {Promise<object>} Available agents info
   */
  async getAvailableAgents() {
    try {
      const response = await fetch(`${this.baseURL}/agents/roles`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get agents error:', error);
      return { agents: {}, total_agents: 0 };
    }
  }

  /**
   * Query a specific agent directly
   * @param {string} agentRole - Agent role endpoint
   * @param {string} message - User message
   * @param {object} portContext - Optional context
   * @returns {Promise<object>} Agent response
   */
  async querySpecificAgent(agentRole, message, portContext = null) {
    return this.queryAgent(message, agentRole, portContext);
  }
}

// Export singleton instance
const aiAgentClient = new AIAgentClient();
