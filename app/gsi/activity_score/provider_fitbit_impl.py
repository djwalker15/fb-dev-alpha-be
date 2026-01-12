from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from .models import FitbitDailySummary
from .provider import FitbitDailySummaryProvider
from .fitbit_mapper import map_fitbit_daily_summary
from app.integrations.fitbit_client import get_fresh_access_token

class ExistingFitbitIntegrationProvider(FitbitDailySummaryProvider):
    """
    This class provides an implementation of the FitbitDailySummaryProvider
    interface for existing Fitbit integrations.
    """
    def __init__(self, fitbit: FitbitClient):
        self._fitbit = fitbit

    # async def _get_fresh_access_token() -> str:
    #     """
    #     Always refresh using the stored refresh token.
    #     This avoids having to persist an access token at all.
    #     """
    #     refresh_token = secrets_store.read("fitbit_refresh_token").strip()
    #     if not refresh_token:
    #         raise HTTPException(status_code=400, detail="Fitbit not connected yet. Run /auth/start.")

    #     client = _get_fitbit_client()
    #     tokens = await client.refresh_tokens(refresh_token)

    #     # Rotate refresh token (critical)
    #     secrets_store.write_new_version("fitbit_refresh_token", tokens.refresh_token)
    #     return tokens.access_token

    async def get_daily_activity_summary(self, date: datetime) -> FitbitDailySummary:
        """
        Retrieves a daily summary for a given user on a specific date.

        Args:
            user_id: The ID of the user.
            date: The date for which to retrieve the summary.

        Returns:
            A FitbitDailySummary object.
        """
        token = await get_fresh_access_token()
        summary = await self._fitbit.get_daily_activity_summary(token, date)
        azmRes = await self._fitbit.get_active_zone_minutes(token, date)
        print(f"AZM: {azmRes}")
        
        data = map_fitbit_daily_summary(summary, azmRes, date)

        return FitbitDailySummary(**data)

    async def get_daily_activity_summaries(
        self, start_date: datetime, end_date: datetime
    ) -> List[FitbitDailySummary]:
        """
        Retrieves a list of daily summaries for a given user within a specified date range.

        Args:
            user_id: The ID of the user.
            start_date: The start date of the range.
            end_date: The end date of the range.

        Returns:
            A list of FitbitDailySummary objects.
        """
        results: List[FitbitDailySummary] = []
        d = start_date
        token = await get_fresh_access_token()
        while d <= end_date:
            payload = await self._fitbit.get_daily_activity_summary(token, d)
            azmRes = await self._fitbit.get_active_zone_minutes(token, d)
            mapped = map_fitbit_daily_summary(payload, azmRes, d)
            results.append(FitbitDailySummary(**mapped))
            d += timedelta(days=1)
        return results
