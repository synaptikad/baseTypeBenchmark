"""
Position Simulator (Valves, Dampers).

Simulates modulating actuators with:
- PID control hunting/modulation behavior
- Occupancy-based demand
- Seasonal adjustments
"""
from __future__ import annotations

import math
import random
from datetime import datetime

from ..point_simulator import PointSimulator, PointConfig, SimulationState
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext


class PositionSimulator(PointSimulator):
    """
    Simulates valve/damper position actuators.

    Positions oscillate around a demand-based setpoint due to
    PID control hunting. The oscillation amplitude and frequency
    are configurable.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.modulation_period = params.get("modulation_period_seconds", 45)
        self.modulation_amplitude = params.get("modulation_amplitude", 5.0)
        self.response_time = params.get("response_time_seconds", 30)
        self.noise_std = params.get("noise_std", 1.0)

        # Track phase offset per point for varied behavior
        self._phase_offsets: dict[str, float] = {}

    def _get_phase_offset(self, point_id: str) -> float:
        """Get random phase offset for this point."""
        if point_id not in self._phase_offsets:
            self._phase_offsets[point_id] = self.rng.uniform(0, 2 * math.pi)
        return self._phase_offsets[point_id]

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """
        Compute next position value.

        Position is based on:
        - Demand (derived from occupancy and environment)
        - Sinusoidal modulation (PID hunting)
        - Random noise
        """
        # Calculate base demand position
        demand = self._calculate_demand(occupancy, environment)

        # Add PID hunting (sinusoidal oscillation around demand)
        phase = self._get_phase_offset(state.point_id)
        time_seconds = timestamp.timestamp()
        modulation = self.modulation_amplitude * math.sin(
            2 * math.pi * time_seconds / self.modulation_period + phase
        )

        # Reduce modulation at extreme positions (saturated)
        if demand < 10:
            modulation *= demand / 10
        elif demand > 90:
            modulation *= (100 - demand) / 10

        # Add noise
        noise = self.rng.gauss(0, self.noise_std)

        # Move towards target with response time
        target = demand + modulation + noise
        alpha = min(1.0, dt / self.response_time)
        new_value = state.current_value + alpha * (target - state.current_value)

        return max(0, min(100, new_value))

    def _calculate_demand(
        self,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """
        Calculate base demand position based on context.

        Override in subclasses for specific valve/damper types.
        """
        # Default: position scales with occupancy
        base = 20  # Minimum position
        occupied_addition = 60 * occupancy.occupancy_level
        return base + occupied_addition


class CoolingValveSimulator(PositionSimulator):
    """Cooling valve - higher position in summer and when occupied."""

    def _calculate_demand(
        self,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        # Cooling demand increases with outdoor temp and occupancy
        if environment.outdoor_temp < 18:
            return 0  # No cooling needed

        # Scale with temperature above 18°C
        temp_factor = min(1.0, (environment.outdoor_temp - 18) / 15)
        occupancy_factor = 0.3 + 0.7 * occupancy.occupancy_level

        return min(100, temp_factor * occupancy_factor * 100)


class HeatingValveSimulator(PositionSimulator):
    """Heating valve - higher position in winter and when occupied."""

    def _calculate_demand(
        self,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        # Heating demand increases as outdoor temp drops
        if environment.outdoor_temp > 16:
            return 0  # No heating needed

        # Scale with temperature below 16°C
        temp_factor = min(1.0, (16 - environment.outdoor_temp) / 20)
        occupancy_factor = 0.3 + 0.7 * occupancy.occupancy_level

        return min(100, temp_factor * occupancy_factor * 100)


class OutsideAirDamperSimulator(PositionSimulator):
    """Outside air damper - economizer behavior."""

    def _calculate_demand(
        self,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        if not occupancy.is_occupied:
            return 10  # Minimum outside air

        # Economizer: more outside air when outdoor temp is favorable
        if 12 < environment.outdoor_temp < 22:
            # Free cooling range - open wide
            return 80 + 20 * occupancy.occupancy_level
        else:
            # Minimum ventilation
            return 20 + 15 * occupancy.occupancy_level
