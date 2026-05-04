/**
 * Main Application Controller
 * 
 * Handles:
 * - Routing between pages
 * - WebSocket integration
 * - Real-time event handling
 * - 2D and 3D visualization setup
 */

import { store } from './store/store.js';
import { wsManager } from './services/websocket.js';
import WebSocketIntegrator from './services/websocket-integrator.js';
import Map3D from './components/map3d.js';
import { DashboardPage } from './pages/dashboard.js';
import { PortDetailPage } from './pages/port-detail.js';
import { AlertsPage } from './pages/alerts.js';
import { OperationsPage } from './pages/operations.js';

export class SmartPortApp {
  constructor(containerId = 'app') {
    this.containerId = containerId;
    this.currentPage = null;
    this.map3d = null;
    this.wsIntegrator = null;
    
    this.pages = {
      dashboard: DashboardPage,
      'port-detail': PortDetailPage,
      alerts: AlertsPage,
      operations: OperationsPage,
    };
    
    this.debug = window.ENV?.DEBUG || false;
  }

  async init() {
    try {
      console.log('[SmartPortApp] Initializing...');

      // Initialize 3D visualization if container exists
      const map3dContainer = document.getElementById('map-3d-container');
      if (map3dContainer) {
        this.map3d = new Map3D('map-3d-container');
        console.log('[SmartPortApp] 3D map initialized');
      }

      // Initialize WebSocket integrator
      this.wsIntegrator = new WebSocketIntegrator(null, this.map3d);
      await this.wsIntegrator.init();

      // Set up route handling
      this.setupRouting();

      // Mount initial page
      this.route();

      // Handle back/forward navigation
      window.addEventListener('popstate', () => this.route());

      // Handle sidebar navigation
      this.setupNavigation();

      // Handle 3D object selection events
      window.addEventListener('3d:objectSelected', (e) => {
        this._handle3DObjectSelected(e.detail);
      });

      console.log('[SmartPortApp] Initialization complete');
    } catch (error) {
      console.error('[SmartPortApp] Initialization error:', error);
    }
  }

  setupRouting() {
    // Route change handler
  }

  route() {
    const path = window.location.pathname;
    const params = new URLSearchParams(window.location.search);

    if (path.startsWith('/ports/')) {
      const portId = path.replace('/ports/', '').replace(/\/$/, '');
      this.loadPage('port-detail', { portId });
    } else if (path === '/alerts' || path === '/alerts/') {
      this.loadPage('alerts');
    } else if (path === '/operations' || path === '/operations/') {
      this.loadPage('operations');
    } else {
      this.loadPage('dashboard');
    }
  }

  async loadPage(pageName, params = {}) {
    try {
      // Save current page for cleanup
      const oldPage = this.currentPage;

      // Cleanup old page
      if (oldPage) {
        oldPage.destroy();
      }

      // Create new page instance
      let pageInstance;

      switch (pageName) {
        case 'port-detail':
          pageInstance = new PortDetailPage(params.portId);
          break;
        case 'alerts':
          pageInstance = new AlertsPage();
          break;
        case 'operations':
          pageInstance = new OperationsPage();
          break;
        default:
          pageInstance = new DashboardPage();
      }

      // Mount page
      await pageInstance.mount(this.containerId);
      this.currentPage = pageInstance;

      // Update page state
      store.setUIState({ currentPage: pageName });

      if (this.debug) {
        console.log('[SmartPortApp] Page loaded:', pageName);
      }
    } catch (error) {
      console.error('[SmartPortApp] Error loading page:', error);
    }
  }

  setupNavigation() {
    const container = document.getElementById(this.containerId);

    if (container) {
      container.addEventListener('click', (e) => {
        const link = e.target.closest('a[data-page]');
        if (link) {
          e.preventDefault();
          const page = link.dataset.page;
          this.navigate(page);
        }

        // Handle port card clicks
        const portCard = e.target.closest('.port-card');
        if (portCard && portCard.onclick) {
          // Let the onclick handler handle it
          return;
        }
      });
    }
  }

  navigate(page, params = {}) {
    let path = '/';

    if (page === 'port-detail' && params.portId) {
      path = `/ports/${params.portId}`;
    } else if (page === 'alerts') {
      path = '/alerts';
    } else if (page === 'operations') {
      path = '/operations';
    }

    window.history.pushState({ page, params }, '', path);
    this.route();
  }

  /**
   * Handle 3D object selection
   */
  _handle3DObjectSelected(userData) {
    if (this.debug) {
      console.log('[SmartPortApp] 3D object selected:', userData);
    }

    // Dispatch custom event for pages to listen to
    window.dispatchEvent(new CustomEvent('entity:selected', {
      detail: userData
    }));
  }

  destroy() {
    if (this.currentPage) {
      this.currentPage.destroy();
    }
    
    if (this.wsIntegrator) {
      this.wsIntegrator.disconnect();
    }
    
    if (this.map3d) {
      this.map3d.destroy();
    }
  }
}

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new SmartPortApp('app');
  app.init();

  // Store app instance globally for debugging
  window.__smartPortApp = app;
});

export default SmartPortApp;
