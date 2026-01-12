from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from .models import FitbitDailySummary

class FitbitDailySummaryProvider(ABC):
    """Abstract base class for providing Fitbit daily summaries."""

    @abstractmethod
    async def get_daily_activity_summary(self, date: date) -> FitbitDailySummary:
        """
        Retrieves a single Fitbit daily summary for a given user and date.

        Args:
            user_id: The ID of the user.
            date: The date of the summary.

        Returns:
            A FitbitDailySummary object.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_daily_activity_summaries(self, start_date: date, end_date: date) -> List[FitbitDailySummary]:
        """
        Retrieves a list of Fitbit daily summaries for a given user and date range.

        Args:
            user_id: The ID of the user.
            start_date: The start date of the period.
            end_date: The end date of the period.

        Returns:
            A list of FitbitDailySummary objects.
        """
        raise NotImplementedError