# SmartPort Galicia Operations Center — Contexto para Claude Code

> Leido automaticamente por Claude Code al arrancar.
> Historial completo extraido de los tickets 1-7.
> Ultima actualizacion: 2026-05-02 (post ticket 7)

---

## Que es este proyecto

Plataforma inteligente de gestion operativa para la red de puertos gallegos.
Practica universitaria XDEI/UDC - Sergio + Enrique.

- Stack: FastAPI + Orion-LD (NGSI-LD) + PostgreSQL + Redis + Celery + Docker Compose
- Frontend: HTML/CSS/JS + Leaflet + Chart.js + WebSocket client
- ML previsto: Prophet (forecasting) + scikit-learn (recomendacion berths)
- LLM previsto: Ollama Llama 2 (ya en docker-compose)
- Repo: https://github.com/Enrichpg/smartports.git (rama main)
- Ruta local Sergio: ~/XDEI/smartports
- Ruta local Enrique: ~/XDEI/SmartPorts

---

## Iteraciones completadas

### Ticket 1 - Documentacion base (commit eeaccb9)
- PRD.md, data_model.md, architecture.md, AGENTS.md, README.md creados
- docker-compose.yml y .env.example como templates

### Ticket 2 - Stack ejecutable (commit 723c785)
- 13 servicios Docker Compose con healthchecks
- Backend FastAPI scaffolding completo
- Frontend base + Nginx + Mosquitto + Prometheus + Grafana

### Ticket 3 - Modelo NGSI-LD y seed
- 211 entidades NGSI-LD para 8 puertos gallegos
- Scripts: validate_payloads.py, generate_seed_json.py, load_seed.py
- 15 tipos de entidad: Port, Berth, Vessel, PortCall, BoatAuthorized...

### Ticket 4 - APIs de datos reales
- AEMET, MeteoGalicia, Puertos del Estado, Open-Meteo Marine + Air Quality
- 8 tareas Celery periodicas (4 reales + 4 simuladores fallback)
- Data provenance tracking completo

### Ticket 5 - Backend operativo de dominio
- API completa: puertos, berths, vessels, portcalls, autorizaciones
- Maquinas de estado, validaciones, calculo disponibilidad, alertas por reglas
- Tests para logica critica

### Ticket 6 - Frontend dashboard (49 archivos, 11595 inserciones)
- Frontend modular: services/, components/, pages/, store/
- Mapa Leaflet interactivo + Chart.js KPIs
- Cliente WebSocket manager integrado
- Push a GitHub exitoso

### Ticket 7 - Infraestructura tiempo real (commit e4c58b7, 24 archivos, 3164 lineas)
- WebSocket: /api/ws, ws_manager.py, event_bus.py
- Eventos: berth.updated, portcall.*, alert.*, availability.updated, port.summary.updated
- Auditoria PostgreSQL: tabla audit_log con JSONB + correlation_id + severity
- Endpoints auditoria: GET /api/v1/audit, /audit/{entity_type}/{id}, /ports/{id}/audit
- Redis Cache: port:summary:{id}, port:availability:{id}, port:alerts:active:{id}
- TTL configurable, invalidacion por evento, fallback si Redis cae
- Celery Tasks: check_port_alerts, recalculate_port_availability,
  refresh_port_summary_cache, broadcast_port_summary_update, warm_dashboard_cache

---

## PROXIMO - Iteracion 8

### Prioridad alta
- ML pipelines: Prophet forecasting ocupacion + scikit-learn recomendador berths
  Endpoints previstos: GET /api/v1/forecasts/occupancy, GET /api/v1/recommendations/berth
- Asistente LLM: Ollama Llama 2 ya en docker-compose, conectar al backend
  Endpoint previsto: POST /api/v1/assistant/chat
- Frontend WebSocket live: conectar dashboard a actualizaciones en tiempo real

### Prioridad media
- Alertas avanzadas: rules engine mejorado, notificaciones multi-canal
- Grafana dashboards con datos reales de TimescaleDB
- 3D visualization con Three.js

---

## Servicios Docker activos

- mosquitto (1883, 9001): MQTT broker
- iot-agent (4041): IoT Agent JSON MQTT a NGSI-LD
- orion-ld (1026): Context broker NGSI-LD
- quantumleap (8668): Time-series a TimescaleDB
- postgresql (5432): Datos operativos + auditoria
- timescaledb (5433): Series temporales
- mongodb (27017): Document store para Orion
- redis (6379): Cache + Cola Celery
- backend (8000): FastAPI REST + WebSocket
- celery-worker: Tareas asincronas
- ollama: LLM Llama 2 (pendiente de conectar)
- nginx (80/443): Reverse proxy
- grafana (3000): Dashboards
- prometheus (9090): Metricas

---

## Estructura backend clave

backend/
├── main.py
├── config.py
├── api/v1.py
├── services/orion.py, quantumleap.py
├── realtime/ws_manager.py, event_bus.py
├── audit/models.py, service.py
├── cache/redis_service.py
└── tasks/celery_app.py, domain_tasks.py, cache_tasks.py, alert_tasks.py

---

## Variables de entorno clave (.env)

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
POSTGRES_URL=postgresql://smartport_user:...@postgresql:5432/smartport
AEMET_API_KEY=<tu_clave>
OLLAMA_BASE_URL=http://ollama:11434
WEBSOCKET_ENABLED=true

---

## Reglas del proyecto (AGENTS.md)

1. Al terminar cada iteracion: actualizar docs/architecture.md, docs/PRD.md, agents/AGENTS.md
2. Ejecutar: git add . && git commit && git push origin main
3. Mensaje de commit con prefijo feat:, fix:, docs:
4. Guardar conversacion en Google Drive > UDC > XDEI > Tickets
   con formato: ticket N - descripcion.json

---

## Equipo

- Sergio: WSL Ubuntu 22.04, ~/XDEI/smartports, Claude Code
- Enrique: WSL Ubuntu 24.04, ~/XDEI/SmartPorts, GitHub Copilot (VS Code)
- Coordinacion: Git rama main + tickets en Drive
