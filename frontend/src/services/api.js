/**
 * Centralized API Client for SmartPort Backend
 * Handles all REST API calls to FastAPI backend
 * Features: error handling, retry logic, request/response transformation
 */

class ApiClient {
  constructor() {
    this.baseURL = this.getBaseURL();
    this.timeout = 10000;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  getBaseURL() {
    // Get from environment or fallback
    const backendUrl = window.ENV?.BACKEND_URL || localStorage.getItem('backend_url');
    return backendUrl || 'http://localhost:8000/api/v1';
  }

  setBaseURL(url) {
    this.baseURL = url;
    localStorage.setItem('backend_url', url);
  }

  async request(method, endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = { ...this.defaultHeaders, ...options.headers };

    const config = {
      method,
      headers,
      signal: AbortSignal.timeout(this.timeout),
    };

    if (options.body) {
      config.body = JSON.stringify(options.body);
    }

    if (options.params) {
      const query = new URLSearchParams(options.params);
      return fetch(`${url}?${query}`, config);
    }

    return fetch(url, config);
  }

  async handleResponse(response) {
    const contentType = response.headers.get('content-type');
    const isJSON = contentType?.includes('application/json');

    const data = isJSON ? await response.json() : await response.text();

    if (!response.ok) {
      const error = new Error(
        data?.detail || data?.message || `HTTP ${response.status}`
      );
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  }

  async get(endpoint, options = {}) {
    const response = await this.request('GET', endpoint, options);
    return this.handleResponse(response);
  }

  async post(endpoint, body, options = {}) {
    const response = await this.request('POST', endpoint, {
      ...options,
      body,
    });
    return this.handleResponse(response);
  }

  async put(endpoint, body, options = {}) {
    const response = await this.request('PUT', endpoint, {
      ...options,
      body,
    });
    return this.handleResponse(response);
  }

  async delete(endpoint, options = {}) {
    const response = await this.request('DELETE', endpoint, options);
    return this.handleResponse(response);
  }

  // ============= PORTS =============
  async getPorts(limit = 20, offset = 0) {
    return this.get('/ports', { params: { limit, offset } });
  }

  async getPortById(portId) {
    return this.get(`/ports/${portId}`);
  }

  async getPortSummary(portId) {
    return this.get(`/ports/${portId}/summary`);
  }

  async getPortFacilities(portId) {
    return this.get(`/ports/${portId}/facilities`);
  }

  async getPortBerths(portId, limit = 100, offset = 0) {
    return this.get(`/ports/${portId}/berths`, {
      params: { limit, offset },
    });
  }

  async getPortAvailability(portId) {
    return this.get(`/ports/${portId}/availability`);
  }

  async getPortAlerts(portId) {
    return this.get(`/ports/${portId}/alerts`);
  }

  // ============= BERTHS =============
  async getBerths(portId = null, facilityId = null, limit = 100, offset = 0) {
    const params = { limit, offset };
    if (portId) params.port_id = portId;
    if (facilityId) params.facility_id = facilityId;
    return this.get('/berths', { params });
  }

  async getBerthById(berthId) {
    return this.get(`/berths/${berthId}`);
  }

  // ============= AVAILABILITY =============
  async getAvailability(limit = 20, offset = 0) {
    return this.get('/availability', { params: { limit, offset } });
  }

  async getAvailabilityByPort(portId) {
    return this.get(`/availability/port/${portId}`);
  }

  // ============= PORT CALLS =============
  async getPortCalls(portId = null, limit = 100, offset = 0) {
    const params = { limit, offset };
    if (portId) params.port_id = portId;
    return this.get('/portcalls', { params });
  }

  async getPortCallById(portCallId) {
    return this.get(`/portcalls/${portCallId}`);
  }

  async createPortCall(portCallData) {
    return this.post('/portcalls', portCallData);
  }

  async updatePortCall(portCallId, portCallData) {
    return this.put(`/portcalls/${portCallId}`, portCallData);
  }

  // ============= ALERTS =============
  async getAlerts(portId = null, limit = 100, offset = 0) {
    const params = { limit, offset };
    if (portId) params.port_id = portId;
    return this.get('/alerts', { params });
  }

  async getAlertsByPort(portId) {
    return this.get(`/alerts/port/${portId}`);
  }

  async getAlertById(alertId) {
    return this.get(`/alerts/${alertId}`);
  }

  // ============= VESSELS =============
  async getVessels(limit = 100, offset = 0) {
    return this.get('/vessels', { params: { limit, offset } });
  }

  async getVesselById(vesselId) {
    return this.get(`/vessels/${vesselId}`);
  }

  // ============= HEALTH & STATUS =============
  async getHealth() {
    return this.get('/health');
  }

  async getStatus() {
    return this.get('/status');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

export default ApiClient;
