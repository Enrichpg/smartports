/**
 * Vessels Page — Fleet overview with filters and detail cards
 */

import { apiClient } from '../services/api.js';
import { EmptyState, LoadingSkeleton } from '../components/base.js';
import { generateVessels, generatePortCalls, PORTS } from '../services/mock-data.js';
import { formatDate } from '../utils/helpers.js';

const STATUS_LABELS = { in_port: 'En Puerto', underway: 'En Ruta', approaching: 'Aproximándose', departing: 'Saliendo', anchored: 'Fondeado' };
const TYPE_LABELS = { container: 'Contenedor', bulk: 'Graneles', tanker: 'Tanquero', roro: 'Ro-Ro', general: 'Carga general', cruise: 'Crucero', fishing: 'Pesca' };
const FLAG_NAMES = { ES: '🇪🇸 España', PT: '🇵🇹 Portugal', NO: '🇳🇴 Noruega', DE: '🇩🇪 Alemania', GR: '🇬🇷 Grecia', IT: '🇮🇹 Italia' };

export class VesselsPage {
  constructor() {
    this.pageId = 'vessels';
    this._all = []; this._filtered = [];
    this._search = ''; this._statusFilter = ''; this._typeFilter = '';
    this._view = 'grid';
    this._selected = null;
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="p-4">' + LoadingSkeleton({ lines: 8 }) + '</div>';
    this._all = await this._loadVessels();
    this._filtered = this._all;
    container.innerHTML = this._render();
    this._bindEvents(container);
  }

  async _loadVessels() {
    try {
      const data = await apiClient.getVessels ? await apiClient.getVessels(50) : null;
      const arr = data?.items || data || [];
      if (arr.length > 0) return arr.map(v => ({
        id: v.id, name: v.name || v.vessel_name, imo: v.imo || v.vessel_imo,
        mmsi: v.mmsi, flag: v.flag, type: v.type || v.vessel_type || 'general',
        grossTonnage: v.gross_tonnage || v.grossTonnage || 0,
        length: v.length || 0, beam: v.beam || 0, draft: v.draft || 0,
        yearBuilt: v.year_built || v.yearBuilt,
        company: v.company || '—',
        status: v.status || 'underway',
        portId: v.port_id || v.portId, portName: v.port_name || v.portName,
        captain: v.captain || '—', phone: v.phone || '—',
      }));
    } catch {}
    return generateVessels();
  }

  _render() {
    const inPort = this._all.filter(v => v.status === 'in_port').length;
    const underway = this._all.filter(v => v.status === 'underway').length;
    const approaching = this._all.filter(v => v.status === 'approaching').length;

    return `
      <div class="page-header">
        <div class="page-title"><i class="fas fa-ship"></i> Buques</div>
        <div class="page-subtitle">${this._all.length} buques registrados en la red portuaria</div>
      </div>

      <div class="row g-3 mb-3">
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="vf-all"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:var(--sp-primary)">${this._all.length}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Total</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="vf-in_port"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#00A651">${inPort}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">En Puerto</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="vf-approaching"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#17a2b8">${approaching}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Aproximándose</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="vf-underway"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#6c757d">${underway}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">En Ruta</div></div></div></div>
      </div>

      <div class="sp-filters">
        <div class="sp-filter-search"><label>Buscar</label><input class="form-control form-control-sm" id="v-search" placeholder="Nombre, IMO, MMSI..."></div>
        <div class="sp-filter-group">
          <label>Estado</label>
          <select class="form-select form-select-sm" id="v-status">
            <option value="">Todos</option>
            ${Object.entries(STATUS_LABELS).map(([v,l]) => `<option value="${v}">${l}</option>`).join('')}
          </select>
        </div>
        <div class="sp-filter-group">
          <label>Tipo</label>
          <select class="form-select form-select-sm" id="v-type">
            <option value="">Todos</option>
            ${Object.entries(TYPE_LABELS).map(([v,l]) => `<option value="${v}">${l}</option>`).join('')}
          </select>
        </div>
        <div class="d-flex align-items-end gap-2">
          <div class="view-toggle">
            <button class="view-toggle-btn active" id="v-view-grid" title="Grid"><i class="fas fa-th-large"></i></button>
            <button class="view-toggle-btn" id="v-view-table" title="Tabla"><i class="fas fa-table"></i></button>
          </div>
        </div>
      </div>

      <div id="v-content">${this._renderGrid()}</div>
    `;
  }

