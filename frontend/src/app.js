/**
 * SmartPort Galicia — Main Application Controller
 * Renders the persistent shell and handles SPA routing.
 */

import { store } from './store/store.js';
import { wsManager } from './services/websocket.js';
import WebSocketIntegrator from './services/websocket-integrator.js';
import {
  renderAppShell,
  updateActiveNav,
  setHeaderTitle,
  updateConnectionBadge,
  initDarkMode,
  initSidebarToggle,
  initNotifDropdown,
  pushNotification,
} from './components/base.js';

// Lazy page loader — avoids importing everything on startup
let _pageCache = {};

async function importPage(name) {
  if (_pageCache[name]) return _pageCache[name];
  const loaders = {
    dashboard:      () => import('./pages/dashboard.js').then(m => m.DashboardPage),
    ports:          () => import('./pages/ports.js').then(m => m.PortsPage),
    'port-detail':  () => import('./pages/port-detail.js').then(m => m.PortDetailPage),
    berths:         () => import('./pages/berths.js').then(m => m.BerthsPage),
    'berth-detail': () => import('./pages/berth-detail.js').then(m => m.BerthDetailPage),
    'port-calls':   () => import('./pages/port-calls.js').then(m => m.PortCallsPage),
    alerts:         () => import('./pages/alerts.js').then(m => m.AlertsPage),
    analytics:      () => import('./pages/analytics.js').then(m => m.AnalyticsPage),
    vessels:        () => import('./pages/vessels.js').then(m => m.VesselsPage),
    users:          () => import('./pages/users.js').then(m => m.UsersPage),
    settings:       () => import('./pages/settings.js').then(m => m.SettingsPage),
    maps:           () => import('./pages/maps.js').then(m => m.MapsPage),
    documents:      () => import('./pages/documents.js').then(m => m.DocumentsPage),
  };
  if (!loaders[name]) return null;
  _pageCache[name] = await loaders[name]();
  return _pageCache[name];
}

const PAGE_TITLES = {
  dashboard: 'Dashboard',
  ports: 'Puertos de Galicia',
  'port-detail': 'Detalle de Puerto',
  berths: 'Atraques',
  'berth-detail': 'Detalle de Atraque',
  'port-calls': 'Escalas',
  alerts: 'Centro de Alertas',
  analytics: 'Analytics',
  vessels: 'Buques',
  users: 'Equipos',
  settings: 'Configuración',
  maps: 'Mapa Interactivo',
  documents: 'Documentos',
};

export class SmartPortApp {
  constructor(containerId = 'app') {
    this.containerId = containerId;
    this.currentPage = null;
    this.wsIntegrator = null;
  }

  async init() {
    const root = document.getElementById(this.containerId);
    if (!root) return;

    // 1. Render the persistent app shell
    root.innerHTML = renderAppShell();

    // 2. Init UI chrome
    initDarkMode();
    initSidebarToggle();
    initNotifDropdown();

    // 3. Sync connection badge with store
    store.subscribe('connectionStatusChanged', ({ status }) => updateConnectionBadge(status));

    // 4. Global click delegation (sidebar nav + data-nav-page + legacy data-page)
    document.addEventListener('click', e => this._handleClick(e));

    // 5. Route immediately, then on history navigation
    this._route();
    window.addEventListener('popstate', () => this._route());

    // 6. Start WebSocket non-blocking
    this.wsIntegrator = new WebSocketIntegrator(null, null);
    this.wsIntegrator.init().catch(() => {});

    // 7. Seed demo notifications
    setTimeout(() => {
      pushNotification({ message: 'Viento fuerte detectado en A Coruña (28 kn)', severity: 'high', timestamp: new Date() });
      pushNotification({ message: '2 escalas autorizadas en Vigo', severity: 'info', timestamp: new Date(Date.now() - 300000) });
      pushNotification({ message: 'Sensor IOT-F07 sin respuesta', severity: 'medium', timestamp: new Date(Date.now() - 900000) });
    }, 1500);

    window.__smartPortApp = this;
  }

