# Assistant Service — conversational port operations assistant powered by Ollama

import logging
from datetime import datetime
from typing import Optional

from llm import ollama_client

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """Eres el asistente operativo del SmartPort Galicia Operations Center.
Ayudas a los operadores portuarios de la red de puertos gallegos con:
- Consultas sobre disponibilidad de amarres y estado de embarcaciones
- Interpretación de alertas y condiciones meteorológicas
- Recomendaciones operativas basadas en datos en tiempo real
- Normativa portuaria española y gallega
- Coordinación de operaciones de atraque y desatraque

Responde siempre en español, de forma concisa y profesional.
Si no tienes datos suficientes para responder con certeza, indícalo claramente.
No inventes datos de buques, amarres ni condiciones meteorológicas concretos.
"""


class AssistantService:
    """Stateless conversational assistant backed by Ollama."""

    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[list[dict]] = None,
        port_context: Optional[dict] = None,
    ) -> dict:
        """
        Process a user message and return the assistant reply.

        conversation_history: list of {"role": ..., "content": ...} prior turns
        port_context: optional live data dict injected into system prompt
        """
        available = await ollama_client.check_ollama_available()
        if not available:
            return self._offline_response(user_message)

        system_content = _SYSTEM_PROMPT
        if port_context:
            system_content += self._format_port_context(port_context)

        messages = [{"role": "system", "content": system_content}]
        if conversation_history:
            messages.extend(conversation_history[-10:])  # keep last 10 turns
        messages.append({"role": "user", "content": user_message})

        try:
            reply = await ollama_client.chat(messages, temperature=0.6)
            return {
                "role": "assistant",
                "content": reply,
                "model": "ollama/llama2",
                "timestamp": datetime.utcnow().isoformat(),
                "offline": False,
            }
        except Exception as e:
            logger.error("Ollama chat error: %s", e)
            return self._offline_response(user_message, error=str(e))

    def _format_port_context(self, ctx: dict) -> str:
        lines = ["\n\n--- Contexto operativo actual ---"]
        if "port_name" in ctx:
            lines.append(f"Puerto activo: {ctx['port_name']}")
        if "total_berths" in ctx:
            lines.append(f"Amarres totales: {ctx['total_berths']}")
        if "available_berths" in ctx:
            lines.append(f"Amarres libres: {ctx['available_berths']}")
        if "active_alerts" in ctx:
            lines.append(f"Alertas activas: {ctx['active_alerts']}")
        if "occupancy_rate" in ctx:
            lines.append(f"Ocupación actual: {ctx['occupancy_rate']:.0%}")
        return "\n".join(lines)

    def _offline_response(self, user_message: str, error: Optional[str] = None) -> dict:
        msg = (
            "El asistente LLM no está disponible en este momento. "
            "El modelo Ollama (Llama 2) debe estar en ejecución y tener el modelo descargado. "
            "Usa `docker exec smartports_ollama ollama pull llama2` para descargarlo."
        )
        if error:
            logger.warning("Assistant offline — %s", error)
        return {
            "role": "assistant",
            "content": msg,
            "model": "offline",
            "timestamp": datetime.utcnow().isoformat(),
            "offline": True,
        }


assistant_service = AssistantService()
