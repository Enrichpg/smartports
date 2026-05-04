/**
 * Global Application State Store
 * 
 * Manages:
 * - Ports, berths, vessels, port calls, alerts
 * - Real-time updates from WebSocket
 * - UI state and filters
 * - KPIs and aggregations
 * 
 * Pattern: Observer pattern with state mutation methods
 */

class Store {
  constructor() {
    // Core data
    this.state = {
      // Ports and berths
      ports: {},           // { port_id: { id, name, lat, lon, berths: [...], kpis: {...} } }
      berths: {},          // { berth_id: { id, port_id, name, status, vessel_id, ... } }
      vessels: {},         // { vessel_id: { id, name, imo, type, length_m, ... } }
      portCalls: {},       // { portcall_id: { id, vessel_id, port_id, status, ... } }
      alerts: [],          // [ { id, type, severity, description, entity_id, ... } ]
      
      // Current sensor readings
      sensors: {},         // { sensor_id: { type, value, unit, timestamp } }
      
      // Occupancy tracking
      occupancy: {},       // { port_id: { total, occupied, reserved, free, percentage, trending } }
      
      // Filters and view state
      filters: {
        selectedPort: null,
        selectedBerth: null,
        eventTypes: [],    // ['berth.updated', 'alert.triggered', ...]
      },
      
      // UI state
      ui: {
        currentPage: 'dashboard',
        sidebarOpen: true,
        websocketStatus: 'disconnected',  // 'disconnected' | 'connecting' | 'connected' | 'error'
        websocketError: null,
        lastUpdate: null,
        debugMode: window.ENV?.DEBUG || false,
      },
      
      // Aggregated metrics
      kpis: {
        totalPorts: 0,
        totalBerths: 0,
        occupiedBerths: 0,
        reservedBerths: 0,
        freeBerths: 0,
        occupancyPercentage: 0,
        activeAlerts: 0,
        activePortCalls: 0,
      },
    };
    
    // Change listeners
    this.listeners = new Map();
    
    if (this.state.ui.debugMode) {
      console.log('[Store] Initialized');
    }
  }

  // =========== STATE QUERIES ===========
  getState() {
    return JSON.parse(JSON.stringify(this.state));
  }

  getPort(portId) {
    return this.state.ports[portId];
  }

  getBerth(berthId) {
    return this.state.berths[berthId];
  }

  getVessel(vesselId) {
    return this.state.vessels[vesselId];
  }

  getOccupancy(portId) {
    return this.state.occupancy[portId] || {};
  }

  getKPIs() {
    return { ...this.state.kpis };
  }

  getUIState() {
    return { ...this.state.ui };
  }

  getAlerts() {
    return [...this.state.alerts];
  }

  // =========== STATE UPDATES ===========
  
  /**
   * Update berth state from real-time event
   */
  updateBerth(berthId, updates) {
    if (!this.state.berths[berthId]) {
      this.state.berths[berthId] = { id: berthId, ...updates };
    } else {
      Object.assign(this.state.berths[berthId], updates);
    }
    
    this._recalculateKPIs();
    this._notifyListeners('berth:updated', { berthId, updates });
    
    if (this.state.ui.debugMode) {
      console.log('[Store] Berth updated:', berthId, updates);
    }
  }

  /**
   * Update port occupancy
   */
  updateOccupancy(portId, occupancyData) {
    this.state.occupancy[portId] = {
      ...this.state.occupancy[portId],
      ...occupancyData,
      timestamp: new Date().toISOString(),
    };
    
    this._recalculateKPIs();
    this._notifyListeners('occupancy:updated', { portId, occupancyData });
    
    if (this.state.ui.debugMode) {
      console.log('[Store] Occupancy updated:', portId, occupancyData);
    }
  }

  /**
   * Update or add vessel
   */
  updateVessel(vesselId, vesselData) {
    if (!this.state.vessels[vesselId]) {
      this.state.vessels[vesselId] = { id: vesselId, ...vesselData };
    } else {
      Object.assign(this.state.vessels[vesselId], vesselData);
    }
    
    this._notifyListeners('vessel:updated', { vesselId, vesselData });
  }

