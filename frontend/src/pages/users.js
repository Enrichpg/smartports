/**
 * Users / Teams Page — Personnel management
 */

import { LoadingSkeleton, EmptyState } from '../components/base.js';
import { generateUsers, PORTS } from '../services/mock-data.js';
import { formatDate } from '../utils/helpers.js';

const ROLE_LABELS = {
  port_captain: 'Capitán de Puerto',
  operations_chief: 'Jefe de Operaciones',
  inspector: 'Inspector',
  operator: 'Operador',
  admin: 'Administrador',
};
const ROLE_COLORS = {
  port_captain: '#0052CC',
  operations_chief: '#00A651',
  inspector: '#17a2b8',
  operator: '#ffa500',
  admin: '#dc3545',
};

export class UsersPage {
  constructor() {
    this.pageId = 'users';
    this._all = []; this._filtered = [];
    this._search = ''; this._portFilter = ''; this._roleFilter = ''; this._statusFilter = '';
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="p-4">' + LoadingSkeleton({ lines: 8 }) + '</div>';
    this._all = generateUsers();
    this._filtered = this._all;
    container.innerHTML = this._render();
    this._bindEvents(container);
  }

  _render() {
    const online = this._all.filter(u => u.status === 'online').length;
    return `
      <div class="page-header">
        <div class="page-title"><i class="fas fa-users"></i> Equipos</div>
        <div class="page-subtitle">Personal operativo de la red portuaria de Galicia</div>
      </div>

      <div class="row g-3 mb-3">
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:var(--sp-primary)">${this._all.length}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Total personal</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="uf-online"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#00A651">${online}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Conectados</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="uf-offline"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#6c757d">${this._all.length - online}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Desconectados</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#17a2b8">${PORTS.length}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Puertos cubiertos</div></div></div></div>
      </div>

      <div class="sp-filters">
        <div class="sp-filter-search"><label>Buscar</label><input class="form-control form-control-sm" id="u-search" placeholder="Nombre, email..."></div>
        <div class="sp-filter-group">
          <label>Puerto</label>
          <select class="form-select form-select-sm" id="u-port">
            <option value="">Todos</option>
            ${PORTS.map(p => `<option value="${p.id}">${p.shortName}</option>`).join('')}
          </select>
        </div>
        <div class="sp-filter-group">
          <label>Rol</label>
          <select class="form-select form-select-sm" id="u-role">
            <option value="">Todos</option>
            ${Object.entries(ROLE_LABELS).map(([v,l]) => `<option value="${v}">${l}</option>`).join('')}
          </select>
        </div>
        <div class="sp-filter-group">
          <label>Estado</label>
          <select class="form-select form-select-sm" id="u-status">
            <option value="">Todos</option>
            <option value="online">Conectado</option>
            <option value="offline">Desconectado</option>
          </select>
        </div>
        <div class="d-flex align-items-end">
          <button class="btn btn-sm btn-primary" onclick="window.showToast('Función disponible próximamente','info')">
            <i class="fas fa-user-plus me-1"></i>Añadir
          </button>
        </div>
      </div>

      <div id="u-content">${this._renderCards()}</div>
    `;
  }

  _renderCards() {
    if (!this._filtered.length) return EmptyState({ icon: 'fa-users', title: 'Sin personal', message: 'No hay usuarios con los filtros aplicados' });
    return `<div class="row g-3">${this._filtered.map(u => `
      <div class="col-sm-6 col-lg-4">
        <div class="sp-card h-100">
          <div class="sp-card-body">
            <div style="display:flex;align-items:flex-start;gap:12px">
              <div style="position:relative;flex-shrink:0">
                <div style="width:48px;height:48px;border-radius:50%;background:${ROLE_COLORS[u.role] || '#0052CC'}22;color:${ROLE_COLORS[u.role] || '#0052CC'};display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1rem">${u.avatar}</div>
                <div style="position:absolute;bottom:1px;right:1px;width:11px;height:11px;border-radius:50%;background:${u.status === 'online' ? '#00A651' : '#6c757d'};border:2px solid var(--sp-surface)"></div>
              </div>
              <div style="flex:1;min-width:0">
                <div style="font-weight:700;font-size:0.95rem">${u.name}</div>
                <div style="font-size:0.78rem;margin-bottom:4px">
                  <span style="background:${ROLE_COLORS[u.role] || '#0052CC'}22;color:${ROLE_COLORS[u.role] || '#0052CC'};padding:2px 8px;border-radius:20px;font-size:0.72rem;font-weight:600">${ROLE_LABELS[u.role] || u.role}</span>
                </div>
                <div style="font-size:0.75rem;color:var(--sp-text-muted)"><i class="fas fa-anchor me-1"></i>${u.portName}</div>
              </div>
            </div>
            <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--sp-border)">
              <div style="font-size:0.75rem;color:var(--sp-text-muted);margin-bottom:4px"><i class="fas fa-envelope me-1"></i>${u.email}</div>
              <div style="font-size:0.75rem;color:var(--sp-text-muted)"><i class="fas fa-phone me-1"></i>${u.phone}</div>
            </div>
            <div style="margin-top:10px;font-size:0.72rem;color:var(--sp-text-muted)">
              <div style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis"><i class="fas fa-history me-1"></i>${u.lastAction}</div>
              <div>${formatDate(u.lastActionTime, 'relative')}</div>
            </div>
            <div class="d-flex gap-2 mt-2">
              <button class="btn btn-sm btn-outline-primary flex-fill" onclick="window.showToast('Mensaje enviado a ${u.name.split(' ')[0]}','success')"><i class="fas fa-comment me-1"></i>Mensaje</button>
              <button class="btn btn-sm btn-outline-secondary" onclick="window.showToast('Ver perfil','info')"><i class="fas fa-eye"></i></button>
            </div>
          </div>
        </div>
      </div>`).join('')}</div>`;
  }

  _applyFilters() {
    this._filtered = this._all.filter(u => {
      const q = this._search.toLowerCase();
      if (q && !u.name.toLowerCase().includes(q) && !u.email.toLowerCase().includes(q)) return false;
      if (this._portFilter && u.portId !== this._portFilter) return false;
      if (this._roleFilter && u.role !== this._roleFilter) return false;
      if (this._statusFilter && u.status !== this._statusFilter) return false;
      return true;
    });
    const c = document.getElementById('u-content');
    if (c) c.innerHTML = this._renderCards();
  }

  _bindEvents(container) {
    container.querySelector('#u-search')?.addEventListener('input', e => { this._search = e.target.value; this._applyFilters(); });
    container.querySelector('#u-port')?.addEventListener('change', e => { this._portFilter = e.target.value; this._applyFilters(); });
    container.querySelector('#u-role')?.addEventListener('change', e => { this._roleFilter = e.target.value; this._applyFilters(); });
    container.querySelector('#u-status')?.addEventListener('change', e => { this._statusFilter = e.target.value; this._applyFilters(); });
    container.querySelector('#uf-online')?.addEventListener('click', () => {
      this._statusFilter = this._statusFilter === 'online' ? '' : 'online';
      const s = container.querySelector('#u-status'); if (s) s.value = this._statusFilter;
      this._applyFilters();
    });
    container.querySelector('#uf-offline')?.addEventListener('click', () => {
      this._statusFilter = this._statusFilter === 'offline' ? '' : 'offline';
      const s = container.querySelector('#u-status'); if (s) s.value = this._statusFilter;
      this._applyFilters();
    });
  }

  destroy() {}
}
