/**
 * Alerts Page — Global alert center with filters, timeline, and charts
 */

import { apiClient } from '../services/api.js';
import { EmptyState, LoadingSkeleton } from '../components/base.js';
import { generateAlerts, PORTS } from '../services/mock-data.js';
import { formatDate } from '../utils/helpers.js';
import { t } from '../services/i18n.js';

function SEV_LABELS() {
  return {
    critical: t('alerts.sev.critical'), high: t('alerts.sev.high'),
    medium: t('alerts.sev.medium'), low: t('alerts.sev.low'),
  };
}
const SEV_COLORS = { critical: '#dc3545', high: '#fd7e14', medium: '#ffc107', low: '#17a2b8' };
function TYPE_LABELS() {
  return {
    SECURITY: t('alerts.type.SECURITY'), OPERATIONAL: t('alerts.type.OPERATIONAL'),
    ENVIRONMENTAL: t('alerts.type.ENVIRONMENTAL'), TECHNICAL: t('alerts.type.TECHNICAL'),
    WEATHER_WIND: t('alerts.type.WEATHER_WIND'), VESSEL_DELAYED: t('alerts.type.VESSEL_DELAYED'),
    WEATHER_WAVE: t('alerts.type.WEATHER_WAVE'), WEATHER_VISIBILITY: t('alerts.type.WEATHER_VISIBILITY'),
    ETA_DEVIATION: t('alerts.type.ETA_DEVIATION'),
  };
}

export class AlertsPage {
  constructor() {
    this.pageId = 'alerts';
    this._all = []; this._filtered = [];
    this._search = ''; this._sevFilter = ''; this._statusFilter = 'active';
    this._portFilter = ''; this._typeFilter = '';
    this._charts = {};
    this._page = 1; this._perPage = 20;
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="p-4">' + LoadingSkeleton({ lines: 8 }) + '</div>';
    this._all = await this._loadAlerts();
    this._applyFilter();
    container.innerHTML = this._render();
    this._initChart();
    this._bindEvents(container);
  }

  async _loadAlerts() {
    try {
      const data = await apiClient.getAlerts(null, 200);
      const arr = data?.alerts || data?.items || data || [];
      if (arr.length > 0) return arr.map(a => ({
        id: a.id || a.alert_id,
        type: a.type || a.alert_type || 'OPERATIONAL',
        severity: a.severity || 'medium',
        status: a.status || 'active',
        portId: a.port_id || a.portId,
        portName: a.port_name || a.portName || 'Puerto',
        berthId: a.berth_id || a.berthId || null,
        message: a.message || a.title || 'Alerta',
        description: a.description || '',
        timestamp: a.timestamp || a.created_at || new Date().toISOString(),
        resolvedAt: a.resolved_at || a.resolvedAt || null,
        assignedTo: a.assigned_to || a.assignedTo || null,
        comments: a.comments || [],
      }));
    } catch {}
    return generateAlerts(40);
  }

  _applyFilter() {
    this._page = 1;
    this._filtered = this._all.filter(a => {
      if (this._search) {
        const q = this._search.toLowerCase();
        if (!a.message.toLowerCase().includes(q) && !a.portName.toLowerCase().includes(q)) return false;
      }
      if (this._sevFilter && a.severity !== this._sevFilter) return false;
      if (this._statusFilter && a.status !== this._statusFilter) return false;
      if (this._portFilter && a.portId !== this._portFilter) return false;
      if (this._typeFilter && a.type !== this._typeFilter) return false;
      return true;
    });
  }

