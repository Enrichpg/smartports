/**
 * Port-specific Components
 * PortCard, PortMap, BerthTable, etc.
 */

import { StatusBadge } from './base.js';

/**
 * Port Card Component
 * Displays port summary in card format
 */

export function PortCard({
  port,
  onClick = null,
  showDetails = true,
  compact = false,
}) {
  if (!port) return '<div class="alert alert-warning">Puerto no disponible</div>';

  const clickHandler = onClick ? `onclick="(${onClick})('${port.id}'); return false;"` : '';
  const cardSize = compact ? 'col-md-4' : 'col-md-6';

  const details = showDetails
    ? `
    <div class="row mt-2 small">
      <div class="col-6">
        <strong>Atraques:</strong> ${port.total_berths || 0}
      </div>
      <div class="col-6">
        <strong>Ocupados:</strong> ${port.occupied_berths || 0}
      </div>
      <div class="col-6">
        <strong>Libres:</strong> ${port.free_berths || 0}
      </div>
      <div class="col-6">
        <strong>Alertas:</strong> ${port.active_alerts || 0}
      </div>
    </div>
  `
    : '';

  return `
    <div class="card cursor-pointer port-card h-100 ${onClick ? 'shadow-hover' : ''}" ${clickHandler} style="transition: all 0.3s;">
      <div class="card-body">
        <h5 class="card-title">${port.name || port.id}</h5>
        <p class="card-text small text-muted">${port.location || 'Ubicación no disponible'}</p>
        ${StatusBadge({ status: port.status || 'active' })}
        ${details}
      </div>
    </div>
  `;
}

/**
 * Berth Table Component
 * Displays list of berths with status, filters, and actions
 */

export function BerthTable({
  berths = [],
  filters = {},
  loading = false,
  onBerthSelect = null,
}) {
  if (loading) {
    return `
      <div class="table-responsive">
        <table class="table table-hover">
          <thead class="table-light">
            <tr>
              <th>Atraque</th>
              <th>Puerto</th>
              <th>Facility</th>
              <th>Estado</th>
              <th>Buque Actual</th>
              <th>Categoría</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colspan="6" class="text-center py-4"><div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div></td></tr>
          </tbody>
        </table>
      </div>
    `;
  }

  if (!berths || berths.length === 0) {
    return `
      <div class="alert alert-info">
        <i class="fas fa-info-circle"></i> No hay atraques disponibles
      </div>
    `;
  }

  const rows = berths
    .map(
      (berth) => `
    <tr class="cursor-pointer ${onBerthSelect ? 'table-row-hover' : ''}" 
        ${onBerthSelect ? `onclick="(${onBerthSelect})('${berth.id}')"` : ''}>
      <td><strong>${berth.name || berth.id}</strong></td>
      <td>${berth.port_name || 'N/A'}</td>
      <td>${berth.facility_name || 'N/A'}</td>
      <td>${StatusBadge({ status: berth.status })}</td>
      <td>${berth.vessel_name || '-'}</td>
      <td><span class="badge bg-secondary">${berth.category || 'General'}</span></td>
    </tr>
  `
    )
    .join('');

  return `
    <div class="table-responsive">
      <table class="table table-hover table-sm">
        <thead class="table-light sticky-top">
          <tr>
            <th>Atraque</th>
            <th>Puerto</th>
            <th>Facility</th>
            <th>Estado</th>
            <th>Buque Actual</th>
            <th>Categoría</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    </div>
  `;
}

/**
 * Port Call Table Component
 */

export function PortCallTable({
  portCalls = [],
  loading = false,
  onPortCallSelect = null,
}) {
  if (loading) {
    return `
      <div class="text-center py-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
      </div>
    `;
  }

  if (!portCalls || portCalls.length === 0) {
    return `
      <div class="alert alert-info">
        <i class="fas fa-info-circle"></i> No hay escalas activas
      </div>
    `;
  }

  const rows = portCalls
    .map(
      (pc) => `
    <tr ${onPortCallSelect ? `onclick="(${onPortCallSelect})('${pc.id}')"` : ''}>
      <td><strong>${pc.vessel_name || pc.id}</strong></td>
      <td>${pc.port_name || 'N/A'}</td>
      <td>${pc.berth_name || '-'}</td>
      <td>${StatusBadge({ status: pc.status })}</td>
      <td>${new Date(pc.eta).toLocaleString() || 'N/A'}</td>
      <td>${pc.authorization_status ? StatusBadge({ status: pc.authorization_status }) : 'N/A'}</td>
    </tr>
  `
    )
    .join('');

  return `
    <div class="table-responsive">
      <table class="table table-hover table-sm">
        <thead class="table-light sticky-top">
          <tr>
            <th>Buque</th>
            <th>Puerto</th>
            <th>Atraque</th>
            <th>Estado</th>
            <th>ETA</th>
            <th>Autorización</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    </div>
  `;
}

/**
 * Alert Panel Component
 */

