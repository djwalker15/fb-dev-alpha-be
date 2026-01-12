from __future__ import annotations

from dataclasses import dataclass

from .models import ActivityScoreBreakdown, ActivityScoreResult, FitbitDailySummary

@dataclass(frozen=True)
class ActivityScoreCalculatorV1:
    """Daily Activity Score Calculator V1"""
    version: str = "1.0.0"

    @staticmethod
    def _steps_points(steps: int) -> int:
        if steps >= 12_000:
            return 4
        elif steps >= 9_000:
            return 3
        elif steps >= 6_000:
            return 2
        elif steps >= 3_000:
            return 1
        else:
            return 0

    @staticmethod
    def _azm_points(azm: int) -> int:
        if azm >= 120:
            return 4
        elif azm >= 80:
            return 3
        elif azm >= 40:
            return 2
        elif azm >= 0:
            return 1
        else:
            return 0

    @staticmethod
    def _floor_point(steps: int, azm: int) -> int:
        return 1 if (steps >= 3_000 or azm >= 5) else 0

    @staticmethod
    def _standard_bonus(steps: int, azm: int) -> int:
        if azm >= 80:
            return 1
        if steps >= 12_000 and azm >= 40:
            return 1
        return 0
        

    def calculate(self, day: FitbitDailySummary) -> ActivityScoreResult:  # type: ignore
        print(f"Summary: {day}")
        steps = int(day.steps)
        azm = int(day.active_zone_minutes)

        floor_point = self._floor_point(steps, azm)
        standard_bonus = self._standard_bonus(steps, azm)
        steps_points = self._steps_points(steps)
        azm_points = self._azm_points(azm)

        raw_total = floor_point + standard_bonus + steps_points + azm_points
        capped_total = min(10, raw_total)

        breakdown = ActivityScoreBreakdown(
            floor_point=floor_point,
            standard_bonus=standard_bonus,
            steps_points=steps_points,
            azm_points=azm_points,
            raw_total=raw_total,
            capped_total=capped_total
        )

        return ActivityScoreResult(
            date=day.date,
            score=capped_total,
            breakdown=breakdown,
            steps=steps,
            active_zone_minutes=azm
        )

