/**
 * Port Calls Page — Timeline and table of vessel port calls
 */

import { apiClient } from '../services/api.js';
import { EmptyState, LoadingSkeleton } from '../components/base.js';
import { generatePortCalls, PORTS } from '../services/mock-data.js';
import { formatDate } from '../utils/helpers.js';

const STATE_LABELS = { active: 'Activa', authorized: 'Autorizada', pending: 'Pendiente', completed: 'Completada', rejected: 'Rechazada' };
const TYPE_LABELS = { container: 'Contenedor', bulk: 'Graneles', tanker: 'Tanquero', roro: 'Ro-Ro', general: 'Carga general', cruise: 'Crucero', fishing: 'Pesca' };

export class PortCallsPage {
  constructor() {
    this.pageId = 'port-calls';
    this._all = []; this._filtered = [];
    this._search = ''; this._stateFilter = ''; this._portFilter = ''; this._view = 'timeline';
    this._page = 1; this._perPage = 15;
    this._charts = {};
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="p-4">' + LoadingSkeleton({ lines: 8 }) + '</div>';
    this._all = await this._loadPortCalls();
    this._filtered = this._all;
    container.innerHTML = this._render();
    this._initChart();
    this._bindEvents(container);
  }

  async _loadPortCalls() {
    try {
      const data = await apiClient.getPortCalls(null, 50);
      const arr = data.items || data || [];
      if (arr.length > 0) return arr.map(pc => ({
        id: pc.id || pc.portcall_id, vesselName: pc.vessel_name || pc.vesselName || 'Buque',
        vesselType: pc.vessel_type || pc.vesselType || 'general',
        portId: pc.port_id || pc.portId, portName: pc.port_name || pc.portName || 'Puerto',
        berthName: pc.berth_name || pc.berthName || '—',
        state: pc.state || pc.portcall_status || 'pending',
        eta: pc.eta || pc.expected_arrival, etd: pc.etd || pc.expected_departure,
        actualArrival: pc.actual_arrival || pc.actualArrival,
        durationHours: pc.duration_hours || pc.durationHours || 0,
        captain: pc.captain || '—', cargo: pc.cargo || '—',
        grossTonnage: pc.gross_tonnage || pc.grossTonnage || 0,
      }));
    } catch {}
    return generatePortCalls(30);
  }

  _render() {
    const byState = { active: 0, authorized: 0, pending: 0, completed: 0 };
    this._all.forEach(pc => { if (byState[pc.state] !== undefined) byState[pc.state]++; });
    return `
      <div class="page-header">
        <div class="page-title"><i class="fas fa-calendar-alt"></i> Escalas Portuarias</div>
        <div class="page-subtitle">${this._all.length} escalas registradas · Últimas 72 horas</div>
      </div>
      <div class="row g-3 mb-3">
        <div class="col-6 col-md-3"><div class="sp-card" id="pcf-active" style="cursor:pointer"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#00A651">${byState.active}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Activas</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" id="pcf-authorized" style="cursor:pointer"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#17a2b8">${byState.authorized}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Autorizadas</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" id="pcf-pending" style="cursor:pointer"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#ffa500">${byState.pending}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Pendientes</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" id="pcf-completed" style="cursor:pointer"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#6c757d">${byState.completed}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Completadas</div></div></div></div>
      </div>

      <div class="row g-3 mb-3">
        <div class="col-lg-8">
          <div class="sp-filters" style="margin-bottom:0">
            <div class="sp-filter-search"><label>Buscar buque</label><input class="form-control form-control-sm" id="pc-search" placeholder="Nombre del buque..."></div>
            <div class="sp-filter-group">
              <label>Estado</label>
              <select class="form-select form-select-sm" id="pc-state">
                <option value="">Todos</option>
                ${Object.entries(STATE_LABELS).map(([v,l]) => `<option value="${v}">${l}</option>`).join('')}
              </select>
            </div>
            <div class="sp-filter-group">
              <label>Puerto</label>
              <select class="form-select form-select-sm" id="pc-port">
                <option value="">Todos</option>
                ${PORTS.map(p => `<option value="${p.id}">${p.shortName}</option>`).join('')}
              </select>
            </div>
            <div class="d-flex align-items-end gap-2">
              <div class="view-toggle">
                <button class="view-toggle-btn active" id="pc-view-timeline" title="Timeline"><i class="fas fa-stream"></i></button>
                <button class="view-toggle-btn" id="pc-view-table" title="Tabla"><i class="fas fa-table"></i></button>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="sp-card"><div class="sp-card-body p-2"><canvas id="pc-state-chart" height="90"></canvas></div></div>
        </div>
      </div>

      <div id="pc-content">${this._renderTimeline()}</div>
    `;
  }

