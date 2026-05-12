/**
 * Port Detail Page — Full detail view of a single port
 */

import { apiClient } from '../services/api.js';
import { LoadingSkeleton, StatusBadge } from '../components/base.js';
import { PORTS, generateBerths, generatePortCalls, generateAlerts, generateOccupancyHistory } from '../services/mock-data.js';
import { formatDate } from '../utils/helpers.js';

export class PortDetailPage {
  constructor(portId) {
    this.pageId = 'port-detail';
    this.portId = portId;
    this._charts = {};
    this._map = null;
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="p-4">' + LoadingSkeleton({ lines: 10 }) + '</div>';

    const port = await this._loadPort();
    if (!port) {
      container.innerHTML = '<div class="p-4 alert alert-warning">Puerto no encontrado.</div>';
      return;
    }
    this._port = port;
    const berths = await this._loadBerths(port);
    const portCalls = generatePortCalls(20).filter(pc => pc.portId === port.id).slice(0, 10);
    const alerts = generateAlerts(20).filter(a => a.portId === port.id).slice(0, 8);
    const history = generateOccupancyHistory(30);

    container.innerHTML = this._render(port, berths, portCalls, alerts);
    this._initCharts(port, history, berths);
    this._initMap(port, berths);
  }

  async _loadPort() {
    try {
      const data = await apiClient.getPortById(this.portId);
      if (data && (data.id || data.port_id)) return {
        id: data.id || data.port_id,
        name: data.name || data.port_name || 'Puerto',
        shortName: (data.name || data.port_name || '').replace('Puerto de ', '') || 'Puerto',
        type: data.type || 'commercial',
        status: data.status || data.port_status || 'active',
        totalBerths: data.total_berths || data.totalBerths || 0,
        freeBerths: data.free_berths || data.freeBerths || 0,
        occupiedBerths: data.occupied_berths || data.occupiedBerths || 0,
        reservedBerths: data.reserved_berths || data.reservedBerths || 0,
        occupancyPct: data.occupancy_pct || data.occupancyPct || 0,
        vessels24h: data.vessels24h || { in: 0, out: 0 },
        description: data.description || '',
        address: data.address || '',
        phone: data.phone || '',
        email: data.email || '',
        location: data.location || { lat: 43.36, lon: -8.41 },
      };
    } catch {}
    if (this.portId) {
      const found = PORTS.find(p => p.id === this.portId);
      if (found) return found;
    }
    return PORTS[0];
  }

  async _loadBerths(port) {
    try {
      const data = await apiClient.getBerths(this.portId, null, 50);
      const arr = data?.items || data || [];
      if (arr.length > 0) return arr.map(b => ({
        id: b.id || b.berth_id, name: b.name || b.berth_name || 'Muelle',
        status: b.status || b.berth_status || 'free',
        type: b.type || 'general',
        length: b.length || 0, depth: b.depth || 0,
        vesselName: b.vessel_name || b.vesselName || null,
        etd: b.etd || b.expected_departure || null,
      }));
    } catch {}
    return generateBerths(port.id, port.totalBerths || 8);
  }

