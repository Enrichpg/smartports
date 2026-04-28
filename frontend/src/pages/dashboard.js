/**
 * Dashboard Page - Main Galicia Port Network View
 */

import { apiClient } from '../services/api.js';
import { wsManager } from '../services/websocket.js';
import { store } from '../store/store.js';
import {
  Header,
  Sidebar,
  KpiCard,
  ConnectionStatus,
  ErrorBanner,
  LoadingSkeleton,
  EmptyState,
} from '../components/base.js';
import {
  PortCard,
  AlertPanel,
  AvailabilityPanel,
} from '../components/domain.js';
import { PortMapController, MapContainer } from '../components/map.js';
import {
  BerthOccupancyChart,
  ChartController,
  ChartContainer,
} from '../components/charts.js';
import {
  formatDate,
  formatNumber,
  handleError,
  showErrorNotification,
} from '../utils/helpers.js';

export class DashboardPage {
  constructor() {
    this.pageId = 'dashboard';
    this.mapController = null;
    this.charts = {};
    this.subscriptions = [];
  }

  async mount(containerId = 'app') {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    // Render initial structure
    container.innerHTML = `
      ${Header({
        currentPage: 'Dashboard - Galicia',
        connectionStatus: store.getConnectionStatus(),
      })}
      
      <div class="container-fluid mt-0">
        <!-- Notification Container -->
        <div id="notification-container" class="mt-3"></div>

        <!-- Connection Status -->
        <div class="row mb-3 mt-2">
          <div class="col-12">
            <div class="d-flex justify-content-between align-items-center">
              <h4><i class="fas fa-chart-line"></i> Dashboard Operativo Galicia</h4>
              <div id="connection-status-container"></div>
            </div>
          </div>
        </div>

        <!-- KPIs Row -->
        <div id="kpis-container" class="row mb-4">
          ${LoadingSkeleton({ lines: 2 })}
        </div>

        <!-- Map and Alerts Row -->
        <div class="row mb-4">
          <div class="col-lg-8">
            <div class="card">
              <div class="card-header bg-light">
                <h5 class="mb-0">
                  <i class="fas fa-map"></i> Mapa de Puertos - Galicia
                </h5>
              </div>
              <div class="card-body" style="height: 500px; padding: 0;">
                ${MapContainer({ mapId: 'map-galicia', width: '100%', height: '500px' })}
              </div>
            </div>
          </div>
          <div class="col-lg-4">
            <div class="card">
              <div class="card-header bg-light">
                <h5 class="mb-0">
                  <i class="fas fa-exclamation-triangle"></i> Alertas Activas
                </h5>
              </div>
              <div class="card-body" style="max-height: 500px; overflow-y: auto;">
                <div id="alerts-container">
                  ${LoadingSkeleton({ lines: 3 })}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Availability and Charts Row -->
        <div class="row mb-4">
          <div class="col-lg-6">
            <div id="availability-container" class="card">
              <div class="card-body">
                ${LoadingSkeleton({ lines: 4 })}
              </div>
            </div>
          </div>
          <div class="col-lg-6">
            ${ChartContainer({
              chartId: 'berth-occupancy-chart',
              title: 'Distribución de Atraques',
            })}
          </div>
        </div>

        <!-- Ports Grid Row -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="card">
              <div class="card-header bg-light">
                <h5 class="mb-0">
                  <i class="fas fa-ship"></i> Puertos Gallegos
                </h5>
              </div>
              <div class="card-body">
                <div id="ports-container" class="row">
                  ${LoadingSkeleton({ lines: 2 })}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Last Update -->
        <div class="row">
          <div class="col-12">
            <small class="text-muted">
              <i class="fas fa-sync"></i> Última actualización:
              <span id="last-update">Nunca</span>
            </small>
          </div>
        </div>
      </div>
    `;

    // Initialize components
    await this.initializeData();
    await this.initializeMap();
    this.initializeWebSocket();
    this.initializeEventListeners();

    // Subscribe to store changes
    this.subscribeToStoreEvents();
  }