  _render() {
    const active = this._all.filter(a => a.status === 'active').length;
    const resolved = this._all.filter(a => a.status === 'resolved').length;
    const critical = this._all.filter(a => a.severity === 'critical' && a.status === 'active').length;
    const high = this._all.filter(a => a.severity === 'high' && a.status === 'active').length;
    const sl = SEV_LABELS(); const tl = TYPE_LABELS();

    return `
      <div class="page-header">
        <div>
          <div class="page-title"><i class="fas fa-exclamation-triangle"></i> ${t('page.alerts')}</div>
          <div class="page-subtitle">${this._all.length} · ${t('dash.section.alerts')}</div>
        </div>
        <button class="btn btn-sm btn-outline-secondary" onclick="window.print()">
          <i class="fas fa-print me-1"></i>${t('alerts.export_pdf')}
        </button>
      </div>
      <div class="print-header">SmartPort Galicia — ${t('page.alerts')} · ${new Date().toLocaleDateString('es-ES', { dateStyle: 'long' })}</div>

      <div class="row g-3 mb-3">
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer;border-left:3px solid #dc3545" id="af-active"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#dc3545">${active}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('alerts.kpi.active')}</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer;border-left:3px solid #fd7e14" id="af-critical"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#fd7e14">${critical + high}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('alerts.kpi.critical_high')}</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer;border-left:3px solid #00A651" id="af-resolved"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#00A651">${resolved}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('alerts.kpi.resolved')}</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer;border-left:3px solid #6c757d" id="af-all"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#6c757d">${this._all.length}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('alerts.kpi.total')}</div></div></div></div>
      </div>

      <div class="row g-3 mb-3">
        <div class="col-lg-8">
          <div class="sp-filters" style="margin-bottom:0">
            <div class="sp-filter-search"><label>${t('ui.search')}</label><input class="form-control form-control-sm" id="a-search" placeholder="${t('alerts.col.message')}, ${t('alerts.col.port')}..."></div>
            <div class="sp-filter-group">
              <label>${t('alerts.col.severity')}</label>
              <select class="form-select form-select-sm" id="a-sev">
                <option value="">${t('ui.all')}</option>
                ${Object.entries(sl).map(([v,l]) => `<option value="${v}">${l}</option>`).join('')}
              </select>
            </div>
            <div class="sp-filter-group">
              <label>${t('alerts.col.status')}</label>
              <select class="form-select form-select-sm" id="a-status">
                <option value="active" selected>${t('alerts.status_opts.active')}</option>
                <option value="resolved">${t('alerts.status_opts.resolved')}</option>
                <option value="ignored">${t('alerts.status_opts.ignored')}</option>
                <option value="">${t('alerts.status_opts.all')}</option>
              </select>
            </div>
            <div class="sp-filter-group">
              <label>${t('alerts.col.port')}</label>
              <select class="form-select form-select-sm" id="a-port">
                <option value="">${t('ui.all')}</option>
                ${PORTS.map(p => `<option value="${p.id}">${p.shortName}</option>`).join('')}
              </select>
            </div>
            <div class="sp-filter-group">
              <label>${t('alerts.col.type')}</label>
              <select class="form-select form-select-sm" id="a-type">
                <option value="">${t('ui.all')}</option>
                ${Object.entries(tl).map(([v,l]) => `<option value="${v}">${l}</option>`).join('')}
              </select>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="sp-card"><div class="sp-card-body p-2"><canvas id="a-chart" height="90"></canvas></div></div>
        </div>
      </div>

      <div id="a-content">${this._renderList()}</div>
    `;
  }

