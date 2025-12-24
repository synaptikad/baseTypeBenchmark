"""
Parallel Simulation Module.

Provides parallel execution of point simulation using multiprocessing.
Each worker process holds its own partition of points and simulators,
avoiding serialization overhead between timesteps.
"""
from __future__ import annotations

import multiprocessing as mp
from multiprocessing import shared_memory
import random
import pickle
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Iterator, List, Dict, Tuple, Optional

from .occupancy import OccupancyModel, OccupancyContext
from .environment import EnvironmentModel, EnvironmentContext, ClimatePreset
from .point_simulator import PointSimulator, PointConfig, SimulationState, SimulationSample, NullSimulator
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

# Golden ratio hash for seed derivation
GOLDEN_RATIO_HASH = 2654435761


@dataclass
class PointInfo:
    """Information about a point to simulate (duplicated for serialization)."""
    id: str
    name: str
    equipment_id: str | None = None
    equipment_type: str | None = None
    unit: str | None = None
    setpoint: float | None = None


@dataclass
class SimulationConfigData:
    """Serializable simulation config for worker init."""
    point_behaviors: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    simulation: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# WORKER STATE (Global per-process)
# ============================================================================

# Global worker state - initialized once per process
_worker_state: Optional["WorkerState"] = None


@dataclass
class WorkerState:
    """State held by each worker process."""
    worker_id: int
    rng: random.Random
    points: List[PointInfo]
    point_states: Dict[str, Tuple[PointInfo, str, SimulationState]]
    simulators: Dict[str, PointSimulator]
    config: SimulationConfigData

    # Simulator class mapping
    SIMULATOR_CLASSES: Dict[str, type] = field(default_factory=lambda: {
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
    })

    def get_simulator(self, point_type: str) -> PointSimulator:
        """Get or create simulator for a point type."""
        if point_type not in self.simulators:
            simulator_class = self.SIMULATOR_CLASSES.get(point_type, NullSimulator)
            behavior = self.config.point_behaviors.get(point_type, {})

            deadband = behavior.get("deadband", behavior.get("deadband_percent", 0))
            config = PointConfig(
                point_type=point_type,
                deadband=deadband,
                sample_interval=behavior.get("sample_interval", 60),
                min_value=behavior.get("min_value", float("-inf")),
                max_value=behavior.get("max_value", float("inf")),
                params=behavior,
            )
            self.simulators[point_type] = simulator_class(config, rng=self.rng)

        return self.simulators[point_type]


def _classify_point(name: str) -> str:
    """Classify point type from name (simplified version for workers)."""
    name_lower = name.lower()

    if any(x in name_lower for x in ["temp", "temperature", "_t"]):
        return "temperature"
    elif any(x in name_lower for x in ["humid", "rh"]):
        return "humidity"
    elif any(x in name_lower for x in ["pressure", "dp", "static"]):
        return "pressure"
    elif any(x in name_lower for x in ["co2", "carbon"]):
        return "co2"
    elif any(x in name_lower for x in ["valve", "damper", "pos", "cmd"]):
        return "position"
    elif any(x in name_lower for x in ["power", "kw", "_w"]):
        return "power"
    elif any(x in name_lower for x in ["energy", "kwh", "wh", "meter", "consumption"]):
        return "energy"
    elif any(x in name_lower for x in ["status", "state", "run", "enable", "_on"]):
        return "status"
    elif any(x in name_lower for x in ["alarm", "fault", "error", "trip"]):
        return "alarm"
    elif any(x in name_lower for x in ["speed", "hz", "rpm", "freq"]):
        return "speed"
    elif any(x in name_lower for x in ["flow", "cfm", "gpm", "airflow"]):
        return "flow"
    else:
        return "unknown"


def _init_worker(
    worker_id: int,
    points_data: List[Dict[str, Any]],
    config_data: Dict[str, Any],
    base_seed: int,
) -> WorkerState:
    """
    Initialize worker with its partition of points.
    """
    # Create deterministic RNG for this worker
    derived_seed = base_seed ^ (worker_id * GOLDEN_RATIO_HASH)
    rng = random.Random(derived_seed)

    # Reconstruct PointInfo objects
    points = [PointInfo(**p) for p in points_data]

    # Create config
    config = SimulationConfigData(
        point_behaviors=config_data.get("point_behaviors", {}),
        simulation=config_data.get("simulation", {}),
    )

    # Initialize worker state
    state = WorkerState(
        worker_id=worker_id,
        rng=rng,
        points=points,
        point_states={},
        simulators={},
        config=config,
    )

    # Initialize states for all points in this partition
    for point in points:
        point_type = _classify_point(point.name)
        simulator = state.get_simulator(point_type)
        sim_state = simulator.init_state(point.id, setpoint=point.setpoint)
        state.point_states[point.id] = (point, point_type, sim_state)

    return state


def _worker_init(worker_id: int, points_data: List[Dict], config_data: Dict, base_seed: int):
    """Initialize worker process with its partition of points."""
    global _worker_state
    _worker_state = _init_worker(worker_id, points_data, config_data, base_seed)


def _worker_task(args: Tuple) -> List[Dict[str, Any]]:
    """
    Process one timestep for a worker.
    Worker state must be initialized via _worker_init.
    """
    global _worker_state

    current_time, occupancy_data, environment_data, is_warmup = args

    if _worker_state is None:
        return []  # Worker not initialized

    # Reconstruct context objects
    occupancy = OccupancyContext(**occupancy_data)
    environment = EnvironmentContext(**environment_data)

    # Process all points in this worker's partition
    samples = []
    for point_id, (point, point_type, state) in _worker_state.point_states.items():
        simulator = _worker_state.get_simulator(point_type)
        sample = simulator.simulate(state, current_time, occupancy, environment)
        if sample is not None and not is_warmup:
            samples.append({
                "point_id": sample.point_id,
                "timestamp": sample.timestamp,
                "value": sample.value,
            })

    return samples


