"""
Status Simulator (Binary/Enum states).

Simulates status/state points with:
- State machine behavior
- Minimum state duration
- Transition probability based on context
"""
from __future__ import annotations

import random
from datetime import datetime

from ..point_simulator import PointSimulator, PointConfig, SimulationState, SimulationSample
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext


class StatusSimulator(PointSimulator):
    """
    Simulates binary or enum status points.

    Status points change state based on:
    - Occupancy (equipment runs when occupied)
    - Time (minimum duration between changes)
    - Random transitions
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.min_state_duration = params.get("min_state_duration", 300)  # 5 min min
        self.on_probability_occupied = params.get("on_probability_occupied", 0.95)
        self.on_probability_unoccupied = params.get("on_probability_unoccupied", 0.1)
        # Do not override PointSimulator.states (dict[str, SimulationState]).
        # Keep the allowed discrete values in a dedicated attribute.
        self.state_values = params.get("states", [0, 1])  # Binary by default

        self._last_change_times: dict[str, datetime] = {}

    def init_state(
        self,
        point_id: str,
        initial_value: float | None = None,
        setpoint: float | None = None,
    ) -> SimulationState:
        """Initialize with a valid state value."""
        if initial_value is None:
            initial_value = self.rng.choice(self.state_values)
        return super().init_state(point_id, initial_value, setpoint)

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """
        Determine current state.

        State changes based on occupancy and random factors.
        """
        # Check minimum duration since last change
        last_change = self._last_change_times.get(state.point_id)
        if last_change is not None:
            elapsed = (timestamp - last_change).total_seconds()
            if elapsed < self.min_state_duration:
                return state.current_value  # Too soon to change

        current = int(state.current_value)

        # Binary status logic
        if len(self.state_values) == 2:
            if occupancy.is_occupied:
                target_prob = self.on_probability_occupied
            else:
                target_prob = self.on_probability_unoccupied

            # Should equipment be on?
            should_be_on = self.rng.random() < target_prob

            if should_be_on and current == 0:
                # Turn on
                self._last_change_times[state.point_id] = timestamp
                return 1
            elif not should_be_on and current == 1:
                # Turn off
                self._last_change_times[state.point_id] = timestamp
                return 0

        return state.current_value

    def simulate(
        self,
        state: SimulationState,
        timestamp: datetime,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> SimulationSample | None:
        """
        Run simulation step.

        Status points only emit on state change.
        """
        if state.last_step_time is None:
            dt = 60
        else:
            dt = (timestamp - state.last_step_time).total_seconds()

        if dt <= 0:
            return None

        new_value = self.step(state, timestamp, dt, occupancy, environment)

        # Update step time
        state.last_step_time = timestamp

        # Only emit if state changed
        if state.last_transmitted_value is None or new_value != state.last_transmitted_value:
            state.current_value = new_value
            state.record_transmission(new_value, timestamp)
            return SimulationSample(
                point_id=state.point_id,
                timestamp=timestamp,
                value=new_value,
            )

        return None


class FanStatusSimulator(StatusSimulator):
    """Fan run status - on when occupied, off when not."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("on_probability_occupied", 0.99)
        config.params.setdefault("on_probability_unoccupied", 0.05)
        config.params.setdefault("min_state_duration", 600)  # 10 min
        super().__init__(config, rng)


class OccupancyModeSimulator(PointSimulator):
    """
    Occupancy mode enum (occupied/unoccupied/standby/bypass).

    Follows the occupancy model directly.
    """

    # Mode values
    UNOCCUPIED = 0
    STANDBY = 1
    OCCUPIED = 2
    BYPASS = 3

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)
        self._last_mode: dict[str, int] = {}

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """Determine occupancy mode from context."""
        if occupancy.occupancy_level > 0.5:
            return self.OCCUPIED
        elif occupancy.occupancy_level > 0.1:
            return self.STANDBY
        else:
            return self.UNOCCUPIED

    def simulate(
        self,
        state: SimulationState,
        timestamp: datetime,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> SimulationSample | None:
        """Emit on mode change."""
        new_mode = self.step(state, timestamp, 0, occupancy, environment)
        state.last_step_time = timestamp

        last_mode = self._last_mode.get(state.point_id)
        if last_mode is None or new_mode != last_mode:
            self._last_mode[state.point_id] = int(new_mode)
            state.current_value = new_mode
            state.record_transmission(new_mode, timestamp)
            return SimulationSample(
                point_id=state.point_id,
                timestamp=timestamp,
                value=new_mode,
            )

        return None
