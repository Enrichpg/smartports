/**
 * Main Application Controller
 * Handles routing, page switching, and app lifecycle
 */

import { store } from './store/store.js';
import { wsManager } from './services/websocket.js';
import { DashboardPage } from './pages/dashboard.js';
import { PortDetailPage } from './pages/port-detail.js';
import { AlertsPage } from './pages/alerts.js';
import { OperationsPage } from './pages/operations.js';

export class SmartPortApp {
  constructor(containerId = 'app') {
    this.containerId = containerId;
    this.currentPage = null;
    this.pages = {
      dashboard: DashboardPage,
      'port-detail': PortDetailPage,
      alerts: AlertsPage,
      operations: OperationsPage,
    };
  }

  async init() {
    // Initialize WebSocket connection
    wsManager.connect();

    // Set up route handling
    this.setupRouting();

    // Mount initial page
    this.route();

    // Handle back/forward navigation
    window.addEventListener('popstate', () => this.route());

    // Handle sidebar navigation
    this.setupNavigation();
  }

  setupRouting() {
    // This will be called whenever route changes
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

  destroy() {
    if (this.currentPage) {
      this.currentPage.destroy();
    }
    wsManager.disconnect();
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
