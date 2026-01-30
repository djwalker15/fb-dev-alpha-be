from __future__ import annotations

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query

from .calculator import ActivityScoreCalculatorV1, ActivityScoreCalculatorV2
from .deps import get_activity_score_calculator_v1, get_activity_score_calculator_v2, get_fitbit_daily_summary_provider
from .models import ActivityScoreResult
from .provider import FitbitDailySummaryProvider

router = APIRouter(prefix="/gsi/activity-score", tags=["GSI"])


@router.get("/day/{day}", response_model=ActivityScoreResult)
async def get_activity_score(
    day: date,
    calculator: ActivityScoreCalculatorV2 = Depends(get_activity_score_calculator_v2),
    provider: FitbitDailySummaryProvider = Depends(get_fitbit_daily_summary_provider)
) -> ActivityScoreResult: 
    summary = await provider.get_daily_activity_summary(day)
    return calculator.calculate(summary)


@router.get("/range", response_model=None)
async def get_range_scores(
    start_date: date = Query(..., description="The start date of the range."),
    end_date: date = Query(..., description="The end date of the range."),
    calculator: ActivityScoreCalculatorV2 = Depends(get_activity_score_calculator_v2),
    provider: FitbitDailySummaryProvider = Depends(get_fitbit_daily_summary_provider)
) -> list[ActivityScoreResult]:
    days = await provider.get_daily_activity_summaries(start_date, end_date)
    results = []
    for day in days:
        print(f"Day: {day}")
        result = calculator.calculate(day)
        print(f"Result: {result}")
        results.append(result)
    return results
# async def get_range_scores(
#     start_date: Query(...),
#     end_date: Query(...),
#     user_id: str = Query(..., description="The ID of the user."),
#     calculator: ActivityScoreCalculatorV1 = Depends(get_activity_score_calculator),
#  ) -> list[ActivityScoreResult]:
#     days = await provider.get_daily_summaries(start_date, end_date)
#     return [calculator.calculate(day) for day in days]
