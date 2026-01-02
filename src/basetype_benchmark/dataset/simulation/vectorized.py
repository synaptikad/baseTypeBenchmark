"""
Vectorized Simulation Module using NumPy.

Generates all timeseries trajectories in a single pass using the analytical
solution to the Ornstein-Uhlenbeck process. This is 100-500x faster than
the step-by-step Python simulation.

The OU process solution:
    X[n+1] = μ + (X[n] - μ) × e^(-θ×dt) + σ × √((1-e^(-2θdt))/(2θ)) × Z

Where Z ~ N(0,1) and all coefficients are constant → vectorizable.
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterator, Tuple, List, Dict, Any


@dataclass
class PointParams:
    """Parameters for a single point type."""
    mean: float           # Target/setpoint value
    theta: float          # Mean reversion rate (1/time_constant)
    sigma: float          # Volatility/noise level
    deadband: float       # Transmission threshold
    min_value: float      # Physical minimum
    max_value: float      # Physical maximum


# Default parameters by point type
# NOTE: sigma values are tuned so that deadband filtering achieves ~85% reduction
# (i.e., only ~15% of samples are transmitted)
DEFAULT_PARAMS: Dict[str, PointParams] = {
    "temperature": PointParams(
        mean=21.0, theta=1.0/(10*60), sigma=0.05,  # 10 min lag, low noise
        deadband=0.5, min_value=10.0, max_value=35.0
    ),
    "humidity": PointParams(
        mean=45.0, theta=1.0/(20*60), sigma=0.3,  # 20 min lag
        deadband=3.0, min_value=0.0, max_value=100.0
    ),
    "pressure": PointParams(
        mean=250.0, theta=1.0/(60), sigma=1.0,  # 1 min response
        deadband=5.0, min_value=0.0, max_value=1000.0
    ),
    "co2": PointParams(
        mean=600.0, theta=1.0/(15*60), sigma=5.0,  # 15 min response
        deadband=50.0, min_value=350.0, max_value=2000.0
    ),
    "position": PointParams(
        mean=50.0, theta=1.0/(5*60), sigma=0.5,  # 5 min modulation
        deadband=2.0, min_value=0.0, max_value=100.0
    ),
    "power": PointParams(
        mean=10.0, theta=1.0/(5*60), sigma=0.1,  # 5 min response
        deadband=0.5, min_value=0.0, max_value=1000.0
    ),
    "energy": PointParams(
        mean=100.0, theta=0.0, sigma=0.0,  # Cumulative (handled separately)
        deadband=1.0, min_value=0.0, max_value=float('inf')
    ),
    "meter": PointParams(
        mean=100.0, theta=0.0, sigma=0.0,  # Cumulative
        deadband=1.0, min_value=0.0, max_value=float('inf')
    ),
    "status": PointParams(
        mean=0.5, theta=1.0/(60*60), sigma=0.1,  # 1 hour avg state duration
        deadband=0.5, min_value=0.0, max_value=1.0
    ),
    "alarm": PointParams(
        mean=0.0, theta=1.0/(60), sigma=0.01,  # Rare events
        deadband=0.5, min_value=0.0, max_value=1.0
    ),
    "speed": PointParams(
        mean=50.0, theta=1.0/(5*60), sigma=0.2,  # 5 min response
        deadband=1.0, min_value=0.0, max_value=100.0
    ),
    "flow": PointParams(
        mean=500.0, theta=1.0/(5*60), sigma=2.0,  # 5 min response
        deadband=10.0, min_value=0.0, max_value=5000.0
    ),
}

# Unknown type fallback
DEFAULT_PARAMS["unknown"] = PointParams(
    mean=50.0, theta=1.0/(5*60), sigma=0.1,
    deadband=1.0, min_value=0.0, max_value=100.0
)


@dataclass
class VectorizedSimulator:
    """
    Generates all timeseries trajectories using vectorized NumPy operations.

    Instead of 70k × 10k Python function calls, this performs a single
    vectorized loop over timesteps with all points computed in parallel.
    """

    n_points: int
    n_timesteps: int
    dt: float = 60.0  # seconds between samples

    # Arrays of parameters (shape: n_points,)
    means: np.ndarray = field(default=None)
    thetas: np.ndarray = field(default=None)
    sigmas: np.ndarray = field(default=None)
    deadbands: np.ndarray = field(default=None)
    min_values: np.ndarray = field(default=None)
    max_values: np.ndarray = field(default=None)

    # Point type indices for special handling
    point_types: np.ndarray = field(default=None)  # int codes

    # Type codes for special handling
    TYPE_CONTINUOUS: int = 0
    TYPE_METER: int = 1
    TYPE_STATUS: int = 2
    TYPE_ALARM: int = 3

    def generate_all(self, seed: int, show_progress: bool = False) -> np.ndarray:
        """
        Generate ALL trajectories in a single vectorized pass.

        Args:
            seed: Random seed for reproducibility
            show_progress: Whether to show progress bar

        Returns:
            trajectories: Array of shape (n_points, n_timesteps)
        """
        from tqdm import tqdm

        rng = np.random.default_rng(seed)

        # Pre-compute OU coefficients (constant for all timesteps)
        decay = np.exp(-self.thetas * self.dt)

        # Exact variance of OU process
        # Var = σ² × (1 - e^(-2θdt)) / (2θ)
        # Handle θ=0 case (pure random walk) separately
        with np.errstate(divide='ignore', invalid='ignore'):
            variance = np.where(
                self.thetas > 1e-10,
                (self.sigmas ** 2) * (1 - np.exp(-2 * self.thetas * self.dt)) / (2 * self.thetas),
                self.sigmas ** 2 * self.dt  # θ→0 limit
            )
        noise_scale = np.sqrt(np.maximum(variance, 0))

        # Pre-generate ALL random values at once (much faster)
        randoms = rng.standard_normal((self.n_points, self.n_timesteps))

        # Allocate trajectories array
        trajectories = np.zeros((self.n_points, self.n_timesteps), dtype=np.float32)

        # Initialize with setpoints (means)
        trajectories[:, 0] = self.means

        # Add some initial variation
        trajectories[:, 0] += noise_scale * randoms[:, 0] * 2
        trajectories[:, 0] = np.clip(trajectories[:, 0], self.min_values, self.max_values)

        # Vectorized OU simulation (single loop over time, all points in parallel)
        time_range = range(1, self.n_timesteps)
        if show_progress:
            time_range = tqdm(
                time_range,
                desc="  Simulating timesteps",
                unit="steps",
                leave=False,
            )

        for t in time_range:
            # OU step: X[t] = μ + (X[t-1] - μ) × decay + noise
            trajectories[:, t] = (
                self.means +
                (trajectories[:, t-1] - self.means) * decay +
                noise_scale * randoms[:, t]
            )

            # Clamp to physical bounds
            trajectories[:, t] = np.clip(
                trajectories[:, t],
                self.min_values,
                self.max_values
            )

        # Handle special types
        if self.point_types is not None:
            self._handle_special_types(trajectories, rng)

        return trajectories

    def _handle_special_types(self, trajectories: np.ndarray, rng: np.random.Generator):
        """Apply special transformations for meter, status, alarm types."""

        # Meter/Energy: cumulative sum of related power points
        meter_mask = self.point_types == self.TYPE_METER
        if np.any(meter_mask):
            # For meters, generate a base consumption rate and cumsum
            base_rate = self.means[meter_mask] / (24 * 60)  # per minute
            noise = rng.standard_normal((np.sum(meter_mask), self.n_timesteps)) * 0.1
            rates = base_rate[:, np.newaxis] * (1 + noise)
            rates = np.maximum(rates, 0)
            trajectories[meter_mask, :] = np.cumsum(rates, axis=1)

        # Status: threshold to binary 0/1
        status_mask = self.point_types == self.TYPE_STATUS
        if np.any(status_mask):
            # Apply hysteresis-like behavior
            trajectories[status_mask, :] = (trajectories[status_mask, :] > 0.5).astype(np.float32)

        # Alarm: rare events (mostly 0, occasional 1)
        alarm_mask = self.point_types == self.TYPE_ALARM
        if np.any(alarm_mask):
            n_alarms = np.sum(alarm_mask)
            # Poisson process: ~0.5 events per day per point
            event_prob = 0.5 / (24 * 60)  # per minute
            events = rng.random((n_alarms, self.n_timesteps)) < event_prob
            trajectories[alarm_mask, :] = events.astype(np.float32)

    def apply_deadband_vectorized(
        self,
        trajectories: np.ndarray,
        last_transmitted: np.ndarray = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Apply deadband filtering using fully vectorized operations.

        Returns three arrays that can be used to construct samples efficiently.

        Args:
            trajectories: shape (n_points, n_timesteps)
            last_transmitted: initial last transmitted values, shape (n_points,)

        Returns:
            point_indices: array of point indices for transmitted samples
            time_indices: array of time indices for transmitted samples
            values: array of transmitted values
        """
        n_points, n_timesteps = trajectories.shape

        # Track last transmitted value per point
        if last_transmitted is None:
            last_tx = trajectories[:, 0].copy()
        else:
            last_tx = last_transmitted.copy()

        # First timestep is always transmitted
        all_point_indices = [np.arange(n_points)]
        all_time_indices = [np.zeros(n_points, dtype=np.int64)]
        all_values = [trajectories[:, 0]]

        # For each subsequent timestep, check deadband
        for t in range(1, n_timesteps):
            current_values = trajectories[:, t]

            # Check which points exceed deadband
            exceeds = np.abs(current_values - last_tx) > self.deadbands

            if np.any(exceeds):
                # Get indices of points that exceeded
                point_idxs = np.where(exceeds)[0]

                all_point_indices.append(point_idxs)
                all_time_indices.append(np.full(len(point_idxs), t, dtype=np.int64))
                all_values.append(current_values[exceeds])

                # Update last transmitted for these points
                last_tx[exceeds] = current_values[exceeds]

        # Concatenate all results
        return (
            np.concatenate(all_point_indices),
            np.concatenate(all_time_indices),
            np.concatenate(all_values),
        )

    def apply_deadband(
        self,
        trajectories: np.ndarray,
    ) -> Iterator[Tuple[int, int, float]]:
        """
        Apply deadband filtering and yield samples one by one.

        This is a convenience method for compatibility with existing code.
        For better performance, use apply_deadband_vectorized().

        Yields:
            (point_idx, time_idx, value) for each transmitted sample
        """
        point_indices, time_indices, values = self.apply_deadband_vectorized(trajectories)

        for p_idx, t_idx, val in zip(point_indices, time_indices, values):
            yield (int(p_idx), int(t_idx), float(val))


