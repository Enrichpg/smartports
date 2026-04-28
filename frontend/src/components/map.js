/**
 * Leaflet Map Component for Port Visualization
 */

export class PortMapController {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.map = null;
    this.markers = new Map();
    this.onPortSelect = options.onPortSelect || null;
    this.options = {
      zoom: options.zoom || 8,
      center: options.center || [42.6, -8.5], // Galicia center
      tileLayer: options.tileLayer || 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: options.attribution || '© OpenStreetMap',
      ...options,
    };
  }

  init() {
    // Initialize Leaflet map
    const container = document.getElementById(this.containerId);
    if (!container) {
      console.error(`Container ${this.containerId} not found`);
      return false;
    }

    try {
      this.map = L.map(this.containerId).setView(this.options.center, this.options.zoom);

      // Add tile layer
      L.tileLayer(this.options.tileLayer, {
        attribution: this.options.attribution,
        maxZoom: 19,
      }).addTo(this.map);

      return true;
    } catch (error) {
      console.error('Failed to initialize Leaflet map:', error);
      return false;
    }
  }

  addPort(port) {
    if (!this.map) {
      console.warn('Map not initialized');
      return;
    }

    if (!port.latitude || !port.longitude) {
      console.warn(`Port ${port.id} missing coordinates`);
      return;
    }

    const marker = L.circleMarker([port.latitude, port.longitude], {
      radius: this.getMarkerRadius(port),
      fillColor: this.getMarkerColor(port),
      color: '#000',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.7,
    }).addTo(this.map);

    const occupancyPercent = port.occupancy_percent || 0;
    const popupContent = `
      <div class="port-popup">
        <h6>${port.name}</h6>
        <p class="mb-1"><small>${port.location || 'Galicia'}</small></p>
        <div class="mb-2">
          <small>
            Ocupación: <strong>${occupancyPercent.toFixed(0)}%</strong><br>
            Atraques: <strong>${port.occupied_berths || 0}/${port.total_berths || 0}</strong><br>
            Alertas: <strong>${port.active_alerts || 0}</strong>
          </small>
        </div>
        <button class="btn btn-sm btn-primary" onclick="window.location.href='/ports/${port.id}'">
          Ver detalles
        </button>
      </div>
    `;

    marker.bindPopup(popupContent);

    // Add click handler
    marker.on('click', () => {
      if (this.onPortSelect) {
        this.onPortSelect(port);
      }
    });

    this.markers.set(port.id, marker);
  }

  updatePort(port) {
    if (this.markers.has(port.id)) {
      const marker = this.markers.get(port.id);
      marker.setRadius(this.getMarkerRadius(port));
      marker.setStyle({
        fillColor: this.getMarkerColor(port),
      });
    } else {
      this.addPort(port);
    }
  }

  removePort(portId) {
    if (this.markers.has(portId)) {
      const marker = this.markers.get(portId);
      marker.removeFrom(this.map);
      this.markers.delete(portId);
    }
  }

  clearPorts() {
    this.markers.forEach((marker) => {
      marker.removeFrom(this.map);
    });
    this.markers.clear();
  }

  fitBounds() {
    if (this.markers.size === 0) {
      this.map.setView(this.options.center, this.options.zoom);
      return;
    }

    const group = new L.featureGroup(Array.from(this.markers.values()));
    this.map.fitBounds(group.getBounds(), { padding: [50, 50] });
  }

  getMarkerColor(port) {
    const occupancyPercent = port.occupancy_percent || 0;

    if (occupancyPercent >= 90) return '#dc3545'; // Red - Critical
    if (occupancyPercent >= 70) return '#fd7e14'; // Orange - High
    if (occupancyPercent >= 50) return '#ffc107'; // Yellow - Medium
    return '#28a745'; // Green - Low occupancy
  }

  getMarkerRadius(port) {
    const totalBerths = port.total_berths || 1;
    return Math.max(5, Math.min(20, totalBerths / 2));
  }

  destroy() {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
    this.markers.clear();
  }
}

export function MapContainer({ mapId = 'map', width = '100%', height = '500px' }) {
  return `
    <div id="${mapId}" style="width: ${width}; height: ${height};" class="rounded"></div>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
  `;
}
