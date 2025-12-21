"""
Occupancy Model for building simulation.

Generates realistic occupancy patterns:
- Weekday vs weekend schedules
- Transition ramps (arrival/departure)
- Random variations
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Any


@dataclass
class OccupancyContext:
    """Occupancy state at a given moment."""
    is_occupied: bool
    occupancy_level: float  # 0.0 to 1.0 (smooth transition)
    people_density: float  # Normalized 0-1, for load calculations

    @property
    def in_transition(self) -> bool:
        """True if in arrival/departure transition (not fully occupied or unoccupied)."""
        return 0.0 < self.occupancy_level < 1.0


@dataclass
class DaySchedule:
    """Schedule for a single type of day."""
    is_occupied: bool = True
    occupied_start: time = field(default_factory=lambda: time(8, 0))
    occupied_end: time = field(default_factory=lambda: time(19, 0))
    transition_minutes: int = 30  # Ramp-up/down duration
    peak_density: float = 1.0  # Max occupancy level for this day type

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DaySchedule":
        """Create from config dict."""
        if not data.get("is_occupied", True):
            return cls(is_occupied=False)

        start_str = data.get("occupied_start", "08:00")
        end_str = data.get("occupied_end", "19:00")

        start_parts = [int(x) for x in start_str.split(":")]
        end_parts = [int(x) for x in end_str.split(":")]

        return cls(
            is_occupied=True,
            occupied_start=time(start_parts[0], start_parts[1]),
            occupied_end=time(end_parts[0], end_parts[1]),
            transition_minutes=data.get("transition_minutes", 30),
            peak_density=data.get("peak_density", 1.0),
        )


@dataclass
class OccupancyModel:
    """
    Generates occupancy patterns for building simulation.

    Handles:
    - Weekday/weekend schedules
    - Smooth transitions (ramp up/down)
    - Random variations in arrival/departure times
    """

    schedules: dict[int, DaySchedule] = field(default_factory=dict)
    variation_minutes: int = 15  # Random variation in start/end times
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self):
        # Default schedules if not provided
        if not self.schedules:
            self.schedules = {
                0: DaySchedule(),  # Monday
                1: DaySchedule(),  # Tuesday
                2: DaySchedule(),  # Wednesday
                3: DaySchedule(),  # Thursday
                4: DaySchedule(),  # Friday
                5: DaySchedule(  # Saturday - reduced hours
                    occupied_start=time(9, 0),
                    occupied_end=time(13, 0),
                    peak_density=0.3,
                ),
                6: DaySchedule(is_occupied=False),  # Sunday
            }

    @classmethod
    def from_config(cls, config: dict[str, Any], rng: random.Random = None) -> "OccupancyModel":
        """Create from config dictionary."""
        schedules = {}

        # Map day names to weekday numbers
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
            "weekday": None,  # Special: applies to 0-4
        }

        for day_name, day_config in config.items():
            if day_name == "variation_minutes":
                continue

            day_num = day_map.get(day_name.lower())

            if day_name.lower() == "weekday":
                # Apply to all weekdays
                schedule = DaySchedule.from_dict(day_config)
                for d in range(5):
                    schedules[d] = schedule
            elif day_num is not None:
                schedules[day_num] = DaySchedule.from_dict(day_config)

        return cls(
            schedules=schedules,
            variation_minutes=config.get("variation_minutes", 15),
            rng=rng or random.Random(),
        )

    def get_occupancy(self, timestamp: datetime) -> OccupancyContext:
        """
        Get occupancy context for a specific timestamp.

        Args:
            timestamp: The moment to evaluate

        Returns:
            OccupancyContext with current state
        """
        weekday = timestamp.weekday()
        schedule = self.schedules.get(weekday)

        if schedule is None or not schedule.is_occupied:
            return OccupancyContext(
                is_occupied=False,
                occupancy_level=0.0,
                people_density=0.0,
            )

        current_time = timestamp.time()
        current_minutes = current_time.hour * 60 + current_time.minute

        start_minutes = schedule.occupied_start.hour * 60 + schedule.occupied_start.minute
        end_minutes = schedule.occupied_end.hour * 60 + schedule.occupied_end.minute
        transition = schedule.transition_minutes

        # Calculate occupancy level with smooth transitions
        if current_minutes < start_minutes - transition:
            # Before arrival transition
            level = 0.0
        elif current_minutes < start_minutes + transition:
            # Arrival transition (ramp up)
            progress = (current_minutes - (start_minutes - transition)) / (2 * transition)
            level = self._smooth_ramp(progress)
        elif current_minutes < end_minutes - transition:
            # Core occupied period
            level = 1.0
        elif current_minutes < end_minutes + transition:
            # Departure transition (ramp down)
            progress = (current_minutes - (end_minutes - transition)) / (2 * transition)
            level = 1.0 - self._smooth_ramp(progress)
        else:
            # After departure
            level = 0.0

        # Apply peak density scaling
        level *= schedule.peak_density

        return OccupancyContext(
            is_occupied=level > 0.1,  # Consider occupied if >10%
            occupancy_level=level,
            people_density=level,
        )

    def _smooth_ramp(self, t: float) -> float:
        """
        Smooth S-curve transition (eased in/out).

        Uses smoothstep function: 3t² - 2t³

        Args:
            t: Progress from 0 to 1

        Returns:
            Smoothed value from 0 to 1
        """
        t = max(0.0, min(1.0, t))
        return t * t * (3 - 2 * t)

    def is_occupied_at(self, timestamp: datetime) -> bool:
        """Quick check if building is occupied at timestamp."""
        return self.get_occupancy(timestamp).is_occupied

    def get_next_transition(self, timestamp: datetime) -> tuple[datetime, str]:
        """
        Find the next occupancy state change.

        Returns:
            Tuple of (next_transition_time, 'arrival' or 'departure')
        """
        for days_ahead in range(7):
            check_date = timestamp.date() + timedelta(days=days_ahead)
            weekday = check_date.weekday()
            schedule = self.schedules.get(weekday)

            if schedule is None or not schedule.is_occupied:
                continue

            if days_ahead == 0:
                # Same day - check if transitions are still ahead
                current_time = timestamp.time()

                arrival_time = datetime.combine(check_date, schedule.occupied_start)
                if current_time < schedule.occupied_start:
                    return arrival_time, "arrival"

                departure_time = datetime.combine(check_date, schedule.occupied_end)
                if current_time < schedule.occupied_end:
                    return departure_time, "departure"
            else:
                # Future day - return arrival time
                return datetime.combine(check_date, schedule.occupied_start), "arrival"

        # Fallback: 7 days from now
        return timestamp + timedelta(days=7), "arrival"
