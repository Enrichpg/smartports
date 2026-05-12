/**
 * Berth Detail Page — Full detail view of a single berth
 */

import { apiClient } from '../services/api.js';
import { EmptyState, LoadingSkeleton, StatusBadge } from '../components/base.js';
import { generateBerths, generateSensorHistory, generatePortCalls, PORTS } from '../services/mock-data.js';
import { formatDate } from '../utils/helpers.js';

export class BerthDetailPage {
  constructor(berthId) {
    this.pageId = 'berth-detail';
    this.berthId = berthId;
    this._charts = {};
    this._map = null;
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="p-4">' + LoadingSkeleton({ lines: 8 }) + '</div>';

    const berth = await this._loadBerth();
    if (!berth) {
      container.innerHTML = '<div class="p-4 alert alert-warning">Atraque no encontrado.</div>';
      return;
    }
    this._berth = berth;
    const sensorData = generateSensorHistory(24);
    const history = generatePortCalls(10).filter((_, i) => i % 3 === 0).slice(0, 8);

    container.innerHTML = this._render(berth, history);
    this._initCharts(sensorData);
    this._initMap(berth);
  }

  async _loadBerth() {
    try {
      const data = await apiClient.getBerthById(this.berthId);
      if (data && (data.id || data.berth_id)) return {
        id: data.id || data.berth_id, name: data.name || data.berth_name || 'Muelle',
        portId: data.port_id || data.portId, portName: data.port_name || data.portName || 'Puerto',
        status: data.status || data.berth_status || 'free',
        type: data.type || 'general', length: data.length || 100,
        beam: data.beam || 20, depth: data.depth || 8,
        equipment: data.equipment || ['Grúa pórtico', 'Toma de agua', 'Corriente eléctrica'],
        tariff: data.tariff || 120,
        vesselName: data.vessel_name || data.vesselName || null,
        vesselIMO: data.vessel_imo || data.vesselIMO || null,
        vesselFlag: data.vessel_flag || data.vesselFlag || null,
        etd: data.etd || data.expected_departure || null,
        occupancyPct: data.occupancy_pct || data.occupancyPct || 0,
        lastActivity: data.last_activity || data.lastActivity || new Date().toISOString(),
      };
    } catch {}
    // Find in mock data
    if (this.berthId) {
      for (const port of PORTS) {
        const berths = generateBerths(port.id, port.totalBerths);
        const found = berths.find(b => b.id === this.berthId);
        if (found) return found;
      }
    }
    // Fallback: first berth of A Coruña
    return generateBerths('galicia-a-coruna', 12)[0];
  }

