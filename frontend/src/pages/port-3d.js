/**
 * Port3DPage - Vista 3D esquemática de un puerto galiego
 *
 * Ruta: /ports/:id/3d
 * Muestra los berths del puerto como cajas 3D coloreadas por estado.
 * Actualización en tiempo real via WebSocket (berth.updated).
 */

import { apiClient } from '../services/api.js';
import { wsManager } from '../services/websocket.js';
import { Header, updateWsBadge } from '../components/base.js';
import { Port3DController } from '../components/port3d.js';
import { handleError, showErrorNotification } from '../utils/helpers.js';

const STATUS_CSS = {
  free:           { cls: 'success', label: 'Libre' },
  occupied:       { cls: 'danger',  label: 'Ocupado' },
  reserved:       { cls: 'warning', label: 'Reservado' },
  unavailable:    { cls: 'secondary', label: 'No disponible' },
  out_of_service: { cls: 'dark',    label: 'Fuera de servicio' },
};

export class Port3DPage {
  constructor(portId) {
    this.portId = portId;
    this.port3d = null;
    this.berths = [];
    this._wsUnsubs = [];
  }

  async mount(containerId = 'app') {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
      ${Header({ currentPage: 'Vista 3D — Puerto', connectionStatus: 'disconnected' })}
      <div class="container-fluid mt-3">
        <div class="d-flex align-items-center gap-3 mb-3">
          <a href="/ports/${this.portId}" class="btn btn-outline-secondary btn-sm">
            <i class="fas fa-arrow-left"></i> Volver
          </a>
          <h4 class="mb-0"><i class="fas fa-cube"></i> Vista 3D — <span id="port-name-3d">${this.portId}</span></h4>
          <span id="ws-status-3d" class="badge bg-secondary ms-2">Conectando...</span>
        </div>

        <!-- 3D Canvas -->
        <div class="card mb-3">
          <div class="card-body p-0">
            <div id="port-3d-canvas"
                 style="width:100%;height:520px;background:#1a3a5c;border-radius:4px;overflow:hidden;">
              <div class="d-flex align-items-center justify-content-center h-100 text-white">
                <div class="text-center">
                  <div class="spinner-border mb-2" role="status"></div>
                  <p>Cargando vista 3D...</p>
                </div>
              </div>
            </div>
          </div>
          <div class="card-footer text-muted small">
            <i class="fas fa-mouse-pointer"></i> Arrastrar para rotar &nbsp;|&nbsp;
            <i class="fas fa-scroll"></i> Scroll para zoom &nbsp;|&nbsp;
            <i class="fas fa-sync fa-xs text-success"></i> Actualización en tiempo real via WebSocket
          </div>
        </div>

        <!-- Legend + Berth list -->
        <div class="row">
          <div class="col-md-4">
            <div class="card">
              <div class="card-header"><h6 class="mb-0">Leyenda</h6></div>
              <div class="card-body py-2">
                ${Object.entries(STATUS_CSS).map(([k, v]) =>
                  `<div class="d-flex align-items-center gap-2 mb-1">
                    <span class="badge bg-${v.cls}">&nbsp;</span>
                    <small>${v.label}</small>
                  </div>`
                ).join('')}
              </div>
            </div>
          </div>
          <div class="col-md-8">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">Atraques</h6>
                <span id="berth-count-3d" class="badge bg-primary">—</span>
              </div>
              <div id="berths-list-3d" class="card-body py-2" style="max-height:200px;overflow-y:auto;">
                <div class="text-muted small">Cargando...</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    await this._loadData();
    this._initWS();
  }

  async _loadData() {
    try {
      const [portRes, berthRes] = await Promise.all([
        apiClient.getPortById(this.portId).catch(() => null),
        apiClient.getBerths(this.portId, null, 30),
      ]);

      if (portRes?.name) {
        const nameEl = document.getElementById('port-name-3d');
        if (nameEl) nameEl.textContent = portRes.name;
      }

      this.berths = berthRes?.berths || berthRes || [];

      this._render3D();
      this._renderBerthList();
    } catch (err) {
      showErrorNotification(handleError(err, 'Error cargando datos del puerto'));
    }
  }

