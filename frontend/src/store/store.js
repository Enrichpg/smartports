/**
 * Global Application State Store
 * Manages dashboard state, caching, and synchronization
 */

class Store {
  constructor() {
    this.state = {
      // Ports data
      ports: [],
      portDetail: null,
      portsLoading: false,
      portsError: null,

      // Berths data
      berths: [],
      berthsLoading: false,
      berthsError: null,

      // Port Calls data
      portCalls: [],
      portCallsLoading: false,
      portCallsError: null,

      // Alerts
      alerts: [],
      alertsLoading: false,
      alertsError: null,

      // Availability
      availability: null,
      availabilityLoading: false,
      availabilityError: null,

      // Filters
      filters: {
        selectedPort: null,
        selectedFacility: null,
        berthState: null,
        alertSeverity: null,
        portCallState: null,
      },

      // UI State
      ui: {
        currentPage: 'dashboard',
        sidebarOpen: true,
        connectionStatus: 'connecting', // connecting, connected, disconnected
        lastUpdate: null,
        loading: false,
      },

      // Aggregated KPIs
      kpis: {
        totalPorts: 0,
        activePorts: 0,
        totalBerths: 0,
        freeBerths: 0,
        occupiedBerths: 0,
        reservedBerths: 0,
        activeAlerts: 0,
        activePortCalls: 0,
        estimatedOccupancy: 0,
      },
    };

    this.listeners = new Map();
  }

  // ============= GETTERS =============
  getState() {
    return { ...this.state };
  }

  getPorts() {
    return this.state.ports;
  }

  getPort(portId) {
    return this.state.ports.find((p) => p.id === portId || p.id.includes(portId));
  }

  getPortDetail() {
    return this.state.portDetail;
  }

  getBerths() {
    return this.state.berths;
  }

  getAlerts() {
    return this.state.alerts;
  }

  getActiveAlerts() {
    return this.state.alerts.filter((a) => a.status === 'active' || !a.status);
  }

  getPortCalls() {
    return this.state.portCalls;
  }

  getActivePortCalls() {
    return this.state.portCalls.filter(
      (pc) => pc.status === 'active' || pc.status === 'authorized'
    );
  }

  getKPIs() {
    return this.state.kpis;
  }

  getFilters() {
    return this.state.filters;
  }

  getUIState() {
    return this.state.ui;
  }

  getConnectionStatus() {
    return this.state.ui.connectionStatus;
  }

  // ============= SETTERS =============
  setPorts(ports, loading = false, error = null) {
    this.state.ports = ports;
    this.state.portsLoading = loading;
    this.state.portsError = error;
    this.updateKPIs();
    this.emit('portsChanged', { ports, loading, error });
  }

  setPortDetail(port) {
    this.state.portDetail = port;
    this.emit('portDetailChanged', { port });
  }

  setBerths(berths, loading = false, error = null) {
    this.state.berths = berths;
    this.state.berthsLoading = loading;
    this.state.berthsError = error;
    this.updateKPIs();
    this.emit('berthsChanged', { berths, loading, error });
  }

  updateBerth(berthId, berthData) {
    const index = this.state.berths.findIndex((b) => b.id === berthId || b.id.includes(berthId));
    if (index > -1) {
      this.state.berths[index] = { ...this.state.berths[index], ...berthData };
      this.updateKPIs();
      this.emit('berthUpdated', { berthId, data: this.state.berths[index] });
    }
  }

  setPortCalls(portCalls, loading = false, error = null) {
    this.state.portCalls = portCalls;
    this.state.portCallsLoading = loading;
    this.state.portCallsError = error;
    this.updateKPIs();
    this.emit('portCallsChanged', { portCalls, loading, error });
  }

  addPortCall(portCall) {
    this.state.portCalls.push(portCall);
    this.updateKPIs();
    this.emit('portCallCreated', { portCall });
  }

  updatePortCall(portCallId, portCallData) {
    const index = this.state.portCalls.findIndex((pc) => pc.id === portCallId || pc.id.includes(portCallId));
    if (index > -1) {
      this.state.portCalls[index] = {
        ...this.state.portCalls[index],
        ...portCallData,
      };
      this.updateKPIs();
      this.emit('portCallUpdated', { portCallId, data: this.state.portCalls[index] });
    }
  }