  /**
   * Add or update alert
   */
  addAlert(alertData) {
    const alertId = alertData.alert_id || alertData.id;
    
    // Check if already exists
    const existingIdx = this.state.alerts.findIndex(a => a.id === alertId);
    if (existingIdx >= 0) {
      this.state.alerts[existingIdx] = { ...this.state.alerts[existingIdx], ...alertData };
    } else {
      this.state.alerts.push({
        id: alertId,
        timestamp: new Date().toISOString(),
        ...alertData,
      });
    }
    
    this._recalculateKPIs();
    this._notifyListeners('alert:added', alertData);
    
    if (this.state.ui.debugMode) {
      console.log('[Store] Alert added:', alertId, alertData);
    }
  }

  /**
   * Remove alert
   */
  removeAlert(alertId) {
    const idx = this.state.alerts.findIndex(a => a.id === alertId);
    if (idx >= 0) {
      this.state.alerts.splice(idx, 1);
      this._recalculateKPIs();
      this._notifyListeners('alert:removed', { alertId });
    }
  }

  /**
   * Update sensor reading
   */
  updateSensor(sensorId, sensorData) {
    this.state.sensors[sensorId] = {
      ...this.state.sensors[sensorId],
      ...sensorData,
      timestamp: new Date().toISOString(),
    };
    
    this._notifyListeners('sensor:updated', { sensorId, sensorData });
  }

  /**
   * Update UI state
   */
  setUIState(uiUpdates) {
    Object.assign(this.state.ui, uiUpdates);
    this._notifyListeners('ui:updated', uiUpdates);
  }

  /**
   * Set websocket connection status
   */
  setWebsocketStatus(status, error = null) {
    this.state.ui.websocketStatus = status;
    if (error) {
      this.state.ui.websocketError = error;
    }
    this._notifyListeners('websocket:status', { status, error });
    
    if (this.state.ui.debugMode) {
      console.log('[Store] WebSocket status:', status, error);
    }
  }

  /**
   * Update multiple berths (bulk operation for snapshot)
   */
  setBerths(berthMap) {
    this.state.berths = { ...this.state.berths, ...berthMap };
    this._recalculateKPIs();
    this._notifyListeners('berths:bulk', {});
  }

  /**
   * Update multiple ports (bulk operation for snapshot)
   */
  setPorts(portMap) {
    this.state.ports = { ...this.state.ports, ...portMap };
    this._notifyListeners('ports:bulk', {});
  }

  // =========== INTERNAL HELPERS ===========
  
  /**
   * Recalculate KPIs based on current state
   */
  _recalculateKPIs() {
    const berths = Object.values(this.state.berths);
    const occupied = berths.filter(b => b.status === 'occupied').length;
    const reserved = berths.filter(b => b.status === 'reserved').length;
    const free = berths.filter(b => b.status === 'free').length;
    const total = berths.length;
    
    const occupancy = total > 0 ? ((occupied + reserved) / total) * 100 : 0;
    
    this.state.kpis = {
      totalBerths: total,
      occupiedBerths: occupied,
      reservedBerths: reserved,
      freeBerths: free,
      occupancyPercentage: Math.round(occupancy * 10) / 10,
      activeAlerts: this.state.alerts.length,
      totalPorts: Object.keys(this.state.ports).length,
      activePortCalls: Object.values(this.state.portCalls).filter(pc => pc.status === 'active').length,
    };
    
    if (this.state.ui.debugMode) {
      console.log('[Store] KPIs recalculated:', this.state.kpis);
    }
  }

  /**
   * Notify all listeners of a change
   */
  _notifyListeners(changeType, data) {
    if (!this.listeners.has(changeType)) {
      return;
    }
    
    const callbacks = this.listeners.get(changeType);
    callbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`[Store] Error in listener for ${changeType}:`, error);
      }
    });
  }

  // =========== OBSERVER PATTERN ===========

  /**
   * Subscribe to state changes
   * Returns unsubscribe function
   */
  subscribe(changeType, callback) {
    if (!this.listeners.has(changeType)) {
      this.listeners.set(changeType, []);
    }
    const callbacks = this.listeners.get(changeType);
    callbacks.push(callback);
    
    // Return unsubscribe function
    return () => {
      const idx = callbacks.indexOf(callback);
      if (idx >= 0) {
        callbacks.splice(idx, 1);
      }
    };
  }

  /**
   * Clear all listeners (useful for cleanup)
   */
  clearListeners(changeType = null) {
    if (changeType) {
      this.listeners.delete(changeType);
    } else {
      this.listeners.clear();
    }
  }
}

// Export singleton
export const store = new Store();
export default Store;
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
