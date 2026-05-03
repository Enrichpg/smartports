# Napkin Runbook — SmartPorts

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead".

## Execution & Validation (Highest Priority)

1. **[2026-05-03] Prophet/sklearn already in requirements.txt**
   Do instead: never re-add them; just import and use directly.

2. **[2026-05-03] Ollama NOT in docker-compose — must be added before testing LLM**
   Do instead: add ollama service to docker-compose.yml before wiring the assistant route.

3. **[2026-05-03] Orion-LD entity chain for berths: Port → hasFacilities → SeaportFacilities → Berth**
   Do instead: always traverse this chain when fetching berths by port.

4. **[2026-05-03] No real historical occupancy data yet — Prophet uses synthetic training data**
   Do instead: generate plausible time-series (seasonal + noise) for Prophet training until TimescaleDB has real data.

## Shell & Command Reliability

1. **[2026-05-03] `grep -i ollama docker-compose.yml` returns nothing if service missing**
   Do instead: always verify with `grep -n "services:"` + `wc -l` to confirm you're reading the full file.

## Domain Behavior Guardrails

1. **[2026-05-03] BerthStatus values: free, reserved, occupied, out_of_service**
   Do instead: import BerthStatus enum from schemas.berth — never use raw strings.

2. **[2026-05-03] API v1 prefix is /api/v1 — all new routes must be registered in api/v1.py**
   Do instead: add include_router() call in v1.py for every new route file.

## User Directives

1. **[2026-05-03] Iteración 8: ML pipelines (Prophet + sklearn) + LLM assistant (Ollama)**
   Do instead: build in this order — config → docker → ML services → LLM client → routes → v1.py registration.
