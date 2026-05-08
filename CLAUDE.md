# SmartPort Galicia Operations Center — Contexto para Claude Code

> Leido automaticamente por Claude Code al arrancar.
> Historial completo extraido de los tickets 1-10.
> Ultima actualizacion: 2026-05-05 (post iteracion 10 - Enrique)

---

## Que es este proyecto

Plataforma inteligente de gestion operativa para la red de puertos gallegos.
Practica universitaria XDEI/UDC - Sergio + Enrique.

- Stack: FastAPI + Orion-LD (NGSI-LD) + PostgreSQL + Redis + Celery + Docker Compose
- Frontend: HTML/CSS/JS + Leaflet + Chart.js + WebSocket live + Three.js 3D
- ML: Prophet fallback determinista (forecast) + scikit-learn RandomForest (berths)
- LLM: Ollama llama2 (asistente portuario en espanol)
- Generadores: ecosistema maritimo sintetico (8 modulos, motor de simulacion)
- Repo: https://github.com/Enrichpg/smartports.git (rama main)
- Ruta local Sergio: ~/XDEI/smartports
- Ruta local Enrique: ~/XDEI/SmartPorts

---

## Iteraciones completadas

### Tickets 1-7 — Base, stack, NGSI-LD, APIs, backend, frontend, infraestructura tiempo real
Ver historial completo en tickets Drive. Resumen: stack completo con 13 servicios,
211 entidades NGSI-LD, APIs reales (AEMET, MeteoGalicia, Puertos del Estado, Open-Meteo),
WebSocket backend, Redis cache, Celery tasks, auditoria PostgreSQL.

### Tickets 8-9 — ML pipelines + LLM (Sergio, commits de05fc5, 8e0f44d)
- Prophet fallback determinista: GET /api/v1/forecasts/occupancy
- RandomForest berth recommender: GET /api/v1/recommendations/berth
- Ollama llama2 asistente: POST /api/v1/assistant/chat
- Bugs resueltos: imports hardcodeados ruta Enrique, IDs Orion-LD URN, refPort berths
- ID puerto correcto: galicia-a-coruna

### Ticket 10 — Iteracion 9: WebSocket live + 3D + Ecosistema sintetico (Enrique)
Commits: b7f3b4c, 5c6204a, b98ef09, d7dfc6c, 75ddcdc, 93637cc

WebSocket live (Fase A):
- Bug URL corregido: apunta a /api/v1/realtime/ws
- Parseo mensajes corregido: {type:"event", data:{event, payload, scope, entity}}
- Badge Live/Offline reactivo en navbar
- Heartbeat keepalive 25s, backoff exponencial reconexion
- frontend/src/services/websocket-integrator.js (332 lineas)
- frontend/src/store/store.js actualizado (343 lineas)

Vista 3D Three.js (Fase B):
- frontend/src/components/map3d.js (534 lineas)
- 12 berths como cajas coloreadas (verde=libre, rojo=ocupado, naranja=reservado)
- Muelle con bollards, agua, iluminacion, labels, orbit drag+scroll+touch
- Hover tooltip con raycasting, updateBerth() conectado al bus WS
- Boton "Vista 3D" en dashboard y port-detail

Ecosistema maritimo sintetico (Iteracion 10):
- backend/generators/: 8 modulos (berth, vessel, sensor, port_profiles, etc.)
- backend/services/simulation_engine.py
- backend/tasks/realtime_events_task.py (296 lineas)
- backend/tasks/simulation_tasks.py
- Tests en tests/generators/ (6 ficheros)
- Documentacion: ITERATION_9_SUMMARY.md, docs/ITERATION_9.md, docs/REALTIME_PROTOCOL.md

---

## Estado actual — Que falta

- Activar Prophet real: fijar cmdstanpy==1.2.4 en requirements.txt y rebuild backend
- iot-agent en Restarting (bug pendiente)
- Grafana dashboards con datos reales de TimescaleDB
- Alertas avanzadas: rules engine mejorado
- Kubernetes/Helm para produccion (fase futura)

---

## Comandos utiles

```bash
# Levantar stack (Ollama sin puerto externo — comentado en docker-compose.yml)
cd ~/XDEI/smartports
docker compose up -d

# Si falla red: docker network prune -f && docker compose up -d
# Si falla Ollama puerto: sudo fuser -k 11434/tcp && docker compose up -d

# Cargar seed (211 entidades) — necesario cada vez que se reinician contenedores
docker exec smartports_backend python3 scripts/load_seed.py --upsert

# Verificar endpoints
curl http://localhost:8000/health
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
- iot-agent: RESTARTING — bug pendiente
- orion-ld (1026): Context broker NGSI-LD
- quantumleap (8668): Time-series a TimescaleDB
- postgresql (5432): Datos operativos + auditoria
- timescaledb (5433): Series temporales
- mongodb (27017): Document store para Orion
- redis (6379): Cache + Cola Celery
- backend (8000): FastAPI REST + WebSocket
- celery-worker: Tareas asincronas
- ollama: llama2 (sin puerto externo, accesible solo dentro de red Docker)
- nginx (80/443): Reverse proxy
- grafana (3000): Dashboards
- prometheus (9090): Metricas

---

## Estructura backend clave

backend/
├── main.py, config.py
├── api/v1.py, routes/realtime.py, routes/admin.py
├── services/orion_ld_client.py, simulation_engine.py
├── realtime/ws_manager.py, event_bus.py, models.py
├── audit/models.py, service.py
├── cache/redis_service.py
├── ml/forecast_service.py, recommender_service.py
├── llm/ollama_client.py, assistant_service.py
├── generators/ (8 modulos ecosistema sintetico)
└── tasks/celery_app.py, realtime_events_task.py, simulation_tasks.py

---

## Reglas del proyecto (AGENTS.md)

1. Al terminar cada iteracion: actualizar docs/architecture.md, docs/PRD.md, agents/AGENTS.md
2. git add . && git commit && git push origin main
3. Prefijo commits: feat:, fix:, docs:
4. Guardar conversacion en Drive > UDC > XDEI > Tickets: ticket N - descripcion.json

---

## Equipo

- Sergio: WSL Ubuntu 22.04, ~/XDEI/smartports, Claude Code (Sonnet 4.6)
- Enrique: WSL Ubuntu 24.04, ~/XDEI/SmartPorts, GitHub Copilot (VS Code)
- Coordinacion: Git rama main + tickets en Drive
