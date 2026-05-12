/**
 * i18n — Internationalization service
 * Supports: es (Español), gl (Galego), en (English)
 *
 * Usage:
 *   import { t, setLang, getCurrentLang, applyI18n } from './i18n.js';
 *   t('nav.ports')          // → "Puertos" / "Portos" / "Ports"
 *   window.t('status.free') // → via window.t shortcut
 */

const TRANSLATIONS = {
  es: {
    // ── Navigation ──────────────────────────
    'nav.dashboard':      'Dashboard',
    'nav.ports':          'Puertos',
    'nav.berths':         'Atraques',
    'nav.port_calls':     'Escalas',
    'nav.alerts':         'Alertas',
    'nav.vessels':        'Buques',
    'nav.documents':      'Documentos',
    'nav.analytics':      'Analytics',
    'nav.maps':           'Mapa',
    'nav.users':          'Equipos',
    'nav.settings':       'Configuración',
    'nav.section.main':   'Principal',
    'nav.section.ops':    'Operaciones',
    'nav.section.analysis': 'Análisis',
    'nav.section.admin':  'Administración',

    // ── Page titles ──────────────────────────
    'page.dashboard':     'Dashboard',
    'page.ports':         'Puertos de Galicia',
    'page.port_detail':   'Detalle de Puerto',
    'page.berths':        'Atraques',
    'page.berth_detail':  'Detalle de Atraque',
    'page.port_calls':    'Escalas Portuarias',
    'page.alerts':        'Centro de Alertas',
    'page.analytics':     'Analytics',
    'page.vessels':       'Buques',
    'page.users':         'Equipos',
    'page.settings':      'Configuración',
    'page.maps':          'Mapa Interactivo',
    'page.documents':     'Documentos',

    // ── Status labels ────────────────────────
    'status.free':        'Libre',
    'status.available':   'Libre',
    'status.occupied':    'Ocupado',
    'status.reserved':    'Reservado',
    'status.maintenance': 'Mantenimiento',
    'status.active':      'Activo',
    'status.inactive':    'Inactivo',
    'status.authorized':  'Autorizado',
    'status.pending':     'Pendiente',
    'status.completed':   'Completada',
    'status.rejected':    'Rechazado',
    'status.in_port':     'En Puerto',
    'status.underway':    'En Ruta',
    'status.approaching': 'Aproximándose',
    'status.departing':   'Saliendo',
    'status.critical':    'Crítica',
    'status.high':        'Alta',
    'status.medium':      'Media',
    'status.low':         'Baja',
    'status.resolved':    'Resuelta',
    'status.ignored':     'Ignorada',
    'status.valid':       'Válido',
    'status.expired':     'Caducado',

    // ── Connection ───────────────────────────
    'conn.connected':     'Live',
    'conn.connecting':    'Conectando...',
    'conn.disconnected':  'Desconectado',
    'conn.error':         'Error',

    // ── Common UI ────────────────────────────
    'ui.search':          'Buscar',
    'ui.filter':          'Filtrar',
    'ui.all':             'Todos',
    'ui.export':          'Exportar',
    'ui.save':            'Guardar cambios',
    'ui.cancel':          'Cancelar',
    'ui.close':           'Cerrar',
    'ui.view_detail':     'Ver detalle',
    'ui.edit':            'Editar',
    'ui.delete':          'Eliminar',
    'ui.loading':         'Cargando...',
    'ui.no_data':         'Sin datos',
    'ui.notifications':   'Notificaciones',
    'ui.clear_all':       'Limpiar todo',
    'ui.no_notif':        'Sin notificaciones',
    'ui.page_of':         'Pág.',
    'ui.results':         'resultados',

    // ── Toast titles ─────────────────────────
    'toast.success':      'Éxito',
    'toast.error':        'Error',
    'toast.warning':      'Aviso',
    'toast.info':         'Información',

    // ── Settings page ────────────────────────
    'settings.title':     'Configuración',
    'settings.appearance': 'Apariencia',
    'settings.theme':     'Tema de la interfaz',
    'settings.theme_light': 'Claro',
    'settings.theme_dark':  'Oscuro',
    'settings.language':  'Idioma',
    'settings.default_port': 'Puerto por defecto',
    'settings.notif':     'Notificaciones',
    'settings.notif_ws':  'Alertas en tiempo real (WebSocket)',
    'settings.notif_browser': 'Notificaciones del navegador',
    'settings.notif_email': 'Resumen diario por email',
    'settings.refresh':   'Actualización de Datos',
    'settings.auto_refresh': 'Actualización automática',
    'settings.interval':  'Intervalo de actualización',
    'settings.save':      'Guardar cambios',
    'settings.reset':     'Restablecer',
  },

  gl: {
    // ── Navigation ──────────────────────────
    'nav.dashboard':      'Panel de control',
    'nav.ports':          'Portos',
    'nav.berths':         'Amarres',
    'nav.port_calls':     'Escalas',
    'nav.alerts':         'Alertas',
    'nav.vessels':        'Buques',
    'nav.documents':      'Documentos',
    'nav.analytics':      'Análise',
    'nav.maps':           'Mapa',
    'nav.users':          'Equipos',
    'nav.settings':       'Configuración',
    'nav.section.main':   'Principal',
    'nav.section.ops':    'Operacións',
    'nav.section.analysis': 'Análise',
    'nav.section.admin':  'Administración',

    // ── Page titles ──────────────────────────
    'page.dashboard':     'Panel de control',
    'page.ports':         'Portos de Galicia',
    'page.port_detail':   'Detalle do Porto',
    'page.berths':        'Amarres',
    'page.berth_detail':  'Detalle do Amarre',
    'page.port_calls':    'Escalas Portuarias',
    'page.alerts':        'Centro de Alertas',
    'page.analytics':     'Análise',
    'page.vessels':       'Buques',
    'page.users':         'Equipos',
    'page.settings':      'Configuración',
    'page.maps':          'Mapa Interactivo',
    'page.documents':     'Documentos',

    // ── Status labels ────────────────────────
    'status.free':        'Libre',
    'status.available':   'Libre',
    'status.occupied':    'Ocupado',
    'status.reserved':    'Reservado',
    'status.maintenance': 'Mantemento',
    'status.active':      'Activo',
    'status.inactive':    'Inactivo',
    'status.authorized':  'Autorizado',
    'status.pending':     'Pendente',
    'status.completed':   'Completada',
    'status.rejected':    'Rexeitado',
    'status.in_port':     'No Porto',
    'status.underway':    'En Ruta',
    'status.approaching': 'Aproximándose',
    'status.departing':   'Saíndo',
    'status.critical':    'Crítica',
    'status.high':        'Alta',
    'status.medium':      'Media',
    'status.low':         'Baixa',
    'status.resolved':    'Resolto',
    'status.ignored':     'Ignorado',
    'status.valid':       'Válido',
    'status.expired':     'Caducado',

    // ── Connection ───────────────────────────
    'conn.connected':     'En liña',
    'conn.connecting':    'Conectando...',
    'conn.disconnected':  'Desconectado',
    'conn.error':         'Erro',

    // ── Common UI ────────────────────────────
    'ui.search':          'Buscar',
    'ui.filter':          'Filtrar',
    'ui.all':             'Todos',
    'ui.export':          'Exportar',
    'ui.save':            'Gardar cambios',
    'ui.cancel':          'Cancelar',
    'ui.close':           'Pechar',
    'ui.view_detail':     'Ver detalle',
    'ui.edit':            'Editar',
    'ui.delete':          'Eliminar',
    'ui.loading':         'Cargando...',
    'ui.no_data':         'Sen datos',
    'ui.notifications':   'Notificacións',
    'ui.clear_all':       'Limpar todo',
    'ui.no_notif':        'Sen notificacións',
    'ui.page_of':         'Páx.',
    'ui.results':         'resultados',

    // ── Toast titles ─────────────────────────
    'toast.success':      'Correcto',
    'toast.error':        'Erro',
    'toast.warning':      'Aviso',
    'toast.info':         'Información',

    // ── Settings page ────────────────────────
    'settings.title':     'Configuración',
    'settings.appearance': 'Aparencia',
    'settings.theme':     'Tema da interface',
    'settings.theme_light': 'Claro',
    'settings.theme_dark':  'Escuro',
    'settings.language':  'Idioma',
    'settings.default_port': 'Porto por defecto',
    'settings.notif':     'Notificacións',
    'settings.notif_ws':  'Alertas en tempo real (WebSocket)',
    'settings.notif_browser': 'Notificacións do navegador',
    'settings.notif_email': 'Resumo diario por correo',
    'settings.refresh':   'Actualización de Datos',
    'settings.auto_refresh': 'Actualización automática',
    'settings.interval':  'Intervalo de actualización',
    'settings.save':      'Gardar cambios',
    'settings.reset':     'Restablecer',
  },

  en: {
    // ── Navigation ──────────────────────────
    'nav.dashboard':      'Dashboard',
    'nav.ports':          'Ports',
    'nav.berths':         'Berths',
    'nav.port_calls':     'Port Calls',
    'nav.alerts':         'Alerts',
    'nav.vessels':        'Vessels',
    'nav.documents':      'Documents',
    'nav.analytics':      'Analytics',
    'nav.maps':           'Map',
    'nav.users':          'Teams',
    'nav.settings':       'Settings',
    'nav.section.main':   'Main',
    'nav.section.ops':    'Operations',
    'nav.section.analysis': 'Analysis',
    'nav.section.admin':  'Administration',

    // ── Page titles ──────────────────────────
    'page.dashboard':     'Dashboard',
    'page.ports':         'Galician Ports',
    'page.port_detail':   'Port Detail',
    'page.berths':        'Berths',
    'page.berth_detail':  'Berth Detail',
    'page.port_calls':    'Port Calls',
    'page.alerts':        'Alert Center',
    'page.analytics':     'Analytics',
    'page.vessels':       'Vessels',
    'page.users':         'Teams',
    'page.settings':      'Settings',
    'page.maps':          'Interactive Map',
    'page.documents':     'Documents',

    // ── Status labels ────────────────────────
    'status.free':        'Free',
    'status.available':   'Available',
    'status.occupied':    'Occupied',
    'status.reserved':    'Reserved',
    'status.maintenance': 'Maintenance',
    'status.active':      'Active',
    'status.inactive':    'Inactive',
    'status.authorized':  'Authorized',
    'status.pending':     'Pending',
    'status.completed':   'Completed',
    'status.rejected':    'Rejected',
    'status.in_port':     'In Port',
    'status.underway':    'Underway',
    'status.approaching': 'Approaching',
    'status.departing':   'Departing',
    'status.critical':    'Critical',
    'status.high':        'High',
    'status.medium':      'Medium',
    'status.low':         'Low',
    'status.resolved':    'Resolved',
    'status.ignored':     'Ignored',
    'status.valid':       'Valid',
    'status.expired':     'Expired',

    // ── Connection ───────────────────────────
    'conn.connected':     'Live',
    'conn.connecting':    'Connecting...',
    'conn.disconnected':  'Disconnected',
    'conn.error':         'Error',

    // ── Common UI ────────────────────────────
    'ui.search':          'Search',
    'ui.filter':          'Filter',
    'ui.all':             'All',
    'ui.export':          'Export',
    'ui.save':            'Save changes',
    'ui.cancel':          'Cancel',
    'ui.close':           'Close',
    'ui.view_detail':     'View detail',
    'ui.edit':            'Edit',
    'ui.delete':          'Delete',
    'ui.loading':         'Loading...',
    'ui.no_data':         'No data',
    'ui.notifications':   'Notifications',
    'ui.clear_all':       'Clear all',
    'ui.no_notif':        'No notifications',
    'ui.page_of':         'Page',
    'ui.results':         'results',

    // ── Toast titles ─────────────────────────
    'toast.success':      'Success',
    'toast.error':        'Error',
    'toast.warning':      'Warning',
    'toast.info':         'Info',

    // ── Settings page ────────────────────────
    'settings.title':     'Settings',
    'settings.appearance': 'Appearance',
    'settings.theme':     'Interface theme',
    'settings.theme_light': 'Light',
    'settings.theme_dark':  'Dark',
    'settings.language':  'Language',
    'settings.default_port': 'Default port',
    'settings.notif':     'Notifications',
    'settings.notif_ws':  'Real-time alerts (WebSocket)',
    'settings.notif_browser': 'Browser notifications',
    'settings.notif_email': 'Daily email summary',
    'settings.refresh':   'Data Refresh',
    'settings.auto_refresh': 'Auto refresh',
    'settings.interval':  'Refresh interval',
    'settings.save':      'Save changes',
    'settings.reset':     'Reset',
  },
};

