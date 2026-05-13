/**
 * Dashboard Page — Main overview of the Galicia port network
 */

import { apiClient } from '../services/api.js';
import { store } from '../store/store.js';
import { animateCounter, KpiCard, EmptyState, LoadingSkeleton } from '../components/base.js';
import { PORTS, generateAlerts, generatePortCalls, getKPISummary, generateOccupancyHistory } from '../services/mock-data.js';
import { formatDate } from '../utils/helpers.js';
import { t } from '../services/i18n.js';

export class DashboardPage {
  constructor() {
    this.pageId = 'dashboard';
    this._charts = {};
    this._intervals = [];
    this._map = null;
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const [kpis, alerts, portCalls] = await Promise.all([
      this._loadKpis(),
      this._loadAlerts(),
      this._loadPortCalls(),
    ]);

    container.innerHTML = this._render(kpis, alerts, portCalls);
    this._initMap();
    this._initCharts();
    this._animateKpis();
    this._setupAutoRefresh();
  }

  async _loadKpis() {
    try {
      const [ports, berths, alertsData, portCalls] = await Promise.all([
        apiClient.getPorts(20), apiClient.getBerths(null, null, 100),
        apiClient.getAlerts(null, 20), apiClient.getPortCalls(null, 20),
      ]);
      const bArr = berths.items || berths || [];
      const aArr = alertsData.items || alertsData || [];
      const pcArr = portCalls.items || portCalls || [];
      return {
        totalPorts: (ports.items || ports || []).length || PORTS.length,
        activePorts: (ports.items || ports || []).filter(p => p.status === 'active').length || PORTS.filter(p => p.status === 'active').length,
        totalBerths: bArr.length || PORTS.reduce((s, p) => s + p.totalBerths, 0),
        freeBerths: bArr.filter(b => (b.status || b.berth_status) === 'free').length || PORTS.reduce((s, p) => s + p.freeBerths, 0),
        occupiedBerths: bArr.filter(b => (b.status || b.berth_status) === 'occupied').length || PORTS.reduce((s, p) => s + p.occupiedBerths, 0),
        activeAlerts: aArr.filter(a => a.status === 'active').length || 8,
        activePortCalls: pcArr.filter(p => (p.state || p.portcall_status) === 'active').length || 6,
        efficiencyPct: 87, portCallsToday: 12, avgStayHours: 28,
      };
    } catch {
      return getKPISummary();
    }
  }

  async _loadAlerts() {
    try { const d = await apiClient.getAlerts(null, 5); return (d.items || d || []).slice(0, 5); }
    catch { return generateAlerts(5); }
  }

  async _loadPortCalls() {
    try { const d = await apiClient.getPortCalls(null, 8); return (d.items || d || []).filter(p => (p.state || p.portcall_status) === 'active').slice(0, 5); }
    catch { return generatePortCalls(10).filter(p => p.state === 'active').slice(0, 5); }
  }

