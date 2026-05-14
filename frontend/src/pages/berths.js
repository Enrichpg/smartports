/**
 * Berths Page — Full berth list with filters, pagination, and stats
 */

import { apiClient } from '../services/api.js';
import { EmptyState, LoadingSkeleton, StatusBadge } from '../components/base.js';
import { getAllBerths, PORTS } from '../services/mock-data.js';
import { formatDate } from '../utils/helpers.js';
import { t } from '../services/i18n.js';

export class BerthsPage {
  constructor() {
    this.pageId = 'berths';
    this._all = []; this._filtered = [];
    this._search = ''; this._statusFilter = ''; this._portFilter = ''; this._view = 'table';
    this._page = 1; this._perPage = 25;
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="p-4">' + LoadingSkeleton({ lines: 8 }) + '</div>';
    this._all = await this._loadBerths();
    this._filtered = this._all;
    container.innerHTML = this._render();
    this._bindEvents(container);
  }

  async _loadBerths() {
    try {
      const data = await apiClient.getBerths(null, null, 200);
      const arr = data.items || data || [];
      if (arr.length > 0) return arr.map(b => ({
        id: b.id || b.berth_id, name: b.name || b.berth_name || 'Muelle',
        portId: b.port_id || b.portId, portName: b.port_name || b.portName || 'Puerto',
        status: b.status || b.berth_status || 'free',
        type: b.type || b.berth_type || 'general',
        length: b.length || b.max_vessel_length || 0,
        depth: b.depth || b.water_depth || 0,
        vesselName: b.vessel_name || b.vesselName || null,
        etd: b.etd || b.expected_departure || null,
        eta: b.eta || b.expected_arrival || null,
        occupancyPct: b.occupancy_pct || b.occupancyPct || 0,
        lastActivity: b.last_activity || b.lastActivity || new Date().toISOString(),
      }));
    } catch {}
    return getAllBerths();
  }

  _render() {
    const free = this._all.filter(b => b.status === 'free').length;
    const occ = this._all.filter(b => b.status === 'occupied').length;
    const res = this._all.filter(b => b.status === 'reserved').length;
    const mnt = this._all.filter(b => b.status === 'maintenance').length;
    return `
      <div class="page-header">
        <div>
          <div class="page-title"><i class="fas fa-ship"></i> ${t('page.berths')}</div>
          <div class="page-subtitle">${this._all.length} ${t('berths.col.name').toLowerCase()} · ${t('nav.ports')}</div>
        </div>
        <button class="btn btn-sm btn-outline-secondary" id="berths-export-csv">
          <i class="fas fa-file-csv me-1"></i>${t('berths.export_csv')}
        </button>
      </div>
      <div class="row g-3 mb-3">
        <div class="col-6 col-lg-3"><div class="sp-card" style="cursor:pointer" id="filter-free"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#00A651">${free}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('berths.kpi.free')}</div></div></div></div>
        <div class="col-6 col-lg-3"><div class="sp-card" style="cursor:pointer" id="filter-occupied"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#dc3545">${occ}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('berths.kpi.occupied')}</div></div></div></div>
        <div class="col-6 col-lg-3"><div class="sp-card" style="cursor:pointer" id="filter-reserved"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#ffa500">${res}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('berths.kpi.reserved')}</div></div></div></div>
        <div class="col-6 col-lg-3"><div class="sp-card" style="cursor:pointer" id="filter-maintenance"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#6c757d">${mnt}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('berths.kpi.maintenance')}</div></div></div></div>
      </div>
      <div class="sp-filters">
        <div class="sp-filter-search"><label>${t('ui.search')}</label><input class="form-control form-control-sm" id="berths-search" placeholder="${t('berths.col.name')}, ${t('berths.col.vessel')}..."></div>
        <div class="sp-filter-group">
          <label>${t('berths.col.status')}</label>
          <select class="form-select form-select-sm" id="berths-status">
            <option value="">${t('ui.all')}</option><option value="free">${t('berths.kpi.free')}</option><option value="occupied">${t('berths.kpi.occupied')}</option><option value="reserved">${t('berths.kpi.reserved')}</option><option value="maintenance">${t('berths.kpi.maintenance')}</option>
          </select>
        </div>
        <div class="sp-filter-group">
          <label>${t('berths.col.port')}</label>
          <select class="form-select form-select-sm" id="berths-port">
            <option value="">${t('ui.all')}</option>
            ${PORTS.map(p => `<option value="${p.id}">${p.shortName}</option>`).join('')}
          </select>
        </div>
        <div class="sp-filter-group">
          <label>${t('ui.per_page')}</label>
          <select class="form-select form-select-sm" id="berths-perpage">
            <option value="10">10</option><option value="25" selected>25</option><option value="50">50</option>
          </select>
        </div>
      </div>
      <div id="berths-content">${this._renderTable()}</div>
    `;
  }

