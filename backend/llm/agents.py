# LLM Agents — Specialized AI agents for different operational roles

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from llm import ollama_client
from llm.tools import tools_registry

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Specialized agent roles in the port operations system."""
    OPERATIONS = "operations"  # General port operations queries
    FORECASTING = "forecasting"  # Occupancy and resource forecasting
    MAINTENANCE = "maintenance"  # Equipment and infrastructure maintenance
    COMPLIANCE = "compliance"  # Regulatory and safety compliance
    INCIDENT = "incident"  # Incident and alert management


# System prompts for different agent roles
SYSTEM_PROMPTS = {
    AgentRole.OPERATIONS: """Eres un especialista en operaciones portuarias del SmartPort Galicia Operations Center.
Tu rol es ayudar con:
- Consultas sobre disponibilidad de amarres en tiempo real
- Estado actual de buques y escalas
- Recomendaciones de asignación de atraques
- Coordinación de operaciones de entrada/salida
- Información sobre puertos específicos

Responde en español de forma clara, concisa y profesional.
Basa tus respuestas en datos en tiempo real consultados a través de las herramientas disponibles.
Si necesitas información específica, usa las funciones disponibles para obtenerla.""",

    AgentRole.FORECASTING: """Eres un especialista en predicción y planificación portuaria del SmartPort Galicia.
Tu rol es ayudar con:
- Predicciones de ocupación y disponibilidad futura
- Planificación de recursos basada en pronósticos
- Análisis de tendencias históricas
- Optimización de capacidad

Utiliza datos históricos y modelos predictivos para proporcionar análisis fundamentados.
Expresa siempre el nivel de confianza de tus predicciones.""",

    AgentRole.MAINTENANCE: """Eres un especialista en mantenimiento e infraestructura portuaria.
Tu rol es ayudar con:
- Estado de equipos e instalaciones
- Planificación de mantenimiento preventivo
- Alertas de mantenimiento
- Gestión de recursos de infraestructura

Coordina con el equipo operativo para minimizar disrupciones.""",

    AgentRole.COMPLIANCE: """Eres un especialista en cumplimiento normativo y seguridad portuaria.
Tu rol es ayudar con:
- Requisitos regulatorios españoles y gallegos
- Seguridad y protección portuaria
- Regulaciones ambientales y marítimas
- Cumplimiento de estándares internacionales

Proporciona información con precisión legal y referencias normativas.""",

    AgentRole.INCIDENT: """Eres un especialista en gestión de incidentes y alertas portuarias.
Tu rol es ayudar con:
- Análisis de alertas activas
- Gestión de incidentes operacionales
- Respuesta a situaciones de emergencia
- Seguimiento de resoluciones