export function AlertPanel({
  alerts = [],
  loading = false,
  maxItems = 10,
  onAlertClick = null,
  filterBySeverity = null,
}) {
  if (loading) {
    return `
      <div class="text-center py-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Cargando alertas...</span>
        </div>
      </div>
    `;
  }

  let filtered = alerts;
  if (filterBySeverity) {
    filtered = alerts.filter((a) => a.severity === filterBySeverity);
  }

  if (!filtered || filtered.length === 0) {
    return `
      <div class="alert alert-success">
        <i class="fas fa-check-circle"></i> Sin alertas activas
      </div>
    `;
  }

  const displayAlerts = filtered.slice(0, maxItems);

  const alertItems = displayAlerts
    .map(
      (alert) => `
    <div class="alert alert-${getSeverityClass(alert.severity)} mb-2 py-2" 
         ${onAlertClick ? `onclick="(${onAlertClick})('${alert.id}')"` : ''} 
         role="alert">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <strong>${alert.title || alert.type}</strong>
          <p class="mb-0 small">${alert.message || 'Sin descripción'}</p>
          <small class="text-muted">${new Date(alert.timestamp).toLocaleString()}</small>
        </div>
        <span class="badge bg-${getSeverityColor(alert.severity)}">${alert.severity || 'info'}</span>
      </div>
    </div>
  `
    )
    .join('');

  const moreAlerts =
    filtered.length > maxItems
      ? `<div class="alert alert-info small">+ ${filtered.length - maxItems} alertas más</div>`
      : '';

  return `
    <div class="alert-panel">
      ${alertItems}
      ${moreAlerts}
    </div>
  `;
}

/**
 * Availability Panel Component
 */

export function AvailabilityPanel({
  availability = null,
  loading = false,
}) {
  if (loading) {
    return `
      <div class="text-center py-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Cargando disponibilidad...</span>
        </div>
      </div>
    `;
  }

  if (!availability) {
    return `
      <div class="alert alert-warning">
        <i class="fas fa-exclamation-triangle"></i> Datos de disponibilidad no disponibles
      </div>
    `;
  }

  const total = availability.total_berths || 0;
  const free = availability.free_berths || 0;
  const occupied = availability.occupied_berths || 0;
  const reserved = availability.reserved_berths || 0;
  const unavailable = availability.unavailable_berths || 0;

  const freePercent = total > 0 ? ((free / total) * 100).toFixed(1) : 0;
  const occupiedPercent = total > 0 ? ((occupied / total) * 100).toFixed(1) : 0;
  const reservedPercent = total > 0 ? ((reserved / total) * 100).toFixed(1) : 0;
  const unavailablePercent = total > 0 ? ((unavailable / total) * 100).toFixed(1) : 0;

  return `
    <div class="availability-panel">
      <div class="card">
        <div class="card-body">
          <h6 class="card-title mb-3">Disponibilidad de Atraques</h6>
          
          <div class="mb-3">
            <div class="progress" style="height: 30px;">
              <div class="progress-bar bg-success" style="width: ${freePercent}%" title="Libre">
                <small>${free}/${total}</small>
              </div>
              <div class="progress-bar bg-danger" style="width: ${occupiedPercent}%" title="Ocupado"></div>
              <div class="progress-bar bg-warning" style="width: ${reservedPercent}%" title="Reservado"></div>
              <div class="progress-bar bg-secondary" style="width: ${unavailablePercent}%" title="No disponible"></div>
            </div>
          </div>

          <div class="row text-center small">
            <div class="col-3">
              <div class="badge bg-success">Libre</div>
              <div>${free}</div>
              <div class="text-muted">${freePercent}%</div>
            </div>
            <div class="col-3">
              <div class="badge bg-danger">Ocupado</div>
              <div>${occupied}</div>
              <div class="text-muted">${occupiedPercent}%</div>
            </div>
            <div class="col-3">
              <div class="badge bg-warning">Reservado</div>
              <div>${reserved}</div>
              <div class="text-muted">${reservedPercent}%</div>
            </div>
            <div class="col-3">
              <div class="badge bg-secondary">No disponible</div>
              <div>${unavailable}</div>
              <div class="text-muted">${unavailablePercent}%</div>
            </div>
          </div>
        </div>
      </div>

      ${availability.by_facility ? getFacilityAvailability(availability.by_facility) : ''}
    </div>
  `;
}

// ============= HELPER FUNCTIONS =============

function getSeverityClass(severity) {
  const severityMap = {
    high: 'danger',
    medium: 'warning',
    low: 'info',
    info: 'info',
  };
  return severityMap[severity] || 'info';
}

function getSeverityColor(severity) {
  const severityMap = {
    high: 'danger',
    medium: 'warning',
    low: 'info',
    info: 'info',
  };
  return severityMap[severity] || 'info';
}

function getFacilityAvailability(byFacility) {
  const facilities = Object.entries(byFacility)
    .map(
      ([facility, stats]) => `
    <div class="facility-item mb-2">
      <div class="d-flex justify-content-between">
        <strong>${facility}</strong>
        <span class="badge bg-info">${stats.free || 0}/${stats.total || 0}</span>
      </div>
      <div class="progress" style="height: 20px;">
        <div class="progress-bar bg-success" style="width: ${stats.total ? ((stats.free / stats.total) * 100).toFixed(0) : 0}%"></div>
      </div>
    </div>
  `
    )
    .join('');

  return `
    <div class="mt-3">
      <h6>Por Facility</h6>
      ${facilities}
    </div>
  `;
}
