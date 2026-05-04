/**
 * WebSocket Integration Layer
 * Bridges WebSocket events to UI state and visualizations
 */

import { wsManager } from './websocket.js';
import { apiClient } from './api.js';
import { store } from '../store/store.js';

class WebSocketIntegrator {
  constructor(map2d = null, map3d = null) {
    this.map2d = map2d;
    this.map3d = map3d;
    this.isInitialized = false;
    this.debug = window.ENV?.DEBUG || false;
  }

  /**
   * Initialize WebSocket integration
   * - Load initial snapshot via REST
   * - Connect WebSocket
   * - Subscribe to events
   * - Set up listeners
   */
  async init() {
    try {
      console.log('[WSIntegrator] Initializing...');
      
      // Step 1: Load initial snapshot via REST
      await this._loadInitialSnapshot();
      
      // Step 2: Set up WebSocket listeners before connecting
      this._setupWebSocketListeners();
      
      // Step 3: Connect WebSocket
      wsManager.connect();
      
      this.isInitialized = true;
      console.log('[WSIntegrator] Initialization complete');
      
    } catch (error) {
      console.error('[WSIntegrator] Initialization error:', error);
      store.setWebsocketStatus('error', error.message);
    }
  }

  /**
   * Load initial port/berth/vessel data via REST API
   */
  async _loadInitialSnapshot() {
    try {
      store.setWebsocketStatus('connecting');
      
      // Load ports
      const portsData = await apiClient.getPorts(100, 0);
      if (portsData && portsData.ports) {
        const portMap = {};
        portsData.ports.forEach(port => {
          portMap[port.id] = port;
        });
        store.setPorts(portMap);
      }
      
      // Load berths
      const berthsData = await apiClient.getBerths(100, 0);
      if (berthsData && berthsData.berths) {
        const berthMap = {};
        berthsData.berths.forEach((berth, idx) => {
          berthMap[berth.id] = { 
            ...berth, 
            position_index: idx % 15 
          };
        });
        store.setBerths(berthMap);
        
        // Render initial berths on 3D map
        if (this.map3d) {
          this.map3d.loadSnapshot({ berths: berthMap });
        }
      }
      
      // Load vessels
      const vesselsData = await apiClient.getVessels(50, 0);
      if (vesselsData && vesselsData.vessels) {
        vesselsData.vessels.forEach(vessel => {
          store.updateVessel(vessel.id, vessel);
          if (this.map3d) {
            this.map3d.updateVessel(vessel.id, vessel);
          }
        });
      }
      
      // Load alerts
      const alertsData = await apiClient.getAlerts(50, 0);
      if (alertsData && alertsData.alerts) {
        alertsData.alerts.forEach(alert => {
          store.addAlert(alert);
          if (this.map3d) {
            this.map3d.updateAlert(alert.id, alert);
          }
        });
      }
      
      console.log('[WSIntegrator] Initial snapshot loaded');
      
    } catch (error) {
      console.error('[WSIntegrator] Error loading snapshot:', error);
      // Continue anyway - WebSocket will fill in the data
    }
  }

  /**
   * Set up WebSocket event listeners
   */
  _setupWebSocketListeners() {
    // Connection state listeners
    wsManager.subscribe('connected', () => {
      console.log('[WSIntegrator] WebSocket connected');
      store.setWebsocketStatus('connected');
      
      // Subscribe to all events
      wsManager.send({
        type: 'subscribe',
        data: {
          event_types: [
            'berth.updated',
            'occupancy.changed',
            'vessel.arrived',
            'alert.triggered',
            'sensor_reading'
          ],
          port_ids: ['galicia-a-coruna'],
        }
      });
    });

    wsManager.subscribe('disconnected', () => {
      console.log('[WSIntegrator] WebSocket disconnected');
      store.setWebsocketStatus('disconnected');
    });

    wsManager.subscribe('reconnecting', (data) => {
      console.log('[WSIntegrator] Reconnecting...', data);
      store.setWebsocketStatus('connecting');
    });

    wsManager.subscribe('error', (error) => {
      console.error('[WSIntegrator] WebSocket error:', error);
      store.setWebsocketStatus('error', error.error || error);
    });

    // Event type listeners
    wsManager.subscribe('berth.updated', (eventData) => {
      this._handleBerthUpdate(eventData);
    });

    wsManager.subscribe('occupancy.changed', (eventData) => {
      this._handleOccupancyUpdate(eventData);
    });

    wsManager.subscribe('vessel.arrived', (eventData) => {
      this._handleVesselArrived(eventData);
    });

    wsManager.subscribe('alert.triggered', (eventData) => {
      this._handleAlertTriggered(eventData);
    });

    wsManager.subscribe('sensor_reading', (eventData) => {
      this._handleSensorReading(eventData);
    });

    if (this.debug) {
      console.log('[WSIntegrator] WebSocket listeners set up');
    }
  }

