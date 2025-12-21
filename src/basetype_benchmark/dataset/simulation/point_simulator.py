"""
Base class for point simulators.

Each point type (temperature, humidity, position, etc.) has its own
simulator that generates realistic values with:
- Physical behavior (inertia, response time)
- Deadband filtering
- Context awareness (occupancy, environment)
"""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator

from .occupancy import OccupancyContext
from .environment import EnvironmentContext


@dataclass
class SimulationState:
    """State of a single point simulation."""
    point_id: str
    current_value: float
    last_transmitted_value: float | None
    last_transmitted_time: datetime | None
    last_step_time: datetime | None

    # Point metadata
    setpoint: float | None = None
    min_value: float = float('-inf')
    max_value: float = float('inf')

    def should_transmit(self, new_value: float, deadband: float) -> bool:
        """Check if value should be transmitted based on deadband."""
        if self.last_transmitted_value is None:
            return True
        return abs(new_value - self.last_transmitted_value) > deadband

    def record_transmission(self, value: float, timestamp: datetime):
        """Record that a value was transmitted."""
        self.last_transmitted_value = value
        self.last_transmitted_time = timestamp


@dataclass
class PointConfig:
    """Configuration for a point simulator."""
    point_type: str
    deadband: float = 0.0
    sample_interval: float = 60.0  # Base sampling interval in seconds
    min_value: float = float('-inf')
    max_value: float = float('inf')
    setpoint: float | None = None

    # Additional type-specific config
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationSample:
    """A single sample from simulation (only emitted when deadband exceeded)."""
    point_id: str
    timestamp: datetime
    value: float


class PointSimulator(ABC):
    """
    Abstract base class for point simulators.

    Subclasses implement specific physical behaviors for different point types.
    """

    def __init__(self, config: PointConfig, rng: random.Random = None):
        self.config = config
        self.rng = rng or random.Random()
        self.states: dict[str, SimulationState] = {}

    @abstractmethod
    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        """
        Compute next value for the point.

        Args:
            state: Current simulation state
            timestamp: Current simulation time
            dt: Time delta since last step (seconds)
            occupancy: Current occupancy context
            environment: Current environmental context

        Returns:
            New value for the point
        """
        pass

    def init_state(
        self,
        point_id: str,
        initial_value: float | None = None,
        setpoint: float | None = None,
    ) -> SimulationState:
        """
        Initialize state for a new point.

        Args:
            point_id: Unique identifier for the point
            initial_value: Starting value (or None for default)
            setpoint: Target setpoint if applicable

        Returns:
            Initialized SimulationState
        """
        if initial_value is None:
            initial_value = self._default_initial_value(setpoint)

        state = SimulationState(
            point_id=point_id,
            current_value=initial_value,
            last_transmitted_value=None,
            last_transmitted_time=None,
            last_step_time=None,
            setpoint=setpoint,
            min_value=self.config.min_value,
            max_value=self.config.max_value,
        )
        self.states[point_id] = state
        return state

    def _default_initial_value(self, setpoint: float | None) -> float:
        """Get default initial value for this point type."""
        if setpoint is not None:
            return setpoint
        if self.config.min_value != float('-inf') and self.config.max_value != float('inf'):
            return (self.config.min_value + self.config.max_value) / 2
        return 0.0

    def simulate(
        self,
        state: SimulationState,
        timestamp: datetime,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> SimulationSample | None:
        """
        Run one simulation step and return sample if deadband exceeded.

        Args:
            state: Current simulation state
            timestamp: Current simulation time
            occupancy: Current occupancy context
            environment: Current environmental context

        Returns:
            SimulationSample if value should be transmitted, None otherwise
        """
        # Calculate time delta
        if state.last_step_time is None:
            dt = self.config.sample_interval
        else:
            dt = (timestamp - state.last_step_time).total_seconds()

        if dt <= 0:
            return None

        # Compute new value
        new_value = self.step(state, timestamp, dt, occupancy, environment)

        # Apply bounds
        new_value = max(state.min_value, min(state.max_value, new_value))
        state.current_value = new_value
        state.last_step_time = timestamp

        # Check deadband
        if state.should_transmit(new_value, self.config.deadband):
            state.record_transmission(new_value, timestamp)
            return SimulationSample(
                point_id=state.point_id,
                timestamp=timestamp,
                value=new_value,
            )

        return None

    def get_state(self, point_id: str) -> SimulationState | None:
        """Get current state for a point."""
        return self.states.get(point_id)


class NullSimulator(PointSimulator):
    """
    Fallback simulator that generates no samples.
    Used for unsupported point types.
    """

    def step(
        self,
        state: SimulationState,
        timestamp: datetime,
        dt: float,
        occupancy: OccupancyContext,
        environment: EnvironmentContext,
    ) -> float:
        return state.current_value
