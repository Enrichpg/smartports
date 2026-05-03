# Recommendations API — GET /api/v1/recommendations/berth
# sklearn-based berth recommendation for a vessel.

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from config import settings
from ml.recommender_service import recommender_service
from services.berth_service import berth_service

router = APIRouter(prefix="/recommendations", tags=["ML Recommendations"])


@router.get("/berth", summary="Recommend berths for a vessel")
async def recommend_berth(
    port_id: str = Query(..., description="NGSI-LD port entity ID"),
    vessel_id: Optional[str] = Query(None, description="NGSI-LD vessel entity ID (for context)"),
    vessel_type: str = Query("cargo", description="Vessel type: cargo, tanker, fishing, passenger, sailboat..."),
    length_m: float = Query(..., ge=1, le=500, description="Vessel overall length in metres"),
    beam_m: float = Query(..., ge=1, le=100, description="Vessel beam in metres"),
    draft_m: float = Query(..., ge=0.5, le=30, description="Vessel draft in metres"),
    top_n: int = Query(5, ge=1, le=20, description="Number of recommendations to return"),
):
    """
    Rank available berths in a port for the given vessel dimensions and type.

    Uses a RandomForest model trained on compatibility features (size fit,
    type compatibility, availability). Returns scored recommendations in
    descending order of suitability.
    """
    if not settings.enable_ml_recommendations:
        raise HTTPException(status_code=503, detail="ML recommendations are disabled")

    try:
        berths_list, _ = await berth_service.get_berths_by_port(port_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch berths for port {port_id}: {e}")

    if not berths_list:
        raise HTTPException(status_code=404, detail=f"No berths found for port {port_id}")

    vessel = {
        "id": vessel_id,
        "vessel_type": vessel_type,
        "length": length_m,
        "beam": beam_m,
        "draft": draft_m,
    }

    # Convert BerthResponse objects to plain dicts for the ML layer.
    # Seed stores length/depth in the dimensions dict; use sensible defaults
    # for beam/draft since those aren't in the current seed schema.
    berths_dicts = []
    for b in berths_list:
        berth_length = b.length or 150.0
        berth_depth = b.depth or 10.0
        berths_dicts.append({
            "id": b.id,
            "name": b.name or b.id,
            "category": b.category or "general",
            "status": b.status.value if hasattr(b.status, "value") else str(b.status),
            "max_length": berth_length,
            "max_beam": berth_length * 0.18,   # typical beam ≈ 18 % of length
            "max_draft": berth_depth,
        })

    try:
        result = recommender_service.recommend_berths(vessel, berths_dicts, top_n=top_n)
        result["port_id"] = port_id
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {e}")
