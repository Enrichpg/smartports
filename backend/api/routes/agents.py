# Agents API — Endpoints for specialized LLM agents

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from llm.agents import AgentRole, get_agent_response, get_available_agents
from config import settings

router = APIRouter(prefix="/agents", tags=["LLM Agents"])


class AgentMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class AgentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    agent_role: Optional[str] = Field(
        default="operations",
        description="Agent role: operations, forecasting, maintenance, compliance, incident",
    )
    port_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional live port data context (occupancy, alerts, etc.)",
    )


class AgentResponse(BaseModel):
    role: str
    content: str
    agent_role: str
    model: str
    timestamp: str
    offline: bool
    tools_used: List[str] = []


@router.post("/query", response_model=AgentResponse, summary="Query a specialized agent")
async def query_agent(request: AgentRequest):
    """
    Send a message to a specialized port operations agent.
    
    **Agent Roles:**
    - `operations`: General port operations, berth availability, vessel coordination
    - `forecasting`: Occupancy predictions, resource planning
    - `maintenance`: Equipment status, maintenance planning
    - `compliance`: Regulatory requirements, safety standards
    - `incident`: Alert management, incident response
    
    Each agent has specialized knowledge and access to different data sources.
    """
    if not settings.enable_llm_assistant:
        raise HTTPException(status_code=503, detail="LLM agent service is disabled")
    
    # Validate agent role
    try:
        role = AgentRole(request.agent_role or "operations")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent role. Available: {', '.join([r.value for r in AgentRole])}",
        )
    
    result = await get_agent_response(
        user_message=request.message,
        agent_role=role,
        port_context=request.port_context,
    )
    return AgentResponse(**result)


@router.get("/roles", summary="Get available agent roles")
async def get_agent_roles():
    """Get list of available agent roles and their capabilities."""
    if not settings.enable_llm_assistant:
        raise HTTPException(status_code=503, detail="LLM agent service is disabled")
    
    agents = get_available_agents()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "agents": agents,
        "total_agents": len(agents),
    }


@router.post("/operations", response_model=AgentResponse, summary="Operations Agent")
async def operations_agent(request: AgentRequest):
    """Direct endpoint for Operations Agent (general port operations)."""
    if not settings.enable_llm_assistant:
        raise HTTPException(status_code=503, detail="LLM assistant is disabled")
    
    request.agent_role = "operations"
    return await query_agent(request)


@router.post("/forecasting", response_model=AgentResponse, summary="Forecasting Agent")
async def forecasting_agent(request: AgentRequest):
    """Direct endpoint for Forecasting Agent (occupancy predictions)."""
    if not settings.enable_llm_assistant:
        raise HTTPException(status_code=503, detail="LLM assistant is disabled")
    
    request.agent_role = "forecasting"
    return await query_agent(request)


@router.post("/maintenance", response_model=AgentResponse, summary="Maintenance Agent")
async def maintenance_agent(request: AgentRequest):
    """Direct endpoint for Maintenance Agent (equipment & infrastructure)."""
    if not settings.enable_llm_assistant:
        raise HTTPException(status_code=503, detail="LLM assistant is disabled")
    
    request.agent_role = "maintenance"
    return await query_agent(request)


@router.post("/compliance", response_model=AgentResponse, summary="Compliance Agent")
async def compliance_agent(request: AgentRequest):
    """Direct endpoint for Compliance Agent (regulatory & safety)."""
    if not settings.enable_llm_assistant:
        raise HTTPException(status_code=503, detail="LLM assistant is disabled")
    
    request.agent_role = "compliance"
    return await query_agent(request)


@router.post("/incident", response_model=AgentResponse, summary="Incident Agent")
async def incident_agent(request: AgentRequest):
    """Direct endpoint for Incident Agent (alert management)."""
    if not settings.enable_llm_assistant:
        raise HTTPException(status_code=503, detail="LLM assistant is disabled")
    
    request.agent_role = "incident"
    return await query_agent(request)


from datetime import datetime
