/**
 * Ports Page — Grid view of all 6 Galician ports
 */

import { apiClient } from '../services/api.js';
import { EmptyState, LoadingSkeleton } from '../components/base.js';
import { PORTS } from '../services/mock-data.js';

export class PortsPage {
  constructor() { this.pageId = 'ports'; this._search = ''; this._filter = ''; this._typeFilter = ''; this._view = 'grid'; this._ports = []; }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="p-4">' + LoadingSkeleton({ lines: 6 }) + '</div>';
    this._ports = await this._loadPorts();
    container.innerHTML = this._render(this._ports);
    this._bindEvents(container);
  }

  async _loadPorts() {
    try {
      const data = await apiClient.getPorts(20);
      const arr = data.items || data || [];
      if (arr.length > 0) return arr.map(p => ({
        id: p.id || p.port_id, name: p.name || p.port_name || 'Puerto',
        shortName: (p.name || p.port_name || '').replace('Puerto de ', ''),
        status: p.status || p.port_status || 'active', type: p.type || 'commercial',
        totalBerths: p.total_berths || p.totalBerths || 0,
        freeBerths: p.free_berths || p.freeBerths || 0,
        occupiedBerths: p.occupied_berths || p.occupiedBerths || 0,
        reservedBerths: p.reserved_berths || p.reservedBerths || 0,
        occupancyPct: p.occupancy_pct || p.occupancyPct || 0,
        vessels24h: p.vessels24h || { in: 0, out: 0 }, description: p.description || '',
      }));
    } catch {}
    return PORTS;
  }

  _render(ports) {
    const active = ports.filter(p => p.status === 'active').length;
    return `
      <div class="page-header">
        <div class="page-title"><i class="fas fa-anchor"></i> Puertos de Galicia</div>
        <div class="page-subtitle">${ports.length} puertos · Red portuaria gestionada por la Autoridad Portuaria</div>
      </div>
      <div class="sp-filters">
        <div class="sp-filter-search">
          <label>Buscar</label>
          <input class="form-control form-control-sm" id="ports-search" placeholder="Nombre del puerto...">
        </div>
        <div class="sp-filter-group">
          <label>Estado</label>
          <select class="form-select form-select-sm" id="ports-filter-status">
            <option value="">Todos</option><option value="active">Activos</option><option value="maintenance">Mantenimiento</option>
          </select>
        </div>
        <div class="sp-filter-group">
          <label>Tipo</label>
          <select class="form-select form-select-sm" id="ports-filter-type">
            <option value="">Todos</option><option value="commercial">Comercial</option><option value="industrial">Industrial</option><option value="fishing">Pesquero</option>
          </select>
        </div>
        <div class="d-flex align-items-end gap-2">
          <div class="view-toggle">
            <button class="view-toggle-btn active" id="view-grid" title="Grid"><i class="fas fa-th-large"></i></button>
            <button class="view-toggle-btn" id="view-table" title="Tabla"><i class="fas fa-list"></i></button>
          </div>
        </div>
      </div>
      <div class="row g-3 mb-3">
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:var(--sp-primary)">${active}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Activos</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#00A651">${ports.reduce((s,p)=>s+p.freeBerths,0)}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Atraques libres</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#dc3545">${ports.reduce((s,p)=>s+p.occupiedBerths,0)}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Ocupados</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#ffa500">${Math.round(ports.reduce((s,p)=>s+p.occupancyPct,0)/ports.length)}%</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Ocupación media</div></div></div></div>
      </div>
      <div id="ports-content">${this._renderGrid(ports)}</div>
    `;
  }

  _renderGrid(ports) {
    const f = this._filter_(ports);
    if (!f.length) return EmptyState({ icon: 'fa-anchor', title: 'Sin puertos', message: 'No hay puertos con los filtros aplicados' });
    const typeLabels = { commercial: 'Puerto Comercial', industrial: 'Puerto Industrial', fishing: 'Puerto Pesquero' };
    return `<div class="port-grid">${f.map(p => {
      const level = p.occupancyPct >= 80 ? 'high' : p.occupancyPct >= 50 ? 'medium' : 'low';
      return `
        <div class="port-card" data-nav-page="port-detail" data-port-id="${p.id}">
          <div class="port-card-header">
            <div><div class="port-card-name">${p.name}</div><div class="port-card-type">${typeLabels[p.type] || p.type}</div></div>
            <span class="sp-badge ${p.status}">${p.status === 'active' ? 'Activo' : 'Mantenimiento'}</span>
          </div>
          <div style="margin:12px 0 6px">
            <div style="display:flex;justify-content:space-between;font-size:0.78rem;color:var(--sp-text-muted);margin-bottom:5px"><span>Ocupación</span><span>${p.occupancyPct}%</span></div>
            <div class="sp-progress"><div class="sp-progress-bar ${level}" style="width:${p.occupancyPct}%"></div></div>
          </div>
          <div class="port-card-berths">
            <div class="berth-stat free"><div class="berth-stat-value">${p.freeBerths}</div><div class="berth-stat-label">Libres</div></div>
            <div class="berth-stat occupied"><div class="berth-stat-value">${p.occupiedBerths}</div><div class="berth-stat-label">Ocupados</div></div>
            <div class="berth-stat reserved"><div class="berth-stat-value">${p.reservedBerths}</div><div class="berth-stat-label">Reservados</div></div>
            <div class="berth-stat"><div class="berth-stat-value">${p.totalBerths}</div><div class="berth-stat-label">Total</div></div>
          </div>
          <div class="port-card-footer">
            <span><i class="fas fa-arrow-down text-success me-1"></i>${p.vessels24h?.in || 0} entradas</span>
            <span><i class="fas fa-arrow-up text-warning me-1"></i>${p.vessels24h?.out || 0} salidas</span>
            <span style="color:var(--sp-primary)"><i class="fas fa-chevron-right"></i> Ver detalle</span>
          </div>
        </div>`;
    }).join('')}</div>`;
  }

  _renderTable(ports) {
    const f = this._filter_(ports);
    if (!f.length) return EmptyState({ icon: 'fa-anchor', title: 'Sin puertos' });
    return `<div class="sp-card"><div class="sp-table-wrapper"><table class="sp-table">
      <thead><tr><th>Puerto</th><th>Tipo</th><th>Estado</th><th>Ocupación</th><th>Libres</th><th>Ocupados</th><th>Entradas 24h</th></tr></thead>
      <tbody>${f.map(p => `
        <tr data-nav-page="port-detail" data-port-id="${p.id}">
          <td><strong>${p.name}</strong></td><td>${p.type}</td>
          <td><span class="sp-badge ${p.status}">${p.status === 'active' ? 'Activo' : 'Mantenimiento'}</span></td>
          <td><div style="display:flex;align-items:center;gap:8px"><div class="sp-progress" style="width:80px"><div class="sp-progress-bar ${p.occupancyPct>=80?'high':p.occupancyPct>=50?'medium':'low'}" style="width:${p.occupancyPct}%"></div></div><small>${p.occupancyPct}%</small></div></td>
          <td class="text-success">${p.freeBerths}</td><td class="text-danger">${p.occupiedBerths}</td><td>${p.vessels24h?.in||0}</td>
        </tr>`).join('')}
      </tbody></table></div></div>`;
  }

  _filter_(ports) {
    return ports.filter(p => {
      if (this._search && !p.name.toLowerCase().includes(this._search.toLowerCase())) return false;
      if (this._filter && p.status !== this._filter) return false;
      if (this._typeFilter && p.type !== this._typeFilter) return false;
      return true;
    });
  }

  _bindEvents(container) {
    const refresh = () => {
      const content = document.getElementById('ports-content');
      if (!content) return;
      content.innerHTML = this._view === 'table' ? this._renderTable(this._ports) : this._renderGrid(this._ports);
    };
    container.querySelector('#ports-search')?.addEventListener('input', e => { this._search = e.target.value; refresh(); });
    container.querySelector('#ports-filter-status')?.addEventListener('change', e => { this._filter = e.target.value; refresh(); });
    container.querySelector('#ports-filter-type')?.addEventListener('change', e => { this._typeFilter = e.target.value; refresh(); });
    container.querySelector('#view-grid')?.addEventListener('click', () => { this._view = 'grid'; container.querySelector('#view-grid')?.classList.add('active'); container.querySelector('#view-table')?.classList.remove('active'); refresh(); });
    container.querySelector('#view-table')?.addEventListener('click', () => { this._view = 'table'; container.querySelector('#view-table')?.classList.add('active'); container.querySelector('#view-grid')?.classList.remove('active'); refresh(); });
  }

  destroy() {}
}