  _renderTimeline() {
    const items = this._paginate(this._filtered);
    if (!this._filtered.length) return EmptyState({ icon: 'fa-calendar', title: 'Sin escalas', message: 'No hay escalas con los filtros aplicados' });
    return `
      <div class="sp-timeline">
        ${items.map(pc => `
          <div class="timeline-item" data-pc-id="${pc.id}">
            <div class="timeline-dot ${pc.state}"></div>
            <div class="timeline-content">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px">
                <div>
                  <div class="timeline-title"><i class="fas fa-ship me-2"></i>${pc.vesselName}</div>
                  <div class="timeline-subtitle">${pc.portName} · ${pc.berthName}</div>
                </div>
                <span class="sp-badge ${pc.state}">${STATE_LABELS[pc.state] || pc.state}</span>
              </div>
              <div class="timeline-meta">
                <span><i class="fas fa-arrow-right"></i> ETA: ${formatDate(pc.eta, 'medium')}</span>
                <span><i class="fas fa-arrow-left"></i> ETD: ${formatDate(pc.etd, 'medium')}</span>
                <span><i class="fas fa-clock"></i> ${pc.durationHours}h</span>
                <span><i class="fas fa-boxes"></i> ${pc.cargo}</span>
                <span><i class="fas fa-weight"></i> ${(pc.grossTonnage || 0).toLocaleString('es-ES')} GT</span>
                <span title="${TYPE_LABELS[pc.vesselType] || pc.vesselType}"><i class="fas fa-tag"></i> ${TYPE_LABELS[pc.vesselType] || pc.vesselType}</span>
              </div>
            </div>
          </div>`).join('')}
      </div>
      ${this._renderPagination()}
    `;
  }

