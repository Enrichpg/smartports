# ML Recommender Service — berth recommendation with scikit-learn
# Ranks available berths for a vessel using a weighted scoring model.
# Uses a RandomForest trained on synthetic compatibility features.

import logging
import numpy as np
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed — recommender will use rule-based scoring")


# Feature vector for a (vessel, berth) pair:
# [length_fit, beam_fit, draft_fit, type_match, status_ok, distance_score]
# All values normalised to [0, 1].

_BERTH_TYPE_COMPAT = {
    # vessel_type -> compatible berth categories
    "cargo": ["commercial", "general", "ro-ro"],
    "tanker": ["tanker", "commercial"],
    "fishing": ["fishing", "small_craft"],
    "passenger": ["passenger", "commercial"],
    "cruise": ["passenger", "cruise"],
    "sailboat": ["recreational", "small_craft", "marina"],
    "motorboat": ["recreational", "small_craft", "marina"],
    "tug": ["service", "general", "commercial"],
    "research": ["general", "commercial"],
}


def _vessel_berth_features(vessel: Dict[str, Any], berth: Dict[str, Any]) -> List[float]:
    """Build normalised feature vector for vessel–berth compatibility."""
    v_length = float(vessel.get("length", 20))
    v_beam = float(vessel.get("beam", 6))
    v_draft = float(vessel.get("draft", 3))
    v_type = str(vessel.get("vessel_type", "")).lower()

    b_max_length = float(berth.get("max_length", 50))
    b_max_beam = float(berth.get("max_beam", 15))
    b_max_draft = float(berth.get("max_draft", 8))
    b_category = str(berth.get("category", "general")).lower()
    b_status = str(berth.get("status", "free")).lower()

    length_fit = float(v_length <= b_max_length) * min(1.0, (b_max_length - v_length + 1) / (b_max_length + 1))
    beam_fit = float(v_beam <= b_max_beam) * min(1.0, (b_max_beam - v_beam + 1) / (b_max_beam + 1))
    draft_fit = float(v_draft <= b_max_draft) * min(1.0, (b_max_draft - v_draft + 1) / (b_max_draft + 1))

    compatible_categories = _BERTH_TYPE_COMPAT.get(v_type, ["general"])
    type_match = 1.0 if b_category in compatible_categories else 0.3

    status_ok = 1.0 if b_status == "free" else (0.5 if b_status == "reserved" else 0.0)

    # Prefer medium utilisation berths (not extremes) — use beam ratio as proxy
    utilisation_score = 1.0 - abs((v_beam / max(b_max_beam, 1)) - 0.7)

    return [length_fit, beam_fit, draft_fit, type_match, status_ok, utilisation_score]


def _synthetic_training_data(n: int = 2000):
    """Generate synthetic (features, score) pairs for RandomForest training."""
    rng = np.random.default_rng(42)
    X, y = [], []
    for _ in range(n):
        feats = rng.uniform(0, 1, 6).tolist()
        # Score is weighted combination of features
        score = (
            0.30 * feats[0]  # length fit
            + 0.20 * feats[1]  # beam fit
            + 0.20 * feats[2]  # draft fit
            + 0.15 * feats[3]  # type match
            + 0.10 * feats[4]  # status
            + 0.05 * feats[5]  # utilisation
            + rng.normal(0, 0.03)
        )
        X.append(feats)
        y.append(float(np.clip(score, 0, 1)))
    return np.array(X), np.array(y)


class RecommenderService:
    """Berth recommendation service."""

    def __init__(self):
        self._model: Optional[Any] = None

    def _get_model(self):
        if self._model is None and SKLEARN_AVAILABLE:
            X, y = _synthetic_training_data()
            self._model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
            self._model.fit(X, y)
            logger.info("Trained RandomForest recommender model")
        return self._model

    def recommend_berths(
        self,
        vessel: Dict[str, Any],
        berths: List[Dict[str, Any]],
        top_n: int = 5,
    ) -> Dict[str, Any]:
        """
        Rank `berths` for a `vessel` and return top_n recommendations.

        vessel dict keys: length, beam, draft, vessel_type
        berth dict keys: id, name, category, status, max_length, max_beam, max_draft
        """
        model = self._get_model()

        scored: List[Dict[str, Any]] = []
        for berth in berths:
            feats = _vessel_berth_features(vessel, berth)

            if model is not None:
                score = float(model.predict([feats])[0])
            else:
                # Rule-based fallback: weighted dot product
                weights = [0.30, 0.20, 0.20, 0.15, 0.10, 0.05]
                score = sum(w * f for w, f in zip(weights, feats))

            score = round(float(np.clip(score, 0.0, 1.0)), 4)

            if feats[4] == 0.0:  # status not ok — skip occupied/OOS berths
                continue

            scored.append({
                "berth_id": berth.get("id"),
                "berth_name": berth.get("name", berth.get("id")),
                "category": berth.get("category"),
                "status": berth.get("status"),
                "score": score,
                "features": {
                    "length_fit": round(feats[0], 3),
                    "beam_fit": round(feats[1], 3),
                    "draft_fit": round(feats[2], 3),
                    "type_match": round(feats[3], 3),
                    "availability": round(feats[4], 3),
                },
            })

        scored.sort(key=lambda x: x["score"], reverse=True)

        return {
            "vessel": {
                "id": vessel.get("id"),
                "type": vessel.get("vessel_type"),
                "length_m": vessel.get("length"),
                "beam_m": vessel.get("beam"),
                "draft_m": vessel.get("draft"),
            },
            "model": "random_forest" if model is not None else "rule_based_fallback",
            "total_candidates": len(berths),
            "recommendations": scored[:top_n],
        }


recommender_service = RecommenderService()
