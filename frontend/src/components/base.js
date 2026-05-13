/**
 * Base Components — Shell, Navigation, Toasts, and Shared UI
 */

import { t, initI18n, applyI18n, setLang, getCurrentLang, getAvailableLangs } from '../services/i18n.js';

/* ── App Shell ────────────────────────────────── */

export function renderAppShell() {
  return `
    <div class="app-shell">
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-brand">
          <i class="fas fa-ship"></i>
          <span class="brand-text">SmartPort</span>
        </div>
        <nav class="sidebar-nav" id="sidebar-nav">
          <div class="nav-section-label" data-i18n="nav.section.main">Principal</div>
          <a class="sidebar-item" data-page="dashboard" href="/">
            <i class="fas fa-tachometer-alt"></i><span class="nav-label" data-i18n="nav.dashboard">Dashboard</span>
          </a>
          <a class="sidebar-item" data-page="ports" href="/ports">
            <i class="fas fa-anchor"></i><span class="nav-label" data-i18n="nav.ports">Puertos</span>
          </a>
          <a class="sidebar-item" data-page="berths" href="/berths">
            <i class="fas fa-ship"></i><span class="nav-label" data-i18n="nav.berths">Atraques</span>
          </a>
          <a class="sidebar-item" data-page="port-calls" href="/port-calls">
            <i class="fas fa-calendar-alt"></i><span class="nav-label" data-i18n="nav.port_calls">Escalas</span>
          </a>
          <a class="sidebar-item" data-page="alerts" href="/alerts">
            <i class="fas fa-bell"></i>
            <span class="nav-label" data-i18n="nav.alerts">Alertas</span>
            <span class="nav-badge badge bg-danger" id="sidebar-alert-badge" style="display:none">0</span>
          </a>

          <div class="nav-section-label" data-i18n="nav.section.ops">Operaciones</div>
          <a class="sidebar-item" data-page="vessels" href="/vessels">
            <i class="fas fa-water"></i><span class="nav-label" data-i18n="nav.vessels">Buques</span>
          </a>
          <a class="sidebar-item" data-page="documents" href="/documents">
            <i class="fas fa-file-alt"></i><span class="nav-label" data-i18n="nav.documents">Documentos</span>
          </a>

          <div class="nav-section-label" data-i18n="nav.section.analysis">Análisis</div>
          <a class="sidebar-item" data-page="analytics" href="/analytics">
            <i class="fas fa-chart-bar"></i><span class="nav-label" data-i18n="nav.analytics">Analytics</span>
          </a>
          <a class="sidebar-item" data-page="maps" href="/maps">
            <i class="fas fa-map-marked-alt"></i><span class="nav-label" data-i18n="nav.maps">Mapa</span>
          </a>

          <div class="nav-section-label" data-i18n="nav.section.admin">Administración</div>
          <a class="sidebar-item" data-page="users" href="/users">
            <i class="fas fa-users"></i><span class="nav-label" data-i18n="nav.users">Equipos</span>
          </a>
          <a class="sidebar-item" data-page="settings" href="/settings">
            <i class="fas fa-cog"></i><span class="nav-label" data-i18n="nav.settings">Configuración</span>
          </a>
        </nav>
        <div class="sidebar-footer">
          <div class="user-avatar-sm">OP</div>
          <div class="user-info">
            <div class="user-name">Operador</div>
            <div class="user-role">Puerto de Galicia</div>
          </div>
        </div>
      </aside>

      <div class="main-wrapper" id="main-wrapper">
        <header class="app-header" id="app-header">
          <button class="header-toggle" id="sidebar-toggle" data-i18n-title="nav.dashboard">
            <i class="fas fa-bars"></i>
          </button>
          <div class="header-title" id="header-title">Dashboard</div>
          <div class="header-actions">
            <div class="conn-badge connecting" id="conn-badge">
              <span class="conn-dot"></span><span id="conn-text" data-i18n="conn.connecting">Conectando...</span>
            </div>
            <div class="notif-btn-wrap">
              <button class="header-btn" id="notif-btn" data-i18n-title="ui.notifications">
                <i class="fas fa-bell"></i>
                <span class="badge-count" id="notif-count" style="display:none">0</span>
              </button>
              <div class="notif-dropdown" id="notif-dropdown">
                <div class="notif-header">
                  <span data-i18n="ui.notifications">Notificaciones</span>
                  <button class="notif-clear" id="notif-clear" data-i18n="ui.clear_all">Limpiar todo</button>
                </div>
                <div id="notif-list"><div class="notif-empty" data-i18n="ui.no_notif">Sin notificaciones</div></div>
              </div>
            </div>
            <select class="lang-selector" id="lang-selector" title="Idioma / Language / Lingua" aria-label="Seleccionar idioma">
              <option value="es">🌐 ES</option>
              <option value="gl">🌐 GL</option>
              <option value="en">🌐 EN</option>
            </select>
            <button class="header-btn" id="dark-mode-btn">
              <i class="fas fa-moon" id="dark-mode-icon"></i>
            </button>
          </div>
        </header>
        <main class="page-content" id="page-content"></main>
      </div>
    </div>
    <div class="toast-container" id="toast-container"></div>
  `;
}