// ── State ────────────────────────────────────────

let _lang = localStorage.getItem('sp-lang') || 'es';

// ── Core API ─────────────────────────────────────

/** Translate a key. Falls back to the ES translation, then the key itself. */
export function t(key, fallback) {
  const dict = TRANSLATIONS[_lang] || TRANSLATIONS.es;
  if (dict[key] !== undefined) return dict[key];
  if (TRANSLATIONS.es[key] !== undefined) return TRANSLATIONS.es[key];
  return fallback !== undefined ? fallback : key;
}

/** Set the active language and persist it. Does NOT re-render — call applyI18n() after. */
export function setLang(lang) {
  if (!TRANSLATIONS[lang]) return;
  _lang = lang;
  localStorage.setItem('sp-lang', lang);
  document.documentElement.setAttribute('lang', lang);
}

export function getCurrentLang() { return _lang; }

export function getAvailableLangs() {
  return [
    { code: 'es', label: 'Español' },
    { code: 'gl', label: 'Galego' },
    { code: 'en', label: 'English' },
  ];
}

/**
 * Walk the DOM and replace text in every [data-i18n] element.
 * Also handles [data-i18n-placeholder] for input placeholders.
 */
export function applyI18n(root = document) {
  root.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const translation = t(key);
    // Preserve child elements (e.g. icons) — only replace text nodes
    const textNodes = Array.from(el.childNodes).filter(n => n.nodeType === Node.TEXT_NODE);
    if (textNodes.length > 0) {
      textNodes[textNodes.length - 1].textContent = translation;
    } else if (!el.children.length) {
      el.textContent = translation;
    }
  });
  root.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
  });
  root.querySelectorAll('[data-i18n-title]').forEach(el => {
    el.title = t(el.getAttribute('data-i18n-title'));
  });
}

/** Called once on app init — loads saved lang and applies it to the document. */
export function initI18n() {
  const saved = localStorage.getItem('sp-lang') || 'es';
  setLang(saved);
}

// Make t() globally accessible for inline templates
window.t = t;