  _renderList() {
    const items = this._paginate(this._filtered);
    const sl = SEV_LABELS(); const tl = TYPE_LABELS();
    if (!this._filtered.length) return EmptyState({ icon: 'fa-check-circle', title: t('ui.no_data'), message: t('ui.no_data') });
    return `
      <div class="sp-card">
        <div class="sp-table-wrapper">
          <table class="sp-table">
            <thead><tr><th style="width:110px">${t('alerts.col.severity')}</th><th>${t('alerts.col.message')}</th><th>${t('alerts.col.type')}</th><th>${t('alerts.col.port')}</th><th>${t('alerts.col.timestamp')}</th><th>${t('alerts.col.status')}</th><th style="width:100px">${t('alerts.col.actions')}</th></tr></thead>
            <tbody>
              ${items.map(a => `
                <tr class="${a.status === 'resolved' ? 'opacity-75' : ''}">
                  <td>
                    <span style="display:inline-flex;align-items:center;gap:6px">
                      <span style="width:8px;height:8px;border-radius:50%;background:${SEV_COLORS[a.severity] || '#6c757d'};flex-shrink:0"></span>
                      <strong style="font-size:0.8rem">${sl[a.severity] || a.severity}</strong>
                    </span>
                  </td>
                  <td>
                    <div style="font-weight:600;font-size:0.85rem">${a.message}</div>
                    ${a.assignedTo ? `<div style="font-size:0.72rem;color:var(--sp-text-muted)"><i class="fas fa-user me-1"></i>${a.assignedTo}</div>` : ''}
                  </td>
                  <td><span style="font-size:0.78rem">${tl[a.type] || a.type}</span></td>
                  <td><span style="font-size:0.83rem">${a.portName}</span></td>
                  <td><span style="font-size:0.78rem">${formatDate(a.timestamp, 'medium')}</span></td>
                  <td>
                    <span class="sp-badge ${a.status === 'resolved' ? 'active' : a.status === 'ignored' ? 'maintenance' : 'occupied'}" style="font-size:0.68rem">
                      ${a.status === 'resolved' ? t('alerts.alert_resolved') : a.status === 'ignored' ? t('alerts.alert_ignored') : t('alerts.alert_active')}
                    </span>
                  </td>
                  <td>
                    ${a.status === 'active' ? `
                      <button class="btn btn-xs btn-outline-success me-1" style="padding:2px 8px;font-size:0.72rem" onclick="window.showToast('${t('alerts.alert_resolved')}','success')">
                        <i class="fas fa-check"></i>
                      </button>
                      <button class="btn btn-xs btn-outline-secondary" style="padding:2px 8px;font-size:0.72rem" onclick="window.showToast('${t('toast.info')}','info')">
                        <i class="fas fa-user-plus"></i>
                      </button>` : `<span style="font-size:0.72rem;color:var(--sp-text-muted)">${a.resolvedAt ? formatDate(a.resolvedAt, 'short') : '—'}</span>`}
                  </td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>
        <div class="px-4 pb-3">${this._renderPagination()}</div>
      </div>
    `;
  }

  _renderPagination() {
    const total = this._filtered.length;
    const pages = Math.ceil(total / this._perPage);
    if (pages <= 1) return `<div style="font-size:0.82rem;color:var(--sp-text-muted);padding-top:12px">${total} alertas</div>`;
    const btns = [];
    btns.push(`<button class="sp-page-btn" id="apg-prev" ${this._page <= 1 ? 'disabled' : ''}><i class="fas fa-chevron-left"></i></button>`);
    for (let i = 1; i <= Math.min(pages, 7); i++) btns.push(`<button class="sp-page-btn ${i === this._page ? 'active' : ''}" data-pg="${i}">${i}</button>`);
    if (pages > 7) btns.push(`<span style="padding:0 4px">...</span><button class="sp-page-btn ${pages === this._page ? 'active' : ''}" data-pg="${pages}">${pages}</button>`);
    btns.push(`<button class="sp-page-btn" id="apg-next" ${this._page >= pages ? 'disabled' : ''}><i class="fas fa-chevron-right"></i></button>`);
    btns.push(`<span class="sp-per-page">Pág. ${this._page}/${pages}</span>`);
    return `<div class="sp-pagination">${btns.join('')}</div>`;
  }

  _paginate(items) { const s = (this._page - 1) * this._perPage; return items.slice(s, s + this._perPage); }

  _refresh() {
    const c = document.getElementById('a-content');
    if (c) {
      c.innerHTML = this._renderList();
      c.addEventListener('click', e => {
        const btn = e.target.closest('[data-pg]');
        if (btn) { this._page = +btn.dataset.pg; this._refresh(); return; }
        if (e.target.closest('#apg-prev') && this._page > 1) { this._page--; this._refresh(); }
        if (e.target.closest('#apg-next')) { const p = Math.ceil(this._filtered.length / this._perPage); if (this._page < p) { this._page++; this._refresh(); } }
      }, { once: true });
    }
  }

  _initChart() {
    if (!window.Chart) return;
    const el = document.getElementById('a-chart');
    if (!el) return;
    const sevs = ['critical', 'high', 'medium', 'low'];
    const sl = SEV_LABELS();
    const data = sevs.map(s => this._all.filter(a => a.severity === s).length);
    this._charts.sev = new window.Chart(el, {
      type: 'doughnut',
      data: {
        labels: sevs.map(s => sl[s]),
        datasets: [{ data, backgroundColor: Object.values(SEV_COLORS), borderWidth: 0 }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '68%',
        plugins: { legend: { position: 'right', labels: { font: { size: 10 }, boxWidth: 8, color: document.documentElement.getAttribute('data-bs-theme') === 'dark' ? '#8b949e' : '#6c757d' } } }
      }
    });
  }

  _bindEvents(container) {
    container.querySelector('#a-search')?.addEventListener('input', e => { this._search = e.target.value; this._applyFilter(); this._refresh(); });
    container.querySelector('#a-sev')?.addEventListener('change', e => { this._sevFilter = e.target.value; this._applyFilter(); this._refresh(); });
    container.querySelector('#a-status')?.addEventListener('change', e => { this._statusFilter = e.target.value; this._applyFilter(); this._refresh(); });
    container.querySelector('#a-port')?.addEventListener('change', e => { this._portFilter = e.target.value; this._applyFilter(); this._refresh(); });
    container.querySelector('#a-type')?.addEventListener('change', e => { this._typeFilter = e.target.value; this._applyFilter(); this._refresh(); });

    container.querySelector('#af-active')?.addEventListener('click', () => {
      this._statusFilter = 'active'; this._sevFilter = '';
      const s = container.querySelector('#a-status'); if (s) s.value = 'active';
      this._applyFilter(); this._refresh();
    });
    container.querySelector('#af-critical')?.addEventListener('click', () => {
      this._statusFilter = 'active'; this._sevFilter = '';
      const s = container.querySelector('#a-status'); if (s) s.value = 'active';
      this._applyFilter(); this._refresh();
    });
    container.querySelector('#af-resolved')?.addEventListener('click', () => {
      this._statusFilter = 'resolved'; this._sevFilter = '';
      const s = container.querySelector('#a-status'); if (s) s.value = 'resolved';
      this._applyFilter(); this._refresh();
    });
    container.querySelector('#af-all')?.addEventListener('click', () => {
      this._statusFilter = ''; this._sevFilter = '';
      const s = container.querySelector('#a-status'); if (s) s.value = '';
      this._applyFilter(); this._refresh();
    });

    this._refresh();
  }

  destroy() {
    Object.values(this._charts).forEach(c => { try { c.destroy(); } catch {} });
    this._charts = {};
  }
}