  _render(port, berths, portCalls, alerts) {
    const free = berths.filter(b => b.status === 'free').length;
    const occ = berths.filter(b => b.status === 'occupied').length;
    const res = berths.filter(b => b.status === 'reserved').length;
    const mnt = berths.filter(b => b.status === 'maintenance').length;
    const typeLabels = { commercial: 'Puerto Comercial', industrial: 'Puerto Industrial', fishing: 'Puerto Pesquero' };
    const sevColors = { critical: '#dc3545', high: '#fd7e14', medium: '#ffc107', low: '#17a2b8' };

    return `
      <div class="page-header">
        <div class="breadcrumb-sp">
          <a data-nav-page="ports">Puertos</a>
          <span class="breadcrumb-sep">/</span>
          <span>${port.name}</span>
        </div>
        <div class="page-title"><i class="fas fa-anchor"></i> ${port.name}</div>
        <div class="page-subtitle">${typeLabels[port.type] || port.type} · ID: ${port.id}</div>
      </div>

      <!-- KPI row -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div class="mb-1"><span class="sp-badge ${port.status}" style="font-size:0.85rem;padding:6px 14px">${port.status === 'active' ? 'Activo' : 'Mantenimiento'}</span></div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Estado</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.6rem;font-weight:700;color:var(--sp-primary)">${port.occupancyPct}%</div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Ocupación actual</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.6rem;font-weight:700;color:#00A651">${port.vessels24h?.in || 0}</div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Entradas 24h</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.6rem;font-weight:700;color:#ffa500">${port.vessels24h?.out || 0}</div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Salidas 24h</div></div></div></div>
      </div>

      <div class="row g-3 mb-4">
        <!-- Port info -->
        <div class="col-lg-4">
          <div class="sp-card h-100">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-info-circle"></i> Información del Puerto</span></div>
            <div class="sp-card-body">
              <table class="table table-sm" style="font-size:0.875rem">
                <tbody>
                  <tr><td class="text-muted">ID</td><td><small>${port.id}</small></td></tr>
                  <tr><td class="text-muted">Tipo</td><td>${typeLabels[port.type] || port.type}</td></tr>
                  <tr><td class="text-muted">Total atraques</td><td>${port.totalBerths}</td></tr>
                  ${port.address ? `<tr><td class="text-muted">Dirección</td><td>${port.address}</td></tr>` : ''}
                  ${port.phone ? `<tr><td class="text-muted">Teléfono</td><td>${port.phone}</td></tr>` : ''}
                  ${port.email ? `<tr><td class="text-muted">Email</td><td><small>${port.email}</small></td></tr>` : ''}
                </tbody>
              </table>
              ${port.description ? `<p style="font-size:0.82rem;color:var(--sp-text-muted);margin:0">${port.description}</p>` : ''}
              <div class="mt-3 d-flex gap-2">
                <button class="btn btn-sm btn-primary" onclick="window.spNavigate('berths')" style="flex:1"><i class="fas fa-ship me-1"></i>Atraques</button>
                <button class="btn btn-sm btn-outline-secondary" onclick="window.spNavigate('maps')"><i class="fas fa-map me-1"></i>Mapa</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Berth status + map -->
        <div class="col-lg-8">
          <div class="row g-3 mb-3">
            <div class="col-6 col-sm-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.6rem;font-weight:700;color:#00A651">${free}</div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Libres</div></div></div></div>
            <div class="col-6 col-sm-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.6rem;font-weight:700;color:#dc3545">${occ}</div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Ocupados</div></div></div></div>
            <div class="col-6 col-sm-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.6rem;font-weight:700;color:#ffa500">${res}</div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Reservados</div></div></div></div>
            <div class="col-6 col-sm-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.6rem;font-weight:700;color:#6c757d">${mnt}</div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Mant.</div></div></div></div>
          </div>
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-map-marker-alt"></i> Ubicación</span></div>
            <div id="port-map" style="height:180px;border-radius:0 0 8px 8px"></div>
          </div>
        </div>
      </div>

      <!-- Charts row -->
      <div class="row g-3 mb-4">
        <div class="col-md-8">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-chart-line"></i> Evolución de Ocupación (30 días)</span></div>
            <div class="sp-card-body"><canvas id="port-trend" height="110"></canvas></div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="sp-card h-100">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-chart-pie"></i> Estado de Atraques</span></div>
            <div class="sp-card-body d-flex align-items-center justify-content-center"><canvas id="port-berth-donut" height="160"></canvas></div>
          </div>
        </div>
      </div>

      <!-- Berths table -->
      <div class="sp-card mb-4">
        <div class="sp-card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span class="sp-card-title"><i class="fas fa-ship"></i> Atraques</span>
          <button class="btn btn-sm btn-outline-primary" onclick="window.spNavigate('berths')">Ver todos</button>
        </div>
        <div class="sp-table-wrapper">
          <table class="sp-table">
            <thead><tr><th>Atraque</th><th>Estado</th><th>Tipo</th><th>Eslora</th><th>Calado</th><th>Buque actual</th><th>ETD</th></tr></thead>
            <tbody>
              ${berths.slice(0, 8).map(b => `
                <tr data-nav-page="berth-detail" data-berth-id="${b.id}" style="cursor:pointer">
                  <td><strong>${b.name}</strong></td>
                  <td><span class="sp-badge ${b.status}">${_bLabel(b.status)}</span></td>
                  <td>${b.type}</td>
                  <td>${b.length}m</td>
                  <td>${b.depth}m</td>
                  <td>${b.vesselName ? `<i class="fas fa-ship me-1 text-muted"></i>${b.vesselName}` : '<span class="text-muted">—</span>'}</td>
                  <td>${b.etd ? formatDate(b.etd, 'medium') : '<span class="text-muted">—</span>'}</td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Port calls + alerts row -->
      <div class="row g-3">
        <div class="col-lg-7">
          <div class="sp-card">
            <div class="sp-card-header" style="display:flex;justify-content:space-between;align-items:center">
              <span class="sp-card-title"><i class="fas fa-calendar-alt"></i> Escalas Recientes</span>
              <button class="btn btn-sm btn-outline-secondary" onclick="window.spNavigate('port-calls')">Ver todas</button>
            </div>
            <div class="sp-table-wrapper">
              <table class="sp-table">
                <thead><tr><th>Buque</th><th>Estado</th><th>ETA</th><th>Duración</th></tr></thead>
                <tbody>
                  ${portCalls.slice(0, 6).map(pc => `
                    <tr>
                      <td><strong>${pc.vesselName}</strong><br><small class="text-muted">${pc.berthName}</small></td>
                      <td><span class="sp-badge ${pc.state}">${_pcLabel(pc.state)}</span></td>
                      <td>${formatDate(pc.eta, 'medium')}</td>
                      <td>${pc.durationHours}h</td>
                    </tr>`).join('')}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="col-lg-5">
          <div class="sp-card">
            <div class="sp-card-header" style="display:flex;justify-content:space-between;align-items:center">
              <span class="sp-card-title"><i class="fas fa-exclamation-triangle"></i> Alertas Activas</span>
              <button class="btn btn-sm btn-outline-secondary" onclick="window.spNavigate('alerts')">Ver todas</button>
            </div>
            <div class="sp-card-body" style="padding:0">
              ${alerts.length ? alerts.slice(0, 5).map(a => `
                <div style="padding:10px 14px;border-bottom:1px solid var(--sp-border);display:flex;gap:10px;align-items:flex-start">
                  <div style="width:8px;height:8px;border-radius:50%;background:${sevColors[a.severity] || '#6c757d'};margin-top:5px;flex-shrink:0"></div>
                  <div>
                    <div style="font-size:0.83rem;font-weight:600">${a.message}</div>
                    <div style="font-size:0.72rem;color:var(--sp-text-muted)">${formatDate(a.timestamp, 'relative')}</div>
                  </div>
                </div>`).join('') : '<div class="text-center py-3 text-muted" style="font-size:0.85rem">Sin alertas activas</div>'}
            </div>
          </div>
        </div>
      </div>
    `;
  }

  _initCharts(port, history, berths) {
    if (!window.Chart) return;
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const tc = isDark ? '#8b949e' : '#6c757d';
    const gc = isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.05)';

    // Trend line
    const trendEl = document.getElementById('port-trend');
    if (trendEl) {
      const labels = history.map((h, i) => i % 5 === 0 ? h.date.slice(5) : '');
      const data = history.map(h => h[port.id] || 0);
      this._charts.trend = new window.Chart(trendEl, {
        type: 'line',
        data: { labels, datasets: [{ data, borderColor: '#0052CC', backgroundColor: '#0052CC22', borderWidth: 2, tension: 0.4, fill: true, pointRadius: 0 }] },
        options: {
          responsive: true, maintainAspectRatio: false,
          scales: { x: { ticks: { color: tc, maxTicksLimit: 8 }, grid: { color: gc } }, y: { ticks: { color: tc }, grid: { color: gc }, min: 0, max: 100 } },
          plugins: { legend: { display: false } }
        }
      });
    }

    // Berth donut
    const donutEl = document.getElementById('port-berth-donut');
    if (donutEl) {
      const free = berths.filter(b => b.status === 'free').length;
      const occ = berths.filter(b => b.status === 'occupied').length;
      const res = berths.filter(b => b.status === 'reserved').length;
      const mnt = berths.filter(b => b.status === 'maintenance').length;
      this._charts.donut = new window.Chart(donutEl, {
        type: 'doughnut',
        data: {
          labels: ['Libre', 'Ocupado', 'Reservado', 'Mant.'],
          datasets: [{ data: [free, occ, res, mnt], backgroundColor: ['#00A651', '#dc3545', '#ffa500', '#6c757d'], borderWidth: 0 }]
        },
        options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom', labels: { color: tc, font: { size: 10 }, boxWidth: 8 } } } }
      });
    }
  }

  _initMap(port, berths) {
    if (!window.L) return;
    const el = document.getElementById('port-map');
    if (!el || el._leaflet_id) return;
    const map = window.L.map('port-map', { scrollWheelZoom: false, zoomControl: false }).setView([port.location.lat, port.location.lon], 14);
    window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(map);
    window.L.circleMarker([port.location.lat, port.location.lon], {
      radius: 12, fillColor: '#0052CC', color: '#fff', weight: 2, fillOpacity: 0.9,
    }).addTo(map).bindPopup(`<strong>${port.name}</strong>`).openPopup();
    this._map = map;
  }

  destroy() {
    Object.values(this._charts).forEach(c => { try { c.destroy(); } catch {} });
    this._charts = {};
    if (this._map) { try { this._map.remove(); } catch {} this._map = null; }
  }
}

function _bLabel(s) { return { free: 'Libre', occupied: 'Ocupado', reserved: 'Reservado', maintenance: 'Mantenimiento' }[s] || s; }
function _pcLabel(s) { return { active: 'Activa', authorized: 'Autorizada', pending: 'Pendiente', completed: 'Completada' }[s] || s; }
