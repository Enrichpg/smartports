# SmartPort Galicia - Frontend Dashboard

## 📊 Descripción

Dashboard operativo profesional para la red de puertos multiservicios de Galicia. Proporciona visualización en tiempo real, gestión de atraques, escalas de buques, alertas y disponibilidad mediante REST API y WebSocket.

## 🎯 Características Principales

### 1. **Dashboard Principal (Galicia)**
- Mapa interactivo de Galicia con marcadores de puertos
- Visualización de ocupación por puerto
- KPIs agregados (puertos activos, atraques libres, escalas, alertas)
- Tarjetas rápidas con resumen operativo
- Gráfica de distribución de atraques

### 2. **Vista Detalle de Puerto**
- Información completa del puerto
- KPIs por puerto (ocupación, disponibilidad)
- Tabla de atraques con filtros
- Tabla de escalas activas
- Panel de alertas locales
- Gráfica de disponibilidad

### 3. **Panel de Alertas**
- Vista consolidada de alertas en tiempo real
- Filtros por severidad, puerto y estado
- Gráficas de distribución de alertas
- Tabla detallada de alertas históricas
- Actualización push via WebSocket

### 4. **Vista de Operaciones**
- Panel consolidado operativo
- Tablas de atraques y escalas
- Filtros avanzados
- Resumen de estadísticas por puerto
- Identificación de puertos críticos

### 5. **Tiempo Real**
- Conexión WebSocket automática
- Reconexión inteligente con backoff exponencial
- Indicador de estado de conexión
- Suscripción a eventos:
  - `berth.updated`
  - `portcall.created`, `portcall.updated`, `portcall.closed`
  - `alert.created`
  - `availability.updated`
  - `port.summary.updated`

## 📁 Estructura del Proyecto

```
frontend/
├── index.html                 # Punto de entrada HTML
├── src/
│   ├── app.js                # Controlador principal de la aplicación
│   ├── services/
│   │   ├── api.js            # Cliente REST centralizado
│   │   └── websocket.js      # Gestor de WebSocket
│   ├── store/
│   │   └── store.js          # Estado global de la aplicación
│   ├── components/
│   │   ├── base.js           # Componentes base (Header, Card, etc)
│   │   ├── domain.js         # Componentes de dominio (Port, Berth, etc)
│   │   ├── map.js            # Componentes de mapa Leaflet
│   │   └── charts.js         # Componentes de gráficos Chart.js
│   ├── pages/
│   │   ├── dashboard.js      # Página principal
│   │   ├── port-detail.js    # Página de detalle de puerto
│   │   ├── alerts.js         # Página de alertas
│   │   └── operations.js     # Página de operaciones
│   ├── utils/
│   │   └── helpers.js        # Funciones utilitarias
│   └── styles/
│       └── dashboard.css     # Estilos principales
├── css/
│   └── style.css             # Estilos legados (opcional)
└── js/
    └── app.js                # Aplicación legada (opcional)
```

## 🚀 Instalación y Ejecución

### Requisitos
- Navegador moderno (Chrome, Firefox, Safari, Edge)
- Backend FastAPI corriendo en `http://localhost:8000`
- WebSocket disponible en `ws://localhost:8000/ws`

### Desarrollo Local

```bash
# Clonar repositorio
git clone <repo>
cd SmartPorts

# Servir frontend con Python
python3 -m http.server 3000 --directory frontend

# O con Node.js
npx http-server frontend -p 3000

# Acceder a
http://localhost:3000
```

### Variables de Entorno

En `frontend/index.html`, las variables están configuradas en:

```javascript
window.ENV = {
    BACKEND_URL: 'http://localhost:8000/api/v1',
    WS_URL: 'ws://localhost:8000/ws',
    DEBUG: false
};
```

## 🎨 Diseño y UX

### Colores por Estado

```
Libre        → Verde (#28a745)
Ocupado      → Rojo (#dc3545)
Reservado    → Amarillo (#ffc107)
No disponible → Gris (#6c757d)

Alerta Alta  → Rojo intenso (#dc3545)
Alerta Media → Naranja (#fd7e14)
Alerta Baja  → Azul (#17a2b8)
```

### Tipografía

- **Primaria**: Segoe UI, Tahoma
- **Monoespaciada**: Courier New
- **Escalas**: Responsive en xs, sm, md, lg, xl

### Componentes

Todos los componentes son funciones que retornan HTML strings. Soportan:
- Atributos reactivos
- Estilos condicionales
- Event handlers
- Estados de carga y error

