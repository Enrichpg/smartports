# ML Forecast Service — occupancy forecasting with Prophet
# Uses synthetic training data (seasonal patterns) until TimescaleDB has sufficient real history.

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Prophet import is optional — graceful degradation if not available at runtime
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("Prophet not installed — forecasting will return synthetic estimates")


def _generate_training_data(port_id: str, days: int = 180) -> pd.DataFrame:
    """
    Generate plausible historical occupancy training data for a port.
    Encodes weekly seasonality (weekends busier) + summer peak (July-August)
    + mild noise. Values are occupancy rate 0.0–1.0.
    """
    rng = np.random.default_rng(seed=hash(port_id) % (2**31))
    end = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=days)
    dates = pd.date_range(start, end, freq="H")

    base = 0.55
    # Weekly seasonality: higher Fri–Sun
    weekly = np.array([0.0, 0.0, 0.05, 0.05, 0.10, 0.15, 0.12])[dates.dayofweek]
    # Summer peak: sinusoidal peak centred on day 200 (mid-July)
    day_of_year = dates.dayofyear
    summer = 0.15 * np.clip(np.sin(np.pi * (day_of_year - 120) / 120), 0, 1)
    # Daily rhythm: busier 08:00–20:00
    hour_factor = np.where((dates.hour >= 8) & (dates.hour < 20), 0.08, -0.04)
    noise = rng.normal(0, 0.04, len(dates))

    occupancy = np.clip(base + weekly + summer + hour_factor + noise, 0.0, 1.0)
    return pd.DataFrame({"ds": dates, "y": occupancy})


class ForecastService:
    """Occupancy forecasting for ports using Prophet."""

    def __init__(self):
        self._models: Dict[str, Any] = {}

    def _get_or_train(self, port_id: str) -> Optional[Any]:
        """Return a cached trained Prophet model, training it on first call.
        Falls back to None (→ synthetic forecast) on any runtime error."""
        if not PROPHET_AVAILABLE:
            return None
        if port_id not in self._models:
            try:
                df = _generate_training_data(port_id)
                m = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=True,
                    daily_seasonality=True,
                    changepoint_prior_scale=0.05,
                    interval_width=0.80,
                )
                m.fit(df)
                self._models[port_id] = m
                logger.info("Trained Prophet model for port %s", port_id)
            except Exception as e:
                logger.warning("Prophet unavailable (%s) — using deterministic fallback", e)
                self._models[port_id] = None
        return self._models[port_id]

    def forecast_occupancy(
        self,
        port_id: str,
        horizon_hours: int = 48,
    ) -> Dict[str, Any]:
        """
        Forecast port occupancy for the next `horizon_hours` hours.
        Returns a dict with forecast list and metadata.
        """
        model = self._get_or_train(port_id)

        if model is None:
            return self._synthetic_forecast(port_id, horizon_hours)

        future = model.make_future_dataframe(periods=horizon_hours, freq="H", include_history=False)
        forecast = model.predict(future)

        points = []
        for _, row in forecast.iterrows():
            points.append({
                "timestamp": row["ds"].isoformat(),
                "occupancy_rate": round(float(np.clip(row["yhat"], 0.0, 1.0)), 3),
                "lower_bound": round(float(np.clip(row["yhat_lower"], 0.0, 1.0)), 3),
                "upper_bound": round(float(np.clip(row["yhat_upper"], 0.0, 1.0)), 3),
            })

        return {
            "port_id": port_id,
            "model": "prophet",
            "horizon_hours": horizon_hours,
            "generated_at": datetime.utcnow().isoformat(),
            "forecast": points,
        }

    def _synthetic_forecast(self, port_id: str, horizon_hours: int) -> Dict[str, Any]:
        """Fallback when Prophet is unavailable: deterministic synthetic curve."""
        rng = np.random.default_rng(seed=hash(port_id) % (2**31))
        now = datetime.utcnow()
        points = []
        for h in range(horizon_hours):
            ts = now + timedelta(hours=h)
            hour_factor = 0.08 if 8 <= ts.hour < 20 else -0.04
            base = 0.55 + hour_factor + rng.normal(0, 0.03)
            val = float(np.clip(base, 0.0, 1.0))
            points.append({
                "timestamp": ts.isoformat(),
                "occupancy_rate": round(val, 3),
                "lower_bound": round(max(0.0, val - 0.08), 3),
                "upper_bound": round(min(1.0, val + 0.08), 3),
            })
        return {
            "port_id": port_id,
            "model": "synthetic_fallback",
            "horizon_hours": horizon_hours,
            "generated_at": datetime.utcnow().isoformat(),
            "forecast": points,
        }


forecast_service = ForecastService()
