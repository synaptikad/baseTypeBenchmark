"""
Simulation module for realistic timeseries generation.

This module provides physical simulation of building automation points with:
- Ornstein-Uhlenbeck processes for temporal correlation
- Deadband filtering for realistic data reduction
- Occupancy and environmental context
- Type-specific simulators for different point categories
"""
from .engine import SimulationEngine, SimulationConfig, PointInfo
from .occupancy import OccupancyModel, OccupancyContext
from .environment import EnvironmentModel, EnvironmentContext, ClimatePreset
from .point_simulator import PointSimulator, PointConfig, SimulationState, SimulationSample
from .ou_process import OUProcess, BoundedOUProcess

__all__ = [
    # Engine
    "SimulationEngine",
    "SimulationConfig",
    "PointInfo",
    # Context models
    "OccupancyModel",
    "OccupancyContext",
    "EnvironmentModel",
    "EnvironmentContext",
    "ClimatePreset",
    # Base classes
    "PointSimulator",
    "PointConfig",
    "SimulationState",
    "SimulationSample",
    # Processes
    "OUProcess",
    "BoundedOUProcess",
]