  _renderGrid() {
    if (!this._filtered.length) return EmptyState({ icon: 'fa-ship', title: 'Sin buques', message: 'No hay buques con los filtros aplicados' });
    return `<div class="row g-3">${this._filtered.map(v => `
      <div class="col-sm-6 col-lg-4 col-xl-3">
        <div class="sp-card vessel-card h-100" data-v-id="${v.id}" style="cursor:pointer;transition:transform 0.15s">
          <div class="sp-card-body">
            <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:12px">
              <div style="width:44px;height:44px;border-radius:10px;background:${_vColor(v.status)}22;color:${_vColor(v.status)};display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0">
                <i class="fas fa-ship"></i>
              </div>
              <div style="flex:1;min-width:0">
                <div style="font-weight:700;font-size:0.95rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${v.name}</div>
                <div style="font-size:0.75rem;color:var(--sp-text-muted)">${v.imo} · ${FLAG_NAMES[v.flag] || v.flag}</div>
              </div>
              <span class="sp-badge ${v.status}" style="font-size:0.68rem;padding:3px 8px;flex-shrink:0">${STATUS_LABELS[v.status] || v.status}</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:0.8rem">
              <div><span style="color:var(--sp-text-muted)">Tipo</span><br><strong>${TYPE_LABELS[v.type] || v.type}</strong></div>
              <div><span style="color:var(--sp-text-muted)">Tonelaje</span><br><strong>${(v.grossTonnage || 0).toLocaleString('es-ES')} GT</strong></div>
              <div><span style="color:var(--sp-text-muted)">Eslora</span><br><strong>${v.length}m</strong></div>
              <div><span style="color:var(--sp-text-muted)">Empresa</span><br><strong style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block">${v.company}</strong></div>
            </div>
            ${v.portName ? `<div class="mt-2 pt-2" style="border-top:1px solid var(--sp-border);font-size:0.78rem;color:var(--sp-text-muted)"><i class="fas fa-anchor me-1"></i>${v.portName}</div>` : `<div class="mt-2 pt-2" style="border-top:1px solid var(--sp-border);font-size:0.78rem;color:var(--sp-text-muted)"><i class="fas fa-water me-1"></i>Navegando</div>`}
          </div>
        </div>
      </div>`).join('')}</div>`;
  }