def create_simulator_from_points(
    points: List[Any],  # List of PointInfo objects
    n_timesteps: int,
    dt: float = 60.0,
    classify_func: callable = None,
) -> VectorizedSimulator:
    """
    Create a VectorizedSimulator from a list of point objects.

    Args:
        points: List of PointInfo objects with id, name, setpoint, etc.
        n_timesteps: Number of timesteps to simulate
        dt: Time step in seconds
        classify_func: Function to classify point type from PointInfo

    Returns:
        Configured VectorizedSimulator
    """
    n_points = len(points)

    # Allocate parameter arrays
    means = np.zeros(n_points)
    thetas = np.zeros(n_points)
    sigmas = np.zeros(n_points)
    deadbands = np.zeros(n_points)
    min_values = np.zeros(n_points)
    max_values = np.zeros(n_points)
    point_types = np.zeros(n_points, dtype=np.int64)

    for i, point in enumerate(points):
        # Get point type
        if classify_func:
            ptype = classify_func(point)
        else:
            ptype = _classify_point_simple(point.name)

        # Get default parameters for this type
        params = DEFAULT_PARAMS.get(ptype, DEFAULT_PARAMS["unknown"])

        # Use point setpoint if available, otherwise default
        if hasattr(point, 'setpoint') and point.setpoint is not None:
            means[i] = point.setpoint
        else:
            means[i] = params.mean

        thetas[i] = params.theta
        sigmas[i] = params.sigma
        deadbands[i] = params.deadband
        min_values[i] = params.min_value
        max_values[i] = params.max_value

        # Set type code for special handling
        if ptype in ("meter", "energy"):
            point_types[i] = VectorizedSimulator.TYPE_METER
        elif ptype == "status":
            point_types[i] = VectorizedSimulator.TYPE_STATUS
        elif ptype == "alarm":
            point_types[i] = VectorizedSimulator.TYPE_ALARM
        else:
            point_types[i] = VectorizedSimulator.TYPE_CONTINUOUS

    return VectorizedSimulator(
        n_points=n_points,
        n_timesteps=n_timesteps,
        dt=dt,
        means=means,
        thetas=thetas,
        sigmas=sigmas,
        deadbands=deadbands,
        min_values=min_values,
        max_values=max_values,
        point_types=point_types,
    )