  async initializeData() {
    try {
      // Load all initial data in parallel
      const [ports, alerts, availability] = await Promise.all([
        apiClient.getPorts(100),
        apiClient.getAlerts(100),
        apiClient.getAvailability(),
      ]);

      store.setPorts(ports.ports || ports);

      // Load berths for each port
      const allPorts = ports.ports || ports;
      if (allPorts.length > 0) {
        const berthsData = await apiClient.getBerths(null, null, 500);
        store.setBerths(berthsData.berths || berthsData);
      }

      store.setAlerts(alerts.alerts || alerts);
      store.setAvailability(availability);

      this.render();
    } catch (error) {
      showErrorNotification(
        handleError(error, 'Error al cargar datos del dashboard')
      );
      this.renderError();
    }
  }

  initializeMap() {
    const mapContainer = document.getElementById('map-galicia');
    if (!mapContainer) {
      console.error('Map container not found');
      return;
    }

    this.mapController = new PortMapController('map-galicia', {
      onPortSelect: (port) => this.navigateToPort(port),
    });

    if (!this.mapController.init()) {
      showErrorNotification('No se pudo inicializar el mapa');
      return;
    }

    // Add ports to map
    const ports = store.getPorts();
    ports.forEach((port) => {
      this.mapController.addPort(port);
    });

    this.mapController.fitBounds();
  }

  initializeWebSocket() {
    wsManager.connect();

    // Subscribe to real-time events
    wsManager.subscribe('berth.updated', (data) => {
      store.updateBerth(data.id, data);
      if (this.mapController && data.port_id) {
        const port = store.getPort(data.port_id);
        if (port) {
          this.mapController.updatePort(port);
        }
      }
    });

    wsManager.subscribe('alert.created', (data) => {
      store.addAlert(data);
    });

    wsManager.subscribe('portcall.created', (data) => {
      store.addPortCall(data);
    });

    wsManager.subscribe('availability.updated', (data) => {
      store.setAvailability(data);
      this.renderAvailability();
    });

    wsManager.subscribe('connected', () => {
      store.setConnectionStatus('connected');
      this.updateConnectionStatus();
    });

    wsManager.subscribe('disconnected', () => {
      store.setConnectionStatus('disconnected');
      this.updateConnectionStatus();
    });

    wsManager.subscribe('reconnecting', () => {
      store.setConnectionStatus('connecting');
      this.updateConnectionStatus();
    });
  }

  subscribeToStoreEvents() {
    this.subscriptions.push(
      store.subscribe('kpisUpdated', () => this.renderKPIs())
    );

    this.subscriptions.push(
      store.subscribe('alertsChanged', () => this.renderAlerts())
    );

    this.subscriptions.push(
      store.subscribe('berthsChanged', () => this.updateChart())
    );

    this.subscriptions.push(
      store.subscribe('portsChanged', () => {
        this.renderPorts();
        if (this.mapController) {
          this.mapController.clearPorts();
          store.getPorts().forEach((port) => {
            this.mapController.addPort(port);
          });
          this.mapController.fitBounds();
        }
      })
    );

    this.subscriptions.push(
      store.subscribe('connectionStatusChanged', () => this.updateConnectionStatus())
    );
  }

  initializeEventListeners() {
    // Will be populated based on interactive elements
  }

  render() {
    this.renderKPIs();
    this.renderAlerts();
    this.renderAvailability();
    this.renderPorts();
    this.updateChart();
    this.updateConnectionStatus();
    this.updateLastUpdate();
  }

  renderKPIs() {
    const kpis = store.getKPIs();
    const container = document.getElementById('kpis-container');
    if (!container) return;

    container.innerHTML = `
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Puertos Activos',
          value: kpis.activePorts,
          icon: 'fa-ship',
          color: 'primary',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Atraques Libres',
          value: kpis.freeBerths,
          icon: 'fa-anchor',
          color: 'success',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Escalas Activas',
          value: kpis.activePortCalls,
          icon: 'fa-calendar',
          color: 'warning',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Alertas Activas',
          value: kpis.activeAlerts,
          icon: 'fa-exclamation-circle',
          color: 'danger',
        })}
      </div>
    `;
  }