## 🔌 API y WebSocket

### Cliente REST (apiClient)

```javascript
// Puertos
await apiClient.getPorts(limit, offset)
await apiClient.getPortById(portId)
await apiClient.getPortSummary(portId)
await apiClient.getPortBerths(portId, limit)
await apiClient.getPortAvailability(portId)

// Atraques
await apiClient.getBerths(portId, facilityId, limit)
await apiClient.getBerthById(berthId)

// Escalas
await apiClient.getPortCalls(portId, limit)
await apiClient.getPortCallById(portCallId)

// Alertas
await apiClient.getAlerts(portId, limit)
await apiClient.getAlertsByPort(portId)

// Disponibilidad
await apiClient.getAvailability()
await apiClient.getAvailabilityByPort(portId)
```

### WebSocket Manager (wsManager)

```javascript
// Conectar
wsManager.connect()

// Suscribirse a eventos
wsManager.subscribe('berth.updated', (data) => {
    console.log('Berth updated:', data)
})

// Enviar mensaje
wsManager.send({ type: 'subscribe', channel: 'ports' })

// Desconectar
wsManager.disconnect()

// Estado
wsManager.getStatus()
```

## 🗄️ Store (Estado Global)

```javascript
// Getters
store.getState()
store.getPorts()
store.getBerths()
store.getAlerts()
store.getPortCalls()
store.getKPIs()
store.getConnectionStatus()

// Setters
store.setPorts(ports, loading, error)
store.setBerths(berths, loading, error)
store.updateBerth(berthId, berthData)
store.addAlert(alert)
store.setConnectionStatus(status)

// Eventos
store.subscribe('alertsChanged', (payload) => {})
store.subscribe('berthsChanged', (payload) => {})
store.emit('custom-event', data)
```

## 🧪 Testing

### Tests Unitarios Básicos

```bash
# Con Jest (opcional)
npm test
```

### Tests Manuales

1. **Carga inicial**: Verificar que se cargan datos del backend
2. **WebSocket**: Abrir DevTools → Console, cambiar estado en backend
3. **Responsividad**: Redimensionar ventana del navegador
4. **Filtros**: Aplicar filtros y verificar actualización
5. **Navegación**: Hacer clic en puertos y verificar navegación

## 📱 Responsividad

### Breakpoints

- **XS (< 576px)**: Móvil (stacked layout)
- **SM (576-768px)**: Tablet pequeña
- **MD (768-992px)**: Tablet
- **LG (992-1200px)**: Desktop
- **XL (>1200px)**: Desktop grande

### Funcionalidad por Pantalla

- **Móvil**: Tabla comprimida, mapa full-width bajo
- **Tablet**: Tabla normal, mapa y panel lado a lado
- **Desktop**: Layout de 3 columnas, mapa grande

## ♿ Accesibilidad

- Etiquetas ARIA
- Contraste de colores WCAG AA
- Navegación por teclado
- Focus visible
- Fuentes legibles
- Respeto a preferencias de movimiento

## 🔒 Seguridad

- HTTPS/WSS en producción
- No hardcodear credenciales
- Validación de entrada
- Sanitización de HTML
- CORS configurado en backend

## 📊 Rendimiento

### Optimizaciones

- Carga perezosa de componentes
- Caché de datos en store
- Actualización incremental (no full re-render)
- Debouncing de eventos
- Compresión de CSS/JS

### Métricas Target

- **LCP**: < 2.5s
- **FID**: < 100ms
- **CLS**: < 0.1

## 🐛 Debugging

En DevTools:

```javascript
// Acceder a la app
window.__smartPortApp

// Acceder al store
window.__smartPortApp.currentPage.store

// Ver estado WebSocket
window.__smartPortApp.currentPage.wsManager.getStatus()

// Logs
localStorage.setItem('debug', '*')
```

## 📈 Próximos Pasos

### Funcionalidades Futuras

1. **3D Visualization** (Three.js)
2. **ML Forecasting** (Prophet)
3. **LLM Assistant** (Ollama)
4. **Dark Mode**
5. **Exportación de reportes (PDF/Excel)**
6. **Notificaciones push**
7. **Modo offline**
8. **PWA**

### Mejoras de Arquitectura

1. Migración a framework ligero (Vue.js o Lit)
2. State management mejorado (Vuex/Pinia)
3. Testing framework completo
4. Build tool (Vite)
5. Componentes web reutilizables

## 📝 Licencia

Parte del proyecto SmartPort Galicia.

## 👥 Contacto

Equipo SmartPort Galicia Operations