  _render(kpis, alerts, portCalls) {
    return `
      <div class="page-header">
        <div class="page-title"><i class="fas fa-tachometer-alt"></i> Dashboard</div>
        <div class="page-subtitle">${t('dash.subtitle')}</div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">${KpiCard({ title: t('dash.kpi.ports'), value: kpis.totalPorts, icon: 'fa-anchor', color: 'primary', trend: 0, page: 'ports' })}</div>
        <div class="col-6 col-md-3">${KpiCard({ title: t('dash.kpi.berths'), value: kpis.totalBerths, icon: 'fa-ship', color: 'info', trend: 2, page: 'berths' })}</div>
        <div class="col-6 col-md-3">${KpiCard({ title: t('dash.kpi.active_calls'), value: kpis.activePortCalls, icon: 'fa-calendar-alt', color: 'success', trend: 15, page: 'port-calls' })}</div>
        <div class="col-6 col-md-3">${KpiCard({ title: t('dash.kpi.active_alerts'), value: kpis.activeAlerts, icon: 'fa-bell', color: 'danger', trend: -12, page: 'alerts' })}</div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">${KpiCard({ title: t('dash.kpi.free_berths'), value: kpis.freeBerths, icon: 'fa-check-circle', color: 'success', page: 'berths' })}</div>
        <div class="col-6 col-md-3">${KpiCard({ title: t('dash.kpi.occ_berths'), value: kpis.occupiedBerths, icon: 'fa-times-circle', color: 'danger', page: 'berths' })}</div>
        <div class="col-6 col-md-3">${KpiCard({ title: t('dash.kpi.efficiency'), value: kpis.efficiencyPct, icon: 'fa-chart-line', color: 'info', unit: '%', trend: 3 })}</div>
        <div class="col-6 col-md-3">${KpiCard({ title: t('dash.kpi.today_calls'), value: kpis.portCallsToday, icon: 'fa-route', color: 'warning', trend: 8, page: 'port-calls' })}</div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-lg-8">
          <div class="sp-card h-100">
            <div class="sp-card-header">
              <span class="sp-card-title"><i class="fas fa-map-marked-alt"></i> ${t('dash.section.network')}</span>
              <button class="btn btn-sm btn-outline-primary" data-nav-page="maps"><i class="fas fa-expand-arrows-alt"></i> ${t('dash.btn.full_map')}</button>
            </div>
            <div class="sp-card-body p-0">
              <div id="dashboard-map" style="height:340px;border-radius:0 0 8px 8px;"></div>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="sp-card h-100">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-chart-pie"></i> ${t('dash.section.occ_by_port')}</span></div>
            <div class="sp-card-body"><canvas id="occupancy-donut" height="240"></canvas></div>
          </div>
        </div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-lg-8">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-chart-line"></i> ${t('dash.section.occ_trend')}</span></div>
            <div class="sp-card-body"><canvas id="occupancy-trend" height="120"></canvas></div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-bars"></i> ${t('dash.section.berths_bar')}</span></div>
            <div class="sp-card-body"><canvas id="berths-bar" height="170"></canvas></div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-lg-6">
          <div class="sp-card">
            <div class="sp-card-header">
              <span class="sp-card-title"><i class="fas fa-anchor"></i> ${t('dash.section.port_status')}</span>
              <button class="btn btn-sm btn-outline-primary" data-nav-page="ports">${t('dash.btn.see_all_ports')}</button>
            </div>
            <div class="sp-card-body p-0">
              <table class="sp-table">
                <thead><tr><th>${t('dash.col.port')}</th><th>${t('dash.col.status')}</th><th>${t('dash.col.occupancy')}</th><th>${t('dash.col.free')}</th></tr></thead>
                <tbody>
                  ${PORTS.map(p => `
                    <tr data-nav-page="port-detail" data-port-id="${p.id}">
                      <td><strong>${p.shortName}</strong></td>
                      <td><span class="sp-badge ${p.status}">${p.status === 'active' ? t('status.active') : t('status.maintenance')}</span></td>
                      <td>
                        <div style="display:flex;align-items:center;gap:8px">
                          <div class="sp-progress" style="flex:1"><div class="sp-progress-bar ${p.occupancyPct >= 80 ? 'high' : p.occupancyPct >= 50 ? 'medium' : 'low'}" style="width:${p.occupancyPct}%"></div></div>
                          <small>${p.occupancyPct}%</small>
                        </div>
                      </td>
                      <td class="text-success fw-bold">${p.freeBerths}</td>
                    </tr>`).join('')}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="sp-card">
            <div class="sp-card-header">
              <span class="sp-card-title"><i class="fas fa-bell"></i> ${t('dash.section.alerts')}</span>
              <button class="btn btn-sm btn-outline-danger" data-nav-page="alerts">${t('dash.btn.see_all_alerts')}</button>
            </div>
            <div class="sp-card-body p-0">
              ${alerts.length === 0 ? EmptyState({ icon: 'fa-bell-slash', title: t('dash.empty.no_alerts') }) : `
              <div class="sp-timeline p-3">
                ${alerts.map(a => `
                  <div class="timeline-item">
                    <div class="timeline-dot ${a.severity || 'medium'}"></div>
                    <div class="timeline-content" data-nav-page="alerts">
                      <div class="timeline-title">${a.message}</div>
                      <div class="timeline-subtitle">${a.portName || '—'} · <span class="sp-badge ${a.severity}">${a.severity || 'info'}</span></div>
                      <div class="timeline-meta"><span><i class="fas fa-clock"></i> ${formatDate(a.timestamp, 'time')}</span></div>
                    </div>
                  </div>`).join('')}
              </div>`}
            </div>
          </div>
        </div>

        <div class="col-12">
          <div class="sp-card">
            <div class="sp-card-header">
              <span class="sp-card-title"><i class="fas fa-calendar-check"></i> ${t('dash.section.calls')}</span>
              <button class="btn btn-sm btn-outline-success" data-nav-page="port-calls">${t('dash.btn.see_all_calls')}</button>
            </div>
            <div class="sp-card-body p-0">
              ${portCalls.length === 0 ? EmptyState({ icon: 'fa-ship', title: t('dash.empty.no_calls') }) : `
              <div class="sp-table-wrapper">
                <table class="sp-table">
                  <thead><tr><th>${t('dash.col.vessel')}</th><th>${t('dash.col.port')}</th><th>${t('dash.col.berth')}</th><th>${t('dash.col.status')}</th><th>${t('dash.col.eta')}</th><th>${t('dash.col.duration')}</th></tr></thead>
                  <tbody>
                    ${portCalls.map(pc => `
                      <tr data-nav-page="port-calls">
                        <td><i class="fas fa-ship me-2 text-muted"></i><strong>${pc.vesselName || pc.vessel_name || 'N/A'}</strong></td>
                        <td>${pc.portName || pc.port_name || '—'}</td>
                        <td>${pc.berthName || pc.berth_name || '—'}</td>
                        <td><span class="sp-badge ${pc.state || pc.portcall_status}">${pc.state || pc.portcall_status || '—'}</span></td>
                        <td>${formatDate(pc.eta || pc.expected_arrival, 'medium')}</td>
                        <td>${pc.durationHours || pc.expected_duration || '—'}h</td>
                      </tr>`).join('')}
                  </tbody>
                </table>
              </div>`}
            </div>
          </div>
        </div>
      </div>
    `;
  }

