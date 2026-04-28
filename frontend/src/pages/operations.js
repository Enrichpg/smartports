/**
 * Operations Page - Consolidated Operational View
 */

import { apiClient } from '../services/api.js';
import { wsManager } from '../services/websocket.js';
import { store } from '../store/store.js';
import {
  Header,
  KpiCard,
  LoadingSkeleton,
  StatusBadge,
  FilterBar,
} from '../components/base.js';
import {
  BerthTable,
  PortCallTable,
} from '../components/domain.js';
import { formatDate, handleError, showErrorNotification } from '../utils/helpers.js';

export class OperationsPage {
  constructor() {
    this.pageId = 'operations';
    this.filters = {
      berthState: null,
      portId: null,
    };
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
        currentPage: 'Vista de Operaciones',
        connectionStatus: store.getConnectionStatus(),
      })}
      
      <div class="container-fluid mt-0">
        <div id="notification-container" class="mt-3"></div>

        <!-- Title -->
        <div class="row mb-3 mt-2">
          <div class="col-12">
            <h3><i class="fas fa-cogs"></i> Panel Operativo Consolidado</h3>
          </div>
        </div>

        <!-- KPIs Row -->
        <div id="kpis-container" class="row mb-4">
          ${LoadingSkeleton({ lines: 2 })}
        </div>

        <!-- Filters -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="card">
              <div class="card-body">
                <div class="row">
                  <div class="col-md-4">
                    <label class="form-label">Puerto</label>
                    <select class="form-select" id="filter-port-select">
                      <option value="">Todos los puertos</option>
                    </select>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Estado de Atraque</label>
                    <select class="form-select" id="filter-berth-state">
                      <option value="">Todos</option>
                      <option value="free">Libre</option>
                      <option value="occupied">Ocupado</option>
                      <option value="reserved">Reservado</option>
                      <option value="unavailable">No disponible</option>
                    </select>
                  </div>
                  <div class="col-md-4 d-flex align-items-end">
                    <button class="btn btn-outline-secondary w-100" id="clear-ops-filters">
                      Limpiar filtros
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tabs -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="card">
              <div class="card-header bg-light">
                <ul class="nav nav-tabs card-header-tabs" role="tablist">
                  <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="berths-tab" data-bs-toggle="tab" data-bs-target="#berths-pane" type="button" role="tab">
                      <i class="fas fa-anchor"></i> Atraques
                    </button>
                  </li>
                  <li class="nav-item" role="presentation">
                    <button class="nav-link" id="portcalls-tab" data-bs-toggle="tab" data-bs-target="#portcalls-pane" type="button" role="tab">
                      <i class="fas fa-ship"></i> Escalas
                    </button>
                  </li>
                  <li class="nav-item" role="presentation">
                    <button class="nav-link" id="summary-tab" data-bs-toggle="tab" data-bs-target="#summary-pane" type="button" role="tab">
                      <i class="fas fa-chart-bar"></i> Resumen
                    </button>
                  </li>
                </ul>
              </div>

              <div class="tab-content">
                <!-- Berths Tab -->
                <div class="tab-pane fade show active" id="berths-pane" role="tabpanel">
                  <div class="card-body">
                    <div id="berths-ops-container">
                      ${LoadingSkeleton({ lines: 5 })}
                    </div>
                  </div>
                </div>

                <!-- PortCalls Tab -->
                <div class="tab-pane fade" id="portcalls-pane" role="tabpanel">
                  <div class="card-body">
                    <div id="portcalls-ops-container">
                      ${LoadingSkeleton({ lines: 5 })}
                    </div>
                  </div>
                </div>

                <!-- Summary Tab -->
                <div class="tab-pane fade" id="summary-pane" role="tabpanel">
                  <div class="card-body">
                    <div id="summary-container">
                      ${LoadingSkeleton({ lines: 4 })}
                    </div>
                  </div>
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

    // Initialize
    await this.loadOperationalData();
    this.initializeFilters();
    this.initializeWebSocket();
    this.subscribeToStoreEvents();
  }

  async loadOperationalData() {
    try {
      // Load all data needed for operations view
      const [
        ports,
        berths,
        portCalls,
      ] = await Promise.all([
        apiClient.getPorts(100),
        apiClient.getBerths(null, null, 500),
        apiClient.getPortCalls(null, 500),
      ]);

      store.setPorts(ports.ports || ports);
      store.setBerths(berths.berths || berths);
      store.setPortCalls(portCalls.portcalls || portCalls);

      this.ports = ports.ports || ports;
      this.render();
    } catch (error) {
      showErrorNotification(
        handleError(error, 'Error al cargar datos operacionales')
      );
    }
  }

  initializeFilters() {
    const portSelect = document.getElementById('filter-port-select');
    const berthStateSelect = document.getElementById('filter-berth-state');
    const clearBtn = document.getElementById('clear-ops-filters');

    // Populate ports
    if (portSelect && this.ports) {
      const portOptions = this.ports
        .map((p) => `<option value="${p.id}">${p.name}</option>`)
        .join('');
      portSelect.innerHTML =
        '<option value="">Todos los puertos</option>' + portOptions;
    }

    // Add event listeners
    if (portSelect) {
      portSelect.addEventListener('change', (e) => {
        this.filters.portId = e.target.value;
        this.renderBerths();
        this.renderPortCalls();
      });
    }

    if (berthStateSelect) {
      berthStateSelect.addEventListener('change', (e) => {
        this.filters.berthState = e.target.value;
        this.renderBerths();
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        this.filters = { berthState: null, portId: null };
        if (portSelect) portSelect.value = '';
        if (berthStateSelect) berthStateSelect.value = '';
        this.renderBerths();
        this.renderPortCalls();
      });
    }
  }

  initializeWebSocket() {
    wsManager.subscribe('berth.updated', () => {
      this.renderBerths();
      this.renderKPIs();
    });

    wsManager.subscribe('portcall.updated', () => {
      this.renderPortCalls();
      this.renderKPIs();
    });
  }

  subscribeToStoreEvents() {
    this.subscriptions.push(
      store.subscribe('berthsChanged', () => this.renderBerths())
    );
    this.subscriptions.push(
      store.subscribe('portCallsChanged', () => this.renderPortCalls())
    );
  }

  render() {
    this.renderKPIs();
    this.renderBerths();
    this.renderPortCalls();
    this.renderSummary();
    this.updateLastUpdate();
  }

  renderKPIs() {
    const berths = store.getBerths();
    const portCalls = store.getPortCalls();

    const free = berths.filter((b) => b.status === 'free').length;
    const occupied = berths.filter((b) => b.status === 'occupied').length;
    const reserved = berths.filter((b) => b.status === 'reserved').length;
    const active = portCalls.filter((pc) => pc.status === 'active').length;

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
          title: 'Atraques Ocupados',
          value: occupied,
          icon: 'fa-times',
          color: 'danger',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Reservados',
          value: reserved,
          icon: 'fa-bookmark',
          color: 'warning',
        })}
      </div>
      <div class="col-md-3 mb-3">
        ${KpiCard({
          title: 'Escalas Activas',
          value: active,
          icon: 'fa-ship',
          color: 'primary',
        })}
      </div>
    `;
  }

  renderBerths() {
    let berths = store.getBerths();

    // Apply filters
    if (this.filters.portId) {
      berths = berths.filter((b) => b.port_id === this.filters.portId);
    }

    if (this.filters.berthState) {
      berths = berths.filter((b) => b.status === this.filters.berthState);
    }

    const container = document.getElementById('berths-ops-container');
    if (!container) return;

    container.innerHTML = BerthTable({
      berths: berths,
    });
  }

  renderPortCalls() {
    let portCalls = store.getPortCalls();

    if (this.filters.portId) {
      portCalls = portCalls.filter((pc) => pc.port_id === this.filters.portId);
    }

    const container = document.getElementById('portcalls-ops-container');
    if (!container) return;

    container.innerHTML = PortCallTable({
      portCalls: portCalls,
    });
  }

  renderSummary() {
    const ports = store.getPorts();
    const berths = store.getBerths();

    const totalBerths = berths.length;
    const avgBerthsPerPort = (totalBerths / ports.length).toFixed(1);
    const mostOccupiedPort = this.getMostOccupiedPort();
    const leastOccupiedPort = this.getLeastOccupiedPort();

    const container = document.getElementById('summary-container');
    if (!container) return;

    container.innerHTML = `
      <div class="row">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">Puerto Más Ocupado</h6>
            </div>
            <div class="card-body">
              ${mostOccupiedPort ? `
                <h5>${mostOccupiedPort.name}</h5>
                <p class="mb-0">Ocupación: ${mostOccupiedPort.occupancy_percent.toFixed(1)}%</p>
              ` : '<p class="text-muted">No hay datos</p>'}
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">Puerto Menos Ocupado</h6>
            </div>
            <div class="card-body">
              ${leastOccupiedPort ? `
                <h5>${leastOccupiedPort.name}</h5>
                <p class="mb-0">Ocupación: ${leastOccupiedPort.occupancy_percent.toFixed(1)}%</p>
              ` : '<p class="text-muted">No hay datos</p>'}
            </div>
          </div>
        </div>
      </div>

      <div class="row mt-3">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">Estadísticas Generales</h6>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-3 text-center">
                  <h4>${ports.length}</h4>
                  <p class="text-muted">Puertos</p>
                </div>
                <div class="col-md-3 text-center">
                  <h4>${totalBerths}</h4>
                  <p class="text-muted">Atraques Totales</p>
                </div>
                <div class="col-md-3 text-center">
                  <h4>${avgBerthsPerPort}</h4>
                  <p class="text-muted">Atraques por Puerto</p>
                </div>
                <div class="col-md-3 text-center">
                  <h4>${store.getKPIs().estimatedOccupancy.toFixed(1)}%</h4>
                  <p class="text-muted">Ocupación Media</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  getMostOccupiedPort() {
    const ports = store.getPorts();
    let mostOccupied = null;
    let maxOccupancy = 0;

    ports.forEach((port) => {
      if (port.occupancy_percent > maxOccupancy) {
        maxOccupancy = port.occupancy_percent;
        mostOccupied = port;
      }
    });

    return mostOccupied;
  }

  getLeastOccupiedPort() {
    const ports = store.getPorts();
    let leastOccupied = null;
    let minOccupancy = 100;

    ports.forEach((port) => {
      const occupancy = port.occupancy_percent || 0;
      if (occupancy < minOccupancy) {
        minOccupancy = occupancy;
        leastOccupied = port;
      }
    });

    return leastOccupied;
  }

  updateLastUpdate() {
    const lastUpdate = document.getElementById('last-update');
    if (!lastUpdate) return;
    lastUpdate.textContent = formatDate(new Date(), 'time');
  }

  destroy() {
    this.subscriptions.forEach((unsubscribe) => unsubscribe());
  }
}
