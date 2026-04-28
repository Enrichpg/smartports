/**
 * Header Component
 * Main navigation header with branding, status, and quick actions
 */

export function Header({ currentPage, onNavigate, connectionStatus }) {
  const statusBadgeClass =
    connectionStatus === 'connected'
      ? 'badge-success'
      : connectionStatus === 'connecting'
        ? 'badge-warning'
        : 'badge-danger';

  const statusText =
    connectionStatus === 'connected'
      ? 'Conectado'
      : connectionStatus === 'connecting'
        ? 'Conectando...'
        : 'Desconectado';

  return `
    <nav class="navbar navbar-dark bg-primary sticky-top shadow-sm">
      <div class="container-fluid">
        <span class="navbar-brand mb-0 h1">
          <i class="fas fa-ship"></i> SmartPort Galicia Operations Center
        </span>
        <div class="d-flex align-items-center gap-3">
          <div class="text-white">
            <small>Página actual: <strong>${currentPage}</strong></small>
          </div>
          <span class="badge ${statusBadgeClass}" id="connection-status-badge">
            <i class="fas fa-circle-fill"></i> ${statusText}
          </span>
        </div>
      </div>
    </nav>
  `;
}

/**
 * Sidebar Component
 * Navigation sidebar with main menu options
 */

export function Sidebar({ isOpen, onNavigate, currentPage }) {
  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: 'fa-chart-line',
      page: 'dashboard',
    },
    {
      id: 'alerts',
      label: 'Alertas',
      icon: 'fa-bell',
      page: 'alerts',
    },
    {
      id: 'operations',
      label: 'Operaciones',
      icon: 'fa-cogs',
      page: 'operations',
    },
  ];

  const menuHTML = menuItems
    .map(
      (item) => `
    <li class="nav-item">
      <a class="nav-link ${currentPage === item.page ? 'active' : ''}" 
         href="#" 
         data-page="${item.page}">
        <i class="fas ${item.icon}"></i>
        <span>${item.label}</span>
      </a>
    </li>
  `
    )
    .join('');

  return `
    <nav class="sidebar bg-dark ${isOpen ? 'open' : 'closed'}">
      <ul class="nav flex-column">
        ${menuHTML}
      </ul>
    </nav>
  `;
}

/**
 * KPI Card Component
 * Displays a single KPI metric with value, label, and trend
 */

export function KpiCard({
  title,
  value,
  icon,
  color = 'primary',
  trend = null,
  unit = '',
  onClick = null,
}) {
  let borderClass = `border-left-${color}`;
  let iconClass = `text-${color}`;

  if (color === 'success') borderClass = 'border-left-success';
  if (color === 'warning') borderClass = 'border-left-warning';
  if (color === 'danger') borderClass = 'border-left-danger';

  const trendHTML =
    trend !== null
      ? `
    <small class="${trend > 0 ? 'text-success' : 'text-danger'}">
      <i class="fas fa-arrow-${trend > 0 ? 'up' : 'down'}"></i> ${Math.abs(trend)}%
    </small>
  `
      : '';

  const clickHandler = onClick ? `onclick="(${onClick})()"` : '';

  return `
    <div class="card ${borderClass} h-100 py-2 ${onClick ? 'cursor-pointer' : ''}" ${clickHandler}>
      <div class="card-body">
        <div class="${iconClass} text-uppercase mb-1">
          <small><i class="fas ${icon}"></i> <strong>${title}</strong></small>
        </div>
        <div class="h3 mb-0">${value}${unit}</div>
        ${trendHTML}
      </div>
    </div>
  `;
}

/**
 * Connection Status Badge Component
 */

export function ConnectionStatus({ status, isDebug = false }) {
  const statusConfig = {
    connected: {
      badge: 'badge-success',
      icon: 'fa-check-circle',
      text: 'Conectado',
    },
    connecting: {
      badge: 'badge-warning',
      icon: 'fa-hourglass-half',
      text: 'Conectando...',
    },
    disconnected: {
      badge: 'badge-danger',
      icon: 'fa-times-circle',
      text: 'Desconectado',
    },
    reconnecting: {
      badge: 'badge-info',
      icon: 'fa-sync',
      text: 'Reconectando...',
    },
  };

  const config = statusConfig[status] || statusConfig.disconnected;

  let debugInfo = '';
  if (isDebug) {
    debugInfo = `<small class="d-block mt-2">Status: ${status}</small>`;
  }

  return `
    <div class="badge ${config.badge}">
      <i class="fas ${config.icon}"></i> ${config.text}
      ${debugInfo}
    </div>
  `;
}