  /**
   * Handle berth update event
   */
  _handleBerthUpdate(eventData) {
    const { raw } = eventData;
    const { entity_id, payload } = raw.data;

    if (this.debug) {
      console.log('[WSIntegrator] Berth updated:', entity_id, payload);
    }

    // Update store
    store.updateBerth(entity_id, {
      status: payload.status,
      vessel_id: payload.vessel_id,
      occupancy_percentage: payload.occupancy_percentage,
    });

    // Update 3D visualization
    if (this.map3d) {
      this.map3d.updateBerth(entity_id, {
        status: payload.status,
        position_index: this._getPositionIndex(entity_id),
      });
    }

    // Update 2D map if available
    if (this.map2d) {
      this.map2d.updateBerthLayer(entity_id, {
        status: payload.status,
        vessel_name: payload.vessel_name,
      });
    }
  }

  /**
   * Handle occupancy update event
   */
  _handleOccupancyUpdate(eventData) {
    const { raw } = eventData;
    const { scope, payload } = raw.data;

    if (this.debug) {
      console.log('[WSIntegrator] Occupancy changed:', scope.port_id, payload);
    }

    store.updateOccupancy(scope.port_id, payload);
  }

  /**
   * Handle vessel arrived event
   */
  _handleVesselArrived(eventData) {
    const { raw } = eventData;
    const { entity_id, payload } = raw.data;

    if (this.debug) {
      console.log('[WSIntegrator] Vessel arrived:', entity_id, payload);
    }

    store.updateVessel(entity_id, {
      name: payload.vessel_name,
      imo: payload.imo,
      type: payload.vessel_type,
      length_m: payload.length_m,
      beam_m: payload.beam_m,
      draft_m: payload.draft_m,
    });

    if (this.map3d) {
      this.map3d.updateVessel(entity_id, {
        length_m: payload.length_m,
        beam_m: payload.beam_m,
        draft_m: payload.draft_m,
      });
    }
  }

  /**
   * Handle alert triggered event
   */
  _handleAlertTriggered(eventData) {
    const { raw } = eventData;
    const { entity_id, payload } = raw.data;

    if (this.debug) {
      console.log('[WSIntegrator] Alert triggered:', entity_id, payload);
    }

    store.addAlert({
      id: entity_id,
      type: payload.alert_type,
      severity: payload.severity,
      description: payload.description,
      entity_id: payload.entity_id,
    });

    if (this.map3d) {
      this.map3d.updateAlert(entity_id, {
        entity_id: payload.entity_id,
        severity: payload.severity,
      });
    }
  }

  /**
   * Handle sensor reading event
   */
  _handleSensorReading(eventData) {
    const { raw } = eventData;
    const { entity_id, payload } = raw.data;

    if (this.debug) {
      console.log('[WSIntegrator] Sensor reading:', entity_id, payload);
    }

    store.updateSensor(entity_id, {
      type: payload.sensor_type,
      value: payload.value,
      unit: payload.unit,
      timestamp: payload.timestamp,
    });

    if (this.map3d) {
      this.map3d.updateSensor(entity_id, {
        sensor_type: payload.sensor_type,
        value: payload.value,
      });
    }
  }

  /**
   * Helper: Get position index for berth visualization
   */
  _getPositionIndex(berthId) {
    // Extract numeric part from berth ID
    const match = berthId.match(/berth-(\d+)/);
    if (match) {
      return parseInt(match[1], 10);
    }
    return 0;
  }

  /**
   * Disconnect WebSocket and clean up
   */
  disconnect() {
    wsManager.disconnect();
    wsManager.clearListeners();
    this.isInitialized = false;
    console.log('[WSIntegrator] Disconnected');
  }
}

export default WebSocketIntegrator;
