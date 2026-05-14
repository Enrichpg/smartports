# SmartPort Galicia Operations Center

[![GitHub](https://img.shields.io/badge/GitHub-Enrichpg%2Fsmartports-blue?logo=github&logoColor=white)](https://github.com/Enrichpg/smartports)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Estado-Activo-success.svg)](https://github.com/Enrichpg/smartports/releases)

**Plataforma inteligente de gestión operativa en tiempo real para la red de puertos de Galicia.**

**Repositorio público:** [github.com/Enrichpg/smartports](https://github.com/Enrichpg/smartports)

---

### Enrique Pardo García — enrique.pardo.garcia@udc.es
### Sergio Varela Rodríguez — sergio.varela1@udc.es

## Visión general

**SmartPort Galicia** es una plataforma basada en FIWARE y conforme a NGSI-LD para gestionar múltiples puertos gallegos como un sistema unificado. Combina control operativo en tiempo real, analítica histórica, predicción mediante aprendizaje automático y soporte a la decisión con agentes inteligentes.

**Estado:** Activo — Iteración 13 completa (agentes LLM con herramientas, i18n global ES/GL/EN)
**Versión:** 1.6
**Última actualización:** 2026-05-14

---

## Índice

- [Funcionalidades](#funcionalidades)
- [Stack tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Inicio rápido](#inicio-rápido)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Configuración](#configuración)
- [Desarrollo](#desarrollo)
- [Despliegue](#despliegue)
- [Documentación](#documentación)
- [Resolución de problemas](#resolución-de-problemas)

---

## Funcionalidades

### Nuevo: Agentes LLM con herramientas (Iteración 13)
- **5 agentes especializados** — Operaciones, Predicciones, Mantenimiento, Cumplimiento, Incidentes
- **Herramientas reales** — los agentes consultan ocupación, atraques, alertas, previsiones y datos de buques en tiempo real
- **Chat integrado** en el frontal (`/ai-agents`), accesible desde el menú lateral
- **Motor Ollama/Llama 2** funcionando dentro de la red Docker

### Internacionalización completa (Iteración 13)
- **3 idiomas**: Español, Galego, English — selector en la barra superior
- **307 claves de traducción** sincronizadas en todas las páginas: dashboard, atraques, escalas, alertas, buques, documentos, analítica, agentes IA

### Infraestructura en tiempo real
- **WebSocket** — streaming de eventos en vivo a clientes conectados (atraques, escalas, alertas)
- **Registro de auditoría PostgreSQL** — historial operativo inmutable con instantáneas JSONB
- **Caché Redis** — latencia reducida, invalidación por eventos
- **Tareas Celery** — procesamiento asíncrono sin bloqueo, trabajos programados

### Integración con datos reales
- **AEMET OpenData** — servicio meteorológico español (autenticado con JWT)
- **MeteoGalicia** — previsiones meteorológicas y oceanográficas regionales
- **Puertos del Estado** — condiciones marítimas oficiales (oleaje, viento, corrientes)
- **Open-Meteo Marine API** — previsiones marítimas offshore sin coste
- Retorno inteligente a simuladores realistas cuando las APIs no están disponibles
- Trazabilidad completa del origen de los datos (fuente, nivel de confianza, marca temporal)

### Operaciones básicas
- Visualización en tiempo real de la red portuaria gallega (11+ puertos)
- Gestión de disponibilidad y ocupación de atraques
- Ciclo de vida de escalas: prevista → activa → completada
- Registro de operaciones (manipulación de carga, servicios, mantenimiento)
- Autorización de buques y seguimiento de cumplimiento
- Vigilancia medioambiental (calidad del aire, meteorología, alertas)

### Inteligencia y ML
- Previsión de ocupación con Prophet (modelo real CmdStan)
- Recomendación inteligente de atraque con Random Forest
- Motor de alertas con umbrales configurables y tipos: meteorológico, demora, seguridad...
- Asistente conversacional con agentes LLM especializados

### Analítica y visualización
- Cuadros de mando en tiempo real (mapas Leaflet, Chart.js)
- Analítica histórica (QuantumLeap / TimescaleDB)
- Dashboards Grafana integrados (aprovisionados automáticamente)
- KPIs: ocupación, tiempo de estancia, ingresos estimados
- Visualización 3D del puerto (Three.js) con actualización en vivo

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| **Broker de contexto** | Orion-LD (NGSI-LD v1.6) |
| **Series temporales** | QuantumLeap + TimescaleDB |
| **Broker de mensajes** | Mosquitto MQTT |
| **Backend** | FastAPI (Python 3.10+) |
| **Base de datos** | PostgreSQL + MongoDB |
| **Caché y cola** | Redis + Celery |
| **ML** | Prophet, scikit-learn |
| **LLM** | Ollama (Llama 2) |
| **Frontend** | HTML/CSS/JS + Leaflet + Three.js |
| **Visualización** | Chart.js + Grafana |
| **Infraestructura** | Docker Compose, Nginx |

---

## Arquitectura

**6 capas principales:**

```
┌──────────────────────────────────────────┐
│ Presentación (Leaflet, Charts, 3D)       │
├──────────────────────────────────────────┤
│ Backend FastAPI (REST, WebSocket, Lógica)│
├──────────────────────────────────────────┤
│ Contexto (Orion-LD) + Series (QL)        │
├──────────────────────────────────────────┤
│ Broker de mensajes (MQTT) + IoT Agent    │
├──────────────────────────────────────────┤
│ Bases de datos (PostgreSQL, TimescaleDB, │
│ MongoDB)                                 │
├──────────────────────────────────────────┤
│ Infraestructura (Docker Compose, Nginx)  │
└──────────────────────────────────────────┘
```

**Detalles completos:** Ver [docs/architecture.md](docs/architecture.md)

---

## Inicio rápido

### Integraciones con APIs reales

SmartPort incluye 4 integraciones con datos en vivo y retorno inteligente a simuladores:

- **AEMET** (meteorología española) — actualización cada 30 min
- **Puertos del Estado** (condiciones marítimas) — actualización cada 15 min
- **MeteoGalicia** (meteorología/océano regional) — actualización cada 30 min
- **Open-Meteo Marine API** (previsiones de oleaje) — actualización cada 30 min

Establece `AEMET_API_KEY` en `.env` para activar AEMET. El resto de fuentes funcionan sin clave.

---

### Requisitos previos

- Docker y Docker Compose (v20.10+)
- Git
- Python 3.10+ (solo para desarrollo local)
- 4+ GB de RAM, 20 GB de espacio en disco recomendados

### 1. Clonar el repositorio

```bash
git clone https://github.com/Enrichpg/smartports.git
cd smartports
```

### 2. Configurar el entorno

```bash
# Copiar la plantilla de entorno
cp .env.example .env

# Editar .env con tus valores (IMPORTANTE: cambia los secretos en producción)
# nano .env
# Variables clave:
#   - SECRET_KEY: cambia a un valor aleatorio seguro
#   - POSTGRES_PASSWORD, TIMESCALE_PASSWORD, MONGO_ROOT_PASSWORD
#   - REDIS_PASSWORD, GRAFANA_PASSWORD
#   - PUBLIC_BASE_URL: establece tu dominio
```

### 3. Arrancar el stack de infraestructura

```bash
# Construir y arrancar todos los servicios (primera vez ~5-10 minutos)
docker compose up -d

# Verificar que todos los servicios están sanos
docker compose ps

# Cargar las 211 entidades NGSI-LD semilla (necesario tras el primer arranque)
docker exec smartports_backend python3 scripts/load_seed.py --upsert

# Comprobar el estado de salud
curl http://localhost:8000/health
```

### 4. Acceder a los servicios

Una vez en marcha, accede a los componentes de SmartPort en:

| Servicio | URL | Credenciales por defecto |
|---------|-----|--------------------------|
| **Frontend (Web UI)** | http://localhost | N/D |
| **API Docs (Swagger)** | http://localhost/api/v1/docs | N/D |
| **Dashboards Grafana** | http://localhost/grafana | admin / admin123 |
| **Métricas Prometheus** | http://localhost/prometheus | N/D |
| **API Orion-LD** | http://localhost/ngsi-ld/v1/ | N/D |
| **API QuantumLeap** | http://localhost/ql/v2/ | N/D |

### 5. Verificación de servicios

```bash
# Comprobar que todos los servicios están corriendo
docker compose ps

# Probar el endpoint de salud del backend
curl http://localhost/health

# Probar el broker de contexto Orion-LD
curl http://localhost/ngsi-ld/v1/entities?limit=1

# Probar la versión de QuantumLeap
curl http://localhost/ql/v2/version

# Probar el broker MQTT (publicar mensaje de prueba)
docker exec smartports_mosquitto mosquitto_pub -h localhost -t test -m "Hola SmartPort"

# Ver logs del backend
docker compose logs -f backend

# Ver logs de todos los servicios
docker compose logs -f
```

### 6. Detener los servicios

```bash
# Detener todos los contenedores en ejecución (preserva los volúmenes)
docker compose down

# Detener y eliminar todos los datos (¡cuidado!)
docker compose down -v

# Reiniciar un servicio específico
docker compose restart backend
```

### 7. Primera ejecución — Cargar datos semilla

SmartPort incluye 211 entidades NGSI-LD pregeneradas para 8 puertos de Galicia:

```bash
# Paso 1: Validar los payloads semilla (verificar cumplimiento NGSI-LD)
python3 backend/scripts/validate_payloads.py
# Esperado: ✓ ALL PAYLOADS VALID

# Paso 2: Generar el fichero JSON semilla
python3 backend/scripts/generate_seed_json.py --pretty
# Crea: data/seed/galicia_entities.json (217 KB)

# Paso 3: Vista previa de lo que se cargará (simulacro)
python3 backend/scripts/load_seed.py --dry-run
# Muestra: 211 entidades listas para cargar

# Paso 4: Cargar en Orion-LD (modo upsert — seguro)
python3 backend/scripts/load_seed.py --upsert
# Resultado: 211 entidades creadas en Orion-LD

# Paso 5: Verificar que los datos se cargaron
curl -H "FIWARE-Service: smartport" \
     -H "FIWARE-ServicePath: /galicia" \
     http://localhost:1026/ngsi-ld/v1/entities?type=Port
# Lista: los 8 puertos gallegos
```

**Cobertura del seed:**
- 8 puertos (A Coruña, Vigo, Ferrol, Marín, Vilagarcía, Ribeira, Burela, Baiona)
- 71 atraques (6-15 por puerto)
- 10 buques maestros (registro estático)
- 10 instancias de buque (naves activas)
- 10 entidades BoatAuthorized
- 32 entidades BoatPlacesAvailable (4 categorías × 8 puertos)
- 32 entidades BoatPlacesPricing
- 11 dispositivos (sensores de calidad del aire y meteorología)
- 6 mediciones AirQualityObserved
- 5 mediciones WeatherObserved

---

## Estructura del proyecto

```
smartports/
├── agents/
│   └── AGENTS.md                  ← Reglas de desarrollo y gobernanza
├── docs/
│   ├── PRD.md                     ← Requisitos del producto
│   ├── data_model.md              ← 15 tipos de entidad NGSI-LD
│   ├── architecture.md            ← Diseño del sistema y flujos de datos
│   ├── APPLICATION.md             ← Resumen académico de la aplicación
│   └── LLM_AGENTS.md              ← Documentación de los agentes LLM
├── backend/                       ← Backend FastAPI (Python)
│   ├── main.py                    ← Punto de entrada de la aplicación
│   ├── config.py                  ← Configuración desde .env
│   ├── api/
│   │   ├── v1.py                  ← Rutas API v1
│   │   └── routes/
│   │       ├── agents.py          ← Endpoints de agentes LLM
│   │       ├── realtime.py        ← WebSocket
│   │       └── admin.py           ← Administración
│   ├── llm/
│   │   ├── agents.py              ← Motor de agentes especializados
│   │   ├── tools.py               ← Herramientas de los agentes
│   │   ├── ollama_client.py       ← Cliente Ollama
│   │   └── assistant_service.py   ← Servicio de asistente
│   ├── ml/
│   │   ├── forecast_service.py    ← Prophet (previsión de ocupación)
│   │   └── recommender_service.py ← Random Forest (recomendación de atraque)
│   ├── generators/                ← Ecosistema marítimo sintético (8 módulos)
│   ├── services/
│   │   ├── orion_ld_client.py     ← Integración con Orion-LD
│   │   └── simulation_engine.py   ← Motor de simulación
│   ├── tasks/
│   │   ├── celery_app.py          ← Configuración de Celery
│   │   ├── realtime_events_task.py← Tarea de eventos en tiempo real
│   │   └── alert_tasks.py         ← Motor de alertas
│   ├── requirements.txt           ← Dependencias Python
│   └── Dockerfile                 ← Imagen del contenedor
├── frontend/                      ← Interfaz web (HTML/CSS/JS)
│   ├── index.html                 ← Página principal (SPA)
│   ├── src/
│   │   ├── app.js                 ← Controlador principal + router
│   │   ├── pages/                 ← Páginas: dashboard, atraques, escalas...
│   │   ├── services/
│   │   │   ├── i18n.js            ← Internacionalización (307 claves, ES/GL/EN)
│   │   │   ├── ai-agent-client.js ← Cliente de agentes LLM
│   │   │   └── api.js             ← Cliente REST
│   │   ├── components/base.js     ← Shell, navegación, toasts
│   │   └── styles/                ← CSS por página
├── nginx/
│   └── nginx.conf                 ← Configuración del proxy inverso
├── grafana/
│   └── provisioning/              ← Datasources y dashboards auto-provisionados
├── docker-compose.yml             ← Orquestación de contenedores (13+ servicios)
├── .env.example                   ← Plantilla de entorno
└── README.md                      ← Este fichero
```

---

## Infraestructura desplegada

### Servicios Docker Compose

El stack completo incluye **13 servicios en contenedores**:

#### Capa 1: IoT y MQTT
- **mosquitto** (1883, 9001): Broker MQTT para ingesta de sensores
- **iot-agent** (4041): IoT Agent JSON (MQTT → NGSI-LD)

#### Capa 2: Contexto FIWARE
- **orion-ld** (1026): Broker de contexto Orion-LD
- **quantumleap** (8668): Gestor de series temporales + persistencia TimescaleDB

#### Capa 3: Bases de datos
- **postgresql** (5432): Base de datos operativa + auditoría
- **timescaledb** (5433): Almacenamiento de series temporales
- **mongodb** (27017): Almacén de documentos (Orion)
- **redis** (6379): Caché y cola de tareas

#### Capa 4: Backend y trabajadores
- **backend** (8000): FastAPI REST + WebSocket
- **celery-worker**: Tareas asíncronas (ML, predicción, alertas)

#### Capa 5: Presentación
- **nginx**: Proxy inverso (80/443)
- **grafana** (3000): Dashboards
- **prometheus** (9090): Métricas
- **ollama**: LLM Llama 2 (red interna Docker)

### Flujo de datos completo

```
Sensores → MQTT → Mosquitto → IoT Agent → Orion-LD ↔ PostgreSQL
                                            ↓
                                        QuantumLeap → TimescaleDB
                                            ↓
                                       Backend ↔ Redis ↔ Celery
                                            ↓
                                    Nginx (Proxy Inverso)
                                       ↙        ↘
                                  Frontend    Grafana/Prometheus
```

---

## Configuración

### Variables de entorno

Ver [.env.example](.env.example) para todas las variables disponibles con descripciones.

**Inicio rápido (.env):**
```bash
# Copiar la plantilla
cp .env.example .env

# Para desarrollo, los valores por defecto son aceptables
# Para producción, CAMBIA ESTOS:
SECRET_KEY=<genera_una_clave_aleatoria_segura>
POSTGRES_PASSWORD=<contraseña_robusta>
TIMESCALE_PASSWORD=<contraseña_robusta>
MONGO_ROOT_PASSWORD=<contraseña_robusta>
REDIS_PASSWORD=<contraseña_robusta>
GRAFANA_PASSWORD=<contraseña_admin>
ENVIRONMENT=production
DEBUG=false
```

### Puertos de los servicios (red interna)

| Servicio | Puerto | Acceso |
|---------|------|--------|
| **Nginx (Frontend)** | 80 → 443 | Externo |
| **Backend API** | 8000 | Interno |
| **Orion-LD** | 1026 | Interno |
| **QuantumLeap** | 8668 | Interno |
| **Grafana** | 3000 | Interno (vía Nginx) |
| **Prometheus** | 9090 | Interno (vía Nginx) |
| **Mosquitto (MQTT)** | 1883, 9001 | Interno |
| **PostgreSQL** | 5432 | Interno |
| **TimescaleDB** | 5433 | Interno |
| **MongoDB** | 27017 | Interno |
| **Redis** | 6379 | Interno |

**Endpoints públicos (vía proxy inverso Nginx):**
- `http://localhost/` → Frontend
- `http://localhost/api/v1/` → API Backend
- `http://localhost/api/v1/docs` → Documentación Swagger
- `http://localhost/grafana/` → Dashboards Grafana
- `http://localhost/prometheus/` → Métricas Prometheus
- `http://localhost/ngsi-ld/` → API Orion-LD
- `http://localhost/ql/` → API QuantumLeap

---

## Desarrollo

### Configuración local

```bash
# Crear entorno virtual Python
python3.10 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Ejecutar tests
pytest backend/tests/ -v

# Arrancar el backend (modo desarrollo)
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Flujo de trabajo Git

```bash
# Trabajamos directamente en main (proyecto académico)
git add .
git commit -m "feat: descripción del cambio"
git push origin main
```

**Prefijos de commits:** `feat:`, `fix:`, `docs:`, `chore:`

**Importante:** Actualiza `docs/architecture.md`, `docs/PRD.md` tras cada iteración.

---

## Despliegue

### Docker Compose (Desarrollo / Pruebas)

```bash
# Arrancar todos los servicios
docker compose up -d

# Detener servicios
docker compose down

# Limpiar (incluyendo volúmenes)
docker compose down -v

# Reconstruir contenedores
docker compose build --no-cache
```

### Producción (fase futura)

Los manifiestos Kubernetes (Helm charts) están planificados para la fase 2.

Por ahora:
1. Usar docker-compose en una VM de producción
2. Montar volúmenes en almacenamiento persistente
3. Configurar certificados SSL (Let's Encrypt)
4. Establecer trabajos cron de backup
5. Monitorizar con Prometheus + AlertManager

---

## Documentación

| Documento | Propósito |
|----------|---------|
| [docs/PRD.md](docs/PRD.md) | Requisitos del producto y funcionalidades |
| [docs/data_model.md](docs/data_model.md) | Definiciones de entidades NGSI-LD |
| [docs/architecture.md](docs/architecture.md) | Diseño del sistema y flujos de datos |
| [docs/APPLICATION.md](docs/APPLICATION.md) | Resumen académico de la aplicación |
| [docs/LLM_AGENTS.md](docs/LLM_AGENTS.md) | Agentes LLM: arquitectura y uso |
| [README.md](README.md) | Este fichero (inicio rápido) |

```bash
# Documentación de la API (generada automáticamente por FastAPI)
# Swagger UI:  http://localhost/api/v1/docs
# ReDoc:       http://localhost/api/v1/redoc
```

---

## Resolución de problemas

### El servicio no arranca

```bash
# Comprobar el daemon de Docker
docker ps

# Ver logs del contenedor
docker compose logs backend

# Comprobar espacio en disco
df -h

# Reconstruir el contenedor
docker compose build --no-cache backend
```

### Errores de conexión a la base de datos

```bash
# Verificar que la base de datos está corriendo
docker compose ps timescaledb

# Comprobar conexión desde el backend
docker compose exec backend psql -h timescaledb -U smartport_user

# Ver logs
docker compose logs timescaledb
```

### Orion-LD no responde

```bash
# Comprobar el estado de Orion
curl -i http://localhost:1026/version

# Comprobar que MongoDB está corriendo
docker compose ps mongodb

# Reiniciar Orion
docker compose restart orion-ld
```

### Problemas de conexión MQTT

```bash
# Probar el broker MQTT
docker exec smartports_mosquitto mosquitto_sub -h localhost -t test

# Ver logs de Mosquitto
docker compose logs mosquitto

# Verificar que IoT Agent está suscrito
docker compose logs iot-agent
```

### Caídas de la conexión WebSocket

```bash
# Ver logs del backend
docker compose logs backend | grep websocket

# Reiniciar el backend
docker compose restart backend
```

### Ollama / Agentes LLM sin respuesta

```bash
# Verificar que Ollama está corriendo
docker compose ps ollama

# Cargar el modelo llama2 (necesario tras restart)
docker exec smartports_ollama ollama pull llama2

# Probar un agente directamente
curl -X POST http://localhost:8000/api/v1/agents/query \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "agent_role": "operations"}'
```

### Problemas de rendimiento

```bash
# Comprobar uso de recursos
docker stats

# Supervisar conexiones a la base de datos
docker compose exec timescaledb \
  psql -U smartport_user -c "SELECT count(*) FROM pg_stat_activity;"

# Comprobar la cola de tareas Celery
docker compose exec backend \
  celery -A tasks.celery_app inspect active

# Supervisar Redis
docker compose exec redis redis-cli info stats
```

### Mensajes de error comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `Connection refused: 1026` | Orion-LD no está corriendo | `docker compose up -d orion-ld` |
| `MQTT: Connection refused` | Mosquitto no está corriendo | `docker compose up -d mosquitto` |
| `permission denied` | Sin acceso al daemon de Docker | `sudo usermod -aG docker $USER` |
| `Bind for 0.0.0.0:80 failed` | Puerto 80 en uso | Cambiar `NGINX_HTTP_PORT` en `.env` |
| `No such image` | Imagen no construida | `docker compose build` |

---

## Comprobaciones de salud

```bash
# Salud general del sistema
curl http://localhost:8000/health

# Estado de Orion-LD
curl http://localhost:1026/version

# Estado de QuantumLeap
curl http://localhost:8668/version

# Métricas (formato Prometheus)
curl http://localhost:8000/metrics

# Probar agente LLM
curl -X POST http://localhost:8000/api/v1/agents/query \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuántos atraques libres hay?", "agent_role": "operations"}'
```

---

## Contacto y contribuciones

- **Issues:** Crear un issue en GitHub con pasos detallados de reproducción
- **Discusiones:** Usar GitHub Discussions para preguntas
- **PRs:** Seguir las guías de desarrollo en [agents/AGENTS.md](agents/AGENTS.md)
- **Documentación:** Actualizar docs tras cada cambio significativo

---

## Licencia

[Por definir]

---

## Referencias

- **FIWARE:** https://www.fiware.org
- **Especificación NGSI-LD:** https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.01.01_60/gs_cim_009v010101p.pdf
- **Smart Data Models:** https://smartdatamodels.org
- **Portos de Galicia:** https://portosdegalicia.gal
- **Puertos del Estado:** https://www.puertos.es

---

**Última actualización:** 2026-05-14
**Mantenido por:** Sergio Varela Rodríguez & Enrique Pardo García — XDEI/UDC
**GitHub:** https://github.com/Enrichpg/smartports
**Estado:** Iteración 13 — Agentes LLM + i18n completo
