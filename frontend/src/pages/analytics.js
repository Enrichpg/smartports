/**
 * Analytics Page — Occupancy trends, traffic stats, and operational KPIs
 */

import { apiClient } from '../services/api.js';
import { LoadingSkeleton } from '../components/base.js';
import { PORTS, generateOccupancyHistory, generatePortCalls, generateAlerts, getKPISummary } from '../services/mock-data.js';
import { formatDate } from '../utils/helpers.js';

export class AnalyticsPage {
  constructor() {
    this.pageId = 'analytics';
    this._charts = {};
    this._portFilter = '';
    this._period = '30';
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="p-4">' + LoadingSkeleton({ lines: 10 }) + '</div>';

    const kpi = await this._loadKPI();
    const history = generateOccupancyHistory(parseInt(this._period));
    const portCalls = generatePortCalls(60);
    const alerts = generateAlerts(40);

    container.innerHTML = this._render(kpi);
    this._initCharts(history, portCalls, alerts);
    this._bindEvents(container);
  }

  async _loadKPI() {
    try {
      const [ports, berths] = await Promise.all([apiClient.getPorts(20), apiClient.getBerths(null, null, 200)]);
      const ps = (ports.items || ports || []);
      const bs = (berths.items || berths || []);
      if (ps.length > 0) return {
        avgOccupancy: Math.round(ps.reduce((s, p) => s + (p.occupancy_pct || p.occupancyPct || 0), 0) / ps.length),
        totalBerths: bs.length || 53,
        freeBerths: bs.filter(b => (b.status || b.berth_status) === 'free').length,
        portCallsMonth: 124,
        avgStay: 28,
        revenue: 284500,
      };
    } catch {}
    return getKPISummary();
  }

  _render(kpi) {
    return `
      <div class="page-header">
        <div class="page-title"><i class="fas fa-chart-line"></i> Analytics</div>
        <div class="page-subtitle">Análisis operativo de la red portuaria de Galicia</div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-6 col-md-4 col-xl-2">
          <div class="sp-card"><div class="sp-card-body text-center">
            <div style="font-size:1.6rem;font-weight:700;color:var(--sp-primary)">${kpi.avgOccupancyPct || kpi.avgOccupancy || 59}%</div>
            <div style="font-size:0.75rem;color:var(--sp-text-muted)">Ocupación media</div>
          </div></div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="sp-card"><div class="sp-card-body text-center">
            <div style="font-size:1.6rem;font-weight:700;color:#00A651">${kpi.freeBerths || kpi.freeBerths || 21}</div>
            <div style="font-size:0.75rem;color:var(--sp-text-muted)">Atraques libres</div>
          </div></div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="sp-card"><div class="sp-card-body text-center">
            <div style="font-size:1.6rem;font-weight:700;color:#17a2b8">${kpi.portCallsToday || 12}</div>
            <div style="font-size:0.75rem;color:var(--sp-text-muted)">Escalas hoy</div>
          </div></div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="sp-card"><div class="sp-card-body text-center">
            <div style="font-size:1.6rem;font-weight:700;color:#ffa500">${kpi.avgStayHours || 28}h</div>
            <div style="font-size:0.75rem;color:var(--sp-text-muted)">Estancia media</div>
          </div></div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="sp-card"><div class="sp-card-body text-center">
            <div style="font-size:1.6rem;font-weight:700;color:#dc3545">${kpi.activeAlerts || 8}</div>
            <div style="font-size:0.75rem;color:var(--sp-text-muted)">Alertas activas</div>
          </div></div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="sp-card"><div class="sp-card-body text-center">
            <div style="font-size:1.6rem;font-weight:700;color:#6f42c1">${((kpi.estimatedRevenue || 284500) / 1000).toFixed(0)}K€</div>
            <div style="font-size:0.75rem;color:var(--sp-text-muted)">Ingresos est.</div>
          </div></div>
        </div>
      </div>

      <!-- Filters -->
      <div class="sp-filters mb-4">
        <div class="sp-filter-group">
          <label>Puerto</label>
          <select class="form-select form-select-sm" id="an-port">
            <option value="">Todos los puertos</option>
            ${PORTS.map(p => `<option value="${p.id}">${p.shortName}</option>`).join('')}
          </select>
        </div>
        <div class="sp-filter-group">
          <label>Período</label>
          <select class="form-select form-select-sm" id="an-period">
            <option value="7">Últimos 7 días</option>
            <option value="30" selected>Últimos 30 días</option>
            <option value="90">Últimos 90 días</option>
          </select>
        </div>
        <div class="d-flex align-items-end">
          <button class="btn btn-sm btn-outline-secondary" onclick="window.showToast('Exportando informe PDF...','info')">
            <i class="fas fa-file-pdf me-1"></i>Exportar
          </button>
        </div>
      </div>

      <!-- Row 1: Occupancy trend (wide) + vessel type donut -->
      <div class="row g-3 mb-3">
        <div class="col-lg-8">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-chart-area"></i> Evolución de Ocupación por Puerto (%)</span></div>
            <div class="sp-card-body"><canvas id="an-occupancy-trend" height="130"></canvas></div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="sp-card h-100">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-ship"></i> Distribución por Tipo de Buque</span></div>
            <div class="sp-card-body d-flex align-items-center justify-content-center"><canvas id="an-vessel-type" height="180"></canvas></div>
          </div>
        </div>
      </div>

      <!-- Row 2: Port calls bar + alerts distribution -->
      <div class="row g-3 mb-3">
        <div class="col-lg-6">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-calendar-check"></i> Escalas por Puerto (últimas 4 semanas)</span></div>
            <div class="sp-card-body"><canvas id="an-portcalls-bar" height="140"></canvas></div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-exclamation-triangle"></i> Alertas por Severidad y Puerto</span></div>
            <div class="sp-card-body"><canvas id="an-alerts-bar" height="140"></canvas></div>
          </div>
        </div>
      </div>

      <!-- Row 3: Stay duration radar + efficiency -->
      <div class="row g-3 mb-3">
        <div class="col-lg-4">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-spider"></i> Perfil Operativo</span></div>
            <div class="sp-card-body d-flex align-items-center justify-content-center"><canvas id="an-radar" height="200"></canvas></div>
          </div>
        </div>
        <div class="col-lg-8">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-clock"></i> Duración Media de Escala por Tipo de Buque (h)</span></div>
            <div class="sp-card-body"><canvas id="an-duration-bar" height="140"></canvas></div>
          </div>
        </div>
      </div>

      <!-- Table: Top port calls -->
      <div class="sp-card">
        <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-table"></i> Top Escalas por Tonelaje (Último Mes)</span></div>
        <div class="sp-table-wrapper">
          <table class="sp-table">
            <thead><tr><th>#</th><th>Buque</th><th>Puerto</th><th>Atraque</th><th>Tipo</th><th>Tonelaje</th><th>Duración</th><th>Estado</th></tr></thead>
            <tbody id="an-top-table"></tbody>
          </table>
        </div>
      </div>
    `;
  }

