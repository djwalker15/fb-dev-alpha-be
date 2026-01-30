from __future__ import annotations

from dataclasses import dataclass

from .models import ActivityScoreBreakdown, ActivityScoreResult, FitbitDailySummary

@dataclass(frozen=True)
class ActivityScoreCalculatorV2:
    """Daily Activity Score Calculator V2 - Efficiency Gradient Model"""
    version: str = "2.0.0"
    @staticmethod
    def _getVersion() -> str:
        return "2.0.0"


    @staticmethod
    def _calculate_steps_signal(steps: int) -> float:
        """Calculates Step Signal (0.0 - 1.0) targeting fat loss volume."""
        if steps < 8000:
            # Linear ramp to 1.0 at 8k steps
            return round(steps / 8000, 2)
        elif 8000 <= steps <= 13000:
            # The Sweet Spot: Peak metabolic efficiency
            return 1.0
        else:
            # Overburn: Slight penalty for excessive joint strain/fatigue
            return 0.8

    @staticmethod
    def _calculate_azm_signal(azm: int) -> float:
        """Calculates AZM Signal (0.0 - 1.0) targeting sustainable intensity."""
        if azm <= 40:
            # Recovery/Ramp-up (0.2 floor to 1.0)
            return round(0.2 + (0.02 * azm), 2)
        elif 40 < azm <= 90:
            # The Sweet Spot: Optimal intensity for weight loss
            return 1.0
        elif 90 < azm <= 120:
            # The Overburn: Efficiency drops as fatigue risk increases
            return round(1.0 - (0.0233 * (azm - 90)), 2)
        else:
            # The Redline: Hard floor to discourage the 120+ crash cycle
            return 0.3

    def calculate(self, day: FitbitDailySummary) -> ActivityScoreResult: # type: ignore
        steps = int(day.steps)
        azm = int(day.active_zone_minutes)
        print(f"Steps: {steps}, AZM: {azm}")
        # 1. Calculate the individual signals
        step_signal = self._calculate_steps_signal(steps)
        azm_signal = self._calculate_azm_signal(azm)
        print(f"Step Signal: {step_signal}, AZM Signal: {azm_signal}")

        points_factor = 5
        steps_score = step_signal * points_factor
        azm_score = azm_signal * points_factor
        print(f"Steps Score: {steps_score}, AZM Score: {azm_score}")

        # 2. Apply Weighted Blending (60% Steps / 40% AZM)
        # We multiply by 10 to fit your original 1-10 scoring scale
        raw_total = (steps_score * 0.6 + azm_score * 0.4)
        print(f"Raw Total: {raw_total}")
        
        # Ensure we return a clean float between 0 and 10
        final_score = round(max(0.0, min(10, raw_total)), 2)
        print(f"Final Score: {final_score}")


        # Breakdown remains for your reporting
        breakdown = ActivityScoreBreakdown(
            version=self._getVersion(),
            steps_points=steps_score,
            azm_points=azm_score,
            raw_total=raw_total,
            capped_total=final_score
        )

        return ActivityScoreResult(
            date=day.date,
            score=final_score,
            breakdown=breakdown,
            steps=steps,
            active_zone_minutes=azm
        )

@dataclass(frozen=True)
class ActivityScoreCalculatorV1:
    """Daily Activity Score Calculator V1"""
    version: str = "1.0.0"
    @staticmethod
    def _getVersion() -> str:
        return "1.0.0"

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
            version=self._getVersion(),
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

