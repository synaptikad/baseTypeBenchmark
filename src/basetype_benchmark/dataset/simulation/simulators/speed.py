"""
Speed Simulator (Fans, Pumps).

Simulates variable speed drives with:
- Demand-based speed control
- Modulation around setpoint
- Min/max speed limits
"""
from __future__ import annotations

import math
import random
from datetime import datetime

from ..point_simulator import PointSimulator, PointConfig, SimulationState
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext
from ..ou_process import BoundedOUProcess, calculate_theta_from_time_constant


class SpeedSimulator(PointSimulator):
    """
    Simulates VFD-controlled equipment speed (fans, pumps).

    Speed varies with demand and includes modulation from
    control system hunting.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.min_speed = params.get("min_speed", 20)  # % or Hz
        self.max_speed = params.get("max_speed", 100)
        self.response_time_seconds = params.get("response_time_seconds", 15)
        self.modulation_amplitude = params.get("modulation_amplitude", 3.0)
        self.modulation_period = params.get("modulation_period_seconds", 60)
        self.noise_std = params.get("noise_std", 1.0)

        self._ou_processes: dict[str, BoundedOUProcess] = {}
        self._phase_offsets: dict[str, float] = {}

    def _get_ou_process(self, state: SimulationState) -> BoundedOUProcess:
        """Get or create OU process for a point."""
        if state.point_id not in self._ou_processes:
            theta = calculate_theta_from_time_constant(self.response_time_seconds)
            self._ou_processes[state.point_id] = BoundedOUProcess(
                mean=self.min_speed,
                theta=theta,
                sigma=self.noise_std,
                current=state.current_value,
                min_value=0,
                max_value=self.max_speed,
                rng=self.rng,
            )
        return self._ou_processes[state.point_id]

    def _get_phase_offset(self, point_id: str) -> float:
        """Get random phase offset for modulation."""
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
        Compute next speed value.

        Speed scales with occupancy demand.
        """
        ou = self._get_ou_process(state)

        if not occupancy.is_occupied:
            # Standby speed or off
            target = self.min_speed * 0.5
        else:
            # Speed scales with occupancy
            demand_range = self.max_speed - self.min_speed
            target = self.min_speed + demand_range * occupancy.occupancy_level

        # Add modulation
        phase = self._get_phase_offset(state.point_id)
        time_seconds = timestamp.timestamp()
        modulation = self.modulation_amplitude * math.sin(
            2 * math.pi * time_seconds / self.modulation_period + phase
        )

        ou.set_mean(target + modulation)
        value = ou.step(dt)

        # Clamp and handle off state
        if value < self.min_speed * 0.3:
            return 0  # VFD off
        return max(self.min_speed, min(self.max_speed, value))


class FanSpeedSimulator(SpeedSimulator):
    """Supply/Return fan speed simulator."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("min_speed", 25)
        config.params.setdefault("max_speed", 60)  # Hz
        super().__init__(config, rng)


class PumpSpeedSimulator(SpeedSimulator):
    """Pump speed simulator - typically slower response."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("min_speed", 30)
        config.params.setdefault("max_speed", 100)
        config.params.setdefault("response_time_seconds", 30)
        super().__init__(config, rng)
