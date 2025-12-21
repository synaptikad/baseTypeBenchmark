"""
Power Simulator.

Simulates electrical power sensors with:
- Base load (standby consumption)
- Occupancy-driven load
- Daily/seasonal patterns
"""
from __future__ import annotations

import math
import random
from datetime import datetime

from ..point_simulator import PointSimulator, PointConfig, SimulationState
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext
from ..ou_process import BoundedOUProcess, calculate_theta_from_time_constant


class PowerSimulator(PointSimulator):
    """
    Simulates electrical power sensors (kW).

    Power consumption varies with:
    - Base load (always-on equipment)
    - Occupancy (lighting, plug loads, HVAC)
    - Environmental conditions (HVAC load)
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.nominal_power = params.get("nominal_power", 10.0)  # kW
        self.base_load_ratio = params.get("base_load_ratio", 0.2)
        self.occupancy_load_ratio = params.get("occupancy_load_ratio", 0.6)
        self.hvac_load_ratio = params.get("hvac_load_ratio", 0.2)
        self.response_time_seconds = params.get("response_time_seconds", 30)
        self.noise_ratio = params.get("noise_ratio", 0.05)

        self._ou_processes: dict[str, BoundedOUProcess] = {}

    def _get_ou_process(self, state: SimulationState) -> BoundedOUProcess:
        """Get or create OU process for a point."""
        if state.point_id not in self._ou_processes:
            theta = calculate_theta_from_time_constant(self.response_time_seconds)
            base_load = self.nominal_power * self.base_load_ratio
            self._ou_processes[state.point_id] = BoundedOUProcess(
                mean=base_load,
                theta=theta,
                sigma=self.nominal_power * self.noise_ratio,
                current=state.current_value,
                min_value=0,
                max_value=self.nominal_power * 1.2,
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
        Compute next power value.

        Power = base + occupancy_load + hvac_load
        """
        ou = self._get_ou_process(state)

        # Base load (always on)
        base = self.nominal_power * self.base_load_ratio

        # Occupancy load (lighting, equipment)
        occ_load = self.nominal_power * self.occupancy_load_ratio * occupancy.occupancy_level

        # HVAC load (heating/cooling based on outdoor temp)
        # Higher in extreme temps
        temp_deviation = abs(environment.outdoor_temp - 20)  # 20°C is neutral
        hvac_factor = min(1.0, temp_deviation / 15)
        hvac_load = self.nominal_power * self.hvac_load_ratio * hvac_factor * occupancy.occupancy_level

        target = base + occ_load + hvac_load
        ou.set_mean(target)

        return max(0, ou.step(dt))


class LightingPowerSimulator(PowerSimulator):
    """Lighting power - strongly correlated with occupancy and daylight."""

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """
        Lighting power based on occupancy and daylight.
        """
        ou = self._get_ou_process(state)

        # Base load (emergency lighting, etc.)
        base = self.nominal_power * 0.05

        if occupancy.is_occupied:
            # Daylight factor - less artificial light when sunny
            daylight_factor = 1.0 - 0.5 * environment.solar_intensity
            occ_load = self.nominal_power * 0.95 * occupancy.occupancy_level * daylight_factor
        else:
            occ_load = 0

        target = base + occ_load
        ou.set_mean(target)

        return max(0, ou.step(dt))


class HVACPowerSimulator(PowerSimulator):
    """HVAC power - strongly correlated with outdoor temperature."""

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """
        HVAC power based on heating/cooling demand.
        """
        ou = self._get_ou_process(state)

        # Standby power (controls, pumps)
        base = self.nominal_power * 0.1

        if not occupancy.is_occupied:
            # Minimal HVAC when unoccupied
            target = base * 2
        else:
            # HVAC load based on outdoor conditions
            neutral_temp = 18  # Outdoor temp where no heating/cooling needed

            if environment.outdoor_temp < neutral_temp:
                # Heating mode
                deviation = neutral_temp - environment.outdoor_temp
                load_factor = min(1.0, deviation / 15)
            else:
                # Cooling mode
                deviation = environment.outdoor_temp - neutral_temp
                load_factor = min(1.0, deviation / 12)

            hvac_load = self.nominal_power * 0.9 * load_factor * occupancy.occupancy_level
            target = base + hvac_load

        ou.set_mean(target)
        return max(0, ou.step(dt))