  renderAlerts() {
    const alerts = store.getActiveAlerts().slice(0, 10);
    const container = document.getElementById('alerts-container');
    if (!container) return;

    container.innerHTML = AlertPanel({
      alerts: alerts,
      maxItems: 10,
      onAlertClick: (alertId) => console.log('Alert clicked:', alertId),
    });
  }

  renderAvailability() {
    const availability = store.state.availability;
    const container = document.getElementById('availability-container');
    if (!container) return;

    container.innerHTML = `
      <div class="card">
        <div class="card-header bg-light">
          <h6 class="mb-0">Disponibilidad Agregada</h6>
        </div>
        <div class="card-body">
          ${AvailabilityPanel({
            availability: availability,
          })}
        </div>
      </div>
    `;
  }

  renderPorts() {
    const ports = store.getPorts().slice(0, 6);
    const container = document.getElementById('ports-container');
    if (!container) return;

    if (ports.length === 0) {
      container.innerHTML = EmptyState({
        icon: 'fa-inbox',
        title: 'Sin puertos',
        message: 'No hay datos de puertos disponibles',
      });
      return;
    }

    container.innerHTML = ports
      .map(
        (port) =>
          `<div class="col-md-4 mb-3">
          ${PortCard({
            port: port,
            onClick: (portId) => this.navigateToPort(port),
            compact: true,
          })}
        </div>`
      )
      .join('');
  }

  updateChart() {
    const berths = store.getBerths();
    const occupied = berths.filter((b) => b.status === 'occupied').length;
    const free = berths.filter((b) => b.status === 'free').length;
    const reserved = berths.filter((b) => b.status === 'reserved').length;
    const unavailable = berths.filter(
      (b) => b.status === 'unavailable' || b.status === 'out_of_service'
    ).length;

    const chartData = BerthOccupancyChart({
      free,
      occupied,
      reserved,
      unavailable,
    });

    if (document.getElementById('berth-occupancy-chart')) {
      if (!this.charts.occupancy) {
        this.charts.occupancy = new ChartController(
          'berth-occupancy-chart',
          'doughnut'
        );
        this.charts.occupancy.init(chartData.data, {
          plugins: {
            title: {
              display: true,
              text: 'Distribución de Atraques',
            },
          },
        });
      } else {
        this.charts.occupancy.update(chartData.data);
      }
    }
  }

  updateConnectionStatus() {
    const status = store.getConnectionStatus();
    const container = document.getElementById('connection-status-container');
    if (!container) return;

    container.innerHTML = ConnectionStatus({ status });
  }

  updateLastUpdate() {
    const lastUpdate = document.getElementById('last-update');
    if (!lastUpdate) return;
    lastUpdate.textContent = formatDate(new Date(), 'time');
  }

  navigateToPort(port) {
    window.location.href = `/ports/${port.id}`;
  }

  renderError() {
    const container = document.getElementById('app');
    if (!container) return;

    container.innerHTML = `
      ${Header({ currentPage: 'Dashboard', connectionStatus: 'disconnected' })}
      <div class="container mt-4">
        ${ErrorBanner({
          message:
            'Error al cargar el dashboard. Por favor, intente nuevamente.',
        })}
      </div>
    `;
  }

  destroy() {
    // Unsubscribe from store events
    this.subscriptions.forEach((unsubscribe) => unsubscribe());

    // Destroy map
    if (this.mapController) {
      this.mapController.destroy();
    }

    // Destroy charts
    Object.values(this.charts).forEach((chart) => chart.destroy());

    // Disconnect WebSocket if needed
    // wsManager.disconnect();
  }
}
