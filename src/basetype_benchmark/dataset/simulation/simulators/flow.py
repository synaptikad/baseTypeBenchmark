"""
Flow Simulator.

Simulates flow sensors (air, water) with:
- Correlation with speed/position
- Demand-based variation
- Measurement noise
"""
from __future__ import annotations

import random
from datetime import datetime

from ..point_simulator import PointSimulator, PointConfig, SimulationState
from ..occupancy import OccupancyContext
from ..environment import EnvironmentContext
from ..ou_process import BoundedOUProcess, calculate_theta_from_time_constant


class FlowSimulator(PointSimulator):
    """
    Simulates flow sensors (CFM, GPM, m³/h).

    Flow varies with system demand and correlates with
    fan/pump speed and valve/damper position.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        super().__init__(config, rng)

        params = config.params
        self.design_flow = params.get("design_flow", 1000)  # Design flow rate
        self.min_flow_ratio = params.get("min_flow_ratio", 0.3)  # Min as ratio of design
        self.response_time_seconds = params.get("response_time_seconds", 30)
        self.noise_std = params.get("noise_std", 0.02)  # As ratio of current flow

        self._ou_processes: dict[str, BoundedOUProcess] = {}

    def _get_ou_process(self, state: SimulationState) -> BoundedOUProcess:
        """Get or create OU process for a point."""
        if state.point_id not in self._ou_processes:
            theta = calculate_theta_from_time_constant(self.response_time_seconds)
            min_flow = self.design_flow * self.min_flow_ratio
            self._ou_processes[state.point_id] = BoundedOUProcess(
                mean=min_flow,
                theta=theta,
                sigma=self.design_flow * self.noise_std,
                current=state.current_value,
                min_value=0,
                max_value=self.design_flow * 1.1,  # Allow slight over-design
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
        Compute next flow value.

        Flow scales with occupancy demand.
        """
        ou = self._get_ou_process(state)

        min_flow = self.design_flow * self.min_flow_ratio

        if not occupancy.is_occupied:
            target = min_flow * 0.5
        else:
            # Flow scales with occupancy
            flow_range = self.design_flow - min_flow
            target = min_flow + flow_range * occupancy.occupancy_level

        ou.set_mean(target)
        value = ou.step(dt)

        return max(0, value)


class AirflowSimulator(FlowSimulator):
    """Supply/Return airflow simulator."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("design_flow", 5000)  # m³/h typical AHU
        config.params.setdefault("min_flow_ratio", 0.3)
        super().__init__(config, rng)


class WaterFlowSimulator(FlowSimulator):
    """Chilled/Hot water flow simulator."""

    def __init__(self, config: PointConfig, rng: random.Random = None):
        config.params.setdefault("design_flow", 100)  # L/min or GPM
        config.params.setdefault("min_flow_ratio", 0.1)
        config.params.setdefault("response_time_seconds", 60)
        super().__init__(config, rng)
