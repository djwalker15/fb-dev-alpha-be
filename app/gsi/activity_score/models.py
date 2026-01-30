from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, NonNegativeInt


class FitbitDailySummary(BaseModel):
    """Minimal daily summary required for the Activity Score.

    Map these from whichever Fitbit endpoint(s) you already ingest.
    """
    date: date
    steps: NonNegativeInt = 0
    active_zone_minutes: NonNegativeInt = Field(default=0, description="Fitbit Active Zone Minutes (AZM).")

    # Optional fields you may add later if you decide to extend scoring (not used in v2.1)
    calories_out: Optional[NonNegativeInt] = None


class ActivityScoreBreakdown(BaseModel):
    version: str
    steps_points: float
    azm_points: float


class ActivityScoreResult(BaseModel):
    date: date
    score: float = Field(ge=0, le=10)
    breakdown: ActivityScoreBreakdown
    steps: int
    active_zone_minutes: int
