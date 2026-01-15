"""Periodic resource sampling during query execution.

Sprint 3 - Benchmark BaseType V3

Provides background thread sampling of container resources at configurable
intervals. Collects memory usage via cgroups v2 and produces aggregate
statistics at the end of sampling.

Key features:
- 100ms sampling interval (configurable)
- Background thread for non-blocking sampling
- Peak memory from cgroups v2 (kernel-tracked, most accurate)
- OOM detection
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable

from .cgroups import CgroupsV2Monitor, CgroupsNotFoundError, CgroupsNotSupportedError
from .docker_client import DockerClient, ContainerNotFoundError


@dataclass
class Sample:
    """Single resource sample."""
    timestamp: float  # Relative to start (seconds)
    memory_bytes: int
    memory_percent: float | None = None


@dataclass
class SamplingResult:
    """Result of a sampling session."""
    samples: list[Sample] = field(default_factory=list)
    memory_peak_bytes: int = 0
    memory_avg_bytes: int = 0
    memory_min_bytes: int = 0
    duration_seconds: float = 0.0
    oom_detected: bool = False
    oom_kill_count: int = 0
    sample_count: int = 0

    @property
    def memory_peak_mb(self) -> float:
        """Peak memory in MB."""
        return self.memory_peak_bytes / (1024 * 1024)

    @property
    def memory_avg_mb(self) -> float:
        """Average memory in MB."""
        return self.memory_avg_bytes / (1024 * 1024)

    @property
    def memory_min_mb(self) -> float:
        """Minimum memory in MB."""
        return self.memory_min_bytes / (1024 * 1024)


class MetricsSampler:
    """Background thread sampler for container resources.

    Uses cgroups v2 for accurate memory measurement. The kernel-tracked
    memory.peak is used for peak detection (more accurate than sampling).

    Example:
        ```python
        sampler = MetricsSampler(container_id)
        sampler.start()

        # ... execute query ...

        result = sampler.stop()
        print(f"Peak memory: {result.memory_peak_mb:.1f} MB")
        print(f"OOM detected: {result.oom_detected}")
        ```
    """

    DEFAULT_INTERVAL_MS = 100  # 10 samples per second

    def __init__(
        self,
        container_id: str,
        interval_ms: int = DEFAULT_INTERVAL_MS,
        on_sample: Callable[[Sample], None] | None = None,
    ):
        """Initialize sampler.

        Args:
            container_id: Full Docker container ID
            interval_ms: Sampling interval in milliseconds
            on_sample: Optional callback for each sample
        """
        self.container_id = container_id
        self.interval_ms = interval_ms
        self.on_sample = on_sample

        self._cgroups: CgroupsV2Monitor | None = None
        self._samples: list[Sample] = []
        self._running = False
        self._thread: threading.Thread | None = None
        self._start_time: float = 0.0
        self._initial_oom_count: int = 0

    def start(self) -> None:
        """Start background sampling.

        Resets memory.peak counter and begins collecting samples.
        """
        if self._running:
            return

        # Initialize cgroups monitor
        self._cgroups = CgroupsV2Monitor(self.container_id)

        # Reset peak counter for accurate measurement
        self._cgroups.reset_memory_peak()

        # Record initial OOM count
        self._initial_oom_count = self._cgroups.get_oom_kill_count()

        # Start sampling
        self._samples = []
        self._start_time = time.perf_counter()
        self._running = True

        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def stop(self) -> SamplingResult:
        """Stop sampling and return results.

        Returns:
            SamplingResult with collected metrics
        """
        if not self._running:
            return SamplingResult()

        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

        # Calculate duration
        duration = time.perf_counter() - self._start_time

        # Get final metrics from cgroups (most accurate)
        final_peak = 0
        final_oom_count = 0

        if self._cgroups:
            try:
                final_peak = self._cgroups.get_memory_peak()
                final_oom_count = self._cgroups.get_oom_kill_count()
            except (CgroupsNotFoundError, FileNotFoundError):
                pass

        # Calculate statistics from samples
        if self._samples:
            memory_values = [s.memory_bytes for s in self._samples]
            avg_bytes = sum(memory_values) // len(memory_values)
            min_bytes = min(memory_values)
            # Use cgroups peak if available, otherwise max from samples
            peak_bytes = final_peak if final_peak > 0 else max(memory_values)
        else:
            avg_bytes = 0
            min_bytes = 0
            peak_bytes = final_peak

        # Detect OOM
        new_oom_kills = final_oom_count - self._initial_oom_count
        oom_detected = new_oom_kills > 0

        return SamplingResult(
            samples=self._samples.copy(),
            memory_peak_bytes=peak_bytes,
            memory_avg_bytes=avg_bytes,
            memory_min_bytes=min_bytes,
            duration_seconds=duration,
            oom_detected=oom_detected,
            oom_kill_count=new_oom_kills,
            sample_count=len(self._samples),
        )

    def _sample_loop(self) -> None:
        """Background sampling loop."""
        interval_seconds = self.interval_ms / 1000.0

        while self._running:
            try:
                sample = self._take_sample()
                if sample:
                    self._samples.append(sample)
                    if self.on_sample:
                        self.on_sample(sample)
            except Exception:
                # Don't crash sampling thread on errors
                pass

            time.sleep(interval_seconds)

    def _take_sample(self) -> Sample | None:
        """Take a single sample."""
        if not self._cgroups:
            return None

        try:
            memory_bytes = self._cgroups.get_memory_current()
            memory_max = self._cgroups.get_memory_max()

            memory_percent = None
            if memory_max is not None and memory_max > 0:
                memory_percent = (memory_bytes / memory_max) * 100

            timestamp = time.perf_counter() - self._start_time

            return Sample(
                timestamp=timestamp,
                memory_bytes=memory_bytes,
                memory_percent=memory_percent,
            )
        except (FileNotFoundError, OSError):
            return None

    @property
    def is_running(self) -> bool:
        """Check if sampler is running."""
        return self._running


class MultiContainerSampler:
    """Sample multiple containers simultaneously.

    Useful for hybrid paradigm (M2) that uses multiple containers.

    Example:
        ```python
        sampler = MultiContainerSampler({
            "graph": graph_container_id,
            "ts": ts_container_id,
        })
        sampler.start()

        # ... execute query ...

        results = sampler.stop()
        print(f"Graph peak: {results['graph'].memory_peak_mb:.1f} MB")
        print(f"TS peak: {results['ts'].memory_peak_mb:.1f} MB")
        ```
    """

    def __init__(
        self,
        containers: dict[str, str],
        interval_ms: int = MetricsSampler.DEFAULT_INTERVAL_MS,
    ):
        """Initialize multi-container sampler.

        Args:
            containers: Mapping of name -> container_id
            interval_ms: Sampling interval
        """
        self.samplers: dict[str, MetricsSampler] = {}

        for name, container_id in containers.items():
            try:
                self.samplers[name] = MetricsSampler(
                    container_id=container_id,
                    interval_ms=interval_ms,
                )
            except (CgroupsNotFoundError, CgroupsNotSupportedError):
                # Skip containers we can't monitor
                pass

    def start(self) -> None:
        """Start all samplers."""
        for sampler in self.samplers.values():
            sampler.start()

    def stop(self) -> dict[str, SamplingResult]:
        """Stop all samplers and return results.

        Returns:
            Mapping of name -> SamplingResult
        """
        results = {}
        for name, sampler in self.samplers.items():
            results[name] = sampler.stop()
        return results

    def get_combined_result(self) -> SamplingResult:
        """Get combined result across all containers.

        Returns:
            SamplingResult with summed memory values
        """
        all_results = self.stop()

        if not all_results:
            return SamplingResult()

        # Sum up memory values
        total_peak = sum(r.memory_peak_bytes for r in all_results.values())
        total_avg = sum(r.memory_avg_bytes for r in all_results.values())
        total_min = sum(r.memory_min_bytes for r in all_results.values())
        max_duration = max(r.duration_seconds for r in all_results.values())
        any_oom = any(r.oom_detected for r in all_results.values())
        total_oom_kills = sum(r.oom_kill_count for r in all_results.values())
        total_samples = max(r.sample_count for r in all_results.values())

        return SamplingResult(
            samples=[],  # Combined samples not meaningful
            memory_peak_bytes=total_peak,
            memory_avg_bytes=total_avg,
            memory_min_bytes=total_min,
            duration_seconds=max_duration,
            oom_detected=any_oom,
            oom_kill_count=total_oom_kills,
            sample_count=total_samples,
        )
