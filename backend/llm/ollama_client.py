# Ollama HTTP client — wraps the Ollama REST API for local LLM inference

import logging
import httpx
from typing import AsyncIterator, Optional
from config import settings

logger = logging.getLogger(__name__)

OLLAMA_GENERATE_URL = f"{settings.ollama_base_url}/api/generate"
OLLAMA_CHAT_URL = f"{settings.ollama_base_url}/api/chat"
OLLAMA_TAGS_URL = f"{settings.ollama_base_url}/api/tags"


async def check_ollama_available() -> bool:
    """Return True if Ollama is reachable and the configured model is present."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(OLLAMA_TAGS_URL)
            if resp.status_code != 200:
                return False
            models = [m["name"] for m in resp.json().get("models", [])]
            return any(settings.ollama_model in m for m in models)
    except Exception:
        return False


async def chat(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: float = 0.7,
    stream: bool = False,
) -> str:
    """
    Send a chat request to Ollama and return the assistant reply as a string.
    messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
    """
    model = model or settings.ollama_model
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "options": {"temperature": temperature},
    }

    async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
        resp = await client.post(OLLAMA_CHAT_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]


async def generate(prompt: str, model: Optional[str] = None) -> str:
    """Simple single-turn generate endpoint (no chat history)."""
    model = model or settings.ollama_model
    payload = {"model": model, "prompt": prompt, "stream": False}
    async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
        resp = await client.post(OLLAMA_GENERATE_URL, json=payload)
        resp.raise_for_status()
        return resp.json()["response"]
