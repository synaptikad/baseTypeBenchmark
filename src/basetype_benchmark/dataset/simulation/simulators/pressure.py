"""
Pressure Simulator.

Simulates pressure sensors with:
- Fast response time
- Correlation with fan speed / flow
- Occupancy-based demand
"""
from __future__ import annotations

import random
from datetime import datetime

from ..point_simulator import PointSimulator, PointConfig, SimulationState
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext
from ..ou_process import BoundedOUProcess, calculate_theta_from_time_constant


class PressureSimulator(PointSimulator):
    """
    Simulates pressure sensors (static, differential).

    Pressure responds quickly to system changes and correlates
    with occupancy-driven demand (VAV boxes open = lower pressure).
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.response_time_seconds = params.get("response_time_seconds", 10)
        self.noise_std = params.get("noise_std", 2.0)
        self.setpoint = params.get("setpoint", 250)  # Pa typical duct static pressure
        self.occupied_drop = params.get("occupied_drop", 30)  # Pa drop when VAVs open

        self._ou_processes: dict[str, BoundedOUProcess] = {}

    def _get_ou_process(self, state: SimulationState) -> BoundedOUProcess:
        """Get or create OU process for a point."""
        if state.point_id not in self._ou_processes:
            theta = calculate_theta_from_time_constant(self.response_time_seconds)
            self._ou_processes[state.point_id] = BoundedOUProcess(
                mean=self.setpoint,
                theta=theta,
                sigma=self.noise_std,
                current=state.current_value,
                min_value=state.min_value if state.min_value != float('-inf') else 0,
                max_value=state.max_value if state.max_value != float('inf') else 2500,
                rng=self.rng,
            )
        return self._ou_processes[state.point_id]

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """
        Compute next pressure value.

        Pressure drops when demand increases (VAV boxes open).
        """
        ou = self._get_ou_process(state)

        # Pressure drops with occupancy (more VAV demand)
        pressure_drop = self.occupied_drop * occupancy.occupancy_level
        target = self.setpoint - pressure_drop

        ou.set_mean(target)
        return ou.step(dt)


class FilterDifferentialPressureSimulator(PointSimulator):
    """
    Simulates filter differential pressure.

    Slowly increases over time (filter loading), resets on filter change.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.clean_dp = params.get("clean_dp", 50)  # Pa when filter is new
        self.dirty_dp = params.get("dirty_dp", 300)  # Pa when filter is dirty
        self.loading_rate = params.get("loading_rate", 0.5)  # Pa per day
        self.noise_std = params.get("noise_std", 3.0)

        self._base_dp: dict[str, float] = {}

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """
        Compute filter differential pressure.

        Slowly increases over time, faster when system is running (occupied).
        """
        if state.point_id not in self._base_dp:
            # Start with clean filter + some random initial loading
            self._base_dp[state.point_id] = self.clean_dp + self.rng.uniform(0, 50)

        # Loading rate per second (faster when occupied)
        loading_per_second = (self.loading_rate / 86400) * (0.2 + 0.8 * occupancy.occupancy_level)
        self._base_dp[state.point_id] += loading_per_second * dt

        # Cap at dirty filter level (simulating filter change)
        if self._base_dp[state.point_id] > self.dirty_dp:
            self._base_dp[state.point_id] = self.clean_dp + self.rng.uniform(0, 20)

        # Add noise
        return self._base_dp[state.point_id] + self.rng.gauss(0, self.noise_std)
