"""
Alarm Simulator.

Simulates alarm/fault points with:
- Event-driven behavior (not periodic)
- Configurable occurrence rate
- Alarm duration
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from ..point_simulator import PointSimulator, PointConfig, SimulationState, SimulationSample
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext


class AlarmSimulator(PointSimulator):
    """
    Simulates alarm/fault points.

    Alarms are event-driven:
    - Random occurrence based on configured rate
    - Duration before auto-clear
    - More likely during operation (occupancy)
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.events_per_day = params.get("events_per_day", 0.5)
        self.duration_minutes = params.get("duration_minutes", 30)
        self.occupied_multiplier = params.get("occupied_multiplier", 3.0)

        self._alarm_end_times: dict[str, datetime] = {}
        self._last_check_times: dict[str, datetime] = {}

    def init_state(
        self,
        point_id: str,
        initial_value: float | None = None,
        setpoint: float | None = None,
    ) -> SimulationState:
        """Initialize alarm in normal (0) state."""
        return super().init_state(point_id, 0, setpoint)

    def _should_trigger_alarm(
        self,
        dt: float,
        occupancy: OccupancyContext,
    ) -> bool:
        """Determine if an alarm should trigger in this interval."""
        # Base probability per second
        base_prob_per_second = self.events_per_day / 86400

        # Higher probability when equipment is running
        if occupancy.is_occupied:
            prob = base_prob_per_second * self.occupied_multiplier
        else:
            prob = base_prob_per_second * 0.2  # Lower when idle

        # Probability of at least one event in dt seconds
        prob_in_interval = 1 - (1 - prob) ** dt

        return self.rng.random() < prob_in_interval

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        # Alarm points are event-driven and are handled in simulate().
        # This method exists to satisfy the PointSimulator abstract interface.
        return state.current_value

    def simulate(
        self,
        state: SimulationState,
        timestamp: datetime,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> SimulationSample | None:
        """
        Run alarm simulation.

        Returns sample only on state change (alarm trigger or clear).
        """
        # Calculate dt
        last_check = self._last_check_times.get(state.point_id)
        if last_check is None:
            dt = 60
        else:
            dt = (timestamp - last_check).total_seconds()

        if dt <= 0:
            return None

        self._last_check_times[state.point_id] = timestamp
        state.last_step_time = timestamp

        current_value = int(state.current_value)

        # Check if active alarm should clear
        alarm_end = self._alarm_end_times.get(state.point_id)
        if alarm_end is not None and timestamp >= alarm_end:
            # Clear alarm
            del self._alarm_end_times[state.point_id]
            state.current_value = 0
            state.record_transmission(0, timestamp)
            return SimulationSample(
                point_id=state.point_id,
                timestamp=timestamp,
                value=0,
            )

        # Check if new alarm should trigger
        if current_value == 0 and self._should_trigger_alarm(dt, occupancy):
            # Trigger alarm
            duration = timedelta(minutes=self.duration_minutes * (0.5 + self.rng.random()))
            self._alarm_end_times[state.point_id] = timestamp + duration

            state.current_value = 1
            state.record_transmission(1, timestamp)
            return SimulationSample(
                point_id=state.point_id,
                timestamp=timestamp,
                value=1,
            )

        return None


class FilterAlarmSimulator(AlarmSimulator):
    """Filter dirty alarm - rare, long duration."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("events_per_day", 0.02)  # ~1 per month
        config.params.setdefault("duration_minutes", 1440)  # 24 hours
        config.params.setdefault("occupied_multiplier", 1.5)
        super().__init__(config, rng)


class FreezeAlarmSimulator(AlarmSimulator):
    """Freeze stat alarm - only in cold weather."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("events_per_day", 0.1)
        config.params.setdefault("duration_minutes", 60)
        super().__init__(config, rng)

    def _should_trigger_alarm(
        self,
        dt: float,
        occupancy: OccupancyContext,
    ) -> bool:
        """Only trigger when cold."""
        # This would need environment context - simplified version
        base_trigger = super()._should_trigger_alarm(dt, occupancy)
        return base_trigger and self.rng.random() < 0.1  # Reduced in absence of temp check


class SmokeAlarmSimulator(AlarmSimulator):
    """Smoke alarm - very rare, critical."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("events_per_day", 0.001)  # Very rare
        config.params.setdefault("duration_minutes", 5)  # Quick response
        config.params.setdefault("occupied_multiplier", 5.0)
        super().__init__(config, rng)
