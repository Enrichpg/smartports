# Forecasts API — GET /api/v1/forecasts/occupancy
# Prophet-based occupancy forecasting per port.

from fastapi import APIRouter, Query, HTTPException
from config import settings
from ml.forecast_service import forecast_service

router = APIRouter(prefix="/forecasts", tags=["ML Forecasting"])


@router.get("/occupancy", summary="Forecast port occupancy")
async def forecast_occupancy(
    port_id: str = Query(..., description="NGSI-LD port entity ID"),
    horizon_hours: int = Query(48, ge=1, le=168, description="Forecast horizon in hours (max 7 days)"),
):
    """
    Return hourly occupancy rate forecast for the given port.

    The model (Prophet) is trained on synthetic seasonal data that encodes
    weekly patterns and summer peaks typical for Galician ports.
    """
    if not settings.enable_ml_forecasting:
        raise HTTPException(status_code=503, detail="ML forecasting is disabled")

    try:
        result = forecast_service.forecast_occupancy(port_id, horizon_hours=horizon_hours)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting error: {e}")


@router.get("/occupancy/summary", summary="Current + next 24h occupancy summary")
async def forecast_occupancy_summary(
    port_id: str = Query(..., description="NGSI-LD port entity ID"),
):
    """Compact summary: current occupancy estimate + next 24h peak/valley."""
    if not settings.enable_ml_forecasting:
        raise HTTPException(status_code=503, detail="ML forecasting is disabled")

    try:
        result = forecast_service.forecast_occupancy(port_id, horizon_hours=24)
        points = result["forecast"]
        rates = [p["occupancy_rate"] for p in points]
        return {
            "port_id": port_id,
            "model": result["model"],
            "generated_at": result["generated_at"],
            "next_24h": {
                "average_occupancy": round(sum(rates) / len(rates), 3) if rates else None,
                "peak_occupancy": max(rates) if rates else None,
                "valley_occupancy": min(rates) if rates else None,
                "peak_hour": points[rates.index(max(rates))]["timestamp"] if rates else None,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting error: {e}")