Sé conciso pero comprensivo. Ayuda a escalar incidentes según su severidad.""",
}


class PortOperationsAgent:
    """Base class for specialized port operations agents."""
    
    def __init__(self, role: AgentRole = AgentRole.OPERATIONS):
        self.role = role
        self.system_prompt = SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS[AgentRole.OPERATIONS])
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history_turns = 10
        self.tools = self._get_tools_for_role(role)
    
    def _get_tools_for_role(self, role: AgentRole) -> List[str]:
        """Return available tools for each role."""
        all_tools = [
            "get_port_occupancy",
            "get_berth_availability",
            "get_active_alerts",
            "get_vessel_info",
            "get_port_call_status",
            "predict_occupancy",
            "recommend_berth",
            "get_weather",
        ]
        
        # Restrict tools by role
        if role == AgentRole.OPERATIONS:
            return all_tools
        elif role == AgentRole.FORECASTING:
            return ["predict_occupancy", "get_port_occupancy", "get_weather"]
        elif role == AgentRole.MAINTENANCE:
            return ["get_active_alerts", "get_port_occupancy"]
        elif role == AgentRole.COMPLIANCE:
            return ["get_active_alerts", "get_vessel_info", "get_port_call_status"]
        elif role == AgentRole.INCIDENT:
            return ["get_active_alerts", "get_port_occupancy", "get_vessel_info", "get_weather"]
        
        return all_tools
    
    async def process_message(
        self,
        user_message: str,
        port_context: Optional[Dict[str, Any]] = None,
        use_tools: bool = True,
    ) -> Dict[str, Any]:
        """Process a user message and return assistant response with possible tool calls."""
        
        # Check Ollama availability
        available = await ollama_client.check_ollama_available()
        if not available:
            return self._offline_response(user_message)
        
        # Build system prompt with context
        system_content = self.system_prompt
        if port_context:
            system_content += self._format_context(port_context)
        
        # Build message list
        messages = [{"role": "system", "content": system_content}]
        messages.extend(self.conversation_history[-self.max_history_turns :])
        messages.append({"role": "user", "content": user_message})
        
        # Add tools to the request if supported
        payload_kwargs = {"messages": messages, "temperature": 0.6}
        
        # For now, use simple chat (tool calling would need function_calling support in Ollama)
        # This is the foundation for future enhancement
        
        try:
            reply = await ollama_client.chat(messages, temperature=0.6)
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": reply})
            
            return {
                "role": "assistant",
                "content": reply,
                "model": f"ollama/{ollama_client.settings.ollama_model}",
                "agent_role": self.role.value,
                "timestamp": datetime.utcnow().isoformat(),
                "offline": False,
                "tools_used": [],
            }
        except Exception as e:
            logger.error(f"Agent {self.role} error: {e}")
            return self._offline_response(user_message, error=str(e))
    
    def _format_context(self, ctx: Dict[str, Any]) -> str:
        """Format port context for inclusion in system prompt."""
        lines = ["\n\n--- Contexto operativo en tiempo real ---"]
        
        if "ports_summary" in ctx:
            lines.append("\nPuertos principales:")
            for port in ctx["ports_summary"]:
                lines.append(
                    f"  {port.get('name')}: {port.get('occupancy_rate', 0):.0%} ocupación, "
                    f"{port.get('available_berths', 0)} atraques libres"
                )
        
        if "active_alerts" in ctx:
            if ctx["active_alerts"]:
                lines.append(f"\nAlertas activas: {len(ctx['active_alerts'])}")
                for alert in ctx["active_alerts"][:3]:
                    lines.append(f"  - {alert.get('description', 'Sin descripción')}")
        
        if "timestamp" in ctx:
            lines.append(f"\nÚltima actualización: {ctx['timestamp']}")
        
        return "\n".join(lines)
    
    def _offline_response(self, user_message: str, error: Optional[str] = None) -> Dict[str, Any]:
        """Return offline message when Ollama is unavailable."""
        msg = (
            "El asistente IA no está disponible en este momento. "
            "Por favor, intenta más tarde o contacta al administrador del sistema."
        )
        if error:
            logger.warning(f"Agent {self.role} offline - {error}")
        
        return {
            "role": "assistant",
            "content": msg,
            "model": "offline",
            "agent_role": self.role.value,
            "timestamp": datetime.utcnow().isoformat(),
            "offline": True,
            "tools_used": [],
        }
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


# Agent instances for each role
_agents: Dict[AgentRole, PortOperationsAgent] = {}


def get_agent(role: AgentRole = AgentRole.OPERATIONS) -> PortOperationsAgent:
    """Get or create an agent for a specific role."""
    if role not in _agents:
        _agents[role] = PortOperationsAgent(role)
    return _agents[role]


async def get_agent_response(
    user_message: str,
    agent_role: AgentRole = AgentRole.OPERATIONS,
    port_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Convenience function to get response from an agent."""
    agent = get_agent(agent_role)
    return await agent.process_message(user_message, port_context)


def get_available_agents() -> Dict[str, Dict[str, Any]]:
    """Get list of available agents and their capabilities."""
    agents_info = {}
    for role in AgentRole:
        agent = get_agent(role)
        agents_info[role.value] = {
            "name": role.value.capitalize(),
            "description": SYSTEM_PROMPTS[role].split("\n")[0],
            "tools": agent.tools,
        }
    return agents_info