/* ── Navigation helpers ────────────────────────── */

export function updateActiveNav(page) {
  document.querySelectorAll('.sidebar-item').forEach(el => {
    el.classList.toggle('active', el.dataset.page === page);
  });
}

export function setHeaderTitle(title) {
  const el = document.getElementById('header-title');
  if (el) el.textContent = title;
}

export function updateConnectionBadge(status) {
  const badge = document.getElementById('conn-badge');
  const text = document.getElementById('conn-text');
  const legacyBadge = document.getElementById('connection-status-badge');
  if (badge && text) {
    badge.className = `conn-badge ${status}`;
    text.textContent = t(`conn.${status}`, status);
  }
  if (legacyBadge) {
    const cls = { connected: 'badge-success', connecting: 'badge-warning', disconnected: 'badge-danger', error: 'badge-danger' }[status] || 'badge-danger';
    legacyBadge.className = `badge ${cls}`;
    legacyBadge.innerHTML = `<span class="status-dot"></span> ${t(`conn.${status}`, status)}`;
  }
}

/* ── Dark mode ─────────────────────────────────── */

export function initDarkMode() {
  const saved = localStorage.getItem('sp-theme') || 'light';
  applyTheme(saved);
  const btn = document.getElementById('dark-mode-btn');
  if (btn) {
    btn.addEventListener('click', () => {
      const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
      applyTheme(isDark ? 'light' : 'dark');
    });
  }
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-bs-theme', theme);
  localStorage.setItem('sp-theme', theme);
  const icon = document.getElementById('dark-mode-icon');
  if (icon) icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

/* ── Sidebar toggle ────────────────────────────── */

export function initSidebarToggle() {
  const btn = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  const wrapper = document.getElementById('main-wrapper');
  if (!btn || !sidebar || !wrapper) return;

  const collapsed = localStorage.getItem('sp-sidebar') === 'collapsed';
  if (collapsed) { sidebar.classList.add('collapsed'); wrapper.classList.add('sidebar-collapsed'); }

  btn.addEventListener('click', () => {
    if (window.innerWidth <= 991) {
      sidebar.classList.toggle('open');
    } else {
      const isCollapsed = sidebar.classList.toggle('collapsed');
      wrapper.classList.toggle('sidebar-collapsed', isCollapsed);
      localStorage.setItem('sp-sidebar', isCollapsed ? 'collapsed' : 'open');
    }
  });

  document.addEventListener('click', e => {
    if (window.innerWidth <= 991 && !sidebar.contains(e.target) && !btn.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

/* ── Toast notifications ───────────────────────── */

const toastIcons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };

export function showToast(message, type = 'info', title = null, duration = 4000) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const defaultTitles = { success: 'Éxito', error: 'Error', warning: 'Aviso', info: 'Información' };
  const icon = toastIcons[type] || 'fa-info-circle';
  const toastTitle = title || defaultTitles[type] || 'Aviso';
  const el = document.createElement('div');
  el.className = `sp-toast ${type}`;
  el.innerHTML = `
    <i class="fas ${icon} sp-toast-icon"></i>
    <div class="sp-toast-body">
      <div class="sp-toast-title">${toastTitle}</div>
      <div class="sp-toast-msg">${message}</div>
    </div>
    <button class="sp-toast-close" aria-label="Cerrar"><i class="fas fa-times"></i></button>
  `;
  el.querySelector('.sp-toast-close').addEventListener('click', () => _removeToast(el));
  container.appendChild(el);
  if (duration > 0) setTimeout(() => _removeToast(el), duration);
}

function _removeToast(el) {
  el.classList.add('hiding');
  el.addEventListener('animationend', () => el.remove(), { once: true });
}

window.showToast = showToast;

/* ── Notification bell ─────────────────────────── */

let _notifications = [];

export function pushNotification(notif) {
  _notifications.unshift({ ...notif, id: Date.now() + Math.random() });
  if (_notifications.length > 20) _notifications = _notifications.slice(0, 20);
  _renderNotifList();
  updateBellBadge(_notifications.length);
}

export function updateBellBadge(count) {
  const badge = document.getElementById('notif-count');
  if (badge) { badge.style.display = count > 0 ? 'block' : 'none'; badge.textContent = count > 9 ? '9+' : count; }
  const sidebar = document.getElementById('sidebar-alert-badge');
  if (sidebar) { sidebar.style.display = count > 0 ? 'inline-block' : 'none'; sidebar.textContent = count > 9 ? '9+' : count; }
}

function _renderNotifList() {
  const list = document.getElementById('notif-list');
  if (!list) return;
  if (_notifications.length === 0) { list.innerHTML = '<div class="notif-empty">Sin notificaciones</div>'; return; }
  list.innerHTML = _notifications.slice(0, 8).map(n => `
    <div class="notif-item">
      <div class="notif-icon ${n.severity || 'info'}"><i class="fas fa-bell"></i></div>
      <div>
        <div class="notif-msg">${n.message || n.text || ''}</div>
        <div class="notif-time">${_relTime(n.timestamp || n.time || new Date())}</div>
      </div>
    </div>`).join('');
}

export function initNotifDropdown() {
  const btn = document.getElementById('notif-btn');
  const dropdown = document.getElementById('notif-dropdown');
  const clearBtn = document.getElementById('notif-clear');
  if (!btn || !dropdown) return;
  btn.addEventListener('click', e => { e.stopPropagation(); dropdown.classList.toggle('open'); });
  document.addEventListener('click', e => {
    if (!dropdown.contains(e.target) && !btn.contains(e.target)) dropdown.classList.remove('open');
  });
  if (clearBtn) clearBtn.addEventListener('click', () => { _notifications = []; _renderNotifList(); updateBellBadge(0); });
}

function _relTime(ts) {
  const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (diff < 60) return 'Ahora mismo';
  if (diff < 3600) return `Hace ${Math.floor(diff / 60)} min`;
  if (diff < 86400) return `Hace ${Math.floor(diff / 3600)}h`;
  return new Date(ts).toLocaleDateString('es-ES');
}

/* ── Animated KPI counter ──────────────────────── */

export function animateCounter(el, target, duration = 800) {
  if (!el) return;
  const startTime = performance.now();
  const update = (now) => {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(target * eased).toLocaleString('es-ES');
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

/* ── Shared component builders ─────────────────── */

export function KpiCard({ title, value, icon, color = 'primary', trend = null, unit = '', onClick = null, page = null } = {}) {
  const navAttr = page ? `data-nav-page="${page}" style="cursor:pointer"` : (onClick ? `onclick="${onClick}" style="cursor:pointer"` : '');
  const trendHtml = trend !== null ? `<div class="kpi-trend ${trend >= 0 ? 'up' : 'down'}"><i class="fas fa-arrow-${trend >= 0 ? 'up' : 'down'}"></i> ${Math.abs(trend)}% vs mes anterior</div>` : '';
  return `
    <div class="kpi-card color-${color}" ${navAttr}>
      <div class="kpi-label"><i class="fas ${icon}"></i> ${title}</div>
      <div class="kpi-value counter-val">${typeof value === 'number' ? value.toLocaleString('es-ES') : value}${unit}</div>
      ${trendHtml}
      <i class="fas ${icon} kpi-icon"></i>
    </div>`;
}

export function StatusBadge({ status } = {}) {
  const key = (status || '').toLowerCase().replace(/ /g, '_');
  const labels = { free: 'Libre', available: 'Libre', occupied: 'Ocupado', reserved: 'Reservado', maintenance: 'Mantenimiento', outofservice: 'Fuera de servicio', out_of_service: 'Fuera de servicio', active: 'Activo', inactive: 'Inactivo', authorized: 'Autorizado', pending: 'Pendiente', rejected: 'Rechazado', completed: 'Completado', in_port: 'En puerto', approaching: 'Aproximándose', underway: 'En ruta', critical: 'Crítico', high: 'Alta', medium: 'Media', low: 'Baja', ignored: 'Ignorada', resolved: 'Resuelta', valid: 'Válido', expired: 'Caducado' };
  return `<span class="sp-badge ${key}">${labels[key] || status || 'N/A'}</span>`;
}

export function LoadingSkeleton({ lines = 3 } = {}) {
  return `<div class="skeleton-loader">${Array(lines).fill('<div class="skeleton-line skeleton mb-2"></div>').join('')}</div>`;
}

export function EmptyState({ icon = 'fa-inbox', title = 'Sin datos', message = 'No hay datos disponibles', action = null } = {}) {
  const btn = action ? `<button class="btn btn-primary btn-sm mt-3" onclick="${action.callback}">${action.label}</button>` : '';
  return `<div class="sp-empty"><i class="fas ${icon}"></i><h6>${title}</h6><p>${message}</p>${btn}</div>`;
}

export function ErrorBanner({ message, onDismiss = null } = {}) {
  const btn = onDismiss ? `<button class="btn-close" onclick="${onDismiss}" aria-label="Close"></button>` : '';
  return `<div class="alert alert-danger alert-dismissible fade show">${message}${btn}</div>`;
}

export function SuccessBanner({ message, onDismiss = null } = {}) {
  const btn = onDismiss ? `<button class="btn-close" onclick="${onDismiss}" aria-label="Close"></button>` : '';
  return `<div class="alert alert-success alert-dismissible fade show">${message}${btn}</div>`;
}

export function Modal({ id = 'sp-modal', title = '', content = '', buttons = [] } = {}) {
  const btns = buttons.map(b => `<button type="button" class="btn btn-${b.type || 'secondary'}" ${b.closeOnClick ? 'data-bs-dismiss="modal"' : ''} onclick="${b.onclick || ''}">${b.label}</button>`).join('');
  return `<div class="modal fade" id="${id}" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">${title}</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body">${content}</div><div class="modal-footer">${btns}</div></div></div></div>`;
}

export function FilterBar({ filters = {}, clearAllHandler = null } = {}) {
  const active = Object.entries(filters).filter(([, v]) => v).map(([k, v]) => `<span class="badge bg-info me-2">${k}: ${v} <button class="btn-close btn-close-white ms-1" onclick="removeFilter('${k}')" style="font-size:.7rem"></button></span>`).join('');
  const btn = clearAllHandler ? `<button class="btn btn-sm btn-outline-secondary" onclick="(${clearAllHandler})()">Limpiar</button>` : '';
  return `<div class="card mb-3"><div class="card-body d-flex align-items-center gap-2 flex-wrap"><strong>Filtros activos:</strong>${active || '<span class="text-muted">Ninguno</span>'}${btn}</div></div>`;
}

/* ── Language selector ─────────────────────────── */

export function initLangSelector() {
  const sel = document.getElementById('lang-selector');
  if (!sel) return;
  sel.value = getCurrentLang();
  sel.addEventListener('change', () => {
    setLang(sel.value);
    applyI18n(document);
    // Re-render header title using current page key if possible
    const badge = document.getElementById('conn-text');
    if (badge) badge.textContent = t('conn.' + (badge.dataset.status || 'connecting'));
  });
}

/* ── Legacy compat (existing pages import these) ── */
export function Header({ currentPage = '', connectionStatus = 'connecting' } = {}) {
  const map = { connected: ['badge-success', 'Live'], connecting: ['badge-warning', 'Conectando...'], disconnected: ['badge-danger', 'Desconectado'] };
  const [cls, txt] = map[connectionStatus] || map.disconnected;
  return `<nav class="navbar navbar-dark bg-primary sticky-top"><div class="container-fluid"><span class="navbar-brand"><i class="fas fa-ship"></i> SmartPort Galicia</span><span class="badge ${cls}" id="connection-status-badge"><span class="status-dot"></span> ${txt}</span></div></nav>`;
}

export function Sidebar() { return ''; }
export function ConnectionStatus() { return ''; }
