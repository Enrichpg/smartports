/**
 * Maps Page — Advanced interactive Leaflet map with layers, clustering, and vessel routes
 */

import { PORTS, generateBerths, generateVessels, generatePortCalls } from '../services/mock-data.js';

export class MapsPage {
  constructor() {
    this.pageId = 'maps';
    this._map = null;
    this._layers = {};
    this._layerControl = null;
    this._vesselMarkers = [];
    this._portMarkers = [];
    this._routeLines = [];
    this._activePorts = new Set(PORTS.map(p => p.id));
    this._activeTypes = new Set(['port', 'vessel', 'route']);
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
      <div class="page-header">
        <div class="page-title"><i class="fas fa-map"></i> Mapa Interactivo</div>
        <div class="page-subtitle">Vista geográfica de la red portuaria de Galicia</div>
      </div>

      <div class="row g-3 mb-3">
        <div class="col-12">
          <div class="sp-card">
            <div class="sp-card-body" style="padding:12px">
              <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center">
                <div style="font-size:0.82rem;font-weight:600;color:var(--sp-text-muted)">CAPAS:</div>
                <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:0.85rem">
                  <input type="checkbox" id="layer-ports" checked> <i class="fas fa-anchor" style="color:#0052CC"></i> Puertos
                </label>
                <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:0.85rem">
                  <input type="checkbox" id="layer-vessels" checked> <i class="fas fa-ship" style="color:#00A651"></i> Buques
                </label>
                <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:0.85rem">
                  <input type="checkbox" id="layer-routes" checked> <i class="fas fa-route" style="color:#ffa500"></i> Rutas
                </label>
                <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:0.85rem">
                  <input type="checkbox" id="layer-heatmap"> <i class="fas fa-fire" style="color:#dc3545"></i> Calor tráfico
                </label>
                <div style="margin-left:auto;display:flex;gap:8px">
                  <button class="btn btn-sm btn-outline-secondary" id="map-fit-all"><i class="fas fa-expand me-1"></i>Encuadrar</button>
                  <button class="btn btn-sm btn-outline-secondary" id="map-3d-hint" onclick="window.showToast('Vista 3D disponible en Detalle de Puerto','info')"><i class="fas fa-cube me-1"></i>Vista 3D</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-lg-8 col-xl-9">
          <div class="sp-card">
            <div id="main-map" style="height:520px;border-radius:0 0 8px 8px"></div>
          </div>
        </div>
        <div class="col-lg-4 col-xl-3">
          <div class="sp-card h-100">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-list"></i> Puertos</span></div>
            <div class="sp-card-body p-0">
              <div id="map-port-list" style="max-height:520px;overflow-y:auto"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Info panel (shown when clicking a port/vessel) -->
      <div id="map-info-panel" style="display:none" class="mt-3">
        <div class="sp-card">
          <div class="sp-card-header" style="display:flex;justify-content:space-between;align-items:center">
            <span class="sp-card-title" id="map-info-title">Detalle</span>
            <button class="btn btn-sm btn-outline-secondary" id="map-info-close"><i class="fas fa-times"></i></button>
          </div>
          <div class="sp-card-body" id="map-info-body"></div>
        </div>
      </div>
    `;

    setTimeout(() => {
      this._initMap();
      this._buildPortList();
    }, 50);

    container.querySelector('#map-fit-all')?.addEventListener('click', () => {
      if (this._map) this._map.fitBounds([[42.0, -9.2], [43.9, -6.8]]);
    });
    container.querySelector('#map-info-close')?.addEventListener('click', () => {
      document.getElementById('map-info-panel').style.display = 'none';
    });

    ['ports', 'vessels', 'routes', 'heatmap'].forEach(layer => {
      container.querySelector(`#layer-${layer}`)?.addEventListener('change', e => {
        this._toggleLayer(layer, e.target.checked);
      });
    });
  }

  _initMap() {
    if (!window.L) return;
    const el = document.getElementById('main-map');
    if (!el || el._leaflet_id) return;

    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const tileUrl = isDark
      ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    const tileAttr = isDark ? '© CARTO' : '© OpenStreetMap';

    this._map = window.L.map('main-map', { zoomControl: true }).setView([43.0, -8.2], 8);
    window.L.tileLayer(tileUrl, { attribution: tileAttr, maxZoom: 18 }).addTo(this._map);

    // Port markers
    this._layers.ports = window.L.layerGroup().addTo(this._map);
    PORTS.forEach(port => {
      const color = port.status === 'maintenance' ? '#6c757d' : (port.occupancyPct >= 75 ? '#dc3545' : '#0052CC');
      const marker = window.L.circleMarker([port.location.lat, port.location.lon], {
        radius: 14, fillColor: color, color: '#fff', weight: 2, fillOpacity: 0.9,
      }).addTo(this._layers.ports);

      const popupContent = `
        <div style="min-width:180px">
          <strong style="font-size:0.95rem">${port.name}</strong><br>
          <span style="font-size:0.8rem;color:#666">${port.type}</span><br>
          <div style="margin:6px 0;font-size:0.82rem">
            <div>Ocupación: <strong>${port.occupancyPct}%</strong></div>
            <div>Libres: <strong style="color:#00A651">${port.freeBerths}</strong> / ${port.totalBerths}</div>
          </div>
          <button onclick="window.spNavigate('port-detail',{portId:'${port.id}'})" style="background:#0052CC;color:#fff;border:none;padding:4px 10px;border-radius:4px;font-size:0.78rem;cursor:pointer">Ver detalle</button>
        </div>`;
      marker.bindPopup(popupContent);
      marker.on('click', () => this._showPortInfo(port));

      // Port label
      window.L.marker([port.location.lat, port.location.lon], {
        icon: window.L.divIcon({
          html: `<div style="background:transparent;font-size:10px;font-weight:700;color:${color};white-space:nowrap;margin-top:16px;text-shadow:0 1px 3px rgba(0,0,0,0.5)">${port.shortName}</div>`,
          className: '', iconAnchor: [0, 0],
        })
      }).addTo(this._layers.ports);

      this._portMarkers.push(marker);
    });

    // Vessel markers (synthetic positions near ports)
    this._layers.vessels = window.L.layerGroup().addTo(this._map);
    const vessels = generateVessels();
    vessels.forEach((v, i) => {
      const port = PORTS.find(p => p.id === v.portId) || PORTS[i % PORTS.length];
      const angle = (i * 47) % 360;
      const dist = 0.02 + (i % 3) * 0.015;
      const lat = port.location.lat + dist * Math.sin(angle * Math.PI / 180);
      const lon = port.location.lon + dist * Math.cos(angle * Math.PI / 180);
      const vColor = { in_port: '#00A651', approaching: '#17a2b8', underway: '#6c757d', departing: '#ffa500' }[v.status] || '#6c757d';

      const vMarker = window.L.circleMarker([lat, lon], {
        radius: 7, fillColor: vColor, color: '#fff', weight: 1.5, fillOpacity: 0.85,
      }).addTo(this._layers.vessels);
      vMarker.bindTooltip(`<strong>${v.name}</strong><br>${v.type}<br>${v.status}`, { permanent: false, direction: 'top' });
      this._vesselMarkers.push(vMarker);
    });

    // Route lines (simplified — lines between port pairs)
    this._layers.routes = window.L.layerGroup().addTo(this._map);
    const portCalls = generatePortCalls(15);
    const activePorts = PORTS.filter(p => p.status === 'active');
    portCalls.slice(0, 8).forEach((pc, i) => {
      const src = activePorts[i % activePorts.length];
      const dst = activePorts[(i + 2) % activePorts.length];
      if (src.id !== dst.id) {
        const line = window.L.polyline(
          [[src.location.lat, src.location.lon], [dst.location.lat, dst.location.lon]],
          { color: '#ffa500', weight: 1.5, opacity: 0.5, dashArray: '6,4' }
        ).addTo(this._layers.routes);
        line.bindTooltip(`${pc.vesselName}: ${src.shortName} → ${dst.shortName}`, { sticky: true });
        this._routeLines.push(line);
      }
    });

    // Heatmap layer placeholder (shown as overlay circles)
    this._layers.heatmap = window.L.layerGroup();
    PORTS.filter(p => p.status !== 'maintenance').forEach(p => {
      window.L.circle([p.location.lat, p.location.lon], {
        radius: p.occupancyPct * 200,
        fillColor: p.occupancyPct >= 70 ? '#dc3545' : p.occupancyPct >= 40 ? '#ffa500' : '#00A651',
        color: 'transparent', fillOpacity: 0.15,
      }).addTo(this._layers.heatmap);
    });
  }

  _toggleLayer(name, visible) {
    const layer = this._layers[name];
    if (!layer || !this._map) return;
    if (visible) this._map.addLayer(layer);
    else this._map.removeLayer(layer);
  }

  _showPortInfo(port) {
    const panel = document.getElementById('map-info-panel');
    const title = document.getElementById('map-info-title');
    const body = document.getElementById('map-info-body');
    if (!panel || !title || !body) return;

    const berths = generateBerths(port.id, port.totalBerths);
    const free = berths.filter(b => b.status === 'free').length;
    const occ = berths.filter(b => b.status === 'occupied').length;
    const res = berths.filter(b => b.status === 'reserved').length;

    title.innerHTML = `<i class="fas fa-anchor me-2"></i>${port.name}`;
    body.innerHTML = `
      <div class="row g-3">
        <div class="col-sm-6">
          <table class="table table-sm" style="font-size:0.875rem">
            <tbody>
              <tr><td class="text-muted">Tipo</td><td>${port.type}</td></tr>
              <tr><td class="text-muted">Estado</td><td><span class="sp-badge ${port.status}">${port.status === 'active' ? 'Activo' : 'Mantenimiento'}</span></td></tr>
              <tr><td class="text-muted">Ocupación</td><td><strong>${port.occupancyPct}%</strong></td></tr>
              <tr><td class="text-muted">Atraques</td><td>${port.totalBerths} total</td></tr>
              <tr><td class="text-muted">Coordenadas</td><td>${port.location.lat.toFixed(4)}, ${port.location.lon.toFixed(4)}</td></tr>
            </tbody>
          </table>
        </div>
        <div class="col-sm-6">
          <div class="row g-2 mb-3">
            <div class="col-4 text-center"><div style="font-size:1.4rem;font-weight:700;color:#00A651">${free}</div><div style="font-size:0.72rem;color:var(--sp-text-muted)">Libres</div></div>
            <div class="col-4 text-center"><div style="font-size:1.4rem;font-weight:700;color:#dc3545">${occ}</div><div style="font-size:0.72rem;color:var(--sp-text-muted)">Ocupados</div></div>
            <div class="col-4 text-center"><div style="font-size:1.4rem;font-weight:700;color:#ffa500">${res}</div><div style="font-size:0.72rem;color:var(--sp-text-muted)">Reservados</div></div>
          </div>
          <div class="sp-progress mb-2"><div class="sp-progress-bar ${port.occupancyPct >= 80 ? 'high' : port.occupancyPct >= 50 ? 'medium' : 'low'}" style="width:${port.occupancyPct}%"></div></div>
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-primary flex-fill" onclick="window.spNavigate('port-detail',{portId:'${port.id}'})">Ver detalle</button>
            <button class="btn btn-sm btn-outline-secondary flex-fill" onclick="window.spNavigate('berths')">Atraques</button>
          </div>
        </div>
      </div>`;
    panel.style.display = 'block';
  }

  _buildPortList() {
    const list = document.getElementById('map-port-list');
    if (!list) return;
    list.innerHTML = PORTS.map(port => `
      <div class="port-list-item" data-port-id="${port.id}" style="padding:10px 14px;border-bottom:1px solid var(--sp-border);cursor:pointer;transition:background 0.15s">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <div>
            <div style="font-weight:600;font-size:0.88rem">${port.shortName}</div>
            <div style="font-size:0.72rem;color:var(--sp-text-muted)">${port.type}</div>
          </div>
          <span class="sp-badge ${port.status}" style="font-size:0.65rem">${port.status === 'active' ? 'Activo' : 'Mtto'}</span>
        </div>
        <div style="margin-top:6px">
          <div class="sp-progress" style="margin-bottom:3px"><div class="sp-progress-bar ${port.occupancyPct >= 80 ? 'high' : port.occupancyPct >= 50 ? 'medium' : 'low'}" style="width:${port.occupancyPct}%"></div></div>
          <div style="font-size:0.72rem;color:var(--sp-text-muted)">${port.occupancyPct}% · ${port.freeBerths} libres / ${port.totalBerths}</div>
        </div>
      </div>`).join('');

    list.querySelectorAll('.port-list-item').forEach(item => {
      item.addEventListener('mouseenter', () => { item.style.background = 'var(--sp-bg)'; });
      item.addEventListener('mouseleave', () => { item.style.background = ''; });
      item.addEventListener('click', () => {
        const port = PORTS.find(p => p.id === item.dataset.portId);
        if (port && this._map) {
          this._map.setView([port.location.lat, port.location.lon], 13, { animate: true });
          this._showPortInfo(port);
        }
      });
    });
  }

  destroy() {
    if (this._map) { try { this._map.remove(); } catch {} this._map = null; }
    this._layers = {};
    this._vesselMarkers = [];
    this._portMarkers = [];
    this._routeLines = [];
  }
}
