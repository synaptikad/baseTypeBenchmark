"""
Simulation Engine.

Orchestrates all point simulators to generate realistic timeseries data
with physical behavior and deadband filtering.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

import yaml

from .occupancy import OccupancyModel
from .environment import EnvironmentModel, ClimatePreset
from .point_simulator import PointSimulator, PointConfig, SimulationSample, NullSimulator
from .simulators import (
    TemperatureSimulator,
    HumiditySimulator,
    PositionSimulator,
    PowerSimulator,
    MeterSimulator,
    StatusSimulator,
    AlarmSimulator,
    PressureSimulator,
    CO2Simulator,
    SpeedSimulator,
    FlowSimulator,
)


@dataclass
class PointInfo:
    """Information about a point to simulate."""
    id: str
    name: str
    equipment_id: str | None = None
    equipment_type: str | None = None
    unit: str | None = None
    setpoint: float | None = None


@dataclass
class SimulationConfig:
    """Configuration for simulation engine."""
    point_behaviors: dict[str, dict[str, Any]] = field(default_factory=dict)
    occupancy: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    simulation: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> "SimulationConfig":
        """Load configuration from YAML file."""
        path = Path(path)
        if not path.exists():
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls(
            point_behaviors=data.get("point_behaviors", {}),
            occupancy=data.get("occupancy", {}),
            environment=data.get("environment", {}),
            simulation=data.get("simulation", {}),
        )

    @classmethod
    def default(cls) -> "SimulationConfig":
        """Create default configuration."""
        return cls(
            point_behaviors={
                "temperature": {"deadband": 0.5, "thermal_lag_minutes": 10},
                "humidity": {"deadband": 3.0, "response_time_minutes": 20},
                "pressure": {"deadband": 5.0, "response_time_seconds": 10},
                "co2": {"deadband": 50},
                "position": {"deadband": 2.0, "modulation_period_seconds": 45},
                "power": {"deadband_percent": 0.5},
                "energy": {"mode": "cumulative", "interval": 900},
                "status": {"mode": "state_machine", "min_state_duration": 300},
                "alarm": {"mode": "event", "events_per_day": 0.5},
                "speed": {"deadband": 1.0},
                "flow": {"deadband": 2.0},
            }
        )


class SimulationEngine:
    """
    Main simulation engine that generates realistic timeseries.

    Manages all point simulators and provides context (occupancy, environment)
    for physical simulation.
    """

    # Mapping of point type to simulator class
    SIMULATOR_CLASSES: dict[str, type[PointSimulator]] = {
        "temperature": TemperatureSimulator,
        "humidity": HumiditySimulator,
        "pressure": PressureSimulator,
        "co2": CO2Simulator,
        "position": PositionSimulator,
        "power": PowerSimulator,
        "energy": MeterSimulator,
        "meter": MeterSimulator,
        "status": StatusSimulator,
        "alarm": AlarmSimulator,
        "speed": SpeedSimulator,
        "flow": FlowSimulator,
    }

    def __init__(
        self,
        config: SimulationConfig | None = None,
        rng: random.Random | None = None,
        start_time: datetime | None = None,
    ):
        self.config = config or SimulationConfig.default()
        self.rng = rng or random.Random()
        self.start_time = start_time or datetime(2024, 1, 1, 0, 0, 0)

        # Initialize models
        self.occupancy = OccupancyModel.from_config(
            self.config.occupancy or {},
            rng=self.rng,
        )
        self.environment = self._init_environment()

        # Compiled type patterns for point classification
        self._type_patterns = self._compile_type_patterns()

        # Simulators by point type
        self._simulators: dict[str, PointSimulator] = {}

        # Point type cache
        self._point_types: dict[str, str] = {}

    def _init_environment(self) -> EnvironmentModel:
        """Initialize environment model from config."""
        env_config = self.config.environment or {}
        climate = env_config.get("climate", "temperate")

        if climate == "continental":
            model = ClimatePreset.continental()
        elif climate == "mediterranean":
            model = ClimatePreset.mediterranean()
        elif climate == "tropical":
            model = ClimatePreset.tropical()
        else:
            model = ClimatePreset.temperate()

        model.rng = self.rng
        return model

    def _compile_type_patterns(self) -> dict[str, list[re.Pattern]]:
        """Compile regex patterns for point type detection."""
        patterns = {}
        sim_config = self.config.simulation or {}
        type_patterns = sim_config.get("type_patterns", {})

        for point_type, pattern_list in type_patterns.items():
            patterns[point_type] = [
                re.compile(p, re.IGNORECASE) for p in pattern_list
            ]

        return patterns

    def classify_point(self, point: PointInfo) -> str:
        """
        Determine the type of a point based on its name.

        Returns one of: temperature, humidity, pressure, co2, position,
        power, energy, status, alarm, speed, flow, or "unknown"
        """
        # Check cache
        if point.id in self._point_types:
            return self._point_types[point.id]

        name_lower = point.name.lower()

        # Check compiled patterns
        for point_type, patterns in self._type_patterns.items():
            for pattern in patterns:
                if pattern.search(name_lower):
                    self._point_types[point.id] = point_type
                    return point_type

        # Fallback heuristics
        if any(x in name_lower for x in ["temp", "temperature", "_t"]):
            result = "temperature"
        elif any(x in name_lower for x in ["humid", "rh"]):
            result = "humidity"
        elif any(x in name_lower for x in ["pressure", "dp", "static"]):
            result = "pressure"
        elif any(x in name_lower for x in ["co2", "carbon"]):
            result = "co2"
        elif any(x in name_lower for x in ["valve", "damper", "pos", "cmd"]):
            result = "position"
        elif any(x in name_lower for x in ["power", "kw", "_w"]):
            result = "power"
        elif any(x in name_lower for x in ["energy", "kwh", "wh", "meter", "consumption"]):
            result = "energy"
        elif any(x in name_lower for x in ["status", "state", "run", "enable", "_on"]):
            result = "status"
        elif any(x in name_lower for x in ["alarm", "fault", "error", "trip"]):
            result = "alarm"
        elif any(x in name_lower for x in ["speed", "hz", "rpm", "freq"]):
            result = "speed"
        elif any(x in name_lower for x in ["flow", "cfm", "gpm", "airflow"]):
            result = "flow"
        else:
            result = "unknown"

        self._point_types[point.id] = result
        return result

    def get_simulator(self, point_type: str) -> PointSimulator:
        """Get or create simulator for a point type."""
        if point_type not in self._simulators:
            simulator_class = self.SIMULATOR_CLASSES.get(point_type, NullSimulator)
            behavior = self.config.point_behaviors.get(point_type, {})

            # Build point config
            deadband = behavior.get("deadband", behavior.get("deadband_percent", 0))
            if "deadband_percent" in behavior:
                # Will be applied as percentage later
                pass

            config = PointConfig(
                point_type=point_type,
                deadband=deadband,
                sample_interval=behavior.get("sample_interval", 60),
                min_value=behavior.get("min_value", float("-inf")),
                max_value=behavior.get("max_value", float("inf")),
                params=behavior,
            )

            self._simulators[point_type] = simulator_class(config, rng=self.rng)

        return self._simulators[point_type]

    def generate(
        self,
        points: list[PointInfo],
        duration_days: float,
        show_progress: bool = True,
        mode: str = "vectorized",
        n_workers: int | None = None,
    ) -> Iterator[SimulationSample]:
        """
        Generate timeseries data for all points.

        Args:
            points: List of points to simulate
            duration_days: Duration of simulation in days
            show_progress: Whether to show progress bar
            mode: Simulation mode:
                - "vectorized": NumPy vectorized (100-500x faster, RECOMMENDED)
                - "sequential": Original Python step-by-step
                - "parallel": Multiprocessing (deprecated, use vectorized)
            n_workers: Number of worker processes (for parallel mode only)

        Yields:
            SimulationSample for each value that exceeds deadband
        """
        # Dispatch to vectorized implementation (fastest)
        if mode == "vectorized":
            yield from self._generate_vectorized(points, duration_days, show_progress)
            return

        # Dispatch to parallel implementation if requested
        if mode == "parallel":
            from .parallel import generate_parallel, PointInfo as ParallelPointInfo

            # Convert PointInfo to parallel module's version
            parallel_points = [
                ParallelPointInfo(
                    id=p.id,
                    name=p.name,
                    equipment_id=p.equipment_id,
                    equipment_type=p.equipment_type,
                    unit=p.unit,
                    setpoint=p.setpoint,
                )
                for p in points
            ]

            # Build config dict for parallel module
            config_dict = {
                "point_behaviors": self.config.point_behaviors,
                "simulation": self.config.simulation,
                "environment": self.config.environment,
                "occupancy": self.config.occupancy,
            }

            sim_config = self.config.simulation or {}
            step_seconds = sim_config.get("base_step_seconds", 60)
            warmup_hours = sim_config.get("warmup_hours", 2)

            yield from generate_parallel(
                points=parallel_points,
                duration_days=duration_days,
                config=config_dict,
                start_time=self.start_time,
                base_seed=self.rng.randint(0, 2**31),
                n_workers=n_workers,
                show_progress=show_progress,
                warmup_hours=warmup_hours,
                step_seconds=step_seconds,
            )
            return

        # Sequential mode (original, slowest)
        yield from self._generate_sequential(points, duration_days, show_progress)

    def _generate_vectorized(
        self,
        points: list[PointInfo],
        duration_days: float,
        show_progress: bool,
    ) -> Iterator[SimulationSample]:
        """
        Generate timeseries using vectorized NumPy operations.

        This is 100-500x faster than the sequential implementation.
        """
        from .vectorized import generate_timeseries_vectorized

        sim_config = self.config.simulation or {}
        step_seconds = sim_config.get("base_step_seconds", 60)

        # Use the high-level vectorized generator
        for point_id, timestamp, value in generate_timeseries_vectorized(
            points=points,
            duration_days=duration_days,
            start_time=self.start_time,
            seed=self.rng.randint(0, 2**31),
            dt=float(step_seconds),
            show_progress=show_progress,
            classify_func=lambda p: self.classify_point(p),
        ):
            yield SimulationSample(
                point_id=point_id,
                timestamp=timestamp,
                value=value,
            )

    def _generate_sequential(
        self,
        points: list[PointInfo],
        duration_days: float,
        show_progress: bool,
    ) -> Iterator[SimulationSample]:
        """Original sequential simulation (slowest, most accurate)."""
        from tqdm import tqdm

        # Initialize states for all points
        point_states = {}
        for point in points:
            point_type = self.classify_point(point)
            simulator = self.get_simulator(point_type)
            state = simulator.init_state(
                point.id,
                setpoint=point.setpoint,
            )
            point_states[point.id] = (point, point_type, state)

        # Simulation parameters
        sim_config = self.config.simulation or {}
        step_seconds = sim_config.get("base_step_seconds", 60)
        warmup_hours = sim_config.get("warmup_hours", 2)

        # Time range
        current_time = self.start_time - timedelta(hours=warmup_hours)
        end_time = self.start_time + timedelta(days=duration_days)

        # Calculate total steps for progress
        total_seconds = (end_time - current_time).total_seconds()
        total_steps = int(total_seconds / step_seconds)

        # Progress bar
        if show_progress:
            pbar = tqdm(
                total=total_steps,
                desc="Simulating timeseries",
                unit="steps",
            )

        step_count = 0
        samples_generated = 0

        while current_time < end_time:
            # Get context for this moment
            occupancy = self.occupancy.get_occupancy(current_time)
            environment = self.environment.get_environment(current_time)

            # Simulate each point
            for point_id, (point, point_type, state) in point_states.items():
                simulator = self.get_simulator(point_type)
                sample = simulator.simulate(
                    state,
                    current_time,
                    occupancy,
                    environment,
                )

                # Only yield samples after warmup and if sample generated
                if sample is not None and current_time >= self.start_time:
                    samples_generated += 1
                    yield sample

            # Advance time
            current_time += timedelta(seconds=step_seconds)
            step_count += 1

            if show_progress:
                pbar.update(1)
                if step_count % 1000 == 0:
                    pbar.set_postfix(samples=samples_generated)

        if show_progress:
            pbar.close()

    def get_statistics(self) -> dict[str, Any]:
        """Get simulation statistics."""
        stats = {
            "point_types": {},
            "simulators_created": len(self._simulators),
        }

        for point_type, simulator in self._simulators.items():
            stats["point_types"][point_type] = {
                "states_count": len(simulator.states),
                "deadband": simulator.config.deadband,
            }

        return stats