  _renderTable() {
    const items = this._paginate(this._filtered);
    if (!this._filtered.length) return EmptyState({ icon: 'fa-ship', title: t('ui.no_data'), message: t('ui.no_data') });
    return `
      <div class="sp-card">
        <div class="sp-table-wrapper">
          <table class="sp-table">
            <thead><tr>
              <th>${t('berths.col.name')}</th><th>${t('berths.col.port')}</th><th>${t('berths.col.status')}</th><th>${t('berths.col.type')}</th>
              <th>${t('berths.col.length')}</th><th>${t('berths.col.depth')}</th><th>${t('berths.col.vessel')}</th><th>${t('berths.col.etd')}</th>
            </tr></thead>
            <tbody>
              ${items.map(b => `
                <tr data-nav-page="berth-detail" data-berth-id="${b.id}">
                  <td><strong>${b.name}</strong><br><small class="text-muted">${b.id}</small></td>
                  <td><span data-nav-page="port-detail" data-port-id="${b.portId}" style="color:var(--sp-primary);cursor:pointer">${b.portName}</span></td>
                  <td><span class="sp-badge ${b.status}">${_statusLabel(b.status)}</span></td>
                  <td>${b.type}</td>
                  <td>${b.length}m</td>
                  <td>${b.depth}m</td>
                  <td>${b.vesselName ? `<i class="fas fa-ship me-1 text-muted"></i>${b.vesselName}` : '<span class="text-muted">—</span>'}</td>
                  <td>${b.etd ? formatDate(b.etd, 'medium') : '<span class="text-muted">—</span>'}</td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>
        <div class="px-4 pb-3">
          ${this._renderPagination()}
        </div>
      </div>
    `;
  }

  _renderPagination() {
    const total = this._filtered.length;
    const pages = Math.ceil(total / this._perPage);
    if (pages <= 1) return `<div style="font-size:0.82rem;color:var(--sp-text-muted);padding-top:12px">Mostrando ${total} atraques</div>`;
    const btns = [];
    btns.push(`<button class="sp-page-btn" id="pg-prev" ${this._page <= 1 ? 'disabled' : ''}><i class="fas fa-chevron-left"></i></button>`);
    for (let i = 1; i <= Math.min(pages, 7); i++) {
      btns.push(`<button class="sp-page-btn ${i === this._page ? 'active' : ''}" data-pg="${i}">${i}</button>`);
    }
    if (pages > 7) btns.push(`<span style="padding:0 4px;color:var(--sp-text-muted)">...</span><button class="sp-page-btn ${pages === this._page ? 'active' : ''}" data-pg="${pages}">${pages}</button>`);
    btns.push(`<button class="sp-page-btn" id="pg-next" ${this._page >= pages ? 'disabled' : ''}><i class="fas fa-chevron-right"></i></button>`);
    btns.push(`<span class="sp-per-page">Pág. ${this._page}/${pages} · ${total} atraques</span>`);
    return `<div class="sp-pagination">${btns.join('')}</div>`;
  }

  _paginate(items) {
    const start = (this._page - 1) * this._perPage;
    return items.slice(start, start + this._perPage);
  }

  _applyFilters() {
    this._page = 1;
    this._filtered = this._all.filter(b => {
      if (this._search) {
        const q = this._search.toLowerCase();
        if (!b.name.toLowerCase().includes(q) && !(b.vesselName || '').toLowerCase().includes(q) && !b.portName.toLowerCase().includes(q)) return false;
      }
      if (this._statusFilter && b.status !== this._statusFilter) return false;
      if (this._portFilter && b.portId !== this._portFilter) return false;
      return true;
    });
    const content = document.getElementById('berths-content');
    if (content) content.innerHTML = this._renderTable();
    this._bindPaginationEvents();
  }

  _exportCSV() {
    const headers = ['ID', t('berths.col.name'), t('berths.col.port'), t('berths.col.status'), t('berths.col.type'), `${t('berths.col.length')} (m)`, `${t('berths.col.depth')} (m)`, t('berths.col.vessel'), t('berths.col.etd')];
    const rows = this._filtered.map(b => [
      b.id, b.name, b.portName, b.status, b.type, b.length, b.depth,
      b.vesselName || '', b.etd || '',
    ]);
    const csv = [headers, ...rows].map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `smartport-atraques-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  _bindEvents(container) {
    container.querySelector('#berths-export-csv')?.addEventListener('click', () => this._exportCSV());
    container.querySelector('#berths-search')?.addEventListener('input', e => { this._search = e.target.value; this._applyFilters(); });
    container.querySelector('#berths-status')?.addEventListener('change', e => { this._statusFilter = e.target.value; this._applyFilters(); });
    container.querySelector('#berths-port')?.addEventListener('change', e => { this._portFilter = e.target.value; this._applyFilters(); });
    container.querySelector('#berths-perpage')?.addEventListener('change', e => { this._perPage = +e.target.value; this._applyFilters(); });

    ['free','occupied','reserved','maintenance'].forEach(s => {
      container.querySelector(`#filter-${s}`)?.addEventListener('click', () => {
        this._statusFilter = this._statusFilter === s ? '' : s;
        const sel = container.querySelector('#berths-status');
        if (sel) sel.value = this._statusFilter;
        this._applyFilters();
      });
    });

    this._bindPaginationEvents();
  }

  _bindPaginationEvents() {
    const content = document.getElementById('berths-content');
    if (!content) return;
    content.addEventListener('click', e => {
      const btn = e.target.closest('[data-pg]');
      if (btn) { this._page = +btn.dataset.pg; const c = document.getElementById('berths-content'); if (c) c.innerHTML = this._renderTable(); this._bindPaginationEvents(); return; }
      if (e.target.closest('#pg-prev') && this._page > 1) { this._page--; const c = document.getElementById('berths-content'); if (c) c.innerHTML = this._renderTable(); this._bindPaginationEvents(); }
      if (e.target.closest('#pg-next')) { const pages = Math.ceil(this._filtered.length / this._perPage); if (this._page < pages) { this._page++; const c = document.getElementById('berths-content'); if (c) c.innerHTML = this._renderTable(); this._bindPaginationEvents(); } }
    }, { once: true });
  }

  destroy() {}
}

function _statusLabel(s) {
  return {
    free: t('berths.kpi.free'), occupied: t('berths.kpi.occupied'),
    reserved: t('berths.kpi.reserved'), maintenance: t('berths.kpi.maintenance'),
  }[s] || s;
}
