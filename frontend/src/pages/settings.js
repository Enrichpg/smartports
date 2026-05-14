/**
 * Settings Page — User preferences, notifications, and system configuration
 */

import { setLang, applyI18n, getCurrentLang } from '../services/i18n.js';

export class SettingsPage {
  constructor() {
    this.pageId = 'settings';
    this._prefs = this._loadPrefs();
  }

  _loadPrefs() {
    try {
      const p = JSON.parse(localStorage.getItem('sp-settings') || '{}');
      if (!p.language) p.language = getCurrentLang();
      return p;
    } catch { return { language: getCurrentLang() }; }
  }

  _savePrefs() {
    try { localStorage.setItem('sp-settings', JSON.stringify(this._prefs)); } catch {}
  }

  async mount(containerId = 'page-content') {
    const container = document.getElementById(containerId);
    if (!container) return;
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const lang = this._prefs.language || 'es';
    const notifEmail = this._prefs.notifEmail !== false;
    const notifBrowser = this._prefs.notifBrowser !== false;
    const notifWs = this._prefs.notifWs !== false;
    const autoRefresh = this._prefs.autoRefresh !== false;
    const refreshInterval = this._prefs.refreshInterval || 30;
    const alertThreshold = this._prefs.alertThreshold || 'medium';
    const defaultPort = this._prefs.defaultPort || '';

    container.innerHTML = `
      <div class="page-header">
        <div class="page-title"><i class="fas fa-cog"></i> Configuración</div>
        <div class="page-subtitle">Preferencias del sistema y del usuario</div>
      </div>

      <div class="row g-3">
        <!-- Appearance -->
        <div class="col-lg-6">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-palette"></i> Apariencia</span></div>
            <div class="sp-card-body">
              <div class="mb-3">
                <label class="form-label fw-semibold">Tema de la interfaz</label>
                <div style="display:flex;gap:12px;flex-wrap:wrap">
                  <label style="cursor:pointer;display:flex;align-items:center;gap:8px;padding:10px 16px;border:2px solid ${!isDark ? 'var(--sp-primary)' : 'var(--sp-border)'};border-radius:8px;flex:1;min-width:120px" id="theme-light-label">
                    <input type="radio" name="theme" value="light" ${!isDark ? 'checked' : ''} id="theme-light">
                    <i class="fas fa-sun"></i> Claro
                  </label>
                  <label style="cursor:pointer;display:flex;align-items:center;gap:8px;padding:10px 16px;border:2px solid ${isDark ? 'var(--sp-primary)' : 'var(--sp-border)'};border-radius:8px;flex:1;min-width:120px" id="theme-dark-label">
                    <input type="radio" name="theme" value="dark" ${isDark ? 'checked' : ''} id="theme-dark">
                    <i class="fas fa-moon"></i> Oscuro
                  </label>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">Idioma</label>
                <select class="form-select form-select-sm" id="s-lang">
                  <option value="es" ${lang === 'es' ? 'selected' : ''}>Español</option>
                  <option value="gl" ${lang === 'gl' ? 'selected' : ''}>Galego</option>
                  <option value="en" ${lang === 'en' ? 'selected' : ''}>English</option>
                </select>
              </div>
              <div class="mb-0">
                <label class="form-label fw-semibold">Puerto por defecto</label>
                <select class="form-select form-select-sm" id="s-default-port">
                  <option value="">Todos los puertos</option>
                  <option value="galicia-a-coruna" ${defaultPort === 'galicia-a-coruna' ? 'selected' : ''}>A Coruña</option>
                  <option value="galicia-vigo" ${defaultPort === 'galicia-vigo' ? 'selected' : ''}>Vigo</option>
                  <option value="galicia-ferrol" ${defaultPort === 'galicia-ferrol' ? 'selected' : ''}>Ferrol</option>
                  <option value="galicia-marin" ${defaultPort === 'galicia-marin' ? 'selected' : ''}>Marín</option>
                  <option value="galicia-vilagarcia" ${defaultPort === 'galicia-vilagarcia' ? 'selected' : ''}>Vilagarcía</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Notifications -->
        <div class="col-lg-6">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-bell"></i> Notificaciones</span></div>
            <div class="sp-card-body">
              <div class="form-check form-switch mb-3">
                <input class="form-check-input" type="checkbox" id="s-notif-ws" ${notifWs ? 'checked' : ''}>
                <label class="form-check-label fw-semibold" for="s-notif-ws">Alertas en tiempo real (WebSocket)</label>
                <div style="font-size:0.78rem;color:var(--sp-text-muted)">Recibe alertas instantáneas cuando el sistema detecta eventos críticos</div>
              </div>
              <div class="form-check form-switch mb-3">
                <input class="form-check-input" type="checkbox" id="s-notif-browser" ${notifBrowser ? 'checked' : ''}>
                <label class="form-check-label fw-semibold" for="s-notif-browser">Notificaciones del navegador</label>
                <div style="font-size:0.78rem;color:var(--sp-text-muted)">Permite notificaciones push incluso cuando la ventana no está activa</div>
              </div>
              <div class="form-check form-switch mb-3">
                <input class="form-check-input" type="checkbox" id="s-notif-email" ${notifEmail ? 'checked' : ''}>
                <label class="form-check-label fw-semibold" for="s-notif-email">Resumen diario por email</label>
                <div style="font-size:0.78rem;color:var(--sp-text-muted)">Recibe un resumen operativo cada mañana a las 07:00</div>
              </div>
              <div class="mb-0">
                <label class="form-label fw-semibold">Nivel mínimo de alertas a mostrar</label>
                <select class="form-select form-select-sm" id="s-alert-threshold">
                  <option value="critical" ${alertThreshold === 'critical' ? 'selected' : ''}>Solo críticas</option>
                  <option value="high" ${alertThreshold === 'high' ? 'selected' : ''}>Críticas y altas</option>
                  <option value="medium" ${alertThreshold === 'medium' ? 'selected' : ''}>Media en adelante</option>
                  <option value="low" ${alertThreshold === 'low' ? 'selected' : ''}>Todas</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Data refresh -->
        <div class="col-lg-6">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-sync"></i> Actualización de Datos</span></div>
            <div class="sp-card-body">
              <div class="form-check form-switch mb-3">
                <input class="form-check-input" type="checkbox" id="s-auto-refresh" ${autoRefresh ? 'checked' : ''}>
                <label class="form-check-label fw-semibold" for="s-auto-refresh">Actualización automática</label>
                <div style="font-size:0.78rem;color:var(--sp-text-muted)">Recarga los datos de operaciones periódicamente</div>
              </div>
              <div id="s-interval-group" ${!autoRefresh ? 'style="opacity:0.5;pointer-events:none"' : ''}>
                <label class="form-label fw-semibold">Intervalo de actualización</label>
                <div style="display:flex;align-items:center;gap:12px">
                  <input type="range" class="form-range" min="10" max="120" step="10" value="${refreshInterval}" id="s-refresh-interval" style="flex:1">
                  <span id="s-interval-label" style="font-weight:700;min-width:40px;text-align:right">${refreshInterval}s</span>
                </div>
              </div>
              <div class="mt-3 pt-3" style="border-top:1px solid var(--sp-border)">
                <div style="font-size:0.85rem;color:var(--sp-text-muted);margin-bottom:8px">Estado de la conexión WebSocket</div>
                <div id="s-ws-status" style="display:flex;align-items:center;gap:8px;font-size:0.85rem">
                  <div style="width:8px;height:8px;border-radius:50%;background:#00A651"></div>
                  <span>Conectado y escuchando eventos</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Security / Profile -->
        <div class="col-lg-6">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-user-shield"></i> Cuenta y Seguridad</span></div>
            <div class="sp-card-body">
              <div style="display:flex;align-items:center;gap:14px;padding:12px;background:var(--sp-bg);border-radius:8px;margin-bottom:16px">
                <div style="width:48px;height:48px;border-radius:50%;background:#0052CC22;color:#0052CC;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.1rem">AG</div>
                <div>
                  <div style="font-weight:700">Ana García Rodríguez</div>
                  <div style="font-size:0.8rem;color:var(--sp-text-muted)">Capitán de Puerto · A Coruña</div>
                  <div style="font-size:0.78rem;color:var(--sp-text-muted)">a.garcia@portsgalicia.es</div>
                </div>
              </div>
              <div class="d-flex flex-column gap-2">
                <button class="btn btn-sm btn-outline-primary" onclick="window.showToast('Función disponible próximamente','info')"><i class="fas fa-key me-2"></i>Cambiar contraseña</button>
                <button class="btn btn-sm btn-outline-secondary" onclick="window.showToast('Sesiones terminadas','success')"><i class="fas fa-sign-out-alt me-2"></i>Cerrar otras sesiones</button>
                <button class="btn btn-sm btn-outline-secondary" onclick="window.showToast('Descargando log de actividad','info')"><i class="fas fa-download me-2"></i>Exportar actividad</button>
              </div>
            </div>
          </div>
        </div>

        <!-- System info -->
        <div class="col-12">
          <div class="sp-card">
            <div class="sp-card-header"><span class="sp-card-title"><i class="fas fa-info-circle"></i> Información del Sistema</span></div>
            <div class="sp-card-body">
              <div class="row g-3">
                <div class="col-sm-6 col-md-3">
                  <div style="font-size:0.78rem;color:var(--sp-text-muted)">Versión</div>
                  <div style="font-weight:600">SmartPort v2.0.0</div>
                </div>
                <div class="col-sm-6 col-md-3">
                  <div style="font-size:0.78rem;color:var(--sp-text-muted)">Backend</div>
                  <div style="font-weight:600">FastAPI + Orion-LD</div>
                </div>
                <div class="col-sm-6 col-md-3">
                  <div style="font-size:0.78rem;color:var(--sp-text-muted)">Entidades NGSI-LD</div>
                  <div style="font-weight:600">211 entidades</div>
                </div>
                <div class="col-sm-6 col-md-3">
                  <div style="font-size:0.78rem;color:var(--sp-text-muted)">Actualización</div>
                  <div style="font-weight:600">Iteración 12</div>
                </div>
              </div>
              <div class="mt-3 d-flex gap-2 flex-wrap">
                <button class="btn btn-sm btn-outline-secondary" onclick="window.showToast('Caché limpiada','success')"><i class="fas fa-broom me-1"></i>Limpiar caché</button>
                <button class="btn btn-sm btn-outline-secondary" onclick="window.showToast('Diagnóstico completado: todo OK','success')"><i class="fas fa-stethoscope me-1"></i>Diagnóstico</button>
                <button class="btn btn-sm btn-outline-secondary" onclick="window.showToast('Exportando configuración','info')"><i class="fas fa-file-export me-1"></i>Exportar config</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Save button -->
        <div class="col-12 d-flex justify-content-end gap-2">
          <button class="btn btn-outline-secondary" id="s-reset">Restablecer</button>
          <button class="btn btn-primary" id="s-save"><i class="fas fa-save me-1"></i>Guardar cambios</button>
        </div>
      </div>
    `;

    this._bindEvents(container);
  }

