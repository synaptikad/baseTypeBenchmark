"""
Temperature Simulator.

Simulates temperature sensors with:
- Thermal inertia (OU process with lag)
- Occupancy influence (heat load from people)
- Outdoor temperature influence
- Day/night setpoint switching
"""
from __future__ import annotations

import random
from datetime import datetime

from ..point_simulator import PointSimulator, PointConfig, SimulationState
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext
from ..ou_process import BoundedOUProcess, calculate_theta_from_lag_minutes


class TemperatureSimulator(PointSimulator):
    """
    Simulates temperature sensors with realistic thermal behavior.

    Uses Ornstein-Uhlenbeck process for mean-reverting behavior with
    thermal inertia. The setpoint varies based on occupancy and the
    actual temperature lags behind due to building thermal mass.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        # Extract parameters from config
        params = config.params
        self.thermal_lag_minutes = params.get("thermal_lag_minutes", 10)
        self.noise_std = params.get("noise_std", 0.1)
        self.occupancy_influence = params.get("occupancy_influence", 2.0)
        self.setpoint_day = params.get("setpoint_day", 21.0)
        self.setpoint_night = params.get("setpoint_night", 18.0)
        self.outdoor_influence = params.get("outdoor_influence", 0.1)

        # OU processes per point (lazy init)
        self._ou_processes: dict[str, BoundedOUProcess] = {}

    def _get_ou_process(self, state: SimulationState) -> BoundedOUProcess:
        """Get or create OU process for a point."""
        if state.point_id not in self._ou_processes:
            theta = calculate_theta_from_lag_minutes(self.thermal_lag_minutes)
            self._ou_processes[state.point_id] = BoundedOUProcess(
                mean=state.setpoint or self.setpoint_day,
                theta=theta,
                sigma=self.noise_std,
                current=state.current_value,
                min_value=state.min_value if state.min_value != float('-inf') else -10,
                max_value=state.max_value if state.max_value != float('inf') else 50,
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
        Compute next temperature value.

        The temperature evolves towards a dynamic setpoint influenced by:
        - Base setpoint (day/night depending on occupancy)
        - Occupancy heat load
        - Outdoor temperature (slight influence through envelope)
        """
        ou = self._get_ou_process(state)

        # Calculate effective setpoint
        if occupancy.is_occupied:
            base_setpoint = self.setpoint_day
            # Add heat load from occupants
            heat_load = self.occupancy_influence * occupancy.occupancy_level
        else:
            base_setpoint = self.setpoint_night
            heat_load = 0.0

        # Outdoor influence (building envelope heat transfer)
        outdoor_delta = environment.outdoor_temp - base_setpoint
        outdoor_effect = self.outdoor_influence * outdoor_delta

        # Update OU process target
        effective_setpoint = base_setpoint + heat_load + outdoor_effect
        ou.set_mean(effective_setpoint)

        # Step the OU process
        return ou.step(dt)


class SupplyAirTempSimulator(TemperatureSimulator):
    """
    Specialized simulator for supply/discharge air temperature.

    Tighter control, faster response, less outdoor influence.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        # Override defaults for supply air
        config.params.setdefault("thermal_lag_minutes", 3)
        config.params.setdefault("noise_std", 0.05)
        config.params.setdefault("outdoor_influence", 0.02)
        super().__init__(config, rng)


class OutdoorTempSimulator(PointSimulator):
    """
    Simulator for outdoor temperature sensors.

    Simply returns the environment outdoor temperature with sensor noise.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)
        self.noise_std = config.params.get("noise_std", 0.2)

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """Return outdoor temperature with sensor noise."""
        return environment.outdoor_temp + self.rng.gauss(0, self.noise_std)