def _classify_point_simple(name: str) -> str:
    """Simple point classification from name (fallback)."""
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


def generate_timeseries_vectorized(
    points: List[Any],
    duration_days: float,
    start_time: datetime,
    seed: int,
    dt: float = 60.0,
    show_progress: bool = True,
    classify_func: callable = None,
) -> Iterator[Tuple[str, datetime, float]]:
    """
    High-level function to generate timeseries using vectorized simulation.

    This is the main entry point for the vectorized simulation.

    Args:
        points: List of PointInfo objects
        duration_days: Duration of simulation in days
        start_time: Start datetime for the simulation
        seed: Random seed for reproducibility
        dt: Time step in seconds (default 60)
        show_progress: Whether to show progress bar
        classify_func: Optional function to classify point types

    Yields:
        (point_id, timestamp, value) tuples for each transmitted sample
    """
    from tqdm import tqdm

    n_timesteps = int(duration_days * 24 * 60 * 60 / dt)
    n_points = len(points)

    if show_progress:
        print(f"Vectorized simulation: {n_points:,} points × {n_timesteps:,} timesteps")

    # Create simulator
    simulator = create_simulator_from_points(
        points=points,
        n_timesteps=n_timesteps,
        dt=dt,
        classify_func=classify_func,
    )

    # Generate all trajectories
    if show_progress:
        mem_estimate_gb = (n_points * n_timesteps * 8) / (1024**3)
        print(f"  Allocating {mem_estimate_gb:.2f} GB for trajectories...")

    trajectories = simulator.generate_all(seed, show_progress=show_progress)

    if show_progress:
        print(f"  Trajectories shape: {trajectories.shape}")
        mem_mb = trajectories.nbytes / (1024 * 1024)
        print(f"  Memory usage: {mem_mb:.1f} MB")

    # Apply deadband filtering
    if show_progress:
        print("  Applying deadband filter...")

    point_indices, time_indices, values = simulator.apply_deadband_vectorized(trajectories)

    n_samples = len(values)
    if show_progress:
        compression = 100 * (1 - n_samples / (n_points * n_timesteps))
        print(f"  Samples after deadband: {n_samples:,} ({compression:.1f}% reduction)")

    # Build point ID lookup
    point_ids = [p.id for p in points]

    # Yield samples (sorted by time for better streaming)
    # Sort by time_indices for temporal ordering
    sort_order = np.argsort(time_indices)
    point_indices = point_indices[sort_order]
    time_indices = time_indices[sort_order]
    values = values[sort_order]

    if show_progress:
        iterator = tqdm(
            zip(point_indices, time_indices, values),
            total=n_samples,
            desc="Emitting samples",
        )
    else:
        iterator = zip(point_indices, time_indices, values)

    for p_idx, t_idx, value in iterator:
        timestamp = start_time + timedelta(seconds=float(t_idx) * dt)
        yield (point_ids[p_idx], timestamp, float(value))


