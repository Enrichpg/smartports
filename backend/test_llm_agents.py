#!/usr/bin/env python3
"""
SmartPort LLM Agents Test Script

Run this script to test the LLM agent system:
    python test_llm_agents.py
"""

import asyncio
import httpx
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30


async def query_agent(
    message: str,
    agent_role: str = "operations",
    port_context: Optional[dict] = None,
) -> dict:
    """Query an agent and return the response."""
    url = f"{BASE_URL}/agents/query"
    
    payload = {
        "message": message,
        "agent_role": agent_role,
        "port_context": port_context,
    }
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


async def get_agent_roles() -> dict:
    """Get available agent roles."""
    url = f"{BASE_URL}/agents/roles"
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


async def main():
    """Run test queries against different agents."""
    
    print("=" * 80)
    print("SmartPort LLM Agents - Test Suite")
    print("=" * 80)
    print()
    
    # 1. Get available agents
    print("📋 Step 1: Fetching available agents...")
    print("-" * 80)
    roles = await get_agent_roles()
    
    if "error" in roles:
        print(f"❌ Error: {roles['error']}")
        return
    
    print(f"✅ Found {roles.get('total_agents', 0)} agents:")
    for role_name, role_info in roles.get("agents", {}).items():
        print(f"  • {role_name.upper()}: {role_info.get('description', 'N/A')}")
    
    print()
    
    # 2. Example context data
    port_context = {
        "ports_summary": [
            {"name": "Vigo", "occupancy_rate": 0.72, "available_berths": 7},
            {"name": "A Coruña", "occupancy_rate": 0.45, "available_berths": 12},
            {"name": "Ferrol", "occupancy_rate": 0.38, "available_berths": 15},
        ],
        "active_alerts": [
            "Alerta de mantenimiento en puerto de Vigo",
            "Mal estado del mar en Ferrol",
        ],
        "timestamp": "2024-05-14T10:30:00Z",
    }
    
    # 3. Test Operations Agent
    print("🤖 Step 2: Testing Operations Agent...")
    print("-" * 80)
    
    test_queries_operations = [
        "¿Cuántos atraques libres hay en Vigo?",
        "¿Cuál es la ocupación en A Coruña?",
    ]
    
    for query in test_queries_operations:
        print(f"\n📝 Query: {query}")
        result = await query_agent(query, agent_role="operations", port_context=port_context)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Agent: {result.get('agent_role', 'N/A')}")
            print(f"📄 Response: {result.get('content', 'N/A')[:200]}...")
            print(f"🔧 Tools used: {result.get('tools_used', [])}")
    
    print()
    
    # 4. Test Forecasting Agent
    print("🤖 Step 3: Testing Forecasting Agent...")
    print("-" * 80)
    
    test_queries_forecasting = [
        "¿Cuál será la ocupación en Vigo en las próximas 48 horas?",
    ]
    
    for query in test_queries_forecasting:
        print(f"\n📝 Query: {query}")
        result = await query_agent(query, agent_role="forecasting", port_context=port_context)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Agent: {result.get('agent_role', 'N/A')}")
            print(f"📄 Response: {result.get('content', 'N/A')[:200]}...")
    
    print()
    
    # 5. Test Incident Agent
    print("🤖 Step 4: Testing Incident Agent...")
    print("-" * 80)
    
    test_queries_incident = [
        "¿Cuáles son las alertas activas críticas?",
    ]
    
    for query in test_queries_incident:
        print(f"\n📝 Query: {query}")
        result = await query_agent(query, agent_role="incident", port_context=port_context)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Agent: {result.get('agent_role', 'N/A')}")
            print(f"📄 Response: {result.get('content', 'N/A')[:200]}...")
    
    print()
    print("=" * 80)
    print("✅ Test suite completed!")
    print("=" * 80)


if __name__ == "__main__":
    print("\n⏳ Starting tests... (this may take a moment)")
    print("   Make sure the backend is running: docker compose up\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
