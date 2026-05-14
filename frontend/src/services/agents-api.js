/**
 * Agents API Service — Client for LLM agents
 * Communicates with /api/v1/agents/* endpoints
 */

class AgentsApiClient {
  constructor(baseUrl = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  async getAvailableRoles() {
    // Get list of available agent roles and their capabilities.
    try {
      const response = await fetch(`${this.baseUrl}/agents/roles`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching agent roles:', error);
      return { agents: {}, total_agents: 0, error: error.message };
    }
  }

  async queryAgent(message, agentRole = 'operations', portContext = null) {
    // Query a specific agent.
    try {
      const payload = {
        message,
        agent_role: agentRole,
        port_context: portContext,
      };

      const response = await fetch(`${this.baseUrl}/agents/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error querying agent:', error);
      return {
        role: 'assistant',
        content: `Error: ${error.message}`,
        offline: true,
      };
    }
  }

  async queryOperationsAgent(message, portContext = null) {
    // Direct query to Operations Agent.
    return this.queryAgent(message, 'operations', portContext);
  }

  async queryForecastingAgent(message, portContext = null) {
    // Direct query to Forecasting Agent.
    return this.queryAgent(message, 'forecasting', portContext);
  }

  async queryMaintenanceAgent(message, portContext = null) {
    // Direct query to Maintenance Agent.
    return this.queryAgent(message, 'maintenance', portContext);
  }

  async queryComplianceAgent(message, portContext = null) {
    // Direct query to Compliance Agent.
    return this.queryAgent(message, 'compliance', portContext);
  }

  async queryIncidentAgent(message, portContext = null) {
    // Direct query to Incident Agent.
    return this.queryAgent(message, 'incident', portContext);
  }
}

export const agentsApiClient = new AgentsApiClient();
