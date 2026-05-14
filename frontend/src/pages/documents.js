/**
 * Documents Page — Port call manifests, certificates, permits, inspections
 */

import { EmptyState, LoadingSkeleton } from '../components/base.js';
import { generateDocuments, PORTS } from '../services/mock-data.js';
import { t } from '../services/i18n.js';

const TYPE_ICONS = { manifest: 'fa-file-alt', certificate: 'fa-certificate', inspection: 'fa-clipboard-check', permit: 'fa-stamp', insurance: 'fa-shield-alt' };
function STATUS_STYLES() {
  return {
    valid: { cls: 'active', label: t('docs.status.valid') },
    pending: { cls: 'reserved', label: t('docs.status.pending') },
    expired: { cls: 'maintenance', label: t('docs.status.expired') },
  };
}

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
        <div class="page-title"><i class="fas fa-folder-open"></i> ${t('page.documents')}</div>
        <div class="page-subtitle">${t('docs.subtitle')}</div>
      </div>

      <div class="row g-3 mb-3">
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:var(--sp-primary)">${this._all.length}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('docs.kpi.total')}</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="df-valid"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#00A651">${valid}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('docs.kpi.valid')}</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="df-pending"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#ffa500">${pending}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('docs.kpi.pending')}</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card" style="cursor:pointer" id="df-expired"><div class="sp-card-body text-center"><div style="font-size:1.8rem;font-weight:700;color:#dc3545">${expired}</div><div style="font-size:0.78rem;color:var(--sp-text-muted)">${t('docs.kpi.expired')}</div></div></div></div>
      </div>

      <div class="sp-filters">
        <div class="sp-filter-search"><label>${t('ui.search')}</label><input class="form-control form-control-sm" id="d-search" placeholder="${t('docs.col.document')}, ${t('docs.col.vessel')}..."></div>
        <div class="sp-filter-group">
          <label>${t('docs.col.type')}</label>
          <select class="form-select form-select-sm" id="d-type">
            <option value="">${t('ui.all')}</option>
            ${types.map(tp => `<option value="${tp}">${_typeLabel(tp)}</option>`).join('')}
          </select>
        </div>
        <div class="sp-filter-group">
          <label>${t('docs.col.status')}</label>
          <select class="form-select form-select-sm" id="d-status">
            <option value="">${t('ui.all')}</option>
            <option value="valid">${t('docs.status.valid')}</option>
            <option value="pending">${t('docs.status.pending')}</option>
            <option value="expired">${t('docs.status.expired')}</option>
          </select>
        </div>
        <div class="sp-filter-group">
          <label>${t('docs.col.port')}</label>
          <select class="form-select form-select-sm" id="d-port">
            <option value="">${t('ui.all')}</option>
            ${PORTS.map(p => `<option value="${p.id}">${p.shortName}</option>`).join('')}
          </select>
        </div>
        <div class="d-flex align-items-end gap-2">
          <div class="view-toggle">
            <button class="view-toggle-btn active" id="d-view-grid" title="Grid"><i class="fas fa-th-large"></i></button>
            <button class="view-toggle-btn" id="d-view-table" title="${t('ui.table')}"><i class="fas fa-table"></i></button>
          </div>
          <button class="btn btn-sm btn-primary" onclick="window.showToast('Función disponible próximamente','info')">
            <i class="fas fa-upload me-1"></i>${t('docs.btn.upload')}
          </button>
        </div>
      </div>

      <div id="d-content">${this._renderGrid()}</div>
    `;
  }

  _renderGrid() {
    if (!this._filtered.length) return EmptyState({ icon: 'fa-folder-open', title: t('ui.no_data'), message: t('ui.no_data') });
    const ss = STATUS_STYLES();
    return `<div class="row g-3">${this._filtered.map(doc => {
      const s = ss[doc.status] || ss.pending;
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
                <span><span class="text-muted">${t('docs.field.emission')}</span> ${doc.issueDate}</span>
                <span class="${isExpired ? 'text-danger fw-semibold' : ''}"><span class="text-muted">${t('docs.field.expires')}</span> ${doc.expiryDate}</span>
              </div>
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span class="sp-badge ${s.cls}" style="font-size:0.68rem;padding:2px 8px">${s.label}</span>
                <span style="font-size:0.72rem;color:var(--sp-text-muted)">${doc.size} · ${doc.version}</span>
              </div>
              <div class="d-flex gap-2 mt-2">
                <button class="btn btn-sm btn-outline-primary flex-fill" data-doc-action="view" data-doc-id="${doc.id}"><i class="fas fa-eye me-1"></i>${t('docs.btn.view')}</button>
                <button class="btn btn-sm btn-outline-secondary" data-doc-action="download" data-doc-id="${doc.id}" title="${t('docs.btn.download')}"><i class="fas fa-download"></i></button>
              </div>
            </div>
          </div>
        </div>`;
    }).join('')}</div>`;
  }

  _renderTable() {
    if (!this._filtered.length) return EmptyState({ icon: 'fa-folder-open', title: t('ui.no_data') });
    const ss = STATUS_STYLES();
    return `
      <div class="sp-card">
        <div class="sp-table-wrapper">
          <table class="sp-table">
            <thead><tr><th>${t('docs.col.document')}</th><th>${t('docs.col.type')}</th><th>${t('docs.col.vessel')}</th><th>${t('docs.col.port')}</th><th>${t('docs.col.status')}</th><th>${t('docs.col.issue_date')}</th><th>${t('docs.col.expiry')}</th><th>${t('docs.col.size')}</th><th></th></tr></thead>
            <tbody>
              ${this._filtered.map(doc => {
                const s = ss[doc.status] || ss.pending;
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
                      <button class="btn btn-sm btn-outline-primary me-1" data-doc-action="view" data-doc-id="${doc.id}" title="${t('docs.btn.view')}"><i class="fas fa-eye"></i></button>
                      <button class="btn btn-sm btn-outline-secondary" data-doc-action="download" data-doc-id="${doc.id}" title="${t('docs.btn.download')}"><i class="fas fa-download"></i></button>
                    </td>
                  </tr>`;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>`;
  }

  _openDocument(doc) {
    const blob = new Blob([this._buildDocHTML(doc)], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const w = window.open(url, '_blank');
    setTimeout(() => URL.revokeObjectURL(url), 15000);
    if (!w) window.showToast('Permite ventanas emergentes para ver documentos', 'warning');
  }

  _downloadDocument(doc) {
    const blob = new Blob([this._buildDocHTML(doc)], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `smartport-${doc.type}-${doc.vessel.replace(/\s+/g, '-').toLowerCase()}-${doc.id}.html`;
    a.click();
    URL.revokeObjectURL(url);
  }

  _buildDocHTML(doc) {
    const statusLabel = { valid: 'VÁLIDO', pending: 'PENDIENTE', expired: 'CADUCADO' }[doc.status] || doc.status.toUpperCase();
    const statusColor = { valid: '#00A651', pending: '#ffa500', expired: '#dc3545' }[doc.status] || '#6c757d';
    return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>${doc.title}</title>
  <style>
    body{font-family:Arial,sans-serif;max-width:820px;margin:40px auto;padding:24px;color:#333;background:#f9f9f9}
    .header{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:3px solid #1a5490;padding-bottom:20px;margin-bottom:28px}
    .logo-block{display:flex;align-items:center;gap:16px}
    .logo-icon{width:56px;height:56px;background:#1a5490;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:26px;flex-shrink:0}
    .org-name{font-size:1.05rem;font-weight:700;color:#1a5490}
    .org-sub{font-size:0.76rem;color:#666;margin-top:2px}
    .doc-ref{text-align:right}
    .doc-ref h1{font-size:1.1rem;color:#1a5490;margin:0 0 4px}
    .doc-id{font-size:0.8rem;color:#888;font-family:monospace}
    .badge{display:inline-block;margin-top:8px;padding:4px 14px;border-radius:20px;color:white;font-size:0.75rem;font-weight:700;background:${statusColor}}
    .section{background:white;border:1px solid #ddd;border-radius:8px;padding:20px;margin-bottom:14px}
    .section h2{font-size:0.78rem;text-transform:uppercase;color:#1a5490;margin:0 0 14px;letter-spacing:1px;font-weight:700}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
    .field label{font-size:0.7rem;color:#888;text-transform:uppercase;letter-spacing:0.5px;display:block;margin-bottom:2px}
    .field span{font-size:0.88rem;font-weight:600}
    .body-text{font-size:0.85rem;line-height:1.75;color:#555;margin:0 0 10px}
    .footer{text-align:center;font-size:0.7rem;color:#aaa;margin-top:28px;border-top:1px solid #e5e5e5;padding-top:14px}
    .watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) rotate(-30deg);font-size:80px;color:rgba(0,0,0,0.03);font-weight:900;pointer-events:none;white-space:nowrap;z-index:-1}
    @media print{.watermark{display:block}}
  </style>
</head>
<body>
  <div class="watermark">SMARTPORT GALICIA</div>
  <div class="header">
    <div class="logo-block">
      <div class="logo-icon">⚓</div>
      <div>
        <div class="org-name">SmartPort Galicia</div>
        <div class="org-sub">Autoridad Portuaria de Galicia</div>
        <div class="org-sub">Sistema de Gestión Documental</div>
      </div>
    </div>
    <div class="doc-ref">
      <h1>${doc.typeLabel}</h1>
      <div class="doc-id">${doc.id.toUpperCase()}</div>
      <span class="badge">${statusLabel}</span>
    </div>
  </div>

  <div class="section">
    <h2>Información del Documento</h2>
    <div class="grid">
      <div class="field"><label>Título</label><span>${doc.title}</span></div>
      <div class="field"><label>Tipo</label><span>${doc.typeLabel}</span></div>
      <div class="field"><label>Fecha de Emisión</label><span>${doc.issueDate}</span></div>
      <div class="field"><label>Fecha de Vencimiento</label><span style="color:${doc.status === 'expired' ? '#dc3545' : 'inherit'}">${doc.expiryDate}</span></div>
      <div class="field"><label>Versión</label><span>${doc.version}</span></div>
      <div class="field"><label>Tamaño estimado</label><span>${doc.size}</span></div>
    </div>
  </div>

  <div class="section">
    <h2>Buque y Puerto</h2>
    <div class="grid">
      <div class="field"><label>Nombre del Buque</label><span>${doc.vessel}</span></div>
      <div class="field"><label>Puerto de Referencia</label><span>${doc.portName}</span></div>
    </div>
  </div>

  <div class="section">
    <h2>Declaración Oficial</h2>
    <p class="body-text">
      El presente documento ha sido emitido por la Autoridad Portuaria de Galicia y certifica que la
      información contenida es conforme a la normativa vigente en materia de tráfico marítimo y gestión
      portuaria (Ley 48/2003 de régimen económico y de prestación de servicios de los puertos de interés
      general, y sus sucesivas modificaciones).
    </p>
    <p class="body-text">
      Este documento es válido únicamente para el buque y período indicados. Cualquier alteración invalida
      el presente certificado. Para renovación o consultas, contacte con la administración portuaria del
      puerto de <strong>${doc.portName}</strong>.
    </p>
  </div>

  <div class="footer">
    <p>Generado por SmartPort Galicia Operations Center · ${new Date().toLocaleString('es-ES')} · Ref: ${doc.id.toUpperCase()}</p>
    <p>Documento digital de referencia — la versión oficial firmada obra en poder de la autoridad portuaria.</p>
  </div>
</body>
</html>`;
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
    // Ver / Descargar delegation — attached to container so survives grid/table re-renders
    container.addEventListener('click', e => {
      const btn = e.target.closest('[data-doc-action]');
      if (!btn) return;
      const doc = this._all.find(d => d.id === btn.dataset.docId);
      if (!doc) return;
      if (btn.dataset.docAction === 'view') this._openDocument(doc);
      else if (btn.dataset.docAction === 'download') this._downloadDocument(doc);
    });

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
  return {
    manifest: t('docs.type.manifest'), certificate: t('docs.type.certificate'),
    inspection: t('docs.type.inspection'), permit: t('docs.type.permit'),
    insurance: t('docs.type.insurance'),
  }[type] || type;
}
