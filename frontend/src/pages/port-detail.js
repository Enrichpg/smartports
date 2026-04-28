/**
 * Port Detail Page
 */

import { apiClient } from '../services/api.js';
import { wsManager } from '../services/websocket.js';
import { store } from '../store/store.js';
import {
  Header,
  KpiCard,
  ConnectionStatus,
  ErrorBanner,
  LoadingSkeleton,
  FilterBar,
  StatusBadge,
} from '../components/base.js';
import {
  BerthTable,
  PortCallTable,
  AlertPanel,
  AvailabilityPanel,
} from '../components/domain.js';
import {
  OccupancyTrendChart,
  ChartController,
  ChartContainer,
} from '../components/charts.js';
import {
  formatDate,
  formatNumber,
  handleError,
  showErrorNotification,
} from '../utils/helpers.js';

export class PortDetailPage {
  constructor(portId) {
    this.pageId = 'port-detail';
    this.portId = portId;
    this.portData = null;
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
        currentPage: `Puerto: ${this.portId}`,
        connectionStatus: store.getConnectionStatus(),
      })}
      
      <div class="container-fluid mt-0">
        <div id="notification-container" class="mt-3"></div>

        <!-- Back Button and Title -->
        <div class="row mb-3 mt-2">
          <div class="col-12">
            <a href="/" class="btn btn-outline-primary btn-sm mb-3">
              <i class="fas fa-arrow-left"></i> Volver al Dashboard
            </a>
            <h3 id="port-name">Cargando...</h3>
            <p id="port-location" class="text-muted">Ubicación desconocida</p>
          </div>
        </div>

        <!-- KPIs Row -->
        <div id="kpis-container" class="row mb-4">
          ${LoadingSkeleton({ lines: 2 })}
        </div>

        <!-- Main Content -->
        <div class="row">
          <!-- Left Column: Berths and PortCalls -->
          <div class="col-lg-8">
            <!-- Berths Table -->
            <div class="card mb-4">
              <div class="card-header bg-light">
                <h5 class="mb-0">
                  <i class="fas fa-anchor"></i> Atraques
                </h5>
              </div>
              <div class="card-body">
                <div id="berths-filter" class="mb-3"></div>
                <div id="berths-container">
                  ${LoadingSkeleton({ lines: 3 })}
                </div>
              </div>
            </div>

            <!-- Port Calls Table -->
            <div class="card">
              <div class="card-header bg-light">
                <h5 class="mb-0">
                  <i class="fas fa-calendar"></i> Escalas Activas
                </h5>
              </div>
              <div class="card-body">
                <div id="portcalls-container">
                  ${LoadingSkeleton({ lines: 3 })}
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column: Alerts and Availability -->
          <div class="col-lg-4">
            <!-- Alerts -->
            <div class="card mb-4">
              <div class="card-header bg-light">
                <h5 class="mb-0">
                  <i class="fas fa-exclamation-triangle"></i> Alertas
                </h5>
              </div>
              <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                <div id="port-alerts-container">
                  ${LoadingSkeleton({ lines: 3 })}
                </div>
              </div>
            </div>

            <!-- Availability -->
            <div class="card">
              <div class="card-header bg-light">
                <h5 class="mb-0">
                  <i class="fas fa-chart-pie"></i> Disponibilidad
                </h5>
              </div>
              <div class="card-body">
                <div id="port-availability-container">
                  ${LoadingSkeleton({ lines: 4 })}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Last Update -->
        <div class="row mt-4">
          <div class="col-12">
            <small class="text-muted">
              <i class="fas fa-sync"></i> Última actualización:
              <span id="last-update">Nunca</span>
            </small>
          </div>
        </div>
      </div>
    `;

    // Initialize
    await this.loadPortData();
    this.initializeWebSocket();
    this.subscribeToStoreEvents();
  }

  async loadPortData() {
    try {
      // Load port details, berths, portcalls, alerts in parallel
      const [port, berths, portCalls, alerts, availability] = await Promise.all([
        apiClient.getPortById(this.portId),
        apiClient.getPortBerths(this.portId, 100),
        apiClient.getPortCalls(this.portId, 100),
        apiClient.getPortAlerts(this.portId),
        apiClient.getPortAvailability(this.portId),
      ]);

      this.portData = port;
      store.setPortDetail(port);
      store.setBerths(berths.berths || berths);
      store.setPortCalls(portCalls.portcalls || portCalls);
      store.setAlerts(alerts.alerts || alerts);
      store.setAvailability(availability);

      this.render();
    } catch (error) {
      showErrorNotification(
        handleError(error, 'Error al cargar datos del puerto')
      );
      this.renderError();
    }
  }

  initializeWebSocket() {
    wsManager.subscribe('berth.updated', (data) => {
      if (data.port_id === this.portId) {
        store.updateBerth(data.id, data);
        this.renderBerths();
      }
    });

    wsManager.subscribe('portcall.updated', (data) => {
      if (data.port_id === this.portId) {
        store.updatePortCall(data.id, data);
        this.renderPortCalls();
      }
    });

    wsManager.subscribe('alert.created', (data) => {
      if (data.port_id === this.portId) {
        store.addAlert(data);
        this.renderAlerts();
      }
    });

    wsManager.subscribe('availability.updated', (data) => {
      if (data.port_id === this.portId) {
        store.setAvailability(data);
        this.renderAvailability();
      }
    });
  }

  subscribeToStoreEvents() {
    this.subscriptions.push(
      store.subscribe('kpisUpdated', () => this.renderKPIs())
    );
  }

  render() {
    this.updatePortHeader();
    this.renderKPIs();
    this.renderBerths();
    this.renderPortCalls();
    this.renderAlerts();
    this.renderAvailability();
    this.updateLastUpdate();
  }

  updatePortHeader() {
    if (this.portData) {
      const nameEl = document.getElementById('port-name');
      const locEl = document.getElementById('port-location');
      if (nameEl) nameEl.textContent = this.portData.name || this.portId;
      if (locEl)
        locEl.textContent =
          this.portData.location || 'Ubicación no disponible';
    }
  }

  renderKPIs() {
    const berths = store.getBerths();
    const portCalls = store.getActivePortCalls();
    const alerts = store.getActiveAlerts();

    const free = berths.filter((b) => b.status === 'free').length;
    const occupied = berths.filter((b) => b.status === 'occupied').length;
    const reserved = berths.filter((b) => b.status === 'reserved').length;
    const occupancy = berths.length > 0 ? ((occupied + reserved) / berths.length * 100).toFixed(1) : 0;

    const container = document.getElementById('kpis-container');
    if (!container) return;

    container.innerHTML = `
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Atraques Libres',
          value: free,
          icon: 'fa-check',
          color: 'success',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Ocupados',
          value: occupied,
          icon: 'fa-times',
          color: 'danger',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Escalas Activas',
          value: portCalls.length,
          icon: 'fa-ship',
          color: 'primary',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Ocupación',
          value: occupancy,
          unit: '%',
          icon: 'fa-percent',
          color: 'warning',
        })}
      </div>
    `;
  }

  renderBerths() {
    const berths = store.getBerths();
    const container = document.getElementById('berths-container');
    if (!container) return;

    container.innerHTML = BerthTable({
      berths: berths,
      onBerthSelect: (berthId) => console.log('Berth selected:', berthId),
    });
  }

  renderPortCalls() {
    const portCalls = store.getPortCalls();
    const container = document.getElementById('portcalls-container');
    if (!container) return;

    container.innerHTML = PortCallTable({
      portCalls: portCalls,
      onPortCallSelect: (pcId) => console.log('PortCall selected:', pcId),
    });
  }

  renderAlerts() {
    const alerts = store.getAlerts();
    const container = document.getElementById('port-alerts-container');
    if (!container) return;

    container.innerHTML = AlertPanel({
      alerts: alerts,
      maxItems: 10,
    });
  }

  renderAvailability() {
    const availability = store.state.availability;
    const container = document.getElementById('port-availability-container');
    if (!container) return;

    container.innerHTML = AvailabilityPanel({
      availability: availability,
    });
  }

  updateLastUpdate() {
    const lastUpdate = document.getElementById('last-update');
    if (!lastUpdate) return;
    lastUpdate.textContent = formatDate(new Date(), 'time');
  }

  renderError() {
    const container = document.getElementById('app');
    if (!container) return;

    container.innerHTML = `
      ${Header({ currentPage: 'Puerto', connectionStatus: 'disconnected' })}
      <div class="container mt-4">
        ${ErrorBanner({
          message:
            'Error al cargar los datos del puerto. Por favor, intente nuevamente.',
        })}
        <a href="/" class="btn btn-primary mt-3">
          <i class="fas fa-arrow-left"></i> Volver al Dashboard
        </a>
      </div>
    `;
  }

  destroy() {
    this.subscriptions.forEach((unsubscribe) => unsubscribe());
    Object.values(this.charts).forEach((chart) => chart.destroy());
  }
}