# ============================================================================
# PARALLEL SIMULATION COORDINATOR
# ============================================================================

def partition_points(
    points: List[PointInfo],
    n_workers: int,
) -> List[List[PointInfo]]:
    """
    Partition points across workers using deterministic hash.

    Args:
        points: List of all points to simulate
        n_workers: Number of worker processes

    Returns:
        List of point lists, one per worker
    """
    partitions: List[List[PointInfo]] = [[] for _ in range(n_workers)]

    for point in points:
        # Use hash of point ID for deterministic assignment
        worker_idx = hash(point.id) % n_workers
        partitions[worker_idx].append(point)

    return partitions


def generate_parallel(
    points: List[PointInfo],
    duration_days: float,
    config: Dict[str, Any],
    start_time: datetime,
    base_seed: int,
    n_workers: int | None = None,
    show_progress: bool = True,
    warmup_hours: int = 2,
    step_seconds: int = 60,
) -> Iterator[SimulationSample]:
    """
    Generate timeseries data using parallel simulation.

    Args:
        points: List of points to simulate
        duration_days: Duration of simulation in days
        config: Simulation configuration dict
        start_time: Start time for simulation
        base_seed: Base random seed
        n_workers: Number of worker processes (default: CPU count)
        show_progress: Whether to show progress bar
        warmup_hours: Hours of warmup before start_time
        step_seconds: Simulation step interval in seconds

    Yields:
        SimulationSample for each value that exceeds deadband
    """
    from tqdm import tqdm

    n_workers = n_workers or mp.cpu_count()

    # For very small workloads, use sequential
    if len(points) < 100 or duration_days < 0.1:
        n_workers = 1

    # Partition points across workers
    partitions = partition_points(points, n_workers)

    # Prepare serializable data for each worker
    worker_data = []
    for worker_id, partition in enumerate(partitions):
        points_data = [
            {
                "id": p.id,
                "name": p.name,
                "equipment_id": p.equipment_id,
                "equipment_type": p.equipment_type,
                "unit": p.unit,
                "setpoint": p.setpoint,
            }
            for p in partition
        ]
        worker_data.append((worker_id, points_data, config, base_seed))

    # Initialize environment model in main process
    env_config = config.get("environment", {})
    climate = env_config.get("climate", "temperate")

    if climate == "continental":
        environment_model = ClimatePreset.continental()
    elif climate == "mediterranean":
        environment_model = ClimatePreset.mediterranean()
    elif climate == "tropical":
        environment_model = ClimatePreset.tropical()
    else:
        environment_model = ClimatePreset.temperate()

    environment_model.rng = random.Random(base_seed)

    # Initialize occupancy model in main process
    occupancy_model = OccupancyModel.from_config(
        config.get("occupancy", {}),
        rng=random.Random(base_seed),
    )

    # Time range
    current_time = start_time - timedelta(hours=warmup_hours)
    end_time = start_time + timedelta(days=duration_days)

    # Calculate total steps for progress
    total_seconds = (end_time - current_time).total_seconds()
    total_steps = int(total_seconds / step_seconds)

    # Create separate worker pools (each with 1 process, initialized with its partition)
    pools = []
    for wid, pts, cfg, seed in worker_data:
        pool = mp.Pool(
            processes=1,
            initializer=_worker_init,
            initargs=(wid, pts, cfg, seed),
        )
        pools.append(pool)

    try:
        # Progress bar
        if show_progress:
            pbar = tqdm(
                total=total_steps,
                desc=f"Simulating ({n_workers} workers)",
                unit="steps",
            )

        step_count = 0
        samples_generated = 0

        while current_time < end_time:
            # Pre-compute context in main process
            occupancy = occupancy_model.get_occupancy(current_time)
            environment = environment_model.get_environment(current_time)

            is_warmup = current_time < start_time

            # Serialize context for workers (small payload now!)
            occupancy_data = {
                "is_occupied": occupancy.is_occupied,
                "occupancy_level": occupancy.occupancy_level,
                "people_density": occupancy.people_density,
            }
            environment_data = {
                "outdoor_temp": environment.outdoor_temp,
                "outdoor_humidity": environment.outdoor_humidity,
                "solar_intensity": environment.solar_intensity,
                "is_daytime": environment.is_daytime,
                "season_factor": environment.season_factor,
            }

            # Task args (no points data - already in worker state)
            task_args = (current_time, occupancy_data, environment_data, is_warmup)

            # Submit to all workers in parallel
            async_results = [pool.apply_async(_worker_task, (task_args,)) for pool in pools]

            # Collect samples from all workers
            for async_result in async_results:
                worker_samples = async_result.get()
                for sample_data in worker_samples:
                    samples_generated += 1
                    yield SimulationSample(
                        point_id=sample_data["point_id"],
                        timestamp=sample_data["timestamp"],
                        value=sample_data["value"],
                    )

            # Advance time
            current_time += timedelta(seconds=step_seconds)
            step_count += 1

            if show_progress:
                pbar.update(1)
                if step_count % 100 == 0:
                    pbar.set_postfix(samples=samples_generated)

        if show_progress:
            pbar.close()

    finally:
        # Clean up pools
        for pool in pools:
            pool.close()
            pool.join()
