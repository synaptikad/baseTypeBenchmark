"""
Meter Simulator (Energy, Water, Gas).

Simulates cumulative meters with:
- Monotonically increasing values
- Fixed sampling interval (no deadband)
- Rate based on demand
"""
from __future__ import annotations

import random
from datetime import datetime

from ..point_simulator import PointSimulator, PointConfig, SimulationState, SimulationSample
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext


class MeterSimulator(PointSimulator):
    """
    Simulates cumulative energy/water/gas meters.

    Meters are special:
    - Values only increase (or stay same)
    - Fixed sampling interval (typically 15 min)
    - No deadband filtering (all samples transmitted)
    - Value represents cumulative consumption
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.base_rate = params.get("base_rate", 1.0)  # Units per hour
        self.max_rate = params.get("max_rate", 10.0)  # Units per hour at full load
        self.interval = params.get("interval", 900)  # Fixed 15-minute interval

        # Meter-specific: track last sample time for fixed interval
        self._last_sample_times: dict[str, datetime] = {}

    def init_state(
        self,
        point_id: str,
        initial_value: float | None = None,
        setpoint: float | None = None,
    ) -> SimulationState:
        """Initialize meter state with realistic starting value."""
        if initial_value is None:
            # Start with random accumulated value (simulating meter history)
            initial_value = self.rng.uniform(10000, 100000)

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
        Compute meter increment.

        Consumption rate varies with occupancy and conditions.
        """
        # Calculate consumption rate (units per hour)
        if occupancy.is_occupied:
            rate = self.base_rate + (self.max_rate - self.base_rate) * occupancy.occupancy_level
        else:
            rate = self.base_rate * 0.3  # Standby consumption

        # Add some randomness
        rate *= 1 + self.rng.gauss(0, 0.1)

        # Convert to increment for this time step
        hours = dt / 3600
        increment = rate * hours

        return state.current_value + max(0, increment)

    def simulate(
        self,
        state: SimulationState,
        timestamp: datetime,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> SimulationSample | None:
        """
        Run simulation step for meter.

        Meters use fixed interval sampling, not deadband.
        """
        # Check if enough time has passed for next sample
        last_time = self._last_sample_times.get(state.point_id)
        if last_time is not None:
            elapsed = (timestamp - last_time).total_seconds()
            if elapsed < self.interval:
                return None  # Not time for next sample yet

        # Calculate time delta
        if state.last_step_time is None:
            dt = self.interval
        else:
            dt = (timestamp - state.last_step_time).total_seconds()

        if dt <= 0:
            return None

        # Compute new value
        new_value = self.step(state, timestamp, dt, occupancy, environment)
        state.current_value = new_value
        state.last_step_time = timestamp

        # Record sample time and emit
        self._last_sample_times[state.point_id] = timestamp
        state.record_transmission(new_value, timestamp)

        return SimulationSample(
            point_id=state.point_id,
            timestamp=timestamp,
            value=new_value,
        )


class EnergyMeterSimulator(MeterSimulator):
    """Electrical energy meter (kWh)."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("base_rate", 5.0)  # kWh base consumption
        config.params.setdefault("max_rate", 50.0)  # kWh at peak
        super().__init__(config, rng)


class WaterMeterSimulator(MeterSimulator):
    """Water meter (m³ or gallons)."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("base_rate", 0.5)  # m³/h base
        config.params.setdefault("max_rate", 5.0)  # m³/h at peak
        super().__init__(config, rng)


class GasMeterSimulator(MeterSimulator):
    """Gas meter (m³ or therms)."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("base_rate", 1.0)
        config.params.setdefault("max_rate", 20.0)
        super().__init__(config, rng)

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """
        Gas consumption - strongly seasonal for heating.
        """
        # Base rate (cooking, hot water)
        base = self.base_rate * 0.3

        # Heating component (seasonal)
        if environment.outdoor_temp < 16:
            heating_factor = min(1.0, (16 - environment.outdoor_temp) / 20)
            heating_rate = (self.max_rate - self.base_rate) * heating_factor
        else:
            heating_rate = 0

        rate = base + heating_rate
        if occupancy.is_occupied:
            rate *= 1.2  # Slightly higher when occupied

        rate *= 1 + self.rng.gauss(0, 0.1)

        hours = dt / 3600
        increment = rate * hours

        return state.current_value + max(0, increment)