  _render(berth, history) {
    const port = PORTS.find(p => p.id === berth.portId);
    const portCoords = port?.location || { lat: 43.36, lon: -8.41 };
    return `
      <div class="page-header">
        <div class="breadcrumb-sp">
          <a data-nav-page="berths">Atraques</a>
          <span class="breadcrumb-sep">/</span>
          <a data-nav-page="port-detail" data-port-id="${berth.portId}">${berth.portName}</a>
          <span class="breadcrumb-sep">/</span>
          <span>${berth.name}</span>
        </div>
        <div class="page-title"><i class="fas fa-ship"></i> ${berth.name}</div>
        <div class="page-subtitle">${berth.portName} · ID: ${berth.id}</div>
      </div>

      <!-- Status bar -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div class="mb-1"><span class="sp-badge ${berth.status}" style="font-size:0.85rem;padding:6px 14px">${_sLabel(berth.status)}</span></div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Estado actual</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.6rem;font-weight:700">${berth.length}m</div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Eslora máxima</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.6rem;font-weight:700">${berth.depth}m</div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Calado</div></div></div></div>
        <div class="col-6 col-md-3"><div class="sp-card"><div class="sp-card-body text-center"><div style="font-size:1.6rem;font-weight:700">${berth.tariff || 120}€/h</div><div style="font-size:0.75rem;color:var(--sp-text-muted)">Tarifa amarre</div></div></div></div>
      </div>

      <div class="row g-3 mb-4">
        <!-- Info + buque actual -->
        <div class="col-lg-6">
          <div class="sp-card h-100">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-info-circle"></i> Información del Atraque</span></div>
            <div class="sp-card-body">
              <table class="table table-sm" style="font-size:0.875rem">
                <tbody>
                  <tr><td class="text-muted">ID</td><td>${berth.id}</td></tr>
                  <tr><td class="text-muted">Puerto</td><td><a data-nav-page="port-detail" data-port-id="${berth.portId}" style="color:var(--sp-primary);cursor:pointer">${berth.portName}</a></td></tr>
                  <tr><td class="text-muted">Tipo</td><td>${berth.type}</td></tr>
                  <tr><td class="text-muted">Eslora máx.</td><td>${berth.length}m</td></tr>
                  <tr><td class="text-muted">Manga máx.</td><td>${berth.beam}m</td></tr>
                  <tr><td class="text-muted">Calado</td><td>${berth.depth}m</td></tr>
                  <tr><td class="text-muted">Equipamiento</td><td>${(berth.equipment || []).join(', ')}</td></tr>
                  <tr><td class="text-muted">Tarifa</td><td>${berth.tariff || 120}€/h</td></tr>
                  <tr><td class="text-muted">Última actividad</td><td>${formatDate(berth.lastActivity, 'medium')}</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Vessel / map -->
        <div class="col-lg-6">
          ${berth.vesselName ? `
          <div class="sp-card mb-3">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-ship text-danger"></i> Buque Atracado</span></div>
            <div class="sp-card-body">
              <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px">
                <div style="width:52px;height:52px;border-radius:50%;background:rgba(0,82,204,0.12);color:var(--sp-primary);display:flex;align-items:center;justify-content:center;font-size:1.5rem"><i class="fas fa-ship"></i></div>
                <div><div style="font-weight:700;font-size:1.05rem">${berth.vesselName}</div><div style="font-size:0.8rem;color:var(--sp-text-muted)">${berth.vesselIMO || '—'} · Bandera: ${berth.vesselFlag || '—'}</div></div>
              </div>
              <div class="row g-2" style="font-size:0.85rem">
                <div class="col-6"><div class="text-muted">ETD</div><div><strong>${formatDate(berth.etd, 'medium')}</strong></div></div>
                <div class="col-6"><div class="text-muted">Ocupación</div><div><strong>${berth.occupancyPct}%</strong></div></div>
              </div>
              <div class="mt-3 d-flex gap-2">
                <button class="btn btn-sm btn-outline-danger" onclick="window.showToast('Liberación de atraque solicitada','warning')"><i class="fas fa-unlock me-1"></i>Liberar atraque</button>
                <button class="btn btn-sm btn-outline-primary" onclick="window.showToast('Acción registrada','success')"><i class="fas fa-edit me-1"></i>Editar</button>
              </div>
            </div>
          </div>` : `
          <div class="sp-card mb-3">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-check-circle text-success"></i> Atraque Disponible</span></div>
            <div class="sp-card-body">
              <div class="text-center py-3">
                <div style="font-size:2rem;color:#00A651;margin-bottom:8px"><i class="fas fa-check-circle"></i></div>
                <div style="font-weight:600">Este atraque está disponible</div>
                <div style="font-size:0.82rem;color:var(--sp-text-muted);margin-top:4px">Puede aceptar un buque de hasta ${berth.length}m de eslora</div>
              </div>
              <div class="d-flex gap-2 justify-content-center mt-3">
                <button class="btn btn-sm btn-success" onclick="window.showToast('Asignación de buque iniciada','success')"><i class="fas fa-plus me-1"></i>Asignar buque</button>
                <button class="btn btn-sm btn-outline-warning" onclick="window.showToast('Atraque reservado','info')"><i class="fas fa-clock me-1"></i>Reservar</button>
              </div>
            </div>
          </div>`}
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-map-marker-alt"></i> Ubicación</span></div>
            <div id="berth-map" style="height:160px;border-radius:0 0 8px 8px"></div>
          </div>
        </div>
      </div>

      <!-- Sensor charts -->
      <div class="row g-3 mb-4">
        <div class="col-12"><div class="sp-card-title mb-2" style="padding:0 4px"><i class="fas fa-microchip me-2"></i>Sensores IoT en Tiempo Real</div></div>
        <div class="col-md-6"><div class="sp-card"><div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-thermometer-half"></i> Temperatura (°C)</span></div><div class="sp-card-body"><canvas id="sensor-temp" height="100"></canvas></div></div></div>
        <div class="col-md-6"><div class="sp-card"><div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-wind"></i> Velocidad de viento (kn)</span></div><div class="sp-card-body"><canvas id="sensor-wind" height="100"></canvas></div></div></div>
        <div class="col-md-6"><div class="sp-card"><div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-tint"></i> Humedad (%)</span></div><div class="sp-card-body"><canvas id="sensor-humidity" height="100"></canvas></div></div></div>
        <div class="col-md-6"><div class="sp-card"><div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-bolt"></i> Corriente eléctrica (A)</span></div><div class="sp-card-body"><canvas id="sensor-current" height="100"></canvas></div></div></div>
      </div>

      <!-- History -->
      <div class="sp-card">
        <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-history"></i> Historial de Escalas en Este Atraque</span></div>
        <div class="sp-table-wrapper">
          <table class="sp-table">
            <thead><tr><th>Buque</th><th>Puerto</th><th>Estado</th><th>ETA</th><th>Duración</th><th>Carga</th></tr></thead>
            <tbody>
              ${history.map(pc => `
                <tr>
                  <td><strong>${pc.vesselName}</strong></td>
                  <td>${pc.portName}</td>
                  <td><span class="sp-badge ${pc.state}">${pc.state}</span></td>
                  <td>${formatDate(pc.eta, 'medium')}</td>
                  <td>${pc.durationHours}h</td>
                  <td>${pc.cargo}</td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  _initCharts(sensorData) {
    if (!window.Chart) return;
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const textColor = isDark ? '#8b949e' : '#6c757d';
    const gridColor = isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.05)';
    const labels = sensorData.map((_, i) => i % 4 === 0 ? `${i}h` : '');
    const opts = (color) => ({
      responsive: true, maintainAspectRatio: false,
      scales: { x: { ticks: { color: textColor, maxTicksLimit: 6 }, grid: { color: gridColor } }, y: { ticks: { color: textColor }, grid: { color: gridColor } } },
      plugins: { legend: { display: false } }, elements: { point: { radius: 0 } }
    });
    const mkLine = (id, data, color) => {
      const el = document.getElementById(id);
      if (!el) return;
      this._charts[id] = new window.Chart(el, { type: 'line', data: { labels, datasets: [{ data, borderColor: color, backgroundColor: color + '22', borderWidth: 2, tension: 0.4, fill: true }] }, options: opts(color) });
    };
    mkLine('sensor-temp', sensorData.map(d => d.temperature), '#dc3545');
    mkLine('sensor-wind', sensorData.map(d => d.windSpeed), '#0052CC');
    mkLine('sensor-humidity', sensorData.map(d => d.humidity), '#17a2b8');
    mkLine('sensor-current', sensorData.map(d => d.current), '#ffa500');
  }

  _initMap(berth) {
    if (!window.L) return;
    const port = PORTS.find(p => p.id === berth.portId);
    if (!port) return;
    const el = document.getElementById('berth-map');
    if (!el || el._leaflet_id) return;
    const map = window.L.map('berth-map', { scrollWheelZoom: false, zoomControl: false }).setView([port.location.lat, port.location.lon], 13);
    window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(map);
    window.L.circleMarker([port.location.lat, port.location.lon], { radius: 10, fillColor: '#0052CC', color: '#fff', weight: 2, fillOpacity: 0.9 }).addTo(map).bindPopup(`<strong>${berth.name}</strong><br>${port.name}`).openPopup();
    this._map = map;
  }

  destroy() {
    Object.values(this._charts).forEach(c => { try{c.destroy();}catch{} });
    this._charts = {};
    if (this._map) { try{this._map.remove();}catch{} this._map = null; }
  }
}

function _sLabel(s) { return { free:'Libre', occupied:'Ocupado', reserved:'Reservado', maintenance:'Mantenimiento' }[s] || s; }