  _bindEvents(container) {
    // Theme toggle
    container.querySelectorAll('input[name="theme"]').forEach(radio => {
      radio.addEventListener('change', e => {
        const theme = e.target.value;
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('sp-theme', theme);
        container.querySelector('#theme-light-label').style.borderColor = theme === 'light' ? 'var(--sp-primary)' : 'var(--sp-border)';
        container.querySelector('#theme-dark-label').style.borderColor = theme === 'dark' ? 'var(--sp-primary)' : 'var(--sp-border)';
        this._prefs.theme = theme;
      });
    });

    // Interval slider
    const slider = container.querySelector('#s-refresh-interval');
    const label = container.querySelector('#s-interval-label');
    if (slider && label) {
      slider.addEventListener('input', () => { label.textContent = slider.value + 's'; this._prefs.refreshInterval = +slider.value; });
    }

    // Auto-refresh toggle
    container.querySelector('#s-auto-refresh')?.addEventListener('change', e => {
      this._prefs.autoRefresh = e.target.checked;
      const g = container.querySelector('#s-interval-group');
      if (g) g.style.cssText = e.target.checked ? '' : 'opacity:0.5;pointer-events:none';
    });

    // Other toggles
    ['notif-ws', 'notif-browser', 'notif-email'].forEach(id => {
      container.querySelector(`#s-${id}`)?.addEventListener('change', e => {
        this._prefs[id.replace('-', '')] = e.target.checked;
      });
    });
    container.querySelector('#s-lang')?.addEventListener('change', e => {
      this._prefs.language = e.target.value;
      setLang(e.target.value);
      const headerSel = document.getElementById('lang-selector');
      if (headerSel) headerSel.value = e.target.value;
      applyI18n(document);
      window.__smartPortApp?._route();
    });
    container.querySelector('#s-alert-threshold')?.addEventListener('change', e => { this._prefs.alertThreshold = e.target.value; });
    container.querySelector('#s-default-port')?.addEventListener('change', e => { this._prefs.defaultPort = e.target.value; });

    // Save
    container.querySelector('#s-save')?.addEventListener('click', () => {
      this._savePrefs();
      setLang(this._prefs.language || 'es');
      applyI18n(document);
      window.showToast('Configuración guardada correctamente', 'success');
    });

    // Reset
    container.querySelector('#s-reset')?.addEventListener('click', () => {
      localStorage.removeItem('sp-settings');
      this._prefs = {};
      window.showToast('Configuración restablecida', 'info');
      this.mount('page-content');
    });
  }

  destroy() {}
}
