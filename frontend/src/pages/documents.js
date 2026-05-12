/**
 * Documents Page — Port call manifests, certificates, permits, inspections
 */

import { EmptyState, LoadingSkeleton } from '../components/base.js';
import { generateDocuments, PORTS } from '../services/mock-data.js';

const TYPE_ICONS = { manifest: 'fa-file-alt', certificate: 'fa-certificate', inspection: 'fa-clipboard-check', permit: 'fa-stamp', insurance: 'fa-shield-alt' };
const STATUS_STYLES = { valid: { cls: 'active', label: 'Válido' }, pending: { cls: 'reserved', label: 'Pendiente' }, expired: { cls: 'maintenance', label: 'Caducado' } };

export class DocumentsPage {
  constructor() {
    this.pageId = 'documents';
    this._all = []; this._filtered = [];
    this._search = ''; this._typeFilter = ''; this._statusFilter = ''; this._portFilter = '';
    this._view = 'grid';
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="p-4">' + LoadingSkeleton({ lines: 8 }) + '</div>';
    this._all = generateDocuments();
    this._filtered = this._all;
    container.innerHTML = this._render();
    this._bindEvents(container);
  }

  _render() {
    const valid = this._all.filter(d => d.status === 'valid').length;
    const pending = this._all.filter(d => d.status === 'pending').length;
    const expired = this._all.filter(d => d.status === 'expired').length;
    const types = [...new Set(this._all.map(d => d.type))];

    return `
      <div class="page-header">
        <div class="page-title"><i class="fas fa-folder-open"></i> Documentos</div>
        <div class="page-subtitle">Centro de documentación portuaria</div>
      </div>

      <div class="row g-3 mb-3">
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:var(--sp-primary)">${this._all.length}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Total documentos</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="df-valid"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#00A651">${valid}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Válidos</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="df-pending"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#ffa500">${pending}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Pendientes</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="df-expired"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#dc3545">${expired}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">Caducados</div></div></div></div>
      </div>

      <div class="sp-filters">
        <div class="sp-filter-search"><label>Buscar</label><input class="form-control form-control-sm" id="d-search" placeholder="Título, buque..."></div>
        <div class="sp-filter-group">
          <label>Tipo</label>
          <select class="form-select form-select-sm" id="d-type">
            <option value="">Todos</option>
            ${types.map(t => `<option value="${t}">${_typeLabel(t)}</option>`).join('')}
          </select>
        </div>
        <div class="sp-filter-group">
          <label>Estado</label>
          <select class="form-select form-select-sm" id="d-status">
            <option value="">Todos</option>
            <option value="valid">Válido</option>
            <option value="pending">Pendiente</option>
            <option value="expired">Caducado</option>
          </select>
        </div>
        <div class="sp-filter-group">
          <label>Puerto</label>
          <select class="form-select form-select-sm" id="d-port">
            <option value="">Todos</option>
            ${PORTS.map(p => `<option value="${p.id}">${p.shortName}</option>`).join('')}
          </select>
        </div>
        <div class="d-flex align-items-end gap-2">
          <div class="view-toggle">
            <button class="view-toggle-btn active" id="d-view-grid" title="Grid"><i class="fas fa-th-large"></i></button>
            <button class="view-toggle-btn" id="d-view-table" title="Tabla"><i class="fas fa-table"></i></button>
          </div>
          <button class="btn btn-sm btn-primary" onclick="window.showToast('Función disponible próximamente','info')">
            <i class="fas fa-upload me-1"></i>Subir
          </button>
        </div>
      </div>

      <div id="d-content">${this._renderGrid()}</div>
    `;
  }

  _renderGrid() {
    if (!this._filtered.length) return EmptyState({ icon: 'fa-folder-open', title: 'Sin documentos', message: 'No hay documentos con los filtros aplicados' });
    return `<div class="row g-3">${this._filtered.map(doc => {
      const s = STATUS_STYLES[doc.status] || STATUS_STYLES.pending;
      const icon = TYPE_ICONS[doc.type] || 'fa-file';
      const isExpired = doc.status === 'expired';
      return `
        <div class="col-sm-6 col-lg-4 col-xl-3">
          <div class="sp-card h-100" style="border-left:3px solid ${isExpired ? '#dc3545' : doc.status === 'pending' ? '#ffa500' : '#00A651'}">
            <div class="sp-card-body">
              <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:10px">
                <div style="width:40px;height:40px;border-radius:8px;background:var(--sp-bg);color:var(--sp-primary);display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0">
                  <i class="fas ${icon}"></i>
                </div>
                <div style="flex:1;min-width:0">
                  <div style="font-size:0.68rem;text-transform:uppercase;color:var(--sp-text-muted);font-weight:600">${doc.typeLabel}</div>
                  <div style="font-weight:600;font-size:0.88rem;line-height:1.3;margin-top:2px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">${doc.title}</div>
                </div>
              </div>
              <div style="font-size:0.78rem;color:var(--sp-text-muted);margin-bottom:8px">
                <div><i class="fas fa-ship me-1"></i>${doc.vessel}</div>
                <div><i class="fas fa-anchor me-1"></i>${doc.portName}</div>
              </div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;font-size:0.75rem">
                <span><span class="text-muted">Emisión:</span> ${doc.issueDate}</span>
                <span class="${isExpired ? 'text-danger fw-semibold' : ''}"><span class="text-muted">Vence:</span> ${doc.expiryDate}</span>
              </div>
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span class="sp-badge ${s.cls}" style="font-size:0.68rem;padding:2px 8px">${s.label}</span>
                <span style="font-size:0.72rem;color:var(--sp-text-muted)">${doc.size} · ${doc.version}</span>
              </div>
              <div class="d-flex gap-2 mt-2">
                <button class="btn btn-sm btn-outline-primary flex-fill" onclick="window.showToast('Abriendo ${doc.id}...','info')"><i class="fas fa-eye me-1"></i>Ver</button>
                <button class="btn btn-sm btn-outline-secondary" onclick="window.showToast('Descargando...','info')"><i class="fas fa-download"></i></button>
              </div>
            </div>
          </div>
        </div>`;
    }).join('')}</div>`;
  }