/**
 * Loading Skeleton Component
 * Displays skeleton loaders while data is loading
 */

export function LoadingSkeleton({ lines = 3, height = 'auto' }) {
  const skeletonLines = Array(lines)
    .fill(0)
    .map(() => '<div class="skeleton-line mb-2"></div>')
    .join('');

  return `
    <div class="skeleton-loader" style="height: ${height}">
      ${skeletonLines}
    </div>
  `;
}

/**
 * Error Banner Component
 */

export function ErrorBanner({ message, onDismiss = null }) {
  const dismissBtn = onDismiss
    ? `<button class="btn-close" onclick="(${onDismiss})()" aria-label="Close"></button>`
    : '';

  return `
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
      <i class="fas fa-exclamation-circle"></i> ${message}
      ${dismissBtn}
    </div>
  `;
}

/**
 * Success Banner Component
 */

export function SuccessBanner({ message, onDismiss = null }) {
  const dismissBtn = onDismiss
    ? `<button class="btn-close" onclick="(${onDismiss})()" aria-label="Close"></button>`
    : '';

  return `
    <div class="alert alert-success alert-dismissible fade show" role="alert">
      <i class="fas fa-check-circle"></i> ${message}
      ${dismissBtn}
    </div>
  `;
}

/**
 * Empty State Component
 */

export function EmptyState({
  icon = 'fa-inbox',
  title = 'Sin datos',
  message = 'No hay datos disponibles en este momento',
  action = null,
}) {
  const actionBtn = action
    ? `<button class="btn btn-primary mt-3" onclick="(${action.callback})()">${action.label}</button>`
    : '';

  return `
    <div class="text-center py-5">
      <i class="fas ${icon} fa-3x text-muted mb-3"></i>
      <h5 class="text-muted">${title}</h5>
      <p class="text-muted">${message}</p>
      ${actionBtn}
    </div>
  `;
}

/**
 * Filter Bar Component
 */

export function FilterBar({ filters, onFilterChange, clearAllHandler = null }) {
  const filterButtons = Object.entries(filters)
    .map(([key, value]) => {
      if (!value) return '';
      return `
    <span class="badge bg-info me-2">
      ${key}: ${value}
      <button class="btn-close btn-close-white ms-1" onclick="removeFilter('${key}')" style="font-size: 0.7rem;"></button>
    </span>
  `;
    })
    .join('');

  const clearBtn = clearAllHandler
    ? `<button class="btn btn-sm btn-outline-secondary" onclick="(${clearAllHandler})()">Limpiar filtros</button>`
    : '';

  return `
    <div class="card mb-3">
      <div class="card-body">
        <div class="d-flex align-items-center gap-2 flex-wrap">
          <strong>Filtros activos:</strong>
          ${filterButtons || '<span class="text-muted">Ninguno</span>'}
          ${clearBtn}
        </div>
      </div>
    </div>
  `;
}

/**
 * Status Badge Component
 */

export function StatusBadge({ status, customColors = {} }) {
  const statusColors = {
    free: 'badge-success',
    reserved: 'badge-warning',
    occupied: 'badge-danger',
    unavailable: 'badge-secondary',
    active: 'badge-success',
    inactive: 'badge-secondary',
    authorized: 'badge-info',
    pending: 'badge-warning',
    rejected: 'badge-danger',
    high: 'badge-danger',
    medium: 'badge-warning',
    low: 'badge-info',
    ...customColors,
  };

  const badgeClass = statusColors[status] || 'badge-secondary';
  const statusLabel =
    {
      free: 'Libre',
      reserved: 'Reservado',
      occupied: 'Ocupado',
      unavailable: 'No disponible',
      active: 'Activo',
      inactive: 'Inactivo',
      authorized: 'Autorizado',
      pending: 'Pendiente',
      rejected: 'Rechazado',
      high: 'Alta',
      medium: 'Media',
      low: 'Baja',
    }[status] || status;

  return `<span class="badge ${badgeClass}">${statusLabel}</span>`;
}

/**
 * Modal Component
 */

export function Modal({
  id = 'modal-default',
  title = 'Modal',
  content = '',
  buttons = [],
}) {
  const buttonHTML = buttons
    .map(
      (btn) =>
        `<button type="button" class="btn btn-${btn.type || 'secondary'}" onclick="${btn.onclick}" ${btn.closeOnClick ? 'data-bs-dismiss="modal"' : ''}>${btn.label}</button>`
    )
    .join('');

  return `
    <div class="modal fade" id="${id}" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">${title}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            ${content}
          </div>
          <div class="modal-footer">
            ${buttonHTML}
          </div>
        </div>
      </div>
    </div>
  `;
}
