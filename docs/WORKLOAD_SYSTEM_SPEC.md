# Spécification : Système de Workloads YAML Composables

## Contexte

Le projet **BaseType Benchmark** compare des paradigmes de stockage (PostgreSQL, Memgraph, Oxigraph) pour applications BOS (Building Operating System) / Digital Twin smart building.

**Problème actuel** : Le benchmark exécute les queries Q1→Q13 séquentiellement, 1x chacune. Ce n'est pas représentatif d'un usage réel où :
- Certaines queries (dashboard) sont appelées fréquemment
- D'autres (rapports) sont rares mais lourdes
- Les appels sont concurrents (multi-utilisateurs)

**Solution** : Système de workloads configurables par YAML.

---

## IMPORTANT : Relation avec RAM-Gradient

Le **RAM-Gradient** (déjà implémenté dans run.py) est le protocole central du benchmark :
```
Pour chaque scénario (P1, M1, O1, ...):
    Pour chaque niveau RAM (512MB, 1GB, 2GB, 4GB, ...):
        1. Redémarrer containers avec limite RAM
        2. Charger les données
        3. Exécuter les queries  ← C'EST ICI QUE LE WORKLOAD INTERVIENT
        4. Collecter métriques
```

**Le workload ne remplace PAS le RAM-Gradient** - il définit *comment* les queries sont exécutées à l'étape 3.

