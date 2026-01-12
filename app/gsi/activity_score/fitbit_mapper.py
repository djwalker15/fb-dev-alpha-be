from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

def _extract_steps(payload: Dict[str, Any]) -> int:
    return int(payload.get("summary", {}).get("steps", 0))

def _extract_azm(payload: Dict[str, Any]) -> int:
    activities = payload.get("activities-active-zone-minutes", [])
    return sum(activity.get("value", {}).get("activeZoneMinutes", 0) for activity in activities)

def map_fitbit_daily_summary(summary: Dict[str, Any], azmPayload: Dict[str, Any], date: date) -> Optional[Dict[str, Any]]:
    
    return {
        "date": date,
        "steps": _extract_steps(summary),
        "active_zone_minutes": _extract_azm(azmPayload),
        "calories_out": summary.get("summary", {}).get("caloriesOut", 0),
    }