  _initCharts(history, portCalls, alerts) {
    if (!window.Chart) return;
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const tc = isDark ? '#8b949e' : '#6c757d';
    const gc = isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.05)';
    const COLORS = ['#0052CC','#00A651','#dc3545','#ffa500','#17a2b8','#6f42c1'];

    const _opts = (height) => ({
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: tc, maxTicksLimit: 8 }, grid: { color: gc } },
        y: { ticks: { color: tc }, grid: { color: gc } }
      },
      plugins: { legend: { labels: { color: tc, font: { size: 10 }, boxWidth: 10 } } }
    });

    // 1. Occupancy trend (multi-line)
    const activePorts = PORTS.filter(p => p.status === 'active');
    const labels = history.map((h, i) => i % 5 === 0 ? h.date.slice(5) : '');
    const el1 = document.getElementById('an-occupancy-trend');
    if (el1) {
      this._charts.trend = new window.Chart(el1, {
        type: 'line',
        data: {
          labels,
          datasets: activePorts.map((p, i) => ({
            label: p.shortName,
            data: history.map(h => h[p.id]),
            borderColor: COLORS[i], backgroundColor: COLORS[i] + '18',
            borderWidth: 2, tension: 0.4, fill: false, pointRadius: 0,
          }))
        },
        options: { ..._opts(), plugins: { legend: { labels: { color: tc, font: { size: 10 }, boxWidth: 10 } } } }
      });
    }

    // 2. Vessel type donut
    const typeCount = {};
    portCalls.forEach(pc => { typeCount[pc.vesselType] = (typeCount[pc.vesselType] || 0) + 1; });
    const typeLabels = { container: 'Contenedor', bulk: 'Graneles', tanker: 'Tanquero', roro: 'Ro-Ro', general: 'General', cruise: 'Crucero', fishing: 'Pesca' };
    const el2 = document.getElementById('an-vessel-type');
    if (el2) {
      this._charts.vesselType = new window.Chart(el2, {
        type: 'doughnut',
        data: {
          labels: Object.keys(typeCount).map(t => typeLabels[t] || t),
          datasets: [{ data: Object.values(typeCount), backgroundColor: COLORS, borderWidth: 0 }]
        },
        options: { responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: { legend: { position: 'bottom', labels: { color: tc, font: { size: 10 }, boxWidth: 10 } } } }
      });
    }

    // 3. Port calls bar per port
    const pcByPort = {};
    activePorts.forEach(p => { pcByPort[p.id] = portCalls.filter(pc => pc.portId === p.id).length; });
    const el3 = document.getElementById('an-portcalls-bar');
    if (el3) {
      this._charts.portCalls = new window.Chart(el3, {
        type: 'bar',
        data: {
          labels: activePorts.map(p => p.shortName),
          datasets: [{ label: 'Escalas', data: activePorts.map(p => pcByPort[p.id] || 0), backgroundColor: COLORS, borderRadius: 4, borderWidth: 0 }]
        },
        options: { ..._opts(), plugins: { legend: { display: false } } }
      });
    }

    // 4. Alerts by severity + port
    const sev = ['critical', 'high', 'medium', 'low'];
    const sevColors = ['#dc3545', '#fd7e14', '#ffc107', '#17a2b8'];
    const el4 = document.getElementById('an-alerts-bar');
    if (el4) {
      this._charts.alerts = new window.Chart(el4, {
        type: 'bar',
        data: {
          labels: activePorts.map(p => p.shortName),
          datasets: sev.map((s, i) => ({
            label: s.charAt(0).toUpperCase() + s.slice(1),
            data: activePorts.map(p => alerts.filter(a => a.portId === p.id && a.severity === s).length),
            backgroundColor: sevColors[i], borderRadius: 3, borderWidth: 0,
          }))
        },
        options: { ..._opts(), scales: { x: { ticks: { color: tc }, grid: { color: gc }, stacked: true }, y: { ticks: { color: tc }, grid: { color: gc }, stacked: true } }, plugins: { legend: { labels: { color: tc, font: { size: 10 }, boxWidth: 10 } } } }
      });
    }

    // 5. Radar: operational profile
    const el5 = document.getElementById('an-radar');
    if (el5) {
      this._charts.radar = new window.Chart(el5, {
        type: 'radar',
        data: {
          labels: ['Ocupación', 'Eficiencia', 'Seguridad', 'Puntualidad', 'Sostenibilidad', 'Capacidad'],
          datasets: [{
            label: 'Red Portuaria',
            data: [59, 87, 92, 76, 68, 74],
            backgroundColor: 'rgba(0,82,204,0.2)', borderColor: '#0052CC',
            pointBackgroundColor: '#0052CC', borderWidth: 2,
          }]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          scales: { r: { ticks: { color: tc, backdropColor: 'transparent', stepSize: 25 }, grid: { color: gc }, angleLines: { color: gc }, pointLabels: { color: tc, font: { size: 10 } } } },
          plugins: { legend: { display: false } }
        }
      });
    }

    // 6. Duration bar by vessel type
    const durationByType = { container: 32, bulk: 48, tanker: 56, roro: 24, general: 28, cruise: 18, fishing: 14 };
    const el6 = document.getElementById('an-duration-bar');
    if (el6) {
      this._charts.duration = new window.Chart(el6, {
        type: 'bar',
        data: {
          labels: Object.keys(durationByType).map(t => typeLabels[t] || t),
          datasets: [{ label: 'Horas', data: Object.values(durationByType), backgroundColor: COLORS, borderRadius: 4, borderWidth: 0 }]
        },
        options: { ..._opts(), plugins: { legend: { display: false } } }
      });
    }

    // Populate table
    const tbody = document.getElementById('an-top-table');
    if (tbody) {
      const sorted = [...portCalls].sort((a, b) => (b.grossTonnage || 0) - (a.grossTonnage || 0)).slice(0, 8);
      const stateLabel = { active: 'Activa', authorized: 'Autorizada', pending: 'Pendiente', completed: 'Completada' };
      const vtLabel = { container: 'Contenedor', bulk: 'Graneles', tanker: 'Tanquero', roro: 'Ro-Ro', general: 'General', cruise: 'Crucero', fishing: 'Pesca' };
      tbody.innerHTML = sorted.map((pc, i) => `
        <tr>
          <td>${i + 1}</td>
          <td><strong>${pc.vesselName}</strong></td>
          <td>${pc.portName}</td>
          <td>${pc.berthName}</td>
          <td>${vtLabel[pc.vesselType] || pc.vesselType}</td>
          <td>${(pc.grossTonnage || 0).toLocaleString('es-ES')} GT</td>
          <td>${pc.durationHours}h</td>
          <td><span class="sp-badge ${pc.state}">${stateLabel[pc.state] || pc.state}</span></td>
        </tr>`).join('');
    }
  }

  _bindEvents(container) {
    container.querySelector('#an-period')?.addEventListener('change', e => {
      this._period = e.target.value;
      const history = generateOccupancyHistory(parseInt(this._period));
      if (this._charts.trend) {
        const activePorts = PORTS.filter(p => p.status === 'active');
        const labels = history.map((h, i) => i % 5 === 0 ? h.date.slice(5) : '');
        this._charts.trend.data.labels = labels;
        activePorts.forEach((p, i) => { this._charts.trend.data.datasets[i].data = history.map(h => h[p.id]); });
        this._charts.trend.update();
      }
    });
    container.querySelector('#an-port')?.addEventListener('change', e => {
      this._portFilter = e.target.value;
      window.showToast(`Filtrando por ${this._portFilter ? PORTS.find(p => p.id === this._portFilter)?.shortName : 'todos los puertos'}`, 'info');
    });
  }

  destroy() {
    Object.values(this._charts).forEach(c => { try { c.destroy(); } catch {} });
    this._charts = {};
  }
}