def export_timeseries_parquet_direct(
    points: List[Any],
    duration_days: float,
    output_path: str,
    start_time: datetime,
    seed: int = 42,
    dt: float = 60.0,
    show_progress: bool = True,
    classify_func=None,
    batch_size: int = 10_000_000,
) -> Dict[str, Any]:
    """
    Export timeseries directly to Parquet without Python iteration.

    This is 10-50x faster than yielding samples one by one because:
    1. Timestamps are computed vectorially with NumPy
    2. Point IDs are mapped vectorially
    3. Parquet is written in large batches directly from NumPy arrays

    Args:
        points: List of point objects with id, name attributes
        duration_days: Duration of simulation in days
        output_path: Path to output Parquet file
        start_time: Start datetime for simulation
        seed: Random seed for reproducibility
        dt: Time step in seconds (default 60)
        show_progress: Whether to show progress
        classify_func: Optional function to classify point types
        batch_size: Number of rows per Parquet batch (default 10M)

    Returns:
        Dictionary with export statistics
    """
    import pyarrow as pa
    import pyarrow.parquet as pq
    from pathlib import Path
    from tqdm import tqdm

    n_points = len(points)
    n_timesteps = int(duration_days * 24 * 3600 / dt)

    if show_progress:
        print(f"  Vectorized simulation: {n_points:,} points × {n_timesteps:,} timesteps")

    # Create simulator
    simulator = create_simulator_from_points(
        points=points,
        n_timesteps=n_timesteps,
        dt=dt,
        classify_func=classify_func,
    )

    # Generate trajectories
    if show_progress:
        mem_estimate_gb = (n_points * n_timesteps * 8) / (1024**3)
        print(f"  Allocating {mem_estimate_gb:.2f} GB for trajectories...")

    trajectories = simulator.generate_all(seed, show_progress=show_progress)

    if show_progress:
        print(f"  Trajectories shape: {trajectories.shape}")

    # Apply deadband filtering
    if show_progress:
        print("  Applying deadband filter...")

    point_indices, time_indices, values = simulator.apply_deadband_vectorized(trajectories)

    # Free trajectory memory early
    del trajectories

    n_samples = len(values)
    if show_progress:
        compression = 100 * (1 - n_samples / (n_points * n_timesteps))
        print(f"  Samples after deadband: {n_samples:,} ({compression:.1f}% reduction)")

    # Build point ID array (vectorized lookup)
    point_ids_list = [p.id for p in points]
    point_ids_array = np.array(point_ids_list, dtype=object)

    # Compute timestamps vectorially
    # start_time + time_indices * dt seconds
    if show_progress:
        print("  Computing timestamps vectorially...")

    start_ts = np.datetime64(start_time, 'us')
    dt_us = np.int64(dt * 1_000_000)  # dt in microseconds
    timestamps = start_ts + (time_indices.astype(np.int64) * dt_us)

    # Map point indices to point IDs
    if show_progress:
        print("  Mapping point IDs...")
    point_id_column = point_ids_array[point_indices]

    # Write to Parquet in batches
    if show_progress:
        print(f"  Writing {n_samples:,} samples to Parquet in batches of {batch_size:,}...")

    schema = pa.schema([
        ("point_id", pa.string()),
        ("timestamp", pa.timestamp("us")),
        ("value", pa.float32())
    ])

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    writer = pq.ParquetWriter(str(output_path), schema)
    total_written = 0

    n_batches = (n_samples + batch_size - 1) // batch_size

    if show_progress:
        batch_iter = tqdm(range(n_batches), desc="  Writing batches", unit="batch")
    else:
        batch_iter = range(n_batches)

    for batch_idx in batch_iter:
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, n_samples)

        # Extract batch slices (zero-copy views where possible)
        batch_point_ids = point_id_column[start_idx:end_idx]
        batch_timestamps = timestamps[start_idx:end_idx]
        batch_values = values[start_idx:end_idx]

        # Create PyArrow table
        table = pa.table({
            "point_id": pa.array(batch_point_ids, type=pa.string()),
            "timestamp": pa.array(batch_timestamps, type=pa.timestamp("us")),
            "value": pa.array(batch_values, type=pa.float32()),
        })

        writer.write_table(table)
        total_written += (end_idx - start_idx)

    writer.close()

    if show_progress:
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  Written {total_written:,} rows to {output_path.name} ({file_size_mb:.1f} MB)")

    return {
        "n_points": n_points,
        "n_timesteps": n_timesteps,
        "n_samples": n_samples,
        "compression_pct": 100 * (1 - n_samples / (n_points * n_timesteps)),
        "file_size_bytes": output_path.stat().st_size,
    }