  // ── Routing ──────────────────────────────────

  _route() {
    const path = window.location.pathname;
    if (path === '/' || path === '/dashboard') { this._load('dashboard'); return; }
    if (path === '/ports') { this._load('ports'); return; }
    if (path.startsWith('/ports/')) { this._load('port-detail', { portId: path.slice(7) }); return; }
    if (path === '/berths') { this._load('berths'); return; }
    if (path.startsWith('/berths/')) { this._load('berth-detail', { berthId: path.slice(8) }); return; }
    if (path === '/port-calls') { this._load('port-calls'); return; }
    if (path === '/alerts') { this._load('alerts'); return; }
    if (path === '/analytics') { this._load('analytics'); return; }
    if (path === '/vessels') { this._load('vessels'); return; }
    if (path === '/users') { this._load('users'); return; }
    if (path === '/settings') { this._load('settings'); return; }
    if (path === '/maps') { this._load('maps'); return; }
    if (path === '/documents') { this._load('documents'); return; }
    this._load('dashboard');
  }

  async _load(pageName, params = {}) {
    if (this.currentPage?.destroy) this.currentPage.destroy();
    this.currentPage = null;

    updateActiveNav(pageName);
    setHeaderTitle(PAGE_TITLES[pageName] || pageName);

    const container = document.getElementById('page-content');
    if (container) {
      container.innerHTML = '<div class="p-5 text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
    }

    try {
      const PageClass = await importPage(pageName);
      if (!PageClass) {
        if (container) container.innerHTML = '<div class="p-4 alert alert-warning">Página no encontrada.</div>';
        return;
      }

      let instance;
      if (pageName === 'port-detail') instance = new PageClass(params.portId);
      else if (pageName === 'berth-detail') instance = new PageClass(params.berthId);
      else instance = new PageClass();

      await instance.mount('page-content');
      this.currentPage = instance;
      store.setUIState({ currentPage: pageName });
    } catch (err) {
      console.error('[App] Page error:', pageName, err);
      if (container) {
        container.innerHTML = `<div class="p-4"><div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>Error cargando la página: ${err.message}</div></div>`;
      }
    }
  }

  navigate(page, params = {}) {
    let path = '/';
    if (page === 'port-detail' && params.portId) path = `/ports/${params.portId}`;
    else if (page === 'berth-detail' && params.berthId) path = `/berths/${params.berthId}`;
    else if (page !== 'dashboard') path = `/${page}`;
    if (window.location.pathname !== path) {
      window.history.pushState({ page, params }, '', path);
    }
    this._route();
  }

  // ── Click delegation ─────────────────────────

  _handleClick(e) {
    const navLink = e.target.closest('.sidebar-item[data-page]');
    if (navLink) {
      e.preventDefault();
      this.navigate(navLink.dataset.page);
      return;
    }
    const navEl = e.target.closest('[data-nav-page]');
    if (navEl) {
      e.preventDefault();
      const params = {};
      if (navEl.dataset.portId) params.portId = navEl.dataset.portId;
      if (navEl.dataset.berthId) params.berthId = navEl.dataset.berthId;
      this.navigate(navEl.dataset.navPage, params);
      return;
    }
    const legacyLink = e.target.closest('a[data-page]');
    if (legacyLink && !legacyLink.classList.contains('sidebar-item')) {
      e.preventDefault();
      this.navigate(legacyLink.dataset.page);
    }
  }

  destroy() {
    if (this.currentPage?.destroy) this.currentPage.destroy();
    if (this.wsIntegrator?.disconnect) this.wsIntegrator.disconnect();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const app = new SmartPortApp('app');
  app.init();
  window.__smartPortApp = app;
});

window.spNavigate = (page, params = {}) => window.__smartPortApp?.navigate(page, params);

export default SmartPortApp;