  _render3D() {
    // Clear loading spinner
    const canvasEl = document.getElementById('port-3d-canvas');
    if (!canvasEl) return;
    canvasEl.innerHTML = '';

    this.port3d = new Port3DController('port-3d-canvas');
    const ok = this.port3d.init(this.berths);
    if (!ok) {
      canvasEl.innerHTML = '<div class="d-flex align-items-center justify-content-center h-100 text-white"><p>Error: Three.js no disponible</p></div>';
    }
  }

  _renderBerthList() {
    const list = document.getElementById('berths-list-3d');
    const count = document.getElementById('berth-count-3d');
    if (count) count.textContent = this.berths.length;
    if (!list) return;

    list.innerHTML = this.berths.map((b, i) => {
      const s = STATUS_CSS[b.status] || { cls: 'secondary', label: b.status || '—' };
      const shortId = b.id?.split(':').pop() || b.id;
      return `<div class="d-flex align-items-center gap-2 mb-1">
        <span class="badge bg-${s.cls}" style="min-width:20px">${i + 1}</span>
        <small class="text-truncate flex-grow-1">${b.name || shortId}</small>
        <span class="badge bg-${s.cls} ms-auto" id="badge-3d-${b.id?.replace(/[^a-z0-9]/gi, '_')}">${s.label}</span>
      </div>`;
    }).join('') || '<div class="text-muted small">Sin atraques</div>';
  }

  _updateBerthBadge(berthId, status) {
    const safeId = berthId?.replace(/[^a-z0-9]/gi, '_');
    const badge = document.getElementById(`badge-3d-${safeId}`);
    if (!badge) return;
    const s = STATUS_CSS[status] || { cls: 'secondary', label: status };
    badge.className = `badge bg-${s.cls} ms-auto`;
    badge.textContent = s.label;
  }

  _initWS() {
    const unsub1 = wsManager.subscribe('berth.updated', ({ payload, scope }) => {
      if (scope?.port_id !== this.portId && scope?.port_id !== `urn:ngsi-ld:Port:${this.portId}`) return;
      const berthId = scope?.berth_id || payload?.id;
      const status = payload?.status;
      if (!berthId || !status) return;

      // Update 3D mesh color
      if (this.port3d) this.port3d.updateBerth(berthId, status);
      // Update list badge
      this._updateBerthBadge(berthId, status);
      // Update local berths array
      const b = this.berths.find((b) => b.id === berthId);
      if (b) b.status = status;
    });

    const unsub2 = wsManager.subscribe('connected', () => {
      updateWsBadge('connected');
      const badge = document.getElementById('ws-status-3d');
      if (badge) { badge.className = 'badge bg-success ms-2'; badge.textContent = 'Live'; }
    });

    const unsub3 = wsManager.subscribe('disconnected', () => {
      updateWsBadge('disconnected');
      const badge = document.getElementById('ws-status-3d');
      if (badge) { badge.className = 'badge bg-danger ms-2'; badge.textContent = 'Offline'; }
    });

    const unsub4 = wsManager.subscribe('reconnecting', () => {
      updateWsBadge('reconnecting');
      const badge = document.getElementById('ws-status-3d');
      if (badge) { badge.className = 'badge bg-warning text-dark ms-2'; badge.textContent = 'Reconectando...'; }
    });

    this._wsUnsubs = [unsub1, unsub2, unsub3, unsub4];

    // Reflect current WS state immediately
    if (wsManager.isConnected) {
      updateWsBadge('connected');
      const badge = document.getElementById('ws-status-3d');
      if (badge) { badge.className = 'badge bg-success ms-2'; badge.textContent = 'Live'; }
    }
  }

  destroy() {
    this._wsUnsubs.forEach((fn) => fn());
    if (this.port3d) this.port3d.destroy();
  }
}
