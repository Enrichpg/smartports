# LLM Tools — Funciones que los agentes IA pueden invocar

import logging
import json
from typing import Any, Optional, Callable, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry of tools available to LLM agents."""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: str, func: Callable, schema: Dict[str, Any]):
        """Register a tool function with its schema."""
        self.tools[name] = func
        self.schemas[name] = schema
        logger.info(f"Tool registered: {name}")
    
    async def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool."""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}
        
        try:
            func = self.tools[tool_name]
            # Check if function is async
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return await func(**kwargs)
            else:
                return func(**kwargs)
        except Exception as e:
            logger.error(f"Tool execution error for '{tool_name}': {e}")
            return {"error": str(e)}
    
    def get_openai_schema(self) -> List[Dict[str, Any]]:
        """Get OpenAI-compatible function schema for all tools."""
        tools = []
        for name, schema in self.schemas.items():
            tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": schema.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": schema.get("parameters", {}),
                        "required": schema.get("required", []),
                    },
                },
            })
        return tools


# Global registry
tools_registry = ToolRegistry()


# ============================================================================
# Port & Berth Tools
# ============================================================================

async def get_port_occupancy(port_id: str) -> Dict[str, Any]:
    """Get current occupancy metrics for a port."""
    # This will be injected with real data from orion_service
    # For now, return structure template
    return {
        "port_id": port_id,
        "total_berths": 0,
        "occupied_berths": 0,
        "available_berths": 0,
        "occupancy_rate": 0.0,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def get_berth_availability(port_id: str, berth_type: Optional[str] = None) -> Dict[str, Any]:
    """Get available berths in a port, optionally filtered by type."""
    return {
        "port_id": port_id,
        "berth_type": berth_type,
        "available_berths": [],
        "count": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def get_active_alerts(port_id: Optional[str] = None, severity: Optional[str] = None) -> Dict[str, Any]:
    """Get active alerts, optionally filtered by port and severity."""
    return {
        "alerts": [],
        "count": 0,
        "port_id": port_id,
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def get_vessel_info(vessel_id: str) -> Dict[str, Any]:
    """Get detailed information about a vessel."""
    return {
        "vessel_id": vessel_id,
        "name": "",
        "type": "",
        "length": 0,
        "beam": 0,
        "draft": 0,
        "status": "unknown",
        "position": None,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def get_port_call_status(portcall_id: str) -> Dict[str, Any]:
    """Get status of a port call/visit."""
    return {
        "portcall_id": portcall_id,
        "vessel": "",
        "port": "",
        "status": "unknown",
        "arrival": None,
        "departure": None,
        "berth": None,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def predict_occupancy(port_id: str, hours_ahead: int = 24) -> Dict[str, Any]:
    """Predict port occupancy for the next N hours."""
    return {
        "port_id": port_id,
        "hours_ahead": hours_ahead,
        "forecast": [],
        "confidence": 0.0,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def recommend_berth(
    port_id: str,
    vessel_type: str,
    length_m: float,
    beam_m: float,
    draft_m: float,
    top_n: int = 5,
) -> Dict[str, Any]:
    """Recommend best berths for a vessel in a port."""
    return {
        "port_id": port_id,
        "recommendations": [],
        "count": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def get_weather(port_id: str) -> Dict[str, Any]:
    """Get current weather conditions for a port."""
    return {
        "port_id": port_id,
        "temperature": 0,
        "wind_speed": 0,
        "wind_direction": "",
        "wave_height": 0,
        "visibility": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Tool Registration
# ============================================================================

def register_all_tools():
    """Register all available tools for the LLM."""
    
    tools_registry.register(
        "get_port_occupancy",
        get_port_occupancy,
        {
            "description": "Get current occupancy metrics for a port (total berths, occupied, available, percentage)",
            "parameters": {
                "port_id": {
                    "type": "string",
                    "description": "Port ID (e.g., 'Vigo', 'CorunaA', 'Ferrol')",
                },
            },
            "required": ["port_id"],
        },
    )
    
    tools_registry.register(
        "get_berth_availability",
        get_berth_availability,
        {
            "description": "Get list of available berths in a port, optionally filtered by berth type",
            "parameters": {
                "port_id": {
                    "type": "string",
                    "description": "Port ID",
                },
                "berth_type": {
                    "type": "string",
                    "description": "Optional berth type (e.g., 'general_cargo', 'container', 'tanker')",
                },
            },
            "required": ["port_id"],
        },
    )
    
    tools_registry.register(
        "get_active_alerts",
        get_active_alerts,
        {
            "description": "Get active alerts in the system, optionally filtered by port and severity",
            "parameters": {
                "port_id": {
                    "type": "string",
                    "description": "Optional port ID to filter alerts",
                },
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Optional severity level filter",
                },
            },
            "required": [],
        },
    )
    
    tools_registry.register(
        "get_vessel_info",
        get_vessel_info,
        {
            "description": "Get detailed information about a specific vessel",
            "parameters": {
                "vessel_id": {
                    "type": "string",
                    "description": "Vessel ID or IMO number",
                },
            },
            "required": ["vessel_id"],
        },
    )
    
    tools_registry.register(
        "get_port_call_status",
        get_port_call_status,
        {
            "description": "Get status of a port call/visit",
            "parameters": {
                "portcall_id": {
                    "type": "string",
                    "description": "Port call ID",
                },
            },
            "required": ["portcall_id"],
        },
    )
    
    tools_registry.register(
        "predict_occupancy",
        predict_occupancy,
        {
            "description": "Predict port occupancy for the next N hours",
            "parameters": {
                "port_id": {
                    "type": "string",
                    "description": "Port ID",
                },
                "hours_ahead": {
                    "type": "integer",
                    "description": "Number of hours to forecast (default 24)",
                    "default": 24,
                },
            },
            "required": ["port_id"],
        },
    )
    
    tools_registry.register(
        "recommend_berth",
        recommend_berth,
        {
            "description": "Recommend best berths for a vessel based on dimensions and type",
            "parameters": {
                "port_id": {
                    "type": "string",
                    "description": "Port ID",
                },
                "vessel_type": {
                    "type": "string",
                    "description": "Vessel type (cargo, tanker, container, passenger, etc.)",
                },
                "length_m": {
                    "type": "number",
                    "description": "Vessel length in meters",
                },
                "beam_m": {
                    "type": "number",
                    "description": "Vessel beam in meters",
                },
                "draft_m": {
                    "type": "number",
                    "description": "Vessel draft in meters",
                },
                "top_n": {
                    "type": "integer",
                    "description": "Number of recommendations to return (default 5)",
                    "default": 5,
                },
            },
            "required": ["port_id", "vessel_type", "length_m", "beam_m", "draft_m"],
        },
    )
    
    tools_registry.register(
        "get_weather",
        get_weather,
        {
            "description": "Get current weather and sea conditions for a port",
            "parameters": {
                "port_id": {
                    "type": "string",
                    "description": "Port ID",
                },
            },
            "required": ["port_id"],
        },
    )


# Initialize on import
register_all_tools()