  _renderTableView() {
    const items = this._paginate(this._filtered);
    if (!this._filtered.length) return EmptyState({ icon: 'fa-calendar', title: 'Sin escalas' });
    return `
      <div class="sp-card">
        <div class="sp-table-wrapper">
          <table class="sp-table">
            <thead><tr><th>Buque</th><th>Puerto</th><th>Atraque</th><th>Estado</th><th>ETA</th><th>Duración</th><th>Carga</th></tr></thead>
            <tbody>
              ${items.map(pc => `
                <tr>
                  <td><strong>${pc.vesselName}</strong><br><small class="text-muted">${TYPE_LABELS[pc.vesselType] || pc.vesselType}</small></td>
                  <td>${pc.portName}</td>
                  <td>${pc.berthName}</td>
                  <td><span class="sp-badge ${pc.state}">${STATE_LABELS[pc.state] || pc.state}</span></td>
                  <td>${formatDate(pc.eta, 'medium')}</td>
                  <td>${pc.durationHours}h</td>
                  <td>${pc.cargo}</td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>
        <div class="px-4 pb-3">${this._renderPagination()}</div>
      </div>`;
  }

  _renderPagination() {
    const total = this._filtered.length;
    const pages = Math.ceil(total / this._perPage);
    if (pages <= 1) return `<div style="font-size:0.82rem;color:var(--sp-text-muted);padding-top:12px">${total} escalas</div>`;
    const btns = [];
    btns.push(`<button class="sp-page-btn" id="pcpg-prev" ${this._page<=1?'disabled':''}><i class="fas fa-chevron-left"></i></button>`);
    for (let i=1;i<=Math.min(pages,7);i++) btns.push(`<button class="sp-page-btn ${i===this._page?'active':''}" data-pg="${i}">${i}</button>`);
    if (pages>7) btns.push(`<span style="padding:0 4px">...</span><button class="sp-page-btn ${pages===this._page?'active':''}" data-pg="${pages}">${pages}</button>`);
    btns.push(`<button class="sp-page-btn" id="pcpg-next" ${this._page>=pages?'disabled':''}><i class="fas fa-chevron-right"></i></button>`);
    btns.push(`<span class="sp-per-page">Pág. ${this._page}/${pages}</span>`);
    return `<div class="sp-pagination">${btns.join('')}</div>`;
  }

  _paginate(items) { const s=(this._page-1)*this._perPage; return items.slice(s,s+this._perPage); }

  _applyFilters() {
    this._page=1;
    this._filtered=this._all.filter(pc => {
      if (this._search && !pc.vesselName.toLowerCase().includes(this._search.toLowerCase())) return false;
      if (this._stateFilter && pc.state !== this._stateFilter) return false;
      if (this._portFilter && pc.portId !== this._portFilter) return false;
      return true;
    });
    this._refreshContent();
  }

  _refreshContent() {
    const c = document.getElementById('pc-content');
    if (!c) return;
    c.innerHTML = this._view === 'table' ? this._renderTableView() : this._renderTimeline();
    c.addEventListener('click', e => {
      const btn = e.target.closest('[data-pg]');
      if (btn) { this._page=+btn.dataset.pg; this._refreshContent(); return; }
      if (e.target.closest('#pcpg-prev') && this._page>1) { this._page--; this._refreshContent(); }
      if (e.target.closest('#pcpg-next')) { const p=Math.ceil(this._filtered.length/this._perPage); if(this._page<p){this._page++;this._refreshContent();} }
    }, { once: true });
  }

  _initChart() {
    if (!window.Chart) return;
    const el = document.getElementById('pc-state-chart');
    if (!el) return;
    const byState = ['active','authorized','pending','completed'].map(s => this._all.filter(pc => pc.state===s).length);
    this._charts.state = new window.Chart(el, {
      type: 'doughnut',
      data: { labels: ['Activa','Autorizada','Pendiente','Completada'], datasets: [{ data: byState, backgroundColor: ['#00A651','#17a2b8','#ffa500','#6c757d'], borderWidth: 0 }] },
      options: { responsive:true, maintainAspectRatio:false, cutout:'70%', plugins:{ legend:{ position:'right', labels:{ font:{size:10}, boxWidth:8, color: document.documentElement.getAttribute('data-bs-theme')==='dark'?'#8b949e':'#6c757d' } } } }
    });
  }

  _bindEvents(container) {
    container.querySelector('#pc-search')?.addEventListener('input', e => { this._search=e.target.value; this._applyFilters(); });
    container.querySelector('#pc-state')?.addEventListener('change', e => { this._stateFilter=e.target.value; this._applyFilters(); });
    container.querySelector('#pc-port')?.addEventListener('change', e => { this._portFilter=e.target.value; this._applyFilters(); });
    container.querySelector('#pc-view-timeline')?.addEventListener('click', () => { this._view='timeline'; container.querySelector('#pc-view-timeline')?.classList.add('active'); container.querySelector('#pc-view-table')?.classList.remove('active'); this._refreshContent(); });
    container.querySelector('#pc-view-table')?.addEventListener('click', () => { this._view='table'; container.querySelector('#pc-view-table')?.classList.add('active'); container.querySelector('#pc-view-timeline')?.classList.remove('active'); this._refreshContent(); });
    ['active','authorized','pending','completed'].forEach(s => {
      container.querySelector(`#pcf-${s}`)?.addEventListener('click', () => {
        this._stateFilter = this._stateFilter===s?'':s;
        const sel=container.querySelector('#pc-state'); if(sel) sel.value=this._stateFilter;
        this._applyFilters();
      });
    });
  }

  destroy() { Object.values(this._charts).forEach(c => { try{c.destroy();}catch{} }); this._charts={}; }
}