def export_timeseries_parquet_chunked(
    points: List[Any],
    duration_days: float,
    output_path: str,
    start_time: datetime,
    seed: int = 42,
    dt: float = 60.0,
    show_progress: bool = True,
    classify_func: Optional[Callable[[str], str]] = None,
    max_ram_gb: float = 10.0,
) -> Dict[str, Any]:
    """
    Export timeseries to Parquet using CHUNKED processing to limit RAM usage.
    
    Processes points in chunks to avoid OOM on large datasets.
    Limits memory to approximately max_ram_gb.
    
    Args:
        points: List of PointInfo objects
        duration_days: Duration in days
        output_path: Output parquet file path
        start_time: Start datetime
        seed: Random seed
        dt: Time step in seconds
        show_progress: Show progress
        classify_func: Point classification function
        max_ram_gb: Maximum RAM to use (default 10 GB)
    
    Returns:
        Dict with statistics
    """
    from tqdm import tqdm
    from pathlib import Path
    import pyarrow as pa
    import pyarrow.parquet as pq
    
    n_timesteps = int(duration_days * 24 * 60 * 60 / dt)
    n_points = len(points)
    
    # Calculate chunk size based on max RAM
    # Each trajectory: n_timesteps * 8 bytes (float64)
    bytes_per_point = n_timesteps * 8
    max_points_per_chunk = int((max_ram_gb * 1024**3) / bytes_per_point)
    max_points_per_chunk = max(100, min(max_points_per_chunk, n_points))
    
    n_chunks = (n_points + max_points_per_chunk - 1) // max_points_per_chunk
    
    if show_progress:
        mem_per_chunk_gb = (max_points_per_chunk * n_timesteps * 8) / (1024**3)
        print(f"  Chunked simulation: {n_points:,} points × {n_timesteps:,} timesteps")
        print(f"  Processing in {n_chunks} chunks of {max_points_per_chunk:,} points (~{mem_per_chunk_gb:.1f} GB/chunk)")
    
    # Prepare Parquet writer
    schema = pa.schema([
        ("point_id", pa.string()),
        ("timestamp", pa.timestamp("us")),
        ("value", pa.float32())
    ])
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    writer = pq.ParquetWriter(str(output_path), schema)
    
    total_samples = 0
    rng = np.random.default_rng(seed)
    
    # Process chunks
    chunk_iter = range(n_chunks)
    if show_progress:
        chunk_iter = tqdm(chunk_iter, desc="  Processing chunks", unit="chunk")
    
    for chunk_idx in chunk_iter:
        start_pt = chunk_idx * max_points_per_chunk
        end_pt = min(start_pt + max_points_per_chunk, n_points)
        chunk_points = points[start_pt:end_pt]
        chunk_seed = seed + chunk_idx  # Different seed per chunk for variety
        
        # Create simulator for this chunk
        simulator = create_simulator_from_points(
            points=chunk_points,
            n_timesteps=n_timesteps,
            dt=dt,
            classify_func=classify_func,
        )
        
        # Generate trajectories for this chunk
        trajectories = simulator.generate_all(chunk_seed, show_progress=False)
        
        # Apply deadband filtering
        point_indices, time_indices, values = simulator.apply_deadband_vectorized(trajectories)
        
        # Free trajectory memory
        del trajectories
        
        n_samples = len(values)
        if n_samples == 0:
            continue
        
        # Build point IDs for this chunk
        point_ids_list = [p.id for p in chunk_points]
        point_ids_array = np.array(point_ids_list, dtype=object)
        
        # Compute timestamps
        start_ts = np.datetime64(start_time, 'us')
        dt_us = np.int64(dt * 1_000_000)
        timestamps = start_ts + (time_indices.astype(np.int64) * dt_us)
        
        # Map point indices to IDs
        point_id_column = point_ids_array[point_indices]
        
        # Write to Parquet
        table = pa.table({
            "point_id": pa.array(point_id_column, type=pa.string()),
            "timestamp": pa.array(timestamps, type=pa.timestamp("us")),
            "value": pa.array(values, type=pa.float32()),
        })
        
        writer.write_table(table)
        total_samples += n_samples
        
        # Free memory
        del point_indices, time_indices, values, timestamps, point_id_column, table
    
    writer.close()
    
    if show_progress:
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  Written {total_samples:,} rows to {output_path.name} ({file_size_mb:.1f} MB)")
    
    return {
        "n_points": n_points,
        "n_timesteps": n_timesteps,
        "n_samples": total_samples,
        "compression_pct": 100 * (1 - total_samples / (n_points * n_timesteps)) if n_points * n_timesteps > 0 else 0,
        "file_size_bytes": output_path.stat().st_size,
        "n_chunks": n_chunks,
    }


