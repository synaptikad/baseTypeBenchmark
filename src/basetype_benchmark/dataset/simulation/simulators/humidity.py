"""
Humidity Simulator.

Simulates humidity sensors with:
- Slow response time (moisture equilibrium)
- Occupancy influence (people add moisture)
- Outdoor humidity influence
- Inverse relationship with temperature
"""
from __future__ import annotations

import random
from datetime import datetime

from ..point_simulator import PointSimulator, PointConfig, SimulationState
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext
from ..ou_process import BoundedOUProcess, calculate_theta_from_lag_minutes


class HumiditySimulator(PointSimulator):
    """
    Simulates humidity sensors with realistic behavior.

    Humidity changes slowly and is influenced by:
    - Occupancy (people add moisture through respiration)
    - Outdoor humidity (infiltration)
    - HVAC dehumidification/humidification
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.response_time_minutes = params.get("response_time_minutes", 20)
        self.noise_std = params.get("noise_std", 1.0)
        self.target_rh = params.get("target_rh", 45.0)
        self.occupancy_moisture = params.get("occupancy_moisture", 5.0)  # %RH increase per full occupancy
        self.outdoor_influence = params.get("outdoor_influence", 0.15)

        self._ou_processes: dict[str, BoundedOUProcess] = {}

    def _get_ou_process(self, state: SimulationState) -> BoundedOUProcess:
        """Get or create OU process for a point."""
        if state.point_id not in self._ou_processes:
            theta = calculate_theta_from_lag_minutes(self.response_time_minutes)
            self._ou_processes[state.point_id] = BoundedOUProcess(
                mean=self.target_rh,
                theta=theta,
                sigma=self.noise_std,
                current=state.current_value,
                min_value=0,
                max_value=100,
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
        Compute next humidity value.

        The humidity evolves towards a target influenced by:
        - HVAC control target
        - Occupancy moisture load
        - Outdoor humidity infiltration
        """
        ou = self._get_ou_process(state)

        # Base target from HVAC control
        base_target = self.target_rh

        # Occupancy moisture load
        moisture_load = self.occupancy_moisture * occupancy.occupancy_level

        # Outdoor influence
        outdoor_delta = environment.outdoor_humidity - base_target
        outdoor_effect = self.outdoor_influence * outdoor_delta

        # Update target
        effective_target = base_target + moisture_load + outdoor_effect
        effective_target = max(0, min(100, effective_target))
        ou.set_mean(effective_target)

        return ou.step(dt)


class OutdoorHumiditySimulator(PointSimulator):
    """
    Simulator for outdoor humidity sensors.

    Returns environment outdoor humidity with sensor noise.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)
        self.noise_std = config.params.get("noise_std", 2.0)

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """Return outdoor humidity with sensor noise."""
        value = environment.outdoor_humidity + self.rng.gauss(0, self.noise_std)
        return max(0, min(100, value))