  _animateKpis() {
    document.querySelectorAll('.counter-val').forEach(el => {
      const num = parseFloat(el.textContent.replace(/\./g, '').replace(',', '.').replace('%', ''));
      if (!isNaN(num) && num > 0) { el.textContent = '0'; animateCounter(el, num); }
    });
  }

  _initMap() {
    if (!window.L) return;
    const el = document.getElementById('dashboard-map');
    if (!el || el._leaflet_id) return;
    const map = window.L.map('dashboard-map', { scrollWheelZoom: false }).setView([42.8, -8.4], 7);
    window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap', maxZoom: 18 }).addTo(map);
    this._map = map;
    PORTS.forEach(p => {
      const color = p.status === 'maintenance' ? '#6c757d' : p.occupancyPct >= 80 ? '#dc3545' : p.occupancyPct >= 50 ? '#ffa500' : '#00A651';
      const m = window.L.circleMarker([p.location.lat, p.location.lon], { radius: 10, fillColor: color, color: '#fff', weight: 2, opacity: 1, fillOpacity: 0.85 }).addTo(map);
      m.bindPopup(`<strong>${p.name}</strong><br>${t('dash.col.status')}: ${p.status === 'active' ? t('status.active') : t('status.maintenance')}<br>${t('dash.col.occupancy')}: <b>${p.occupancyPct}%</b><br>${t('dash.col.free')}: <b>${p.freeBerths}/${p.totalBerths}</b>`);
      m.on('click', () => window.spNavigate('port-detail', { portId: p.id }));
    });
  }

  _initCharts() {
    if (!window.Chart) return;
    this._destroyCharts();
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const textColor = isDark ? '#8b949e' : '#6c757d';
    const gridColor = isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.05)';

    const donutEl = document.getElementById('occupancy-donut');
    if (donutEl) {
      this._charts.donut = new window.Chart(donutEl, {
        type: 'doughnut',
        data: { labels: PORTS.map(p => p.shortName), datasets: [{ data: PORTS.map(p => p.occupancyPct), backgroundColor: ['#0052CC','#00A651','#ffa500','#17a2b8','#dc3545','#6c757d'], borderWidth: 0 }] },
        options: { responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: { legend: { position: 'bottom', labels: { color: textColor, font: { size: 11 }, boxWidth: 10 } } } }
      });
    }

    const trendEl = document.getElementById('occupancy-trend');
    if (trendEl) {
      const history = generateOccupancyHistory(30);
      this._charts.trend = new window.Chart(trendEl, {
        type: 'line',
        data: { labels: history.map(h => h.date.slice(5)), datasets: PORTS.slice(0, 3).map((p, i) => ({ label: p.shortName, data: history.map(h => h[p.id] || 0), borderColor: ['#0052CC','#00A651','#ffa500'][i], backgroundColor: 'transparent', borderWidth: 2, pointRadius: 0, tension: 0.4 })) },
        options: { responsive: true, maintainAspectRatio: false, interaction: { mode: 'index' }, scales: { x: { ticks: { color: textColor, maxTicksLimit: 8 }, grid: { color: gridColor } }, y: { ticks: { color: textColor, callback: v => v + '%' }, grid: { color: gridColor }, min: 0, max: 100 } }, plugins: { legend: { labels: { color: textColor, font: { size: 11 }, boxWidth: 10 } } } }
      });
    }

    const barEl = document.getElementById('berths-bar');
    if (barEl) {
      this._charts.bar = new window.Chart(barEl, {
        type: 'bar',
        data: { labels: PORTS.map(p => p.shortName), datasets: [{ label: t('dash.col.free'), data: PORTS.map(p => p.freeBerths), backgroundColor: '#00A651cc' }, { label: t('status.occupied'), data: PORTS.map(p => p.occupiedBerths), backgroundColor: '#dc3545cc' }, { label: t('status.reserved'), data: PORTS.map(p => p.reservedBerths), backgroundColor: '#ffa500cc' }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true, ticks: { color: textColor }, grid: { color: gridColor } }, y: { stacked: true, ticks: { color: textColor }, grid: { color: gridColor } } }, plugins: { legend: { labels: { color: textColor, font: { size: 11 }, boxWidth: 10 } } } }
      });
    }
  }

  _destroyCharts() {
    Object.values(this._charts).forEach(c => { try { c.destroy(); } catch {} });
    this._charts = {};
  }

  _setupAutoRefresh() {
    const id = setInterval(() => { if (!document.getElementById('occupancy-donut')) clearInterval(id); }, 30000);
    this._intervals.push(id);
  }

  destroy() {
    this._destroyCharts();
    this._intervals.forEach(id => clearInterval(id));
    this._intervals = [];
    if (this._map) { try { this._map.remove(); } catch {} this._map = null; }
  }
}
