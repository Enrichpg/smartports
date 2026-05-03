# SmartPort Galicia Operations Center — Contexto para Claude Code

> Leido automaticamente por Claude Code al arrancar.
> Historial completo extraido de los tickets 1-10.
> Ultima actualizacion: 2026-05-03 (post ticket 10 - verificacion iteracion 8)

---

## Que es este proyecto

Plataforma inteligente de gestion operativa para la red de puertos gallegos.
Practica universitaria XDEI/UDC - Sergio + Enrique.

- Stack: FastAPI + Orion-LD (NGSI-LD) + PostgreSQL + Redis + Celery + Docker Compose
- Frontend: HTML/CSS/JS + Leaflet + Chart.js + WebSocket client
- ML: Prophet fallback determinista (forecast) + scikit-learn RandomForest (berths)
- LLM: Ollama llama2 (asistente portuario en espanol, FUNCIONANDO)
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

### Ticket 7 - Infraestructura tiempo real (commit e4c58b7, 24 archivos, 3164 lineas)
- WebSocket: /api/ws, ws_manager.py, event_bus.py
- Eventos: berth.updated, portcall.*, alert.*, availability.updated, port.summary.updated
- Auditoria PostgreSQL: tabla audit_log con JSONB + correlation_id + severity
- Redis Cache: port:summary:{id}, port:availability:{id}, port:alerts:active:{id}
- Celery Tasks: check_port_alerts, recalculate_port_availability,
  refresh_port_summary_cache, broadcast_port_summary_update, warm_dashboard_cache

### Tickets 8-10 - ML pipelines + LLM + verificacion (commits de05fc5, 8e0f44d)
- backend/ml/forecast_service.py: fallback determinista funcional (Prophet falla por
  incompatibilidad cmdstanpy; fix: fijar cmdstanpy==1.2.4 en requirements.txt y rebuild)
- backend/ml/recommender_service.py: RandomForest funcional, 12 berths candidatos,
  top 5 con scores detallados (length_fit, beam_fit, draft_fit, type_match, availability)
- backend/llm/ollama_client.py + assistant_service.py: asistente portuario en espanol,
  historial 10 turnos, modo offline graceful. llama2 descargado y funcionando
- backend/api/routes/forecasts.py: GET /api/v1/forecasts/occupancy?port_id=&horizon_hours=
- backend/api/routes/recommendations.py: GET /api/v1/recommendations/berth?port_id=&length_m=&beam_m=&draft_m=&vessel_type=
- backend/api/routes/assistant.py: POST /api/v1/assistant/chat + GET /api/v1/assistant/status
- Bugs resueltos: imports hardcodeados a ruta Enrique, IDs Orion-LD en formato URN,
  refPort en berths, contexto JSON-LD invalido, fiware_service namespace
- Seed: 211 entidades cargadas correctamente en Orion-LD
- ID de puerto correcto: galicia-a-coruna (no CorA)

---

## PROXIMO - Iteracion 9 (Advanced Features)

### Prioridad alta
- Frontend WebSocket live: conectar dashboard HTML/JS a actualizaciones en tiempo real
  ws_manager.py existe en backend, cliente WS en frontend tambien, hay que conectarlos
  y que el mapa y KPIs se actualicen sin recargar
- 3D visualization con Three.js (mencionado en PRD)

### Prioridad media
- Alertas avanzadas: rules engine mejorado, notificaciones multi-canal
- Grafana dashboards con datos reales de TimescaleDB
- Activar Prophet real: fijar cmdstanpy==1.2.4 en requirements.txt y docker compose build backend

---

## Comandos utiles

```bash
# Levantar stack
cd ~/XDEI/smartports
docker compose up -d

# Si falla por red: docker network prune -f && docker compose up -d

# Cargar seed (211 entidades)
docker exec smartports_backend python3 scripts/load_seed.py --upsert

# Verificar endpoints iteracion 8
curl "http://localhost:8000/api/v1/forecasts/occupancy?port_id=galicia-a-coruna&horizon_hours=24"
curl "http://localhost:8000/api/v1/recommendations/berth?port_id=galicia-a-coruna&length_m=50&beam_m=10&draft_m=4&vessel_type=cargo"
curl -X POST http://localhost:8000/api/v1/assistant/chat -H "Content-Type: application/json" -d '{"message": "Hola"}'

# Exportar ticket al terminar sesion
source .venv/bin/activate
python3 ~/XDEI/smartports/scripts/export_ticket.py --description "descripcion"
```

---

## Servicios Docker activos

- mosquitto (1883, 9001): MQTT broker
- iot-agent (4041): RESTARTING — bug pendiente de revisar
- orion-ld (1026): Context broker NGSI-LD
- quantumleap (8668): Time-series a TimescaleDB
- postgresql (5432): Datos operativos + auditoria
- timescaledb (5433): Series temporales
- mongodb (27017): Document store para Orion
- redis (6379): Cache + Cola Celery
- backend (8000): FastAPI REST + WebSocket
- celery-worker: Tareas asincronas
- ollama: LLM llama2 descargado y funcionando
- nginx (80/443): Reverse proxy
- grafana (3000): Dashboards
- prometheus (9090): Metricas

---

## Estructura backend clave

backend/
├── main.py
├── config.py
├── api/v1.py
├── services/orion.py, quantumleap.py, orion_ld_client.py
├── realtime/ws_manager.py, event_bus.py
├── audit/models.py, service.py
├── cache/redis_service.py
├── ml/forecast_service.py, recommender_service.py
├── llm/ollama_client.py, assistant_service.py
└── tasks/celery_app.py, domain_tasks.py, cache_tasks.py, alert_tasks.py

---

## Variables de entorno clave (.env)

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
POSTGRES_URL=postgresql://smartport_user:...@postgresql:5432/smartport
AEMET_API_KEY=<tu_clave>
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
WEBSOCKET_ENABLED=true
ENABLE_LLM_ASSISTANT=true

---

## Reglas del proyecto (AGENTS.md)

1. Al terminar cada iteracion: actualizar docs/architecture.md, docs/PRD.md, agents/AGENTS.md
2. Ejecutar: git add . && git commit && git push origin main
3. Mensaje de commit con prefijo feat:, fix:, docs:
4. Guardar conversacion en Drive > UDC > XDEI > Tickets con formato: ticket N - descripcion.json

---

## Equipo

- Sergio: WSL Ubuntu 22.04, ~/XDEI/smartports, Claude Code (Sonnet 4.6)
- Enrique: WSL Ubuntu 24.04, ~/XDEI/SmartPorts, GitHub Copilot (VS Code)
- Coordinacion: Git rama main + tickets en Drive