  _renderTable() {
    if (!this._filtered.length) return EmptyState({ icon: 'fa-ship', title: 'Sin buques' });
    return `
      <div class="sp-card">
        <div class="sp-table-wrapper">
          <table class="sp-table">
            <thead><tr><th>Buque</th><th>IMO / MMSI</th><th>Tipo</th><th>Bandera</th><th>Estado</th><th>Puerto</th><th>Tonelaje</th><th>Eslora</th><th>Capitán</th></tr></thead>
            <tbody>
              ${this._filtered.map(v => `
                <tr data-v-id="${v.id}" style="cursor:pointer">
                  <td><strong>${v.name}</strong><br><small class="text-muted">${v.company}</small></td>
                  <td><small>${v.imo}<br>${v.mmsi || '—'}</small></td>
                  <td>${TYPE_LABELS[v.type] || v.type}</td>
                  <td>${FLAG_NAMES[v.flag] || v.flag}</td>
                  <td><span class="sp-badge ${v.status}">${STATUS_LABELS[v.status] || v.status}</span></td>
                  <td>${v.portName || '<span class="text-muted">—</span>'}</td>
                  <td>${(v.grossTonnage || 0).toLocaleString('es-ES')} GT</td>
                  <td>${v.length}m</td>
                  <td>${v.captain}</td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>`;
  }

  _renderDetail(vessel) {
    const portCalls = generatePortCalls(30).filter(pc => pc.vesselName === vessel.name).slice(0, 5);
    return `
      <div class="sp-card mb-3">
        <div class="sp-card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span class="sp-card-title"><i class="fas fa-ship me-2"></i>${vessel.name}</span>
          <button class="btn btn-sm btn-outline-secondary" id="v-back"><i class="fas fa-arrow-left me-1"></i>Volver</button>
        </div>
        <div class="sp-card-body">
          <div class="row g-3">
            <div class="col-md-6">
              <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
                <div style="width:64px;height:64px;border-radius:50%;background:${_vColor(vessel.status)}22;color:${_vColor(vessel.status)};display:flex;align-items:center;justify-content:center;font-size:2rem">
                  <i class="fas fa-ship"></i>
                </div>
                <div>
                  <div style="font-size:1.2rem;font-weight:700">${vessel.name}</div>
                  <div style="color:var(--sp-text-muted);font-size:0.85rem">${vessel.company}</div>
                  <span class="sp-badge ${vessel.status}">${STATUS_LABELS[vessel.status] || vessel.status}</span>
                </div>
              </div>
              <table class="table table-sm" style="font-size:0.875rem">
                <tbody>
                  <tr><td class="text-muted">IMO</td><td>${vessel.imo}</td></tr>
                  <tr><td class="text-muted">MMSI</td><td>${vessel.mmsi || '—'}</td></tr>
                  <tr><td class="text-muted">Bandera</td><td>${FLAG_NAMES[vessel.flag] || vessel.flag}</td></tr>
                  <tr><td class="text-muted">Tipo</td><td>${TYPE_LABELS[vessel.type] || vessel.type}</td></tr>
                  <tr><td class="text-muted">Año de construcción</td><td>${vessel.yearBuilt || '—'}</td></tr>
                  <tr><td class="text-muted">Puerto actual</td><td>${vessel.portName || 'En ruta'}</td></tr>
                </tbody>
              </table>
            </div>
            <div class="col-md-6">
              <table class="table table-sm" style="font-size:0.875rem">
                <tbody>
                  <tr><td class="text-muted">Tonelaje bruto</td><td>${(vessel.grossTonnage || 0).toLocaleString('es-ES')} GT</td></tr>
                  <tr><td class="text-muted">Eslora</td><td>${vessel.length}m</td></tr>
                  <tr><td class="text-muted">Manga</td><td>${vessel.beam}m</td></tr>
                  <tr><td class="text-muted">Calado</td><td>${vessel.draft}m</td></tr>
                  <tr><td class="text-muted">Capitán</td><td>${vessel.captain}</td></tr>
                  <tr><td class="text-muted">Contacto</td><td>${vessel.phone}</td></tr>
                </tbody>
              </table>
              <div class="d-flex gap-2 mt-2">
                <button class="btn btn-sm btn-primary" onclick="window.showToast('Contactando con el buque...','info')"><i class="fas fa-phone me-1"></i>Contactar</button>
                <button class="btn btn-sm btn-outline-secondary" onclick="window.showToast('Descargando ficha','info')"><i class="fas fa-download me-1"></i>Ficha</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      ${portCalls.length ? `
      <div class="sp-card">
        <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-history"></i> Historial de Escalas</span></div>
        <div class="sp-table-wrapper">
          <table class="sp-table">
            <thead><tr><th>Puerto</th><th>Atraque</th><th>Estado</th><th>ETA</th><th>Duración</th><th>Carga</th></tr></thead>
            <tbody>${portCalls.map(pc => `
              <tr>
                <td>${pc.portName}</td>
                <td>${pc.berthName}</td>
                <td><span class="sp-badge ${pc.state}">${pc.state}</span></td>
                <td>${formatDate(pc.eta, 'medium')}</td>
                <td>${pc.durationHours}h</td>
                <td>${pc.cargo}</td>
              </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>` : ''}`;
  }

  _applyFilters() {
    this._filtered = this._all.filter(v => {
      const q = this._search.toLowerCase();
      if (q && !v.name.toLowerCase().includes(q) && !(v.imo || '').toLowerCase().includes(q) && !(v.mmsi || '').includes(q)) return false;
      if (this._statusFilter && v.status !== this._statusFilter) return false;
      if (this._typeFilter && v.type !== this._typeFilter) return false;
      return true;
    });
    this._refreshContent();
  }

  _refreshContent() {
    const c = document.getElementById('v-content');
    if (c) c.innerHTML = this._view === 'table' ? this._renderTable() : this._renderGrid();
  }

  _showDetail(vesselId) {
    const vessel = this._all.find(v => v.id === vesselId);
    if (!vessel) return;
    const c = document.getElementById('v-content');
    if (c) {
      c.innerHTML = this._renderDetail(vessel);
      c.querySelector('#v-back')?.addEventListener('click', () => {
        this._selected = null;
        this._refreshContent();
      });
    }
  }

  _bindEvents(container) {
    container.querySelector('#v-search')?.addEventListener('input', e => { this._search = e.target.value; this._applyFilters(); });
    container.querySelector('#v-status')?.addEventListener('change', e => { this._statusFilter = e.target.value; this._applyFilters(); });
    container.querySelector('#v-type')?.addEventListener('change', e => { this._typeFilter = e.target.value; this._applyFilters(); });
    container.querySelector('#v-view-grid')?.addEventListener('click', () => {
      this._view = 'grid';
      container.querySelector('#v-view-grid')?.classList.add('active');
      container.querySelector('#v-view-table')?.classList.remove('active');
      this._refreshContent();
    });
    container.querySelector('#v-view-table')?.addEventListener('click', () => {
      this._view = 'table';
      container.querySelector('#v-view-table')?.classList.add('active');
      container.querySelector('#v-view-grid')?.classList.remove('active');
      this._refreshContent();
    });

    ['all', 'in_port', 'approaching', 'underway'].forEach(s => {
      container.querySelector(`#vf-${s}`)?.addEventListener('click', () => {
        this._statusFilter = (s === 'all') ? '' : (this._statusFilter === s ? '' : s);
        const sel = container.querySelector('#v-status');
        if (sel) sel.value = this._statusFilter;
        this._applyFilters();
      });
    });

    document.getElementById('v-content')?.addEventListener('click', e => {
      const card = e.target.closest('[data-v-id]');
      if (card) this._showDetail(card.dataset.vId);
    });
  }

  destroy() {}
}

function _vColor(status) {
  return { in_port: '#00A651', approaching: '#17a2b8', underway: '#6c757d', departing: '#ffa500', anchored: '#0052CC' }[status] || '#6c757d';
}