  removePortCall(portCallId) {
    this.state.portCalls = this.state.portCalls.filter(
      (pc) => pc.id !== portCallId && !pc.id.includes(portCallId)
    );
    this.updateKPIs();
    this.emit('portCallRemoved', { portCallId });
  }

  setAlerts(alerts, loading = false, error = null) {
    this.state.alerts = alerts;
    this.state.alertsLoading = loading;
    this.state.alertsError = error;
    this.updateKPIs();
    this.emit('alertsChanged', { alerts, loading, error });
  }

  addAlert(alert) {
    this.state.alerts.unshift(alert);
    this.updateKPIs();
    this.emit('alertCreated', { alert });
  }

  setAvailability(availability, loading = false, error = null) {
    this.state.availability = availability;
    this.state.availabilityLoading = loading;
    this.state.availabilityError = error;
    this.emit('availabilityChanged', { availability, loading, error });
  }

  setFilter(filterKey, filterValue) {
    this.state.filters[filterKey] = filterValue;
    this.emit('filtersChanged', { filters: this.state.filters });
  }

  setFilters(filters) {
    this.state.filters = { ...this.state.filters, ...filters };
    this.emit('filtersChanged', { filters: this.state.filters });
  }

  setUIState(uiUpdates) {
    this.state.ui = { ...this.state.ui, ...uiUpdates };
    this.emit('uiStateChanged', { ui: this.state.ui });
  }

  setConnectionStatus(status) {
    this.state.ui.connectionStatus = status;
    this.emit('connectionStatusChanged', { status });
  }

  setLastUpdate() {
    this.state.ui.lastUpdate = new Date();
    this.emit('lastUpdateChanged', { timestamp: this.state.ui.lastUpdate });
  }

  // ============= KPIs CALCULATION =============
  updateKPIs() {
    const berths = this.state.berths;
    const ports = this.state.ports;
    const alerts = this.state.alerts;
    const portCalls = this.state.portCalls;

    this.state.kpis = {
      totalPorts: ports.length,
      activePorts: ports.filter((p) => p.status !== 'inactive').length,
      totalBerths: berths.length,
      freeBerths: berths.filter((b) => b.status === 'free').length,
      occupiedBerths: berths.filter((b) => b.status === 'occupied').length,
      reservedBerths: berths.filter((b) => b.status === 'reserved').length,
      activeAlerts: alerts.filter((a) => a.status !== 'resolved').length,
      activePortCalls: portCalls.filter(
        (pc) => pc.status === 'active' || pc.status === 'authorized'
      ).length,
      estimatedOccupancy:
        berths.length > 0
          ? ((berths.filter((b) => b.status === 'occupied').length +
              berths.filter((b) => b.status === 'reserved').length) /
              berths.length) *
            100
          : 0,
    };

    this.emit('kpisUpdated', { kpis: this.state.kpis });
  }

  // ============= EVENT SYSTEM =============
  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    };
  }

  unsubscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      return;
    }
    const callbacks = this.listeners.get(eventType);
    const index = callbacks.indexOf(callback);
    if (index > -1) {
      callbacks.splice(index, 1);
    }
  }

  emit(eventType, payload) {
    if (!this.listeners.has(eventType)) {
      return;
    }
    this.listeners.get(eventType).forEach((callback) => {
      try {
        callback(payload);
      } catch (error) {
        console.error(`Error in ${eventType} listener:`, error);
      }
    });
  }

  // ============= UTILITIES =============
  clearState() {
    this.state = {
      ports: [],
      portDetail: null,
      berths: [],
      portCalls: [],
      alerts: [],
      availability: null,
      filters: {
        selectedPort: null,
        selectedFacility: null,
        berthState: null,
        alertSeverity: null,
        portCallState: null,
      },
      ui: {
        currentPage: 'dashboard',
        sidebarOpen: true,
        connectionStatus: 'connecting',
        lastUpdate: null,
        loading: false,
      },
      kpis: {
        totalPorts: 0,
        activePorts: 0,
        totalBerths: 0,
        freeBerths: 0,
        occupiedBerths: 0,
        reservedBerths: 0,
        activeAlerts: 0,
        activePortCalls: 0,
        estimatedOccupancy: 0,
      },
    };
    this.emit('stateCleared');
  }
}

// Export singleton instance
export const store = new Store();

export default Store;
