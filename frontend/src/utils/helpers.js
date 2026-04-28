/**
 * Utility Functions
 */

export function formatDate(date, format = 'medium') {
  if (!date) return 'N/A';
  const d = new Date(date);
  
  const formats = {
    short: () => d.toLocaleDateString('es-ES'),
    medium: () => d.toLocaleString('es-ES'),
    time: () => d.toLocaleTimeString('es-ES'),
    iso: () => d.toISOString(),
  };

  return formats[format] ? formats[format]() : d.toLocaleString('es-ES');
}

export function formatNumber(num, decimals = 0) {
  if (typeof num !== 'number') return 'N/A';
  return num.toLocaleString('es-ES', { maximumFractionDigits: decimals });
}

export function formatPercent(num, decimals = 1) {
  if (typeof num !== 'number') return 'N/A';
  return `${num.toFixed(decimals)}%`;
}

export function truncate(text, maxLength = 50) {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

export function debounce(fn, delay = 300) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

export function throttle(fn, limit = 300) {
  let lastRun = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastRun >= limit) {
      fn(...args);
      lastRun = now;
    }
  };
}

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function retryAsync(fn, maxAttempts = 3, delayMs = 1000) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxAttempts - 1) throw error;
      await sleep(delayMs * (i + 1));
    }
  }
}

export function getQueryParam(param) {
  const params = new URLSearchParams(window.location.search);
  return params.get(param);
}

export function setQueryParam(param, value) {
  const params = new URLSearchParams(window.location.search);
  params.set(param, value);
  window.history.replaceState({}, '', `?${params.toString()}`);
}

export function removeQueryParam(param) {
  const params = new URLSearchParams(window.location.search);
  params.delete(param);
  window.history.replaceState({}, '', `?${params.toString()}`);
}

export function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

export function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map((x) => {
    const hex = x.toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('');
}

export function getDaysDifference(date1, date2) {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  const diffTime = Math.abs(d2 - d1);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}

export function getHoursDifference(date1, date2) {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  const diffTime = Math.abs(d2 - d1);
  const diffHours = Math.ceil(diffTime / (1000 * 60 * 60));
  return diffHours;
}

export function getMinutesDifference(date1, date2) {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  const diffTime = Math.abs(d2 - d1);
  const diffMinutes = Math.ceil(diffTime / (1000 * 60));
  return diffMinutes;
}

export function isWithinLastMinutes(date, minutes = 5) {
  const now = new Date();
  const diff = getMinutesDifference(date, now);
  return diff <= minutes;
}

export function isWithinLastHours(date, hours = 24) {
  const now = new Date();
  const diff = getHoursDifference(date, now);
  return diff <= hours;
}

export function calculateOccupancy(occupied, total) {
  if (!total || total === 0) return 0;
  return ((occupied / total) * 100).toFixed(1);
}

export function getOccupancyStatus(occupancy) {
  if (occupancy >= 90) return 'critical';
  if (occupancy >= 70) return 'high';
  if (occupancy >= 50) return 'medium';
  return 'low';
}

export function getStatusIcon(status) {
  const icons = {
    free: 'fa-check-circle text-success',
    occupied: 'fa-times-circle text-danger',
    reserved: 'fa-exclamation-circle text-warning',
    unavailable: 'fa-lock text-secondary',
    active: 'fa-check-circle text-success',
    inactive: 'fa-times-circle text-danger',
    authorized: 'fa-check text-success',
    pending: 'fa-clock text-warning',
    rejected: 'fa-times text-danger',
  };
  return icons[status] || 'fa-question-circle text-muted';
}

export function filterByText(items, searchText, fields = []) {
  if (!searchText) return items;
  const lowerSearch = searchText.toLowerCase();
  return items.filter((item) =>
    fields.some((field) => {
      const value = item[field];
      return value && value.toString().toLowerCase().includes(lowerSearch);
    })
  );
}

export function filterByField(items, field, value) {
  if (!value) return items;
  return items.filter((item) => item[field] === value);
}

export function groupBy(items, key) {
  return items.reduce((groups, item) => {
    const groupKey = item[key];
    if (!groups[groupKey]) {
      groups[groupKey] = [];
    }
    groups[groupKey].push(item);
    return groups;
  }, {});
}

export function sortBy(items, key, ascending = true) {
  return [...items].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
    return ascending ? comparison : -comparison;
  });
}

export function countBy(items, key) {
  return items.reduce((counts, item) => {
    const groupKey = item[key];
    counts[groupKey] = (counts[groupKey] || 0) + 1;
    return counts;
  }, {});
}

export function handleError(error, defaultMessage = 'Error desconocido') {
  let message = defaultMessage;
  
  if (error instanceof Error) {
    message = error.message;
  } else if (typeof error === 'string') {
    message = error;
  } else if (error.detail) {
    message = error.detail;
  } else if (error.message) {
    message = error.message;
  }

  console.error('[ERROR]', message, error);
  return message;
}

export function showNotification(message, type = 'info', duration = 5000) {
  const notificationDiv = document.getElementById('notification-container');
  if (!notificationDiv) {
    console.warn('Notification container not found');
    return;
  }

  const alertClass = `alert-${type}`;
  const html = `
    <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  `;

  notificationDiv.insertAdjacentHTML('beforeend', html);

  if (duration > 0) {
    setTimeout(() => {
      const alerts = notificationDiv.querySelectorAll('.alert');
      if (alerts.length > 0) {
        alerts[0].remove();
      }
    }, duration);
  }
}

export function showSuccessNotification(message, duration = 3000) {
  showNotification(message, 'success', duration);
}

export function showErrorNotification(message, duration = 5000) {
  showNotification(message, 'danger', duration);
}

export function showWarningNotification(message, duration = 5000) {
  showNotification(message, 'warning', duration);
}

export function showInfoNotification(message, duration = 4000) {
  showNotification(message, 'info', duration);
}

export function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

export function validateURL(url) {
  try {
    new URL(url);
    return true;
  } catch (_) {
    return false;
  }
}

export function generateId(prefix = 'id') {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

export function mergeObjects(target, source) {
  return { ...target, ...source };
}

export function objectToQueryString(obj) {
  return Object.entries(obj)
    .filter(([_, v]) => v !== null && v !== undefined)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');
}

export function queryStringToObject(queryString) {
  const params = new URLSearchParams(queryString);
  const obj = {};
  for (const [key, value] of params) {
    obj[key] = value;
  }
  return obj;
}
