"""
CO2 / Air Quality Simulator.

Simulates CO2 concentration with:
- Occupancy-driven accumulation
- Ventilation-driven decay
- Baseline outdoor level
"""
from __future__ import annotations

import random
from datetime import datetime

from ..point_simulator import PointSimulator, PointConfig, SimulationState
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext
from ..ou_process import BoundedOUProcess, calculate_theta_from_lag_minutes


class CO2Simulator(PointSimulator):
    """
    Simulates CO2 concentration sensors.

    CO2 builds up with occupancy (people exhale CO2) and
    decays with ventilation. The rate of buildup depends on
    number of occupants and ventilation rate.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.baseline = params.get("baseline", 400)  # ppm outdoor
        self.response_time_minutes = params.get("response_time_minutes", 5)
        self.max_co2 = params.get("max_co2", 1500)  # ppm typical max
        self.occupancy_rate = params.get("occupancy_rate", 30)  # ppm per person-minute equivalent
        self.ventilation_decay = params.get("ventilation_decay", 0.1)  # Decay rate when unoccupied
        self.noise_std = params.get("noise_std", 10)

        self._ou_processes: dict[str, BoundedOUProcess] = {}

    def _get_ou_process(self, state: SimulationState) -> BoundedOUProcess:
        """Get or create OU process for a point."""
        if state.point_id not in self._ou_processes:
            theta = calculate_theta_from_lag_minutes(self.response_time_minutes)
            self._ou_processes[state.point_id] = BoundedOUProcess(
                mean=self.baseline,
                theta=theta,
                sigma=self.noise_std,
                current=state.current_value,
                min_value=self.baseline * 0.9,  # Can't go below outdoor
                max_value=5000,  # Physical max
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
        Compute next CO2 value.

        CO2 builds with occupancy and decays with ventilation.
        """
        ou = self._get_ou_process(state)

        # Target CO2 level based on occupancy
        if occupancy.is_occupied:
            # CO2 builds up with occupancy
            occupancy_contribution = self.occupancy_rate * occupancy.occupancy_level * 10
            target = min(self.max_co2, self.baseline + occupancy_contribution)
        else:
            # Decay to baseline
            target = self.baseline

        ou.set_mean(target)
        return ou.step(dt)


class VOCSensor(PointSimulator):
    """
    Simulates VOC (Volatile Organic Compound) sensor.

    Similar behavior to CO2 but with different baseline and sensitivity.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.baseline = params.get("baseline", 100)  # ppb or µg/m³
        self.response_time_minutes = params.get("response_time_minutes", 10)
        self.noise_std = params.get("noise_std", 20)

        self._ou_processes: dict[str, BoundedOUProcess] = {}

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """Compute next VOC value."""
        if state.point_id not in self._ou_processes:
            from ..ou_process import calculate_theta_from_lag_minutes
            theta = calculate_theta_from_lag_minutes(self.response_time_minutes)
            self._ou_processes[state.point_id] = BoundedOUProcess(
                mean=self.baseline,
                theta=theta,
                sigma=self.noise_std,
                current=state.current_value,
                min_value=0,
                max_value=2000,
                rng=self.rng,
            )

        ou = self._ou_processes[state.point_id]

        # VOC increases with occupancy (off-gassing, cleaning products, etc.)
        if occupancy.is_occupied:
            target = self.baseline * (1 + 2 * occupancy.occupancy_level)
        else:
            target = self.baseline

        ou.set_mean(target)
        return ou.step(dt)
