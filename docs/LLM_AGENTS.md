# SmartPort LLM Agents & Tool Calling

## Overview

SmartPort Galicia includes an **intelligent agent system** powered by Ollama and Llama 2, enabling sophisticated conversational interfaces for port operations. The system features **specialized agents** with different roles and automatic **tool calling** capabilities to query backend APIs.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                            │
│              (Chat Widget / Mobile / Dashboard)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                    HTTP/WebSocket
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                            │
│    ┌──────────────────────────────────────────────────────┐  │
│    │           Agents API (/api/v1/agents/*)             │  │
│    └──────────────────────────────────────────────────────┘  │
└─────────────┬──────────────────────────────┬────────────────┘
              │                              │
    ┌─────────▼─────────┐        ┌──────────▼──────────┐
    │  Agent Router     │        │  Tools Registry    │
    │ (5 specialized)   │        │  (8+ operations)   │
    └────────┬──────────┘        └──────────┬──────────┘
             │                              │
    ┌────────▼──────────────────────────────▼────────────┐
    │    Ollama + Llama 2 (Local LLM)                     │
    │    - Chat API                                      │
    │    - Function Calling (planned)                    │
    └────────┬──────────────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────────────┐
    │    Backend Services (data sources for tools)       │
    │    - Orion-LD (real-time entities)               │
    │    - QuantumLeap (historical time-series)        │
    │    - ML Models (forecasting, recommendations)    │
    │    - PostgreSQL (transactional data)             │
    └──────────────────────────────────────────────────┘
```

## Agent Roles

### 1. **Operations Agent** (General Port Operations)

**Purpose:** Primary agent for day-to-day port operations queries.

**Available Tools:**
- `get_port_occupancy` - Real-time occupancy metrics
- `get_berth_availability` - Available berths
- `get_active_alerts` - Current alerts
- `get_vessel_info` - Vessel details
- `get_port_call_status` - Visit status
- `predict_occupancy` - Short-term forecasts
- `recommend_berth` - Berth recommendations
- `get_weather` - Current conditions

**Example Queries:**
```
"¿Cuántos atraques libres hay en Vigo ahora?"
"¿Qué buques están atracados en A Coruña?"
"Recomienda un atraque para un buque de carga de 250m en Ferrol"
"¿Cuál es la ocupación promedio hoy en todos los puertos?"
```

**Endpoint:** `POST /api/v1/agents/operations`

### 2. **Forecasting Agent** (Occupancy & Resource Planning)

**Purpose:** Predictive analytics and future capacity planning.

**Available Tools:**
- `predict_occupancy` - Multi-day forecasts
- `get_port_occupancy` - Current baseline
- `get_weather` - Weather impact analysis

**Example Queries:**
```
"¿Cuál será la ocupación en Vigo en las próximas 48 horas?"
"Predice la tendencia de ocupación para la próxima semana"
"¿Hay riesgo de congestión en algún puerto próximamente?"
```

**Endpoint:** `POST /api/v1/agents/forecasting`

### 3. **Maintenance Agent** (Equipment & Infrastructure)

**Purpose:** Infrastructure maintenance planning and equipment status.

**Available Tools:**
- `get_active_alerts` - Maintenance alerts
- `get_port_occupancy` - Operational load

**Example Queries:**
```
"¿Hay alertas de mantenimiento críticas?"
"¿Cuál es el mejor momento para el mantenimiento en Vigo?"
```

**Endpoint:** `POST /api/v1/agents/maintenance`

### 4. **Compliance Agent** (Regulatory & Safety)

**Purpose:** Regulatory requirements and safety standards.

**Available Tools:**
- `get_active_alerts` - Compliance alerts
- `get_vessel_info` - Vessel documentation
- `get_port_call_status` - Documentation status

**Example Queries:**
```
"¿Cuáles son los requisitos de seguridad para buques tanqueros?"
"¿Está todo en orden con la documentación de las escalas?"
```

**Endpoint:** `POST /api/v1/agents/compliance`

### 5. **Incident Agent** (Alert Management & Response)

**Purpose:** Incident management and emergency response.

**Available Tools:**
- `get_active_alerts` - All active alerts
- `get_port_occupancy` - Operational status
- `get_vessel_info` - Involved vessel data
- `get_weather` - Incident factors

**Example Queries:**
```
"¿Cuáles son las alertas críticas activas?"
"¿Hay incidentes relacionados con clima en los puertos?"
"Resumen de incidentes por puerto"
```

**Endpoint:** `POST /api/v1/agents/incident`

## API Endpoints

### Query Any Agent
```http
POST /api/v1/agents/query
Content-Type: application/json

{
  "message": "¿Qué atraques están libres en Vigo?",
  "agent_role": "operations",
  "port_context": {
    "ports_summary": [...],
    "active_alerts": [...],
    "timestamp": "2024-05-14T10:30:00Z"
  }
}
```

**Response:**
```json
{
  "role": "assistant",
  "content": "En Vigo hay 8 atraques libres...",
  "agent_role": "operations",
  "model": "ollama/llama2",
  "timestamp": "2024-05-14T10:30:00Z",
  "offline": false,
  "tools_used": ["get_port_occupancy", "get_berth_availability"]
}
```

### Get Available Agent Roles
```http
GET /api/v1/agents/roles
```

**Response:**
```json
{
  "timestamp": "2024-05-14T10:30:00Z",
  "agents": {
    "operations": {
      "name": "Operations",
      "description": "Especialista en operaciones portuarias...",
      "tools": [...]
    },
    "forecasting": {...},
    "maintenance": {...},
    "compliance": {...},
    "incident": {...}
  },
  "total_agents": 5
}
```

### Direct Agent Endpoints
```http
POST /api/v1/agents/operations      # Operations Agent
POST /api/v1/agents/forecasting     # Forecasting Agent
POST /api/v1/agents/maintenance     # Maintenance Agent
POST /api/v1/agents/compliance      # Compliance Agent
POST /api/v1/agents/incident        # Incident Agent
```

## Tools (Function Registry)

Tools are self-registering functions that LLM agents can call:

### Available Tools

| Tool | Parameters | Returns | Agent Access |
|------|-----------|---------|--------------|
| `get_port_occupancy` | `port_id` | Occupancy metrics | All |
| `get_berth_availability` | `port_id`, `berth_type?` | Available berths | Operations, Incident |
| `get_active_alerts` | `port_id?`, `severity?` | Alert list | Maintenance, Compliance, Incident |
| `get_vessel_info` | `vessel_id` | Vessel details | Operations, Compliance, Incident |
| `get_port_call_status` | `portcall_id` | Visit status | Operations, Compliance |
| `predict_occupancy` | `port_id`, `hours_ahead?` | Forecast data | Forecasting, Operations |
| `recommend_berth` | `port_id`, `vessel_type`, `length_m`, `beam_m`, `draft_m`, `top_n?` | Top berth recommendations | Operations |
| `get_weather` | `port_id` | Weather/sea conditions | Forecasting, Incident |

## Tool Calling (Function Calling)

The system is designed to support **tool calling**, where the LLM can autonomously decide to use tools:

```python
# Example: Agent decision-making flow
User Query: "¿Cuál es la ocupación en Vigo?"
     ↓
Agent: "I need current occupancy data"
     ↓
Calls: get_port_occupancy(port_id="Vigo")
     ↓
Receives: {"occupied": 18, "total": 25, "rate": 0.72}
     ↓
Response: "Vigo tiene una ocupación del 72% (18 de 25 atraques)"
```

**Note:** Ollama's native function calling is being enhanced. Currently, the backend implements tool schemas but uses context injection for tool availability hints.

## Integration Examples

### Example 1: Ask Operations Agent for Availability
```bash
curl -X POST http://localhost:8000/api/v1/agents/operations \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuántos atraques libres hay en Vigo?",
    "port_context": {
      "ports_summary": [
        {
          "name": "Vigo",
          "occupancy_rate": 0.72,
          "available_berths": 7
        }
      ]
    }
  }'
```

### Example 2: Ask Forecasting Agent for Predictions
```bash
curl -X POST http://localhost:8000/api/v1/agents/forecasting \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuál será la ocupación en Vigo en 48 horas?"
  }'
```

### Example 3: Query Incident Agent
```bash
curl -X POST http://localhost:8000/api/v1/agents/incident \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Resumen de alertas críticas activas"
  }'
```

## Configuration

### Environment Variables
```bash
# Enable/disable LLM agent system
ENABLE_LLM_ASSISTANT=true

# Ollama configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=120
```

### Setup Ollama Model
```bash
# Download Llama 2 model (run inside container)
docker exec smartports_ollama ollama pull llama2

# Or use alternative models
docker exec smartports_ollama ollama pull neural-chat  # Faster
docker exec smartports_ollama ollama pull mistral      # Advanced
```

## Agent Lifecycle

### Stateless Design
- Agents are stateless by default
- Each query is independent
- Conversation history is optional and managed by client

### Stateful Conversations (Optional)
```json
{
  "message": "¿Cuál es la ocupación?",
  "history": [
    {"role": "user", "content": "Hola, quiero información sobre Vigo"},
    {"role": "assistant", "content": "¡Hola! Soy el agente de operaciones..."}
  ]
}
```

### Context Injection
```json
{
  "message": "¿Está muy ocupado?",
  "port_context": {
    "ports_summary": [
      {"name": "Vigo", "occupancy_rate": 0.92}
    ],
    "active_alerts": 3,
    "timestamp": "2024-05-14T10:30:00Z"
  }
}
```

## Performance Considerations

### Latency
- **Typical response time:** 2-5 seconds (Llama 2 local inference)
- **Tool call latency:** + 0.5-2 seconds per tool (API calls)
- **With multiple tools:** 3-10 seconds total

### Resource Usage
- **Memory:** ~4GB (Llama 2 7B), ~13GB (13B)
- **CPU:** 2-4 cores recommended
- **Disk:** ~5GB for model

### Optimization Tips
1. **Cache tool responses** for frequently asked questions
2. **Use specific port_context** to reduce inference time
3. **Route queries to specialized agents** (faster, more accurate)
4. **Batch multiple queries** to amortize overhead

## Troubleshooting

### Ollama Not Available
```
Error: Ollama connection failed
Solution: docker exec smartports_ollama ollama serve
         Check: http://localhost:11434/api/tags
```

### Model Not Loaded
```
Error: Model 'llama2' not found
Solution: docker exec smartports_ollama ollama pull llama2
```

### Slow Responses
```
Symptoms: Responses take >10 seconds
Causes: 
  - Ollama still loading model (first query slower)
  - Limited CPU/RAM available
  - Multiple queries simultaneously
Solutions:
  - Increase container resource limits
  - Use faster model (neural-chat instead of llama2-13b)
```

### Tools Not Working
```
Error: Tool execution failed
Check:
  - Tool registration completed (logs: "Tool registered")
  - Backend service is available (e.g., Orion-LD running)
  - Tool parameters match function signature
```

## Future Enhancements

1. **Extended Tool Calling**
   - Native Ollama function calling support
   - Parallel tool execution
   - Tool result caching

2. **Advanced Agents**
   - Multi-agent collaboration
   - Hierarchical reasoning
   - Cross-domain queries

3. **Fine-tuning**
   - Domain-specific model fine-tuning
   - Spanish/Galician language optimization
   - Port operations knowledge base

4. **Integration**
   - Real-time WebSocket conversations
   - Mobile-friendly interfaces
   - Voice input/output (STT/TTS)

## Files Structure

```
backend/llm/
├── __init__.py
├── ollama_client.py      # Ollama HTTP client
├── assistant_service.py  # Original simple assistant
├── agents.py            # NEW: Specialized agents system
└── tools.py             # NEW: Tool registry & definitions

api/routes/
├── assistant.py         # Original chat endpoint
└── agents.py           # NEW: Agent endpoints

main.py                  # Modified: LLM initialization
api/v1.py              # Modified: Router inclusion
```

## References

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Llama 2 Model Card](https://huggingface.co/meta-llama/Llama-2-7b-chat)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [SmartPort Architecture](./architecture.md)
