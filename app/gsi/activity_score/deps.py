from __future__ import annotations

from functools import lru_cache

from .calculator import ActivityScoreCalculatorV1, ActivityScoreCalculatorV2
from .provider import FitbitDailySummaryProvider
from .provider_fitbit_impl import ExistingFitbitIntegrationProvider


@lru_cache
def get_activity_score_calculator_v1() -> ActivityScoreCalculatorV1:
    return ActivityScoreCalculatorV1()

    
@lru_cache
def get_activity_score_calculator_v2() -> ActivityScoreCalculatorV2:
    return ActivityScoreCalculatorV2()


def get_fitbit_daily_summary_provider() -> FitbitDailySummaryProvider:

    from app.integrations.fitbit_client import get_fitbit_client

    fitbit_client = get_fitbit_client()
    return ExistingFitbitIntegrationProvider(fitbit_client)
