from __future__ import annotations

from functools import lru_cache

from .calculator import ActivityScoreCalculatorV1
from .provider import FitbitDailySummaryProvider
from .provider_fitbit_impl import ExistingFitbitIntegrationProvider


@lru_cache
def get_activity_score_calculator() -> ActivityScoreCalculatorV1:
    return ActivityScoreCalculatorV1()


def get_fitbit_daily_summary_provider() -> FitbitDailySummaryProvider:

    from app.integrations.fitbit_client import get_fitbit_client

    fitbit_client = get_fitbit_client()
    return ExistingFitbitIntegrationProvider(fitbit_client)