| Aspect | RAM-Gradient (existant) | Workload (nouveau) |
|--------|------------------------|-------------------|
| Contrôle | Limite mémoire Docker | Pattern d'exécution queries |
| Boucle | Externe (niveaux RAM) | Interne (queries) |
| Fichier | run.py lignes 800-1200 | workload/*.py |
| Config | Menu interactif / AUTO | YAML templates |

**Intégration** : Le workload s'exécute à CHAQUE niveau RAM du gradient :
```python
for ram_gb in ram_levels:           # RAM-Gradient (inchangé)
    restart_with_ram_limit(ram_gb)
    load_data()

    # NOUVEAU: Exécution via workload
    if workload_config:
        executor = WorkloadExecutor(config=workload_config, ...)
        result = executor.run()
    else:
        # Ancien comportement: Q1→Q13 séquentiel
        for query in queries:
            execute_query(query)
```

---

## Architecture Cible

```
src/basetype_benchmark/runner/
├── metrics/                    # NOUVEAU MODULE (remplace metrics.py)
│   ├── __init__.py            # Re-exports backward compatible
│   ├── cgroup.py              # Fonctions bas niveau cgroup v2
│   ├── snapshot.py            # Metrics dataclass + capture()
│   ├── strategies.py          # PerQueryCollector, AggregateCollector
│   ├── monitor.py             # ResourceMonitor (background sampling)
│   └── utils.py               # check_oom, compute_delta
│
├── workload/                   # NOUVEAU MODULE
│   ├── __init__.py            # Public API
│   ├── config.py              # Dataclasses + chargement YAML
│   ├── selector.py            # Sélecteurs de queries
│   └── executor.py            # WorkloadExecutor
│
├── metrics.py                  # À SUPPRIMER après migration
├── protocol.py                 # Inchangé
└── scenario.py                 # Inchangé

config/workloads/               # NOUVEAU
├── debug_sequential.yaml       # Mode actuel (backward compat)
├── bos_operational.yaml        # Stress réaliste BOS
├── dashboard_only.yaml         # Queries dashboard
├── analytics_heavy.yaml        # Focus analytics
├── report_batch.yaml           # Rapports lourds
└── mixed_realistic.yaml        # Mix pondéré
```

---

## Phase 1 : Refactorisation metrics.py → metrics/

### Fichier source actuel

**Chemin** : `c:\DEV\benchmark\src\basetype_benchmark\runner\metrics.py` (367 lignes)

**Structure actuelle** :
```
Lignes 1-16    : Imports + IS_LINUX
Lignes 22-59   : get_cgroup_path()
Lignes 61-74   : read_memory_current(), read_memory_peak()
Lignes 77-112  : reset_memory_peak() [FIXÉ récemment]
Lignes 115-159 : read_cpu_usage(), get_cgroup_metrics()
Lignes 166-233 : Metrics dataclass + capture() + reset_peak()
Lignes 236-249 : compute_delta()
Lignes 252-269 : check_oom(), get_peak_memory_mb()
Lignes 276-366 : ResourceMonitor, ResourceSnapshot, ResourceStats
```

### 1.1 Créer metrics/cgroup.py

```python
"""Low-level cgroup v2 filesystem operations.

Reads container metrics directly from Linux cgroup v2 filesystem.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional

IS_LINUX = os.name == "posix" and os.path.exists("/sys/fs/cgroup")


def get_cgroup_path(container_name: str) -> Optional[Path]:
    """Get cgroup v2 path for a Docker container.

    Args:
        container_name: Docker container name (e.g., "btb_timescaledb")

    Returns:
        Path to cgroup directory or None if not found
    """
    if not IS_LINUX:
        return None

    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.Id}}", container_name],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return None

        container_id = result.stdout.strip()
        if not container_id:
            return None

        # cgroup v2 paths (Linux)
        candidates = [
            Path(f"/sys/fs/cgroup/system.slice/docker-{container_id}.scope"),
            Path(f"/sys/fs/cgroup/docker/{container_id}"),
        ]

        for path in candidates:
            if path.exists():
                return path

        return None
    except Exception:
        return None


def read_memory_current(cgroup_path: Path) -> int:
    """Read current memory usage in bytes."""
    mem_file = cgroup_path / "memory.current"
    if mem_file.exists():
        return int(mem_file.read_text().strip())
    return 0


def read_memory_peak(cgroup_path: Path) -> int:
    """Read peak memory usage in bytes."""
    mem_file = cgroup_path / "memory.peak"
    if mem_file.exists():
        return int(mem_file.read_text().strip())
    return 0


def reset_memory_peak(cgroup_path: Path) -> bool:
    """Reset memory.peak counter (requires root).

    Returns True only if peak was actually reset (value decreased).
    This verification is critical - without it, peak accumulates across queries.
    """
    if not cgroup_path:
        return False

    peak_file = cgroup_path / "memory.peak"
    if not peak_file.exists():
        return False

    try:
        # 1. Read BEFORE
        peak_before = int(peak_file.read_text().strip())

        # 2. Write "0"
        try:
            peak_file.write_text("0")
        except PermissionError:
            # Try with sudo if direct write fails
            if not str(peak_file).startswith("/sys/fs/cgroup/"):
                return False
            result = subprocess.run(
                ["sudo", "-n", "tee", str(peak_file)],
                input="0", text=True, capture_output=True,
            )
            if result.returncode != 0:
                return False

        # 3. Verify AFTER - did the reset actually work?
        peak_after = int(peak_file.read_text().strip())
        return peak_after < peak_before

    except Exception:
        return False


def read_cpu_usage(cgroup_path: Path) -> int:
    """Read CPU usage in microseconds."""
    cpu_file = cgroup_path / "cpu.stat"
    if cpu_file.exists():
        for line in cpu_file.read_text().splitlines():
            if line.startswith("usage_usec"):
                return int(line.split()[1])
    return 0


def get_cgroup_metrics(cgroup_path: Path) -> Optional[Dict]:
    """Read all cgroup v2 metrics from filesystem.

    Returns:
        Dict with memory_bytes, memory_peak_bytes, cpu_usage_usec, etc.
    """
    if not cgroup_path or not cgroup_path.exists():
        return None

    metrics = {}
    try:
        mem_current = cgroup_path / "memory.current"
        if mem_current.exists():
            metrics["memory_bytes"] = int(mem_current.read_text().strip())

        mem_peak = cgroup_path / "memory.peak"
        if mem_peak.exists():
            metrics["memory_peak_bytes"] = int(mem_peak.read_text().strip())

        cpu_stat = cgroup_path / "cpu.stat"
        if cpu_stat.exists():
            for line in cpu_stat.read_text().strip().split("\n"):
                parts = line.split()
                if len(parts) == 2:
                    key, value = parts
                    if key == "usage_usec":
                        metrics["cpu_usage_usec"] = int(value)
                    elif key == "user_usec":
                        metrics["cpu_user_usec"] = int(value)
                    elif key == "system_usec":
                        metrics["cpu_system_usec"] = int(value)

        return metrics if metrics else None
    except Exception:
        return None
```

### 1.2 Créer metrics/snapshot.py

```python
"""Container metrics snapshot.

Captures point-in-time resource usage from Docker containers.
"""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .cgroup import get_cgroup_path, get_cgroup_metrics, reset_memory_peak


@dataclass
class Metrics:
    """Container metrics snapshot."""
    container: str
    timestamp: float
    memory_mb: float
    memory_peak_mb: float
    cpu_time_sec: float
    cgroup_path: Optional[Path] = None

    @classmethod
    def capture(cls, container_name: str) -> "Metrics":
        """Capture current metrics for a container."""
        cgroup_path = get_cgroup_path(container_name)
        metrics = get_cgroup_metrics(cgroup_path) if cgroup_path else None

        if metrics:
            return cls(
                container=container_name,
                timestamp=time.time(),
                memory_mb=metrics.get("memory_bytes", 0) / (1024 * 1024),
                memory_peak_mb=metrics.get("memory_peak_bytes", 0) / (1024 * 1024),
                cpu_time_sec=metrics.get("cpu_usage_usec", 0) / 1_000_000,
                cgroup_path=cgroup_path,
            )

        # Fallback to docker stats
        return cls._from_docker_stats(container_name)

    @classmethod
    def _from_docker_stats(cls, container_name: str) -> "Metrics":
        """Fallback: get metrics from docker stats."""
        try:
            result = subprocess.run(
                f"docker stats --no-stream --format '{{{{.MemUsage}}}}' {container_name}",
                shell=True, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                usage = result.stdout.strip().split("/")[0].strip()
                mem_mb = 0.0
                if "GiB" in usage:
                    mem_mb = float(usage.replace("GiB", "").strip()) * 1024
                elif "MiB" in usage:
                    mem_mb = float(usage.replace("MiB", "").strip())

                return cls(
                    container=container_name,
                    timestamp=time.time(),
                    memory_mb=mem_mb,
                    memory_peak_mb=mem_mb,  # No peak available via docker stats
                    cpu_time_sec=0.0,
                )
        except Exception:
            pass

        return cls(
            container=container_name,
            timestamp=time.time(),
            memory_mb=0.0,
            memory_peak_mb=0.0,
            cpu_time_sec=0.0,
        )

    def reset_peak(self) -> bool:
        """Reset memory peak counter (for query-only measurements)."""
        if self.cgroup_path:
            return reset_memory_peak(self.cgroup_path)
        return False
```

### 1.3 Créer metrics/utils.py

```python
"""Utility functions for metrics processing."""

import subprocess
from typing import Dict

from .cgroup import get_cgroup_path, read_memory_peak
from .snapshot import Metrics


def compute_delta(before: Metrics, after: Metrics) -> Dict:
    """Compute resource usage delta between two snapshots."""
    wall_time = after.timestamp - before.timestamp
    cpu_delta = after.cpu_time_sec - before.cpu_time_sec

    return {
        "memory_before_mb": before.memory_mb,
        "memory_after_mb": after.memory_mb,
        "memory_delta_mb": after.memory_mb - before.memory_mb,
        "memory_peak_mb": after.memory_peak_mb,
        "cpu_time_sec": cpu_delta,
        "cpu_percent": (cpu_delta / wall_time * 100) if wall_time > 0 else 0.0,
        "wall_time_sec": wall_time,
    }


def check_oom(container_name: str) -> bool:
    """Check if container was OOM-killed."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.OOMKilled}}", container_name],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip().lower() == "true"
    except Exception:
        return False


def get_peak_memory_mb(container_name: str) -> float:
    """Get peak memory usage for a container in MB."""
    cgroup_path = get_cgroup_path(container_name)
    if cgroup_path:
        return read_memory_peak(cgroup_path) / (1024 * 1024)
    return 0.0
```

### 1.4 Créer metrics/monitor.py

```python
"""Background resource monitoring for containers.

Provides continuous sampling of container resources during workload execution.
"""

import time
from dataclasses import dataclass
from pathlib import Path
from threading import Event, Thread
from typing import List, Optional

from .cgroup import get_cgroup_path, read_memory_current, read_cpu_usage


@dataclass
class ResourceSnapshot:
    """Single resource measurement."""
    timestamp: float
    mem_bytes: int
    cpu_usage_usec: int


@dataclass
class ResourceStats:
    """Aggregated resource statistics."""
    mem_mb_avg: float = 0.0
    mem_mb_max: float = 0.0
    mem_mb_min: float = 0.0
    cpu_pct_avg: float = 0.0
    samples: int = 0


class ResourceMonitor:
    """Background resource monitor for containers.

    Usage:
        monitor = ResourceMonitor("btb_timescaledb", interval_s=1.0)
        monitor.start()
        # ... run workload ...
        stats = monitor.stop()
    """

    def __init__(self, container_name: str, interval_s: float = 1.0):
        self.container_name = container_name
        self.interval_s = interval_s
        self._samples: List[ResourceSnapshot] = []
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._cgroup_path: Optional[Path] = None

    def start(self) -> bool:
        """Start background monitoring."""
        self._cgroup_path = get_cgroup_path(self.container_name)
        if not self._cgroup_path:
            return False

        self._samples.clear()
        self._stop_event.clear()
        self._thread = Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> ResourceStats:
        """Stop monitoring and return aggregated stats."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

        return self._compute_stats()

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while not self._stop_event.is_set():
            if self._cgroup_path:
                snapshot = ResourceSnapshot(
                    timestamp=time.time(),
                    mem_bytes=read_memory_current(self._cgroup_path),
                    cpu_usage_usec=read_cpu_usage(self._cgroup_path),
                )
                self._samples.append(snapshot)

            self._stop_event.wait(self.interval_s)

    def _compute_stats(self) -> ResourceStats:
        """Compute aggregated statistics from samples."""
        if not self._samples:
            return ResourceStats()

        mem_mb = [s.mem_bytes / (1024 * 1024) for s in self._samples]

        # CPU percentage: delta usage / delta time
        cpu_pcts = []
        for i in range(1, len(self._samples)):
            dt = self._samples[i].timestamp - self._samples[i - 1].timestamp
            du = self._samples[i].cpu_usage_usec - self._samples[i - 1].cpu_usage_usec
            if dt > 0:
                cpu_pcts.append((du / 1_000_000) / dt * 100)

        return ResourceStats(
            mem_mb_avg=sum(mem_mb) / len(mem_mb) if mem_mb else 0,
            mem_mb_max=max(mem_mb) if mem_mb else 0,
            mem_mb_min=min(mem_mb) if mem_mb else 0,
            cpu_pct_avg=sum(cpu_pcts) / len(cpu_pcts) if cpu_pcts else 0,
            samples=len(self._samples),
        )
```

### 1.5 Créer metrics/strategies.py

```python
"""Metrics collection strategies for different workload types.

Two strategies:
- PerQueryCollector: Reset peak before each query (debug/isolation mode)
- AggregateCollector: Reset only after load (realistic stress test)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from .snapshot import Metrics


@dataclass
class QueryMetrics:
    """Metrics result for a single query execution."""
    query_id: str
    latency_ms: float
    row_count: int
    memory_mb: float
    peak_memory_mb: float
    status: str = "ok"
    error: Optional[str] = None


class MetricsCollector(ABC):
    """Abstract interface for metrics collection.

    Implementations define when/how memory peak is reset.
    """

    def __init__(self, containers: List[str]):
        """Initialize collector.

        Args:
            containers: Container names WITHOUT btb_ prefix (e.g., ["timescaledb"])
        """
        self.containers = [f"btb_{c}" for c in containers]
        self._results: List[QueryMetrics] = []

    @abstractmethod
    def on_workload_start(self) -> None:
        """Called at workload start (after data load)."""
        pass

    @abstractmethod
    def before_query(self, query_id: str) -> None:
        """Called before each query execution."""
        pass

    @abstractmethod
    def after_query(
        self,
        query_id: str,
        latency_ms: float,
        row_count: int,
        error: Optional[str] = None
    ) -> QueryMetrics:
        """Called after each query. Returns metrics for this query."""
        pass

    @abstractmethod
    def on_workload_end(self) -> dict:
        """Called at workload end. Returns aggregated stats."""
        pass

    def get_results(self) -> List[QueryMetrics]:
        """Get all collected query metrics."""
        return self._results


class PerQueryCollector(MetricsCollector):
    """Reset peak before each query (debug/isolation mode).

    Use this strategy when you need to measure memory impact
    of each query in isolation.
    """

    def on_workload_start(self) -> None:
        # Initial reset
        for container in self.containers:
            m = Metrics.capture(container)
            m.reset_peak()

    def before_query(self, query_id: str) -> None:
        # Reset peak for isolated measurement
        for container in self.containers:
            m = Metrics.capture(container)
            m.reset_peak()

    def after_query(
        self,
        query_id: str,
        latency_ms: float,
        row_count: int,
        error: Optional[str] = None
    ) -> QueryMetrics:
        # Capture peak (isolated to this query)
        total_mem = sum(Metrics.capture(c).memory_mb for c in self.containers)
        total_peak = sum(Metrics.capture(c).memory_peak_mb for c in self.containers)

        qm = QueryMetrics(
            query_id=query_id,
            latency_ms=latency_ms,
            row_count=row_count,
            memory_mb=total_mem,
            peak_memory_mb=total_peak,
            status="error" if error else "ok",
            error=error,
        )
        self._results.append(qm)
        return qm

    def on_workload_end(self) -> dict:
        return {
            "strategy": "per_query",
            "total_queries": len(self._results),
            "peak_max_mb": max(r.peak_memory_mb for r in self._results) if self._results else 0,
        }


class AggregateCollector(MetricsCollector):
    """No reset between queries (realistic stress mode).

    Use this strategy for stress testing where you want to see
    cumulative memory behavior under sustained load.
    """

    def __init__(self, containers: List[str]):
        super().__init__(containers)
        self._baseline_peak = 0.0

    def on_workload_start(self) -> None:
        # Reset only once after load
        for container in self.containers:
            m = Metrics.capture(container)
            m.reset_peak()
        self._baseline_peak = sum(
            Metrics.capture(c).memory_peak_mb for c in self.containers
        )

    def before_query(self, query_id: str) -> None:
        # NO reset - accumulate
        pass

    def after_query(
        self,
        query_id: str,
        latency_ms: float,
        row_count: int,
        error: Optional[str] = None
    ) -> QueryMetrics:
        # Capture cumulative peak
        total_mem = sum(Metrics.capture(c).memory_mb for c in self.containers)
        total_peak = sum(Metrics.capture(c).memory_peak_mb for c in self.containers)

        qm = QueryMetrics(
            query_id=query_id,
            latency_ms=latency_ms,
            row_count=row_count,
            memory_mb=total_mem,
            peak_memory_mb=total_peak,  # Cumulative since load
            status="error" if error else "ok",
            error=error,
        )
        self._results.append(qm)
        return qm

    def on_workload_end(self) -> dict:
        final_peak = sum(Metrics.capture(c).memory_peak_mb for c in self.containers)
        return {
            "strategy": "aggregate",
            "total_queries": len(self._results),
            "baseline_peak_mb": self._baseline_peak,
            "final_peak_mb": final_peak,
            "peak_growth_mb": final_peak - self._baseline_peak,
        }


def create_collector(strategy: str, containers: List[str]) -> MetricsCollector:
    """Factory to create appropriate collector.

    Args:
        strategy: "per_query" or "aggregate"
        containers: Container names without btb_ prefix

    Returns:
        MetricsCollector instance
    """
    if strategy == "aggregate":
        return AggregateCollector(containers)
    return PerQueryCollector(containers)
```

### 1.6 Créer metrics/__init__.py

```python
"""Resource metrics collection for Docker containers.

This module provides:
- Metrics: Point-in-time container resource snapshot
- MetricsCollector strategies: per_query vs aggregate
- ResourceMonitor: Background continuous monitoring
- Low-level cgroup v2 functions

Backward compatible with previous metrics.py imports:
    from basetype_benchmark.runner.metrics import Metrics, check_oom, compute_delta
"""

from .snapshot import Metrics
from .utils import check_oom, compute_delta, get_peak_memory_mb
from .strategies import (
    MetricsCollector,
    PerQueryCollector,
    AggregateCollector,
    QueryMetrics,
    create_collector,
)
from .monitor import ResourceMonitor, ResourceSnapshot, ResourceStats
from .cgroup import (
    get_cgroup_path,
    read_memory_current,
    read_memory_peak,
    reset_memory_peak,
    read_cpu_usage,
    get_cgroup_metrics,
    IS_LINUX,
)

__all__ = [
    # Backward compatible exports
    "Metrics",
    "check_oom",
    "compute_delta",
    "get_peak_memory_mb",
    # New strategies
    "MetricsCollector",
    "PerQueryCollector",
    "AggregateCollector",
    "QueryMetrics",
    "create_collector",
    # Monitor
    "ResourceMonitor",
    "ResourceSnapshot",
    "ResourceStats",
    # Low-level (for advanced use)
    "get_cgroup_path",
    "read_memory_current",
    "read_memory_peak",
    "reset_memory_peak",
    "read_cpu_usage",
    "get_cgroup_metrics",
    "IS_LINUX",
]
```

### 1.7 Actions post-création

1. **Supprimer** l'ancien fichier :
   ```
   c:\DEV\benchmark\src\basetype_benchmark\runner\metrics.py
   ```

2. **Vérifier** que run.py fonctionne toujours :
   ```bash
   cd c:\DEV\benchmark
   python -c "from basetype_benchmark.runner.metrics import Metrics, check_oom, compute_delta; print('OK')"
   ```

---

## Phase 2 : Module workload/

### 2.1 Créer workload/config.py

```python
"""Workload configuration dataclasses and YAML loading."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

import yaml


class MetricsStrategy(Enum):
    """How to collect metrics during workload."""
    PER_QUERY = "per_query"      # Reset peak before each query
    AGGREGATE = "aggregate"      # Reset only after load


class ExecutionMode(Enum):
    """How to execute the workload."""
    SEQUENTIAL = "sequential"    # Each query N times in order
    DURATION = "duration"        # Run for N seconds
    ITERATIONS = "iterations"    # Run N total queries


class SelectionStrategy(Enum):
    """How to select next query."""
    SEQUENTIAL = "sequential"        # Q1, Q2, ..., Q13, Q1, ...
    WEIGHTED_RANDOM = "weighted_random"  # Random based on weights
    ROUND_ROBIN = "round_robin"      # Proportional to weights


@dataclass
class QuerySpec:
    """Specification for a single query in workload."""
    id: str                          # Q1, Q2, ..., Q13, or ALL
    weight: int = 10                 # Relative weight (default 10)
    category: str = "default"        # For reporting: dashboard, analytics, report


@dataclass
class MetricsConfig:
    """Metrics collection configuration."""
    strategy: MetricsStrategy = MetricsStrategy.PER_QUERY


@dataclass
class ExecutionConfig:
    """Workload execution configuration."""
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    duration_seconds: int = 60           # For DURATION mode
    iterations: int = 100                # For ITERATIONS mode
    iterations_per_query: int = 1        # For SEQUENTIAL mode
    concurrency: int = 1                 # Number of threads
    warmup_iterations: int = 0           # Warmup before measurement


@dataclass
class SelectionConfig:
    """Query selection configuration."""
    strategy: SelectionStrategy = SelectionStrategy.SEQUENTIAL
    seed: Optional[int] = None           # For reproducibility


@dataclass
class WorkloadConfig:
    """Complete workload configuration."""
    name: str
    description: str = ""
    version: str = "1.0"
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    queries: List[QuerySpec] = field(default_factory=list)
    selection: SelectionConfig = field(default_factory=SelectionConfig)

    @classmethod
    def load(cls, path: Path) -> "WorkloadConfig":
        """Load workload configuration from YAML file.

        Args:
            path: Path to YAML file

        Returns:
            WorkloadConfig instance
        """
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        wl = data.get("workload", {})
        metrics_data = data.get("metrics", {})
        exec_data = data.get("execution", {})
        sel_data = data.get("selection", {})
        queries_data = data.get("queries", [])

        # Parse metrics
        metrics = MetricsConfig(
            strategy=MetricsStrategy(metrics_data.get("strategy", "per_query"))
        )

        # Parse execution
        execution = ExecutionConfig(
            mode=ExecutionMode(exec_data.get("mode", "sequential")),
            duration_seconds=exec_data.get("duration_seconds", 60),
            iterations=exec_data.get("iterations", 100),
            iterations_per_query=exec_data.get("iterations_per_query", 1),
            concurrency=exec_data.get("concurrency", 1),
            warmup_iterations=exec_data.get("warmup_iterations", 0),
        )

        # Parse selection
        selection = SelectionConfig(
            strategy=SelectionStrategy(sel_data.get("strategy", "sequential")),
            seed=sel_data.get("seed"),
        )

        # Parse queries
        queries = []
        for q in queries_data:
            if isinstance(q, str):
                queries.append(QuerySpec(id=q))
            else:
                queries.append(QuerySpec(
                    id=q.get("id", "Q1"),
                    weight=q.get("weight", 10),
                    category=q.get("category", "default"),
                ))

        return cls(
            name=wl.get("name", path.stem),
            description=wl.get("description", ""),
            version=wl.get("version", "1.0"),
            metrics=metrics,
            execution=execution,
            queries=queries,
            selection=selection,
        )

    def expand_queries(self, all_queries: List[str]) -> List[QuerySpec]:
        """Expand 'ALL' to actual query list.

        Args:
            all_queries: List of all available query IDs (e.g., ["Q1", "Q2", ...])

        Returns:
            List of QuerySpec with ALL expanded
        """
        result = []
        for q in self.queries:
            if q.id == "ALL":
                for qid in all_queries:
                    result.append(QuerySpec(
                        id=qid,
                        weight=q.weight,
                        category=q.category,
                    ))
            else:
                result.append(q)
        return result
```

### 2.2 Créer workload/selector.py

```python
"""Query selectors for workload execution."""

import random
from abc import ABC, abstractmethod
from typing import List, Optional

from .config import QuerySpec, SelectionStrategy


class QuerySelector(ABC):
    """Abstract base for query selection."""

    def __init__(self, queries: List[QuerySpec], seed: Optional[int] = None):
        self.queries = queries
        self.seed = seed
        self._index = 0

    @abstractmethod
    def next(self) -> QuerySpec:
        """Get next query to execute."""
        pass

    def reset(self) -> None:
        """Reset selector state."""
        self._index = 0


class SequentialSelector(QuerySelector):
    """Select queries in order: Q1, Q2, ..., Q13, Q1, ..."""

    def next(self) -> QuerySpec:
        query = self.queries[self._index % len(self.queries)]
        self._index += 1
        return query


class WeightedRandomSelector(QuerySelector):
    """Select queries randomly based on weights."""

    def __init__(self, queries: List[QuerySpec], seed: Optional[int] = None):
        super().__init__(queries, seed)
        self._rng = random.Random(seed)
        self._weights = [q.weight for q in queries]

    def next(self) -> QuerySpec:
        return self._rng.choices(self.queries, weights=self._weights, k=1)[0]

    def reset(self) -> None:
        super().reset()
        self._rng = random.Random(self.seed)


class RoundRobinSelector(QuerySelector):
    """Select queries proportionally to weights in round-robin fashion.

    Example: Q1(weight=2), Q2(weight=1) -> Q1, Q1, Q2, Q1, Q1, Q2, ...
    """

    def __init__(self, queries: List[QuerySpec], seed: Optional[int] = None):
        super().__init__(queries, seed)
        # Build expanded list based on weights
        self._expanded: List[QuerySpec] = []
        for q in queries:
            self._expanded.extend([q] * q.weight)

    def next(self) -> QuerySpec:
        query = self._expanded[self._index % len(self._expanded)]
        self._index += 1
        return query


def create_selector(
    strategy: SelectionStrategy,
    queries: List[QuerySpec],
    seed: Optional[int] = None
) -> QuerySelector:
    """Factory to create appropriate selector.

    Args:
        strategy: Selection strategy
        queries: List of query specs
        seed: Random seed for reproducibility

    Returns:
        QuerySelector instance
    """
    if strategy == SelectionStrategy.WEIGHTED_RANDOM:
        return WeightedRandomSelector(queries, seed)
    elif strategy == SelectionStrategy.ROUND_ROBIN:
        return RoundRobinSelector(queries, seed)
    return SequentialSelector(queries, seed)
```

### 2.3 Créer workload/executor.py

```python
"""Workload executor with multi-threading support."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Callable, Dict, List, Optional

from .config import WorkloadConfig, ExecutionMode, QuerySpec
from .selector import create_selector
from ..metrics import create_collector, QueryMetrics, MetricsCollector


@dataclass
class WorkloadResult:
    """Results from workload execution."""
    workload_name: str
    total_queries: int
    total_duration_s: float
    throughput_qps: float
    peak_memory_mb: float
    queries_by_category: Dict[str, int] = field(default_factory=dict)
    query_metrics: List[QueryMetrics] = field(default_factory=list)
    errors: int = 0
    strategy_stats: Dict = field(default_factory=dict)


# Type alias for query executor function
QueryExecutorFn = Callable[[str], tuple]  # (row_count, latency_ms, error)


class WorkloadExecutor:
    """Execute workload with configurable strategy and concurrency.

    Usage:
        config = WorkloadConfig.load("config/workloads/bos_operational.yaml")
        executor = WorkloadExecutor(
            config=config,
            query_executor=lambda qid: engine.execute_query(qid),
            containers=["timescaledb"],
            all_queries=["Q1", "Q2", ..., "Q13"],
        )
        result = executor.run()
    """

    def __init__(
        self,
        config: WorkloadConfig,
        query_executor: QueryExecutorFn,
        containers: List[str],
        all_queries: List[str],
    ):
        """Initialize executor.

        Args:
            config: Workload configuration
            query_executor: Function to execute a query, returns (row_count, latency_ms, error)
            containers: Container names without btb_ prefix
            all_queries: List of all available query IDs
        """
        self.config = config
        self.query_executor = query_executor
        self.containers = containers

        # Expand queries (handle ALL)
        self.queries = config.expand_queries(all_queries)

        # Create selector and collector
        self.selector = create_selector(
            config.selection.strategy,
            self.queries,
            config.selection.seed,
        )
        self.collector = create_collector(
            config.metrics.strategy.value,
            containers,
        )

        # Thread safety
        self._lock = Lock()
        self._stop_flag = False

    def run(self) -> WorkloadResult:
        """Execute the workload.

        Returns:
            WorkloadResult with all metrics
        """
        start_time = time.time()

        # Signal workload start to collector
        self.collector.on_workload_start()

        # Run warmup if configured
        if self.config.execution.warmup_iterations > 0:
            self._run_warmup()

        # Execute based on mode
        mode = self.config.execution.mode
        if mode == ExecutionMode.DURATION:
            self._run_duration_mode()
        elif mode == ExecutionMode.ITERATIONS:
            self._run_iterations_mode()
        else:  # SEQUENTIAL
            self._run_sequential_mode()

        # Signal workload end
        strategy_stats = self.collector.on_workload_end()

        end_time = time.time()
        duration = end_time - start_time

        # Compute results
        results = self.collector.get_results()
        categories: Dict[str, int] = {}
        errors = 0
        peak_max = 0.0

        for r in results:
            # Find category for this query
            for q in self.queries:
                if q.id == r.query_id:
                    cat = q.category
                    categories[cat] = categories.get(cat, 0) + 1
                    break
            if r.status == "error":
                errors += 1
            if r.peak_memory_mb > peak_max:
                peak_max = r.peak_memory_mb

        return WorkloadResult(
            workload_name=self.config.name,
            total_queries=len(results),
            total_duration_s=duration,
            throughput_qps=len(results) / duration if duration > 0 else 0,
            peak_memory_mb=peak_max,
            queries_by_category=categories,
            query_metrics=results,
            errors=errors,
            strategy_stats=strategy_stats,
        )

    def _run_warmup(self) -> None:
        """Run warmup iterations (no metrics collection)."""
        for _ in range(self.config.execution.warmup_iterations):
            query = self.selector.next()
            try:
                self.query_executor(query.id)
            except Exception:
                pass
        self.selector.reset()

    def _run_sequential_mode(self) -> None:
        """Execute each query N times in order."""
        n = self.config.execution.iterations_per_query
        concurrency = self.config.execution.concurrency

        if concurrency > 1:
            self._run_concurrent(self._sequential_tasks(n), concurrency)
        else:
            for query in self.queries:
                for _ in range(n):
                    self._execute_one(query)

    def _run_iterations_mode(self) -> None:
        """Execute N total queries using selector."""
        n = self.config.execution.iterations
        concurrency = self.config.execution.concurrency

        if concurrency > 1:
            self._run_concurrent(self._iteration_tasks(n), concurrency)
        else:
            for _ in range(n):
                query = self.selector.next()
                self._execute_one(query)

    def _run_duration_mode(self) -> None:
        """Execute queries for N seconds."""
        duration = self.config.execution.duration_seconds
        concurrency = self.config.execution.concurrency
        end_time = time.time() + duration

        if concurrency > 1:
            self._run_concurrent_duration(end_time, concurrency)
        else:
            while time.time() < end_time:
                query = self.selector.next()
                self._execute_one(query)

    def _execute_one(self, query: QuerySpec) -> Optional[QueryMetrics]:
        """Execute a single query with metrics collection."""
        self.collector.before_query(query.id)

        start = time.time()
        error = None
        row_count = 0

        try:
            result = self.query_executor(query.id)
            if isinstance(result, tuple) and len(result) >= 2:
                row_count = result[0]
                # latency_ms might be in result[1], but we measure ourselves
            elif isinstance(result, int):
                row_count = result
        except Exception as e:
            error = str(e)

        latency_ms = (time.time() - start) * 1000

        return self.collector.after_query(query.id, latency_ms, row_count, error)

    def _sequential_tasks(self, n: int):
        """Generator for sequential mode tasks."""
        for query in self.queries:
            for _ in range(n):
                yield query

    def _iteration_tasks(self, n: int):
        """Generator for iteration mode tasks."""
        for _ in range(n):
            yield self.selector.next()

    def _run_concurrent(self, tasks, concurrency: int) -> None:
        """Run tasks with thread pool."""
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for query in tasks:
                futures.append(executor.submit(self._execute_one_threadsafe, query))

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass

    def _run_concurrent_duration(self, end_time: float, concurrency: int) -> None:
        """Run concurrent queries until end_time."""
        self._stop_flag = False

        def worker():
            while not self._stop_flag and time.time() < end_time:
                with self._lock:
                    query = self.selector.next()
                self._execute_one_threadsafe(query)

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker) for _ in range(concurrency)]

            # Wait for end time
            while time.time() < end_time:
                time.sleep(0.1)

            self._stop_flag = True

            for future in futures:
                try:
                    future.result(timeout=5)
                except Exception:
                    pass

    def _execute_one_threadsafe(self, query: QuerySpec) -> Optional[QueryMetrics]:
        """Thread-safe query execution."""
        with self._lock:
            self.collector.before_query(query.id)

        start = time.time()
        error = None
        row_count = 0

        try:
            result = self.query_executor(query.id)
            if isinstance(result, tuple) and len(result) >= 2:
                row_count = result[0]
            elif isinstance(result, int):
                row_count = result
        except Exception as e:
            error = str(e)

        latency_ms = (time.time() - start) * 1000

        with self._lock:
            return self.collector.after_query(query.id, latency_ms, row_count, error)
```

### 2.4 Créer workload/__init__.py

```python
"""Workload configuration and execution.

This module provides a YAML-configurable workload system for
running realistic benchmark scenarios.

Usage:
    from basetype_benchmark.runner.workload import WorkloadConfig, WorkloadExecutor

    config = WorkloadConfig.load("config/workloads/bos_operational.yaml")
    executor = WorkloadExecutor(
        config=config,
        query_executor=lambda qid: engine.execute_query(qid),
        containers=["timescaledb"],
        all_queries=["Q1", "Q2", ..., "Q13"],
    )
    result = executor.run()
"""

from .config import (
    WorkloadConfig,
    QuerySpec,
    MetricsStrategy,
    ExecutionMode,
    SelectionStrategy,
    MetricsConfig,
    ExecutionConfig,
    SelectionConfig,
)
from .selector import (
    QuerySelector,
    SequentialSelector,
    WeightedRandomSelector,
    RoundRobinSelector,
    create_selector,
)
from .executor import WorkloadExecutor, WorkloadResult

__all__ = [
    # Config
    "WorkloadConfig",
    "QuerySpec",
    "MetricsStrategy",
    "ExecutionMode",
    "SelectionStrategy",
    "MetricsConfig",
    "ExecutionConfig",
    "SelectionConfig",
    # Selectors
    "QuerySelector",
    "SequentialSelector",
    "WeightedRandomSelector",
    "RoundRobinSelector",
    "create_selector",
    # Executor
    "WorkloadExecutor",
    "WorkloadResult",
]
```

---

## Phase 3 : Templates YAML

### 3.1 config/workloads/debug_sequential.yaml

```yaml
# Debug mode - reproduces current behavior
# Each query executed once in order, with per-query peak reset

workload:
  name: debug_sequential
  description: "Sequential execution Q1→Q13, reset peak between queries (debug mode)"
  version: "1.0"

metrics:
  strategy: per_query

execution:
  mode: sequential
  iterations_per_query: 1
  concurrency: 1

queries:
  - id: ALL

selection:
  strategy: sequential
```

### 3.2 config/workloads/bos_operational.yaml

```yaml
# BOS Digital Twin - Operational stress test
# Simulates realistic middleware usage with weighted queries

workload:
  name: bos_operational
  description: "BOS middleware stress test - 5min duration, 4 threads, weighted queries"
  version: "1.0"

metrics:
  strategy: aggregate

execution:
  mode: duration
  duration_seconds: 300
  concurrency: 4
  warmup_iterations: 20

queries:
  # Dashboard queries - very frequent (operators monitoring)
  - id: Q1
    weight: 25
    category: dashboard
  - id: Q2
    weight: 20
    category: dashboard
  - id: Q3
    weight: 15
    category: dashboard
  - id: Q4
    weight: 10
    category: dashboard
  - id: Q5
    weight: 10
    category: dashboard

  # Direct TS query - frequent (real-time values)
  - id: Q6
    weight: 15
    category: realtime

  # Hybrid analytics - moderate frequency
  - id: Q7
    weight: 8
    category: analytics
  - id: Q8
    weight: 6
    category: analytics
  - id: Q9
    weight: 5
    category: analytics
  - id: Q10
    weight: 5
    category: analytics
  - id: Q11
    weight: 4
    category: analytics
  - id: Q12
    weight: 3
    category: analytics

  # Heavy report - rare
  - id: Q13
    weight: 2
    category: report

selection:
  strategy: weighted_random
  seed: 42
```

### 3.3 config/workloads/dashboard_only.yaml

```yaml
# Dashboard-only workload
# Simulates operator console refreshing frequently

workload:
  name: dashboard_only
  description: "Dashboard queries only - high frequency graph traversals"
  version: "1.0"

metrics:
  strategy: per_query

execution:
  mode: iterations
  iterations: 500
  concurrency: 2

queries:
  - id: Q1
    weight: 30
    category: dashboard
  - id: Q2
    weight: 25
    category: dashboard
  - id: Q3
    weight: 20
    category: dashboard
  - id: Q4
    weight: 15
    category: dashboard
  - id: Q5
    weight: 10
    category: dashboard

selection:
  strategy: weighted_random
  seed: 123
```

### 3.4 config/workloads/analytics_heavy.yaml

```yaml
# Analytics-heavy workload
# Simulates batch analysis / reporting system

workload:
  name: analytics_heavy
  description: "Focus on hybrid analytics queries (Q6-Q12)"
  version: "1.0"

metrics:
  strategy: aggregate

execution:
  mode: duration
  duration_seconds: 120
  concurrency: 2

queries:
  - id: Q6
    weight: 20
    category: analytics
  - id: Q7
    weight: 15
    category: analytics
  - id: Q8
    weight: 15
    category: analytics
  - id: Q9
    weight: 10
    category: analytics
  - id: Q10
    weight: 10
    category: analytics
  - id: Q11
    weight: 10
    category: analytics
  - id: Q12
    weight: 20
    category: analytics

selection:
  strategy: weighted_random
  seed: 456
```

### 3.5 config/workloads/report_batch.yaml

```yaml
# Report batch workload
# Simulates end-of-day/week report generation

workload:
  name: report_batch
  description: "Heavy report queries (Q13) with some analytics"
  version: "1.0"

metrics:
  strategy: aggregate

execution:
  mode: iterations
  iterations: 50
  concurrency: 1

queries:
  - id: Q12
    weight: 30
    category: analytics
  - id: Q13
    weight: 70
    category: report

selection:
  strategy: weighted_random
  seed: 789
```

### 3.6 config/workloads/mixed_realistic.yaml

```yaml
# Mixed realistic workload
# Balanced mix simulating typical BOS daily operation

workload:
  name: mixed_realistic
  description: "Balanced daily BOS operation - all query types"
  version: "1.0"

metrics:
  strategy: aggregate

execution:
  mode: duration
  duration_seconds: 180
  concurrency: 3
  warmup_iterations: 10

queries:
  # Dashboard (50% of traffic)
  - id: Q1
    weight: 15
    category: dashboard
  - id: Q2
    weight: 12
    category: dashboard
  - id: Q3
    weight: 10
    category: dashboard
  - id: Q4
    weight: 8
    category: dashboard
  - id: Q5
    weight: 5
    category: dashboard

  # Real-time (15% of traffic)
  - id: Q6
    weight: 15
    category: realtime

  # Analytics (30% of traffic)
  - id: Q7
    weight: 8
    category: analytics
  - id: Q8
    weight: 6
    category: analytics
  - id: Q9
    weight: 5
    category: analytics
  - id: Q10
    weight: 4
    category: analytics
  - id: Q11
    weight: 4
    category: analytics
  - id: Q12
    weight: 3
    category: analytics

  # Reports (5% of traffic)
  - id: Q13
    weight: 5
    category: report

selection:
  strategy: weighted_random
  seed: 2024
```

---

## Phase 4 : Intégration run.py

### 4.1 Ajouter import (ligne ~27)

```python
# Après les imports existants
from basetype_benchmark.runner.workload import WorkloadConfig, WorkloadExecutor, WorkloadResult
```

### 4.2 Ajouter argument CLI (fonction main, ~ligne 1650)

```python
# Ajouter dans le parser
parser.add_argument(
    "--workload",
    type=str,
    help="Path to workload YAML file (e.g., config/workloads/bos_operational.yaml)"
)
```

### 4.3 Ajouter menu interactif (~ligne 915, après sélection queries)

```python
# Ajouter une nouvelle sous-section après la sélection des queries

def select_workload_mode(repo_root: Path) -> Optional[WorkloadConfig]:
    """Menu interactif pour sélection du mode workload."""
    log_subsection("Mode d'exécution")

    workloads_dir = repo_root / "config" / "workloads"
    available = []

    if workloads_dir.exists():
        available = sorted(workloads_dir.glob("*.yaml"))

    if not available:
        log_info("Aucun workload YAML trouvé, mode séquentiel par défaut")
        return None

    # Option 0: Mode actuel (séquentiel)
    log_item(f"[0] Séquentiel (défaut) - Q1→Q13, 1x chaque, per_query metrics")

    # Liste des workloads disponibles
    for i, wl_path in enumerate(available, 1):
        try:
            config = WorkloadConfig.load(wl_path)
            log_item(f"[{i}] {config.name}: {config.description[:50]}...")
        except Exception:
            log_item(f"[{i}] {wl_path.name} (erreur de lecture)")

    choice = input("\nChoix [0]: ").strip()

    if not choice or choice == "0":
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(available):
            return WorkloadConfig.load(available[idx])
    except (ValueError, IndexError):
        pass

    log_warning("Choix invalide, mode séquentiel par défaut")
    return None
```

### 4.4 Modifier la boucle d'exécution des queries (~ligne 1104-1180)

```python
# Remplacer la boucle actuelle par:

if workload_config:
    # Mode workload YAML
    log_subsection(f"Exécution workload: {workload_config.name}")
    log_info(f"Mode: {workload_config.execution.mode.value}")
    log_info(f"Stratégie metrics: {workload_config.metrics.strategy.value}")
    log_info(f"Concurrence: {workload_config.execution.concurrency} thread(s)")

    def query_executor_fn(query_id: str) -> tuple:
        """Wrapper pour exécuter une query."""
        row_count, latency_ms = execute_query_for_scenario(
            engine, scenario, query_id, scenario_queries_dir, profile
        )
        return (row_count, latency_ms, None)

    executor = WorkloadExecutor(
        config=workload_config,
        query_executor=query_executor_fn,
        containers=sc_info["containers"],
        all_queries=QUERIES,  # from protocol.py
    )

    wl_result = executor.run()

    # Convertir WorkloadResult en format existant pour résultats
    for qm in wl_result.query_metrics:
        results.append({
            "scenario": scenario,
            "profile": profile,
            "ram_gb": ram_gb,
            "query": qm.query_id,
            "latency_ms": qm.latency_ms,
            "row_count": qm.row_count,
            "peak_ram_mb": qm.peak_memory_mb,
            "status": qm.status,
        })

    log_success(f"Workload terminé: {wl_result.total_queries} queries en {wl_result.total_duration_s:.1f}s")
    log_info(f"Throughput: {wl_result.throughput_qps:.2f} q/s")
    log_info(f"Peak RAM: {wl_result.peak_memory_mb:.1f} MB")

else:
    # Mode séquentiel actuel (backward compatible)
    # ... code existant inchangé ...
```

---

## Améliorations intégrées

### A1. Validation YAML avec Pydantic

Remplacer les dataclasses simples par Pydantic pour validation automatique :

```python
# Dans workload/config.py - utiliser pydantic au lieu de dataclasses

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum

class MetricsStrategy(str, Enum):
    PER_QUERY = "per_query"
    AGGREGATE = "aggregate"

class QuerySpec(BaseModel):
    id: str = Field(..., pattern=r"^(Q\d{1,2}|ALL)$")
    weight: int = Field(default=10, ge=1, le=100)
    category: str = Field(default="default")

    @field_validator("id")
    @classmethod
    def validate_query_id(cls, v):
        if v != "ALL" and v not in [f"Q{i}" for i in range(1, 14)]:
            raise ValueError(f"Invalid query ID: {v}")
        return v

class WorkloadConfig(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    # ... autres champs avec validation
```

**Note** : Si Pydantic n'est pas souhaité (dépendance supplémentaire), garder dataclasses avec validation manuelle dans `load()`.

### A2. Percentiles de latence dans WorkloadResult

```python
# Dans workload/executor.py

import statistics
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class LatencyStats:
    """Latency statistics with percentiles."""
    min_ms: float = 0.0
    max_ms: float = 0.0
    avg_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0

    @classmethod
    def from_latencies(cls, latencies: List[float]) -> "LatencyStats":
        if not latencies:
            return cls()
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        return cls(
            min_ms=sorted_lat[0],
            max_ms=sorted_lat[-1],
            avg_ms=statistics.mean(sorted_lat),
            p50_ms=sorted_lat[int(n * 0.50)],
            p95_ms=sorted_lat[int(n * 0.95)] if n >= 20 else sorted_lat[-1],
            p99_ms=sorted_lat[int(n * 0.99)] if n >= 100 else sorted_lat[-1],
        )

@dataclass
class WorkloadResult:
    """Results from workload execution."""
    workload_name: str
    total_queries: int
    total_duration_s: float
    throughput_qps: float

    # Latency stats
    latency_stats: LatencyStats = field(default_factory=LatencyStats)
    latency_by_query: Dict[str, LatencyStats] = field(default_factory=dict)

    # Memory
    peak_memory_mb: float = 0.0
    memory_by_container: Dict[str, float] = field(default_factory=dict)

    # ... reste inchangé
```

### A3. Catégories de queries centralisées

Créer un fichier de référence plutôt que redéfinir dans chaque YAML :

```python
# Dans src/basetype_benchmark/runner/protocol.py (existant)

# Ajouter après QUERY_TYPE

QUERY_CATEGORY = {
    "Q1": "dashboard",
    "Q2": "dashboard",
    "Q3": "dashboard",
    "Q4": "dashboard",
    "Q5": "dashboard",
    "Q6": "realtime",
    "Q7": "analytics",
    "Q8": "analytics",
    "Q9": "analytics",
    "Q10": "analytics",
    "Q11": "analytics",
    "Q12": "analytics",
    "Q13": "report",
}

def get_query_category(query_id: str) -> str:
    """Get default category for a query."""
    return QUERY_CATEGORY.get(query_id, "default")
```

Dans les YAML, la catégorie devient optionnelle (utilise le défaut si non spécifiée) :

```yaml
queries:
  - id: Q1
    weight: 25
    # category: dashboard  # optionnel, utilise QUERY_CATEGORY["Q1"] par défaut
```

### A4. Reset peak après warmup

```python
# Dans workload/executor.py

def _run_warmup(self) -> None:
    """Run warmup iterations (no metrics collection)."""
    for _ in range(self.config.execution.warmup_iterations):
        query = self.selector.next()
        try:
            self.query_executor(query.id)
        except Exception:
            pass

    # IMPORTANT: Reset peak RAM après warmup
    # Sinon le peak du warmup pollue les mesures
    for container in self.collector.containers:
        m = Metrics.capture(container)
        m.reset_peak()

    self.selector.reset()
```

### A5. Avertissement per_query + concurrency

```python
# Dans workload/executor.py - __init__

def __init__(self, config: WorkloadConfig, ...):
    # ... existing code ...

    # Warn about incompatible settings
    if (config.metrics.strategy == MetricsStrategy.PER_QUERY
        and config.execution.concurrency > 1):
        import warnings
        warnings.warn(
            "per_query metrics strategy with concurrency > 1 may give "
            "inaccurate per-query peak RAM (race condition on reset). "
            "Consider using 'aggregate' strategy for concurrent workloads.",
            UserWarning
        )
```

### A6. Agrégation multi-containers (réponse à la question)

Pour les scénarios hybrides (M2 = Memgraph + TimescaleDB), l'agrégation se fait ainsi :

```python
# Dans metrics/strategies.py

class MetricsCollector(ABC):
    """Abstract interface for metrics collection."""

    def __init__(self, containers: List[str]):
        """Initialize collector.

        Args:
            containers: Container names WITHOUT btb_ prefix
                       Ex: ["memgraph", "timescaledb"] for M2
        """
        self.containers = [f"btb_{c}" for c in containers]
        self._results: List[QueryMetrics] = []
        self._per_container_peak: Dict[str, float] = {}

    def _capture_all(self) -> tuple:
        """Capture metrics from all containers.

        Returns:
            (total_memory_mb, total_peak_mb, per_container_dict)
        """
        total_mem = 0.0
        total_peak = 0.0
        per_container = {}

        for container in self.containers:
            m = Metrics.capture(container)
            total_mem += m.memory_mb
            total_peak += m.memory_peak_mb
            per_container[container] = {
                "memory_mb": m.memory_mb,
                "peak_mb": m.memory_peak_mb,
            }
            # Track max peak per container
            if container not in self._per_container_peak:
                self._per_container_peak[container] = 0.0
            self._per_container_peak[container] = max(
                self._per_container_peak[container],
                m.memory_peak_mb
            )

        return total_mem, total_peak, per_container
```

**Dans WorkloadResult** :

```python
@dataclass
class WorkloadResult:
    # ... existing fields ...

    # Multi-container breakdown
    memory_by_container: Dict[str, float] = field(default_factory=dict)
    # Ex: {"btb_memgraph": 512.3, "btb_timescaledb": 234.1}
```

**Mapping scénario → containers** (à ajouter dans scenario.py ou utiliser l'existant) :

```python
SCENARIO_CONTAINERS = {
    "P1": ["timescaledb"],
    "P2": ["timescaledb"],
    "M1": ["memgraph"],
    "M2": ["memgraph", "timescaledb"],
    "O1": ["oxigraph"],
    "O2": ["oxigraph", "timescaledb"],
}
```

L'appel dans run.py utilise déjà `sc_info["containers"]` qui contient cette info.

---

## Commandes de test

### Test backward compatibility

```bash
cd c:\DEV\benchmark
python -c "from basetype_benchmark.runner.metrics import Metrics, check_oom, compute_delta; print('Metrics OK')"
python -c "from basetype_benchmark.runner.workload import WorkloadConfig, WorkloadExecutor; print('Workload OK')"
```

### Test chargement YAML

```bash
python -c "
from basetype_benchmark.runner.workload import WorkloadConfig
config = WorkloadConfig.load('config/workloads/debug_sequential.yaml')
print(f'Name: {config.name}')
print(f'Mode: {config.execution.mode}')
print(f'Queries: {len(config.queries)}')
"
```

### Test exécution complète

```bash
# Mode séquentiel (backward compat)
python run.py

# Mode workload YAML
python run.py --workload config/workloads/bos_operational.yaml
```

---

## Checklist d'implémentation

### Phase 1 : metrics/ module
- [ ] Créer `src/basetype_benchmark/runner/metrics/` directory
- [ ] Créer `metrics/cgroup.py`
- [ ] Créer `metrics/snapshot.py`
- [ ] Créer `metrics/utils.py`
- [ ] Créer `metrics/monitor.py`
- [ ] Créer `metrics/strategies.py`
- [ ] Créer `metrics/__init__.py`
- [ ] Supprimer `metrics.py` (l'ancien fichier)
- [ ] Tester import backward compatible

### Phase 2 : workload/ module
- [ ] Créer `src/basetype_benchmark/runner/workload/` directory
- [ ] Créer `workload/config.py`
- [ ] Créer `workload/selector.py`
- [ ] Créer `workload/executor.py`
- [ ] Créer `workload/__init__.py`
- [ ] Tester chargement YAML

### Phase 3 : Templates YAML
- [ ] Créer `config/workloads/` directory
- [ ] Créer `debug_sequential.yaml`
- [ ] Créer `bos_operational.yaml`
- [ ] Créer `dashboard_only.yaml`
- [ ] Créer `analytics_heavy.yaml`
- [ ] Créer `report_batch.yaml`
- [ ] Créer `mixed_realistic.yaml`

### Phase 4 : Intégration run.py
- [ ] Ajouter import workload
- [ ] Ajouter argument CLI `--workload`
- [ ] Ajouter menu interactif
- [ ] Modifier boucle d'exécution
- [ ] Tester mode séquentiel (backward compat)
- [ ] Tester mode workload YAML

---

## Notes techniques

### Dépendance PyYAML
Le module `yaml` est requis. Vérifier qu'il est installé :
```bash
pip install pyyaml
```

### Thread-safety
Le `WorkloadExecutor` utilise un `Lock` pour protéger :
- L'accès au selector (génération des queries)
- L'accès au collector (stockage des métriques)

### Backward compatibility
L'import existant continue de fonctionner :
```python
from basetype_benchmark.runner.metrics import Metrics, check_oom, compute_delta
```

Sans `--workload`, run.py utilise le comportement actuel.