def export_timeseries_parquet_by_frequency(
    points: List[Any],
    duration_days: float,
    output_path: str,
    start_time: datetime,
    seed: int = 42,
    show_progress: bool = True,
    classify_func: Optional[Callable[[str], str]] = None,
    max_ram_gb: float = 10.0,
) -> Dict[str, Any]:
    """
    Export timeseries to Parquet using REALISTIC Digital Twin semantics.
    
    In a real Digital Twin for smart buildings:
    1. Energy/meter points: NO deadband, regular 15-minute intervals (regulatory requirement)
    2. Other points: deadband filtering (only record when value changes beyond threshold)
    
    This produces realistic data volumes matching actual BMS/SCADA systems.
    
    Args:
        points: List of point objects with id, name, frequency, point_type attributes
        duration_days: Duration in days
        output_path: Output parquet file path
        start_time: Start datetime
        seed: Random seed
        show_progress: Show progress
        classify_func: Point classification function
        max_ram_gb: Maximum RAM per frequency group
    
    Returns:
        Dict with statistics
    """
    from tqdm import tqdm
    from pathlib import Path
    from collections import defaultdict
    import pyarrow as pa
    import pyarrow.parquet as pq
    
    # ==========================================================================
    # DIGITAL TWIN STORAGE MODEL
    # ==========================================================================
    # In real BMS/SCADA systems:
    # - Sensors sample at high frequency (1s, 5s) but we don't store every sample
    # - Storage is based on Change-of-Value (COV) / deadband filtering
    # - Minimum storage interval depends on point type:
    #   * Energy/meters: fixed 15min intervals (no deadband) - regulatory requirement
    #   * Fast sensors (temp, pressure): evaluated every 1min, stored on COV
    #   * Slow sensors (filters, efficiency): evaluated every 5-15min
    #   * Status/alarms: event-driven only
    # ==========================================================================
    
    # Minimum storage interval by category (in seconds)
    # This normalizes unrealistic frequencies from docs (1s, 5s) to real storage rates
    MIN_STORAGE_INTERVAL = {
        'fast': 60,      # Fast sensors: 1 min minimum
        'normal': 300,   # Normal sensors: 5 min minimum
        'slow': 900,     # Slow/efficiency: 15 min minimum
        'energy': 900,   # Energy meters: fixed 15 min
    }
    
    # Keywords to classify points
    ENERGY_KEYWORDS = {'energy', 'meter', 'power', 'kwh', 'kw', 'consumption', 'production', 
                       'compteur', 'énergie', 'puissance', 'consommation', 'wh', 'watt'}
    FAST_KEYWORDS = {'temp', 'temperature', 'pressure', 'humidity', 'co2', 'flow', 'speed',
                     'current', 'voltage', 'setpoint', 'cmd', 'valve', 'damper'}
    SLOW_KEYWORDS = {'filter', 'efficiency', 'recovery', 'cop', 'eer', 'occupancy'}
    
    def classify_point_storage(p) -> tuple:
        """
        Classify point for storage: (category, min_interval, use_deadband)
        
        Returns:
            (category, minimum_storage_interval, apply_deadband)
        """
        name_lower = getattr(p, 'name', '').lower()
        point_type = getattr(p, 'point_type', '').lower()
        orig_freq = getattr(p, 'frequency', 300) or 300
        
        # Energy/meters: no deadband, fixed 15min
        for kw in ENERGY_KEYWORDS:
            if kw in name_lower:
                return ('energy', MIN_STORAGE_INTERVAL['energy'], False)
        if point_type in ('energy', 'meter', 'compteur'):
            return ('energy', MIN_STORAGE_INTERVAL['energy'], False)
        
        # Status/alarms: event-driven with deadband
        if point_type in ('etat', 'status', 'alarme', 'alarm'):
            # For status, use original frequency but minimum 1min
            return ('status', max(60, orig_freq), True)
        
        # Slow sensors
        for kw in SLOW_KEYWORDS:
            if kw in name_lower:
                return ('slow', max(MIN_STORAGE_INTERVAL['slow'], orig_freq), True)
        
        # Fast sensors
        for kw in FAST_KEYWORDS:
            if kw in name_lower:
                return ('fast', max(MIN_STORAGE_INTERVAL['fast'], orig_freq), True)
        
        # Default: normal sensor
        return ('normal', max(MIN_STORAGE_INTERVAL['normal'], orig_freq), True)
    
    # Classify all points
    energy_points = []
    regular_points_by_freq = defaultdict(list)
    
    storage_stats = defaultdict(int)
    
    for p in points:
        category, storage_freq, use_deadband = classify_point_storage(p)
        storage_stats[category] += 1
        
        if not use_deadband:
            energy_points.append((p, storage_freq))
        else:
            regular_points_by_freq[storage_freq].append(p)
    
    if show_progress:
        print(f"  Point classification for storage:")
        for cat, n in sorted(storage_stats.items(), key=lambda x: -x[1]):
            print(f"    {cat}: {n:,} points")
        print(f"  Energy/meter (no deadband): {len(energy_points):,} points")
        print(f"  Regular (with deadband): {sum(len(v) for v in regular_points_by_freq.values()):,} points")
    
    # Prepare Parquet writer
    schema = pa.schema([
        ("point_id", pa.string()),
        ("timestamp", pa.timestamp("us")),
        ("value", pa.float32())
    ])
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    writer = pq.ParquetWriter(str(output_path), schema)
    
    total_samples = 0
    total_raw_samples = 0
    energy_samples = 0
    regular_samples = 0
    
    # =========================================================================
    # 1. Process ENERGY points: NO deadband, fixed 15-minute intervals
    # =========================================================================
    if energy_points:
        energy_dt = 900.0  # 15 minutes
        n_timesteps_energy = int(duration_days * 24 * 3600 / energy_dt)
        
        # Extract just the points (discard storage_freq since all energy = 15min)
        energy_pts_only = [p for p, _ in energy_points]
        
        if show_progress:
            print(f"  Processing energy points: {len(energy_pts_only):,} × {n_timesteps_energy:,} timesteps (no deadband)")
        
        # Process energy points in chunks if needed
        mem_gb = (len(energy_pts_only) * n_timesteps_energy * 8) / (1024**3)
        
        if mem_gb > max_ram_gb:
            max_pts = int((max_ram_gb * 1024**3) / (n_timesteps_energy * 8))
            max_pts = max(100, max_pts)
        else:
            max_pts = len(energy_pts_only)
        
        for chunk_start in range(0, len(energy_pts_only), max_pts):
            chunk_end = min(chunk_start + max_pts, len(energy_pts_only))
            chunk_points = energy_pts_only[chunk_start:chunk_end]
            chunk_seed = seed + chunk_start
            
            # Create simulator
            simulator = create_simulator_from_points(
                points=chunk_points,
                n_timesteps=n_timesteps_energy,
                dt=energy_dt,
                classify_func=classify_func,
            )
            
            # Generate trajectories
            trajectories = simulator.generate_all(chunk_seed, show_progress=False)
            
            # NO deadband for energy - keep ALL values
            n_pts_chunk = len(chunk_points)
            n_samples_chunk = n_pts_chunk * n_timesteps_energy
            
            # Build arrays for all samples (no filtering)
            point_ids_list = [p.id for p in chunk_points]
            point_ids_array = np.array(point_ids_list, dtype=object)
            
            # Create full index arrays
            point_indices = np.repeat(np.arange(n_pts_chunk), n_timesteps_energy)
            time_indices = np.tile(np.arange(n_timesteps_energy), n_pts_chunk)
            values = trajectories.flatten()
            
            # Compute timestamps
            start_ts = np.datetime64(start_time, 'us')
            dt_us = np.int64(energy_dt * 1_000_000)
            timestamps = start_ts + (time_indices.astype(np.int64) * dt_us)
            
            # Map point indices to IDs
            point_id_column = point_ids_array[point_indices]
            
            # Write to Parquet
            table = pa.table({
                "point_id": pa.array(point_id_column, type=pa.string()),
                "timestamp": pa.array(timestamps, type=pa.timestamp("us")),
                "value": pa.array(values, type=pa.float32()),
            })
            
            writer.write_table(table)
            
            energy_samples += n_samples_chunk
            total_samples += n_samples_chunk
            total_raw_samples += n_samples_chunk
            
            # Free memory
            del trajectories, point_indices, time_indices, values, timestamps, point_id_column, table
    
    # =========================================================================
    # 2. Process REGULAR points: WITH deadband, grouped by storage frequency
    # =========================================================================
    if regular_points_by_freq:
        if show_progress:
            print(f"  Regular points by storage frequency (with deadband):")
            for freq in sorted(regular_points_by_freq.keys()):
                n = len(regular_points_by_freq[freq])
                n_ts = int(duration_days * 24 * 3600 / freq)
                print(f"    {freq}s ({freq//60}min): {n:,} points × {n_ts:,} timesteps")
        
        # Process each frequency group
        freq_iter = sorted(regular_points_by_freq.keys())
        if show_progress:
            freq_iter = tqdm(list(freq_iter), desc="  Processing frequency groups", unit="freq")
        
        for freq in freq_iter:
            group_points = regular_points_by_freq[freq]
            n_points_group = len(group_points)
            n_timesteps = int(duration_days * 24 * 3600 / freq)
            dt = float(freq)
            
            if n_timesteps == 0:
                continue
            
            # Check memory for this group
            mem_gb = (n_points_group * n_timesteps * 8) / (1024**3)
            
            if mem_gb > max_ram_gb:
                max_points_per_chunk = int((max_ram_gb * 1024**3) / (n_timesteps * 8))
                max_points_per_chunk = max(100, max_points_per_chunk)
                n_chunks = (n_points_group + max_points_per_chunk - 1) // max_points_per_chunk
            else:
                max_points_per_chunk = n_points_group
                n_chunks = 1
            
            for chunk_idx in range(n_chunks):
                start_pt = chunk_idx * max_points_per_chunk
                end_pt = min(start_pt + max_points_per_chunk, n_points_group)
                chunk_points = group_points[start_pt:end_pt]
                chunk_seed = seed + freq + chunk_idx
                
                # Create simulator
                simulator = create_simulator_from_points(
                    points=chunk_points,
                    n_timesteps=n_timesteps,
                    dt=dt,
                    classify_func=classify_func,
                )
                
                # Generate trajectories
                trajectories = simulator.generate_all(chunk_seed, show_progress=False)
                
                # Apply DEADBAND filtering (this is the key difference)
                point_indices, time_indices, values = simulator.apply_deadband_vectorized(trajectories)
                
                # Free memory
                del trajectories
                
                n_samples = len(values)
                if n_samples == 0:
                    continue
                
                total_raw_samples += len(chunk_points) * n_timesteps
                
                # Build point IDs
                point_ids_list = [p.id for p in chunk_points]
                point_ids_array = np.array(point_ids_list, dtype=object)
                
                # Compute timestamps
                start_ts = np.datetime64(start_time, 'us')
                dt_us = np.int64(dt * 1_000_000)
                timestamps = start_ts + (time_indices.astype(np.int64) * dt_us)
                
                # Map point indices to IDs
                point_id_column = point_ids_array[point_indices]
                
                # Write to Parquet
                table = pa.table({
                    "point_id": pa.array(point_id_column, type=pa.string()),
                    "timestamp": pa.array(timestamps, type=pa.timestamp("us")),
                    "value": pa.array(values, type=pa.float32()),
                })
                
                writer.write_table(table)
                total_samples += n_samples
                regular_samples += n_samples
                
                # Free memory
                del point_indices, time_indices, values, timestamps, point_id_column, table
    
    writer.close()
    
    if show_progress:
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        compression_pct = 100 * (1 - total_samples / total_raw_samples) if total_raw_samples > 0 else 0
        print(f"  Written {total_samples:,} rows to {output_path.name} ({file_size_mb:.1f} MB)")
        print(f"    Energy samples (no deadband): {energy_samples:,}")
        print(f"    Regular samples (with deadband): {regular_samples:,}")
        print(f"  Overall compression: {compression_pct:.1f}%")
    
    n_regular_points = sum(len(v) for v in regular_points_by_freq.values())
    
    return {
        "n_points": len(points),
        "n_energy_points": len(energy_points),
        "n_regular_points": n_regular_points,
        "n_samples": total_samples,
        "n_energy_samples": energy_samples,
        "n_regular_samples": regular_samples,
        "n_raw_samples": total_raw_samples,
        "compression_pct": 100 * (1 - total_samples / total_raw_samples) if total_raw_samples > 0 else 0,
        "file_size_bytes": output_path.stat().st_size,
    }
