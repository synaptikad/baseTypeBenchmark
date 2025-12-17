"""
Outils de mesure des performances et des ressources pour le benchmark.
Les métriques visent la reproductibilité plutôt que l'optimisation.

Inclut:
- Latence des requêtes (p50, p95, min, max)
- Consommation mémoire (steady state, peak)
- Utilisation CPU (moyenne, pics)
- Estimation de la consommation énergétique (via CPU time et RAPL si disponible)
- Usage disque des volumes Docker
"""
from __future__ import annotations

import json
import os
import statistics
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    k = (len(ordered) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(ordered) - 1)
    if f == c:
        return ordered[int(k)]
    d0 = ordered[f] * (c - k)
    d1 = ordered[c] * (k - f)
    return d0 + d1


def latency_stats(latencies: List[float]) -> Dict[str, float]:
    if not latencies:
        return {"p50": 0.0, "p95": 0.0, "min": 0.0, "max": 0.0}
    return {
        "p50": percentile(latencies, 50),
        "p95": percentile(latencies, 95),
        "min": min(latencies),
        "max": max(latencies),
    }


class ResourceSample:
    def __init__(self, timestamp: float, mem_mb: float | None, cpu_pct: float | None):
        self.timestamp = timestamp
        self.mem_mb = mem_mb
        self.cpu_pct = cpu_pct

    def to_dict(self) -> dict:
        return {"t": self.timestamp, "mem_mb": self.mem_mb, "cpu_pct": self.cpu_pct}


class ResourceMonitor:
    def __init__(self, container: Optional[str], interval: float = 1.0):
        self.container = container
        self.interval = interval
        self.samples: List[ResourceSample] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _probe_once(self) -> ResourceSample:
        ts = time.time()
        if not self.container:
            return ResourceSample(ts, None, None)
        try:
            cmd = [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "{{.MemUsage}};{{.CPUPerc}}",
                self.container,
            ]
            out = subprocess.check_output(cmd, text=True).strip().split(";")
            mem_raw = out[0] if out else "0MiB"
            cpu_raw = out[1] if len(out) > 1 else "0.0%"
            mem_mb = _parse_mem_mb(mem_raw)
            cpu_pct = float(cpu_raw.replace("%", "")) if cpu_raw else None
            return ResourceSample(ts, mem_mb, cpu_pct)
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            return ResourceSample(ts, None, None)

    def _run(self) -> None:
        while not self._stop.is_set():
            self.samples.append(self._probe_once())
            time.sleep(self.interval)

    def start(self) -> None:
        if self._thread is None:
            self._stop.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return
        self._stop.set()
        self._thread.join(timeout=self.interval * 2)
        self._thread = None

    def summarize(self) -> dict:
        mem_values = [s.mem_mb for s in self.samples if s.mem_mb is not None]
        cpu_values = [s.cpu_pct for s in self.samples if s.cpu_pct is not None]
        steady_state = statistics.median(mem_values) if mem_values else None
        return {
            "steady_state_mem_mb": steady_state,
            "peak_mem_mb": max(mem_values) if mem_values else None,
            "avg_cpu_pct": statistics.mean(cpu_values) if cpu_values else None,
            "samples": [s.to_dict() for s in self.samples],
        }


def _parse_mem_mb(raw: str) -> float | None:
    try:
        cleaned = raw.split("/")[0].strip()
        value, unit = cleaned.replace("iB", "B").split()
        value = float(value)
        unit = unit.upper()
        if unit.startswith("GB"):
            return value * 1024
        if unit.startswith("MB"):
            return value
        if unit.startswith("KB"):
            return value / 1024
        return None
    except Exception:
        return None


def volume_disk_usage(volume: Optional[str]) -> Optional[float]:
    if not volume:
        return None
    try:
        out = subprocess.check_output(
            ["docker", "volume", "inspect", volume], text=True
        )
        info = json.loads(out)[0]
        usage = info.get("UsageData") or {}
        size = usage.get("Size")
        if size is None:
            return None
        return round(size / (1024 * 1024), 2)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, IndexError):
        return None


def export_csv(path: Path, rows: Iterable[dict], field_order: List[str]) -> None:
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=field_order)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def export_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
