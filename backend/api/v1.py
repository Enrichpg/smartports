# API v1 Routes
# Main API endpoint structure

from fastapi import APIRouter

router = APIRouter()


@router.get("/", name="API v1 Root")
async def api_v1_root():
    """SmartPort API v1 root endpoint"""
    return {
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "ports": "/ports",
            "berths": "/berths",
            "vessels": "/vessels",
            "operations": "/operations",
            "observations": "/observations",
            "health": "/health",
        }
    }


@router.get("/ports", name="List Ports")
async def get_ports():
    """List all ports in the Galician network"""
    return {
        "message": "Ports endpoint",
        "status": "not_implemented_yet",
    }


@router.get("/berths", name="List Berths")
async def get_berths():
    """List all berths across ports"""
    return {
        "message": "Berths endpoint",
        "status": "not_implemented_yet",
    }


@router.get("/vessels", name="List Vessels")
async def get_vessels():
    """List all vessels in system"""
    return {
        "message": "Vessels endpoint",
        "status": "not_implemented_yet",
    }


@router.get("/operations", name="List Operations")
async def get_operations():
    """List port operations"""
    return {
        "message": "Operations endpoint",
        "status": "not_implemented_yet",
    }


@router.get("/observations", name="List Observations")
async def get_observations():
    """Get sensor observations and measurements"""
    return {
        "message": "Observations endpoint",
        "status": "not_implemented_yet",
    }
