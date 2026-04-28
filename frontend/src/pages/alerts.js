/**
 * Alerts Page - Global Alerts Management
 */

import { apiClient } from '../services/api.js';
import { wsManager } from '../services/websocket.js';
import { store } from '../store/store.js';
import {
  Header,
  KpiCard,
  FilterBar,
  StatusBadge,
  LoadingSkeleton,
  ErrorBanner,
} from '../components/base.js';
import {
  AlertSeverityChart,
  ChartController,
  ChartContainer,
} from '../components/charts.js';
import {
  formatDate,
  handleError,
  showErrorNotification,
} from '../utils/helpers.js';

export class AlertsPage {
  constructor() {
    this.pageId = 'alerts';
    this.filters = {
      severity: null,
      port: null,
      status: 'active',
    };
    this.charts = {};
    this.subscriptions = [];
  }

  async mount(containerId = 'app') {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    container.innerHTML = `
      ${Header({
        currentPage: 'Panel de Alertas',
        connectionStatus: store.getConnectionStatus(),
      })}
      
      <div class="container-fluid mt-0">
        <div id="notification-container" class="mt-3"></div>

        <!-- Title -->
        <div class="row mb-3 mt-2">
          <div class="col-12">
            <h3><i class="fas fa-bell"></i> Centro de Alertas Operativas</h3>
          </div>
        </div>

        <!-- KPIs Row -->
        <div id="kpis-container" class="row mb-4">
          ${LoadingSkeleton({ lines: 2 })}
        </div>

        <!-- Filters Row -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="card">
              <div class="card-body">
                <div class="row">
                  <div class="col-md-3">
                    <label class="form-label">Severidad</label>
                    <select class="form-select" id="filter-severity">
                      <option value="">Todas</option>
                      <option value="high">Alta</option>
                      <option value="medium">Media</option>
                      <option value="low">Baja</option>
                    </select>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Estado</label>
                    <select class="form-select" id="filter-status">
                      <option value="active">Activas</option>
                      <option value="resolved">Resueltas</option>
                      <option value="">Todas</option>
                    </select>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Puerto</label>
                    <select class="form-select" id="filter-port">
                      <option value="">Todos</option>
                    </select>
                  </div>
                  <div class="col-md-3 d-flex align-items-end">
                    <button class="btn btn-outline-secondary w-100" id="clear-filters">
                      Limpiar filtros
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Alerts Table -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="card">
              <div class="card-header bg-light">
                <h5 class="mb-0">
                  <i class="fas fa-list"></i> Alertas
                </h5>
              </div>
              <div class="card-body">
                <div id="alerts-table-container">
                  ${LoadingSkeleton({ lines: 5 })}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Alert Chart -->
        <div class="row mb-4">
          <div class="col-lg-6">
            ${ChartContainer({
              chartId: 'alert-severity-chart',
              title: 'Alertas por Severidad',
            })}
          </div>
          <div class="col-lg-6">
            <div class="card">
              <div class="card-header bg-light">
                <h5 class="mb-0">Estadísticas</h5>
              </div>
              <div class="card-body">
                <div id="stats-container">
                  ${LoadingSkeleton({ lines: 3 })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Initialize
    await this.loadAlerts();
    this.initializeFilters();
    this.initializeWebSocket();
    this.subscribeToStoreEvents();
  }

  async loadAlerts() {
    try {
      const alerts = await apiClient.getAlerts(500);
      store.setAlerts(alerts.alerts || alerts);

      // Load ports for filter dropdown
      const ports = await apiClient.getPorts(100);
      this.ports = ports.ports || ports;

      this.render();
    } catch (error) {
      showErrorNotification(
        handleError(error, 'Error al cargar alertas')
      );
    }
  }

  initializeFilters() {
    const severitySelect = document.getElementById('filter-severity');
    const statusSelect = document.getElementById('filter-status');
    const portSelect = document.getElementById('filter-port');
    const clearBtn = document.getElementById('clear-filters');

    // Populate ports
    if (portSelect && this.ports) {
      const portOptions = this.ports
        .map((p) => `<option value="${p.id}">${p.name}</option>`)
        .join('');
      portSelect.innerHTML =
        '<option value="">Todos</option>' + portOptions;
    }

    // Add event listeners
    if (severitySelect) {
      severitySelect.addEventListener('change', (e) => {
        this.filters.severity = e.target.value;
        this.renderAlerts();
      });
    }

    if (statusSelect) {
      statusSelect.addEventListener('change', (e) => {
        this.filters.status = e.target.value;
        this.renderAlerts();
      });
    }

    if (portSelect) {
      portSelect.addEventListener('change', (e) => {
        this.filters.port = e.target.value;
        this.renderAlerts();
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        this.filters = {
          severity: null,
          port: null,
          status: 'active',
        };
        if (severitySelect) severitySelect.value = '';
        if (statusSelect) statusSelect.value = 'active';
        if (portSelect) portSelect.value = '';
        this.renderAlerts();
      });
    }
  }

  initializeWebSocket() {
    wsManager.subscribe('alert.created', (data) => {
      store.addAlert(data);
      this.render();
    });
  }

  subscribeToStoreEvents() {
    this.subscriptions.push(
      store.subscribe('alertsChanged', () => this.render())
    );
  }

  render() {
    this.renderKPIs();
    this.renderAlerts();
    this.updateChart();
    this.renderStats();
  }

  renderKPIs() {
    const allAlerts = store.getAlerts();
    const activeAlerts = allAlerts.filter(
      (a) => a.status === 'active' || !a.status
    );
    const highSeverity = allAlerts.filter((a) => a.severity === 'high').length;
    const mediumSeverity = allAlerts.filter((a) => a.severity === 'medium').length;

    const container = document.getElementById('kpis-container');
    if (!container) return;

    container.innerHTML = `
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Alertas Activas',
          value: activeAlerts.length,
          icon: 'fa-exclamation-circle',
          color: 'danger',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Severidad Alta',
          value: highSeverity,
          icon: 'fa-warning',
          color: 'danger',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Severidad Media',
          value: mediumSeverity,
          icon: 'fa-info-circle',
          color: 'warning',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Total',
          value: allAlerts.length,
          icon: 'fa-bell',
          color: 'primary',
        })}
      </div>
    `;
  }

  renderAlerts() {
    const allAlerts = store.getAlerts();

    // Apply filters
    let filtered = allAlerts;

    if (this.filters.severity) {
      filtered = filtered.filter((a) => a.severity === this.filters.severity);
    }

    if (this.filters.status) {
      filtered = filtered.filter((a) => a.status === this.filters.status);
    }

    if (this.filters.port) {
      filtered = filtered.filter((a) => a.port_id === this.filters.port);
    }

    // Sort by timestamp descending
    filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    const container = document.getElementById('alerts-table-container');
    if (!container) return;

    if (filtered.length === 0) {
      container.innerHTML =
        '<div class="alert alert-info">No hay alertas que coincidan con los filtros</div>';
      return;
    }

    const rows = filtered
      .map(
        (alert) => `
      <tr>
        <td>${StatusBadge({ status: alert.severity })}</td>
        <td>${alert.title || alert.type}</td>
        <td>${alert.message}</td>
        <td>${alert.port_name || 'N/A'}</td>
        <td>${formatDate(alert.timestamp, 'medium')}</td>
        <td>${StatusBadge({ status: alert.status || 'active' })}</td>
      </tr>
    `
      )
      .join('');

    container.innerHTML = `
      <div class="table-responsive">
        <table class="table table-hover">
          <thead class="table-light">
            <tr>
              <th>Severidad</th>
              <th>Título</th>
              <th>Descripción</th>
              <th>Puerto</th>
              <th>Timestamp</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;
  }

  updateChart() {
    const allAlerts = store.getAlerts();
    const high = allAlerts.filter((a) => a.severity === 'high').length;
    const medium = allAlerts.filter((a) => a.severity === 'medium').length;
    const low = allAlerts.filter((a) => a.severity === 'low').length;

    const chartData = {
      labels: ['Alta', 'Media', 'Baja'],
      datasets: [
        {
          label: 'Alertas',
          data: [high, medium, low],
          backgroundColor: ['#dc3545', '#fd7e14', '#17a2b8'],
          borderColor: ['#bb2d3b', '#dc6311', '#0c5460'],
          borderWidth: 2,
        },
      ],
    };

    if (document.getElementById('alert-severity-chart')) {
      if (!this.charts.severity) {
        this.charts.severity = new ChartController(
          'alert-severity-chart',
          'bar'
        );
        this.charts.severity.init(chartData);
      } else {
        this.charts.severity.update(chartData);
      }
    }
  }

  renderStats() {
    const allAlerts = store.getAlerts();
    const activeAlerts = allAlerts.filter(
      (a) => a.status === 'active' || !a.status
    );
    const avgPerPort = (allAlerts.length / (store.getPorts().length || 1)).toFixed(1);

    const container = document.getElementById('stats-container');
    if (!container) return;

    container.innerHTML = `
      <div class="stat-item mb-3">
        <div class="d-flex justify-content-between">
          <strong>Alertas Activas</strong>
          <span class="badge bg-danger">${activeAlerts.length}</span>
        </div>
      </div>
      <div class="stat-item mb-3">
        <div class="d-flex justify-content-between">
          <strong>Alertas Resueltas</strong>
          <span class="badge bg-success">${allAlerts.filter((a) => a.status === 'resolved').length}</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="d-flex justify-content-between">
          <strong>Promedio por Puerto</strong>
          <span class="badge bg-info">${avgPerPort}</span>
        </div>
      </div>
    `;
  }

  destroy() {
    this.subscriptions.forEach((unsubscribe) => unsubscribe());
    Object.values(this.charts).forEach((chart) => chart.destroy());
  }
}