  _renderTable() {
    if (!this._filtered.length) return EmptyState({ icon: 'fa-folder-open', title: 'Sin documentos' });
    return `
      <div class="sp-card">
        <div class="sp-table-wrapper">
          <table class="sp-table">
            <thead><tr><th>Documento</th><th>Tipo</th><th>Buque</th><th>Puerto</th><th>Estado</th><th>Emisión</th><th>Vencimiento</th><th>Tamaño</th><th></th></tr></thead>
            <tbody>
              ${this._filtered.map(doc => {
                const s = STATUS_STYLES[doc.status] || STATUS_STYLES.pending;
                return `
                  <tr>
                    <td><strong>${doc.title}</strong><br><small class="text-muted">${doc.version}</small></td>
                    <td><i class="fas ${TYPE_ICONS[doc.type] || 'fa-file'} me-1"></i>${doc.typeLabel}</td>
                    <td>${doc.vessel}</td>
                    <td>${doc.portName}</td>
                    <td><span class="sp-badge ${s.cls}">${s.label}</span></td>
                    <td>${doc.issueDate}</td>
                    <td class="${doc.status === 'expired' ? 'text-danger fw-semibold' : ''}">${doc.expiryDate}</td>
                    <td>${doc.size}</td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary me-1" onclick="window.showToast('Abriendo...','info')"><i class="fas fa-eye"></i></button>
                      <button class="btn btn-sm btn-outline-secondary" onclick="window.showToast('Descargando...','info')"><i class="fas fa-download"></i></button>
                    </td>
                  </tr>`;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>`;
  }

  _applyFilters() {
    this._filtered = this._all.filter(d => {
      const q = this._search.toLowerCase();
      if (q && !d.title.toLowerCase().includes(q) && !d.vessel.toLowerCase().includes(q)) return false;
      if (this._typeFilter && d.type !== this._typeFilter) return false;
      if (this._statusFilter && d.status !== this._statusFilter) return false;
      if (this._portFilter && d.portId !== this._portFilter) return false;
      return true;
    });
    const c = document.getElementById('d-content');
    if (c) c.innerHTML = this._view === 'table' ? this._renderTable() : this._renderGrid();
  }

  _bindEvents(container) {
    container.querySelector('#d-search')?.addEventListener('input', e => { this._search = e.target.value; this._applyFilters(); });
    container.querySelector('#d-type')?.addEventListener('change', e => { this._typeFilter = e.target.value; this._applyFilters(); });
    container.querySelector('#d-status')?.addEventListener('change', e => { this._statusFilter = e.target.value; this._applyFilters(); });
    container.querySelector('#d-port')?.addEventListener('change', e => { this._portFilter = e.target.value; this._applyFilters(); });

    container.querySelector('#d-view-grid')?.addEventListener('click', () => {
      this._view = 'grid';
      container.querySelector('#d-view-grid')?.classList.add('active');
      container.querySelector('#d-view-table')?.classList.remove('active');
      this._applyFilters();
    });
    container.querySelector('#d-view-table')?.addEventListener('click', () => {
      this._view = 'table';
      container.querySelector('#d-view-table')?.classList.add('active');
      container.querySelector('#d-view-grid')?.classList.remove('active');
      this._applyFilters();
    });

    ['valid', 'pending', 'expired'].forEach(s => {
      container.querySelector(`#df-${s}`)?.addEventListener('click', () => {
        this._statusFilter = this._statusFilter === s ? '' : s;
        const sel = container.querySelector('#d-status'); if (sel) sel.value = this._statusFilter;
        this._applyFilters();
      });
    });
  }

  destroy() {}
}

function _typeLabel(type) {
  return { manifest: 'Manifiesto', certificate: 'Certificado', inspection: 'Inspección', permit: 'Permiso', insurance: 'Seguro' }[type] || type;
}
