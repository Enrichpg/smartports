# Assistant API — POST /api/v1/assistant/chat
# Conversational port operations assistant powered by Ollama (Llama 2).

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from config import settings
from llm.assistant_service import assistant_service
from llm.ollama_client import check_ollama_available

router = APIRouter(prefix="/assistant", tags=["LLM Assistant"])


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[ChatMessage]] = Field(default=None, description="Prior conversation turns")
    port_context: Optional[dict] = Field(default=None, description="Live port data to inject into context")


class ChatResponse(BaseModel):
    role: str
    content: str
    model: str
    timestamp: str
    offline: bool


@router.post("/chat", response_model=ChatResponse, summary="Chat with the port operations assistant")
async def chat(request: ChatRequest):
    """
    Send a message to the SmartPort conversational assistant.

    The assistant is backed by Ollama (Llama 2) and has domain knowledge of
    Galician port operations. Optionally pass `history` to maintain conversation
    context, and `port_context` (occupancy, alerts, etc.) to ground responses
    in live data.

    If Ollama is unavailable the endpoint returns an offline message with HTTP 200
    (the `offline: true` flag indicates degraded mode).
    """
    if not settings.enable_llm_assistant:
        raise HTTPException(status_code=503, detail="LLM assistant is disabled")

    history = [m.model_dump() for m in request.history] if request.history else None

    result = await assistant_service.chat(
        user_message=request.message,
        conversation_history=history,
        port_context=request.port_context,
    )
    return result


@router.get("/status", summary="Check Ollama availability")
async def assistant_status():
    """Return Ollama reachability and model status."""
    available = await check_ollama_available()
    return {
        "ollama_available": available,
        "model": settings.ollama_model,
        "base_url": settings.ollama_base_url,
        "enabled": settings.enable_llm_assistant,
        "note": (
            "Run `docker exec smartports_ollama ollama pull llama2` to download the model."
            if not available else "Ready"
        ),
    }
