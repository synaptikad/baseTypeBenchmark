"""Extended Resource Monitor for cloud/Docker benchmarks.

Collects comprehensive metrics during query execution:
- CPU: user, system, iowait, per-core utilization
- Memory: RSS, cache, swap, page faults
- I/O: IOPS, throughput, latency (via iostat)
- Network: packets, bytes, errors
- Energy: RAPL power estimation (if available on Intel CPUs)

Designed for Linux servers with Docker containers (OVH, VPS, etc.).
"""
from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class ResourceSample:
    """Single resource sample at a point in time."""
    timestamp: float = 0.0

    # CPU metrics
    cpu_pct: float = 0.0
    cpu_user_pct: float = 0.0
    cpu_system_pct: float = 0.0
    cpu_iowait_pct: float = 0.0
    cpu_cores_pct: List[float] = field(default_factory=list)

    # Memory metrics (MB)
    mem_used_mb: float = 0.0
    mem_rss_mb: float = 0.0
    mem_cache_mb: float = 0.0
    mem_swap_mb: float = 0.0
    mem_limit_mb: float = 0.0
    mem_pct: float = 0.0

    # I/O metrics
    block_read_mb: float = 0.0
    block_write_mb: float = 0.0
    block_read_iops: float = 0.0
    block_write_iops: float = 0.0

    # Network metrics
    net_rx_mb: float = 0.0
    net_tx_mb: float = 0.0
    net_rx_packets: int = 0
    net_tx_packets: int = 0

    # Energy (Intel RAPL, microjoules)
    energy_pkg_uj: int = 0
    energy_dram_uj: int = 0

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "cpu": {
                "total_pct": self.cpu_pct,
                "user_pct": self.cpu_user_pct,
                "system_pct": self.cpu_system_pct,
                "iowait_pct": self.cpu_iowait_pct,
                "cores_pct": self.cpu_cores_pct,
            },
            "memory": {
                "used_mb": self.mem_used_mb,
                "rss_mb": self.mem_rss_mb,
                "cache_mb": self.mem_cache_mb,
                "swap_mb": self.mem_swap_mb,
                "limit_mb": self.mem_limit_mb,
                "pct": self.mem_pct,
            },
            "io": {
                "block_read_mb": self.block_read_mb,
                "block_write_mb": self.block_write_mb,
                "read_iops": self.block_read_iops,
                "write_iops": self.block_write_iops,
            },
            "network": {
                "rx_mb": self.net_rx_mb,
                "tx_mb": self.net_tx_mb,
                "rx_packets": self.net_rx_packets,
                "tx_packets": self.net_tx_packets,
            },
            "energy": {
                "pkg_uj": self.energy_pkg_uj,
                "dram_uj": self.energy_dram_uj,
            }
        }


class DockerStatsCollector:
    """Collect detailed stats from Docker container using docker stats API."""

    def __init__(self, container_name: str):
        self.container_name = container_name
        self._container_id = None

    def _get_container_id(self) -> Optional[str]:
        """Get container ID from name."""
        if self._container_id:
            return self._container_id
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.Id}}", self.container_name],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self._container_id = result.stdout.strip()[:12]
                return self._container_id
        except Exception:
            pass
        return None

    def collect(self) -> Optional[ResourceSample]:
        """Collect a single sample from Docker stats API (JSON)."""
        try:
            # Use docker stats with JSON format for detailed metrics
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format",
                 '{"cpu":"{{.CPUPerc}}","mem":"{{.MemUsage}}","mem_pct":"{{.MemPerc}}",'
                 '"net":"{{.NetIO}}","block":"{{.BlockIO}}","pids":"{{.PIDs}}"}'],
                capture_output=True, text=True, timeout=10
            )

            # Get stats for our specific container
            lines = result.stdout.strip().split('\n')

            # Run again with container name to get correct stats
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format",
                 '{"cpu":"{{.CPUPerc}}","mem":"{{.MemUsage}}","mem_pct":"{{.MemPerc}}",'
                 '"net":"{{.NetIO}}","block":"{{.BlockIO}}","pids":"{{.PIDs}}"}',
                 self.container_name],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                return None

            data = json.loads(result.stdout.strip())
            sample = ResourceSample(timestamp=time.time())

            # Parse CPU
            sample.cpu_pct = self._parse_pct(data.get("cpu", "0%"))

            # Parse Memory: "1.5GiB / 8GiB"
            mem_parts = data.get("mem", "0B / 0B").split("/")
            sample.mem_used_mb = self._parse_size(mem_parts[0])
            sample.mem_limit_mb = self._parse_size(mem_parts[1]) if len(mem_parts) > 1 else 0
            sample.mem_pct = self._parse_pct(data.get("mem_pct", "0%"))

            # Parse Block I/O: "1.5GB / 500MB"
            block_parts = data.get("block", "0B / 0B").split("/")
            sample.block_read_mb = self._parse_size(block_parts[0])
            sample.block_write_mb = self._parse_size(block_parts[1]) if len(block_parts) > 1 else 0

            # Parse Network: "1.5GB / 500MB"
            net_parts = data.get("net", "0B / 0B").split("/")
            sample.net_rx_mb = self._parse_size(net_parts[0])
            sample.net_tx_mb = self._parse_size(net_parts[1]) if len(net_parts) > 1 else 0

            return sample

        except (json.JSONDecodeError, subprocess.TimeoutExpired, Exception):
            return None

    def collect_detailed(self) -> Optional[ResourceSample]:
        """Collect detailed stats using docker API directly via inspect."""
        container_id = self._get_container_id()
        if not container_id:
            return self.collect()  # Fallback to basic stats

        try:
            # Use cgroup files directly for more detailed stats
            sample = self.collect()  # Start with basic stats
            if not sample:
                sample = ResourceSample(timestamp=time.time())

            # Try to get detailed CPU from cgroup (Docker uses cgroup v2 on modern systems)
            cpu_stats = self._read_cgroup_cpu(container_id)
            if cpu_stats:
                sample.cpu_user_pct = cpu_stats.get("user_pct", 0)
                sample.cpu_system_pct = cpu_stats.get("system_pct", 0)

            # Try to get detailed memory stats
            mem_stats = self._read_cgroup_memory(container_id)
            if mem_stats:
                sample.mem_rss_mb = mem_stats.get("rss_mb", 0)
                sample.mem_cache_mb = mem_stats.get("cache_mb", 0)
                sample.mem_swap_mb = mem_stats.get("swap_mb", 0)

            return sample

        except Exception:
            return self.collect()  # Fallback

    def _read_cgroup_cpu(self, container_id: str) -> Optional[Dict]:
        """Read CPU stats from cgroup (requires host access)."""
        # This would require mounting cgroup fs or using docker exec
        # For now, return None and rely on docker stats
        return None

    def _read_cgroup_memory(self, container_id: str) -> Optional[Dict]:
        """Read memory stats from cgroup."""
        return None

    @staticmethod
    def _parse_pct(s: str) -> float:
        """Parse percentage string: '25.5%' -> 25.5"""
        try:
            return float(s.replace("%", "").strip())
        except (ValueError, AttributeError):
            return 0.0

    @staticmethod
    def _parse_size(s: str) -> float:
        """Parse size string to MB."""
        s = s.strip()
        try:
            if "GiB" in s or "GB" in s:
                return float(s.replace("GiB", "").replace("GB", "").strip()) * 1024
            elif "MiB" in s or "MB" in s:
                return float(s.replace("MiB", "").replace("MB", "").strip())
            elif "KiB" in s or "KB" in s or "kB" in s:
                return float(s.replace("KiB", "").replace("KB", "").replace("kB", "").strip()) / 1024
            elif "B" in s:
                return float(s.replace("B", "").strip()) / (1024 * 1024)
            return 0.0
        except (ValueError, AttributeError):
            return 0.0


class HostStatsCollector:
    """Collect host-level stats (CPU, memory, disk I/O, energy)."""

    def __init__(self):
        self._prev_cpu_stats: Optional[Dict] = None
        self._prev_io_stats: Optional[Dict] = None
        self._prev_time: float = 0
        self._rapl_available = self._check_rapl()

    def _check_rapl(self) -> bool:
        """Check if Intel RAPL is available for energy measurement."""
        rapl_path = Path("/sys/class/powercap/intel-rapl")
        return rapl_path.exists()

    def collect(self) -> ResourceSample:
        """Collect host-level metrics."""
        sample = ResourceSample(timestamp=time.time())

        # CPU stats from /proc/stat
        cpu_stats = self._read_proc_stat()
        if cpu_stats and self._prev_cpu_stats:
            delta_time = sample.timestamp - self._prev_time
            if delta_time > 0:
                cpu_delta = self._calc_cpu_delta(self._prev_cpu_stats, cpu_stats, delta_time)
                sample.cpu_user_pct = cpu_delta.get("user", 0)
                sample.cpu_system_pct = cpu_delta.get("system", 0)
                sample.cpu_iowait_pct = cpu_delta.get("iowait", 0)
                sample.cpu_pct = cpu_delta.get("total", 0)
                sample.cpu_cores_pct = cpu_delta.get("cores", [])

        self._prev_cpu_stats = cpu_stats
        self._prev_time = sample.timestamp

        # Memory stats from /proc/meminfo
        mem_stats = self._read_proc_meminfo()
        if mem_stats:
            sample.mem_used_mb = mem_stats.get("used_mb", 0)
            sample.mem_cache_mb = mem_stats.get("cached_mb", 0)
            sample.mem_swap_mb = mem_stats.get("swap_used_mb", 0)

        # Disk I/O from /proc/diskstats
        io_stats = self._read_proc_diskstats()
        if io_stats and self._prev_io_stats:
            delta_time = sample.timestamp - self._prev_time
            if delta_time > 0:
                sample.block_read_iops = (io_stats["reads"] - self._prev_io_stats["reads"]) / delta_time
                sample.block_write_iops = (io_stats["writes"] - self._prev_io_stats["writes"]) / delta_time
        self._prev_io_stats = io_stats

        # Energy from RAPL
        if self._rapl_available:
            energy = self._read_rapl_energy()
            sample.energy_pkg_uj = energy.get("pkg", 0)
            sample.energy_dram_uj = energy.get("dram", 0)

        return sample

    def _read_proc_stat(self) -> Optional[Dict]:
        """Read /proc/stat for CPU statistics."""
        try:
            with open("/proc/stat", "r") as f:
                lines = f.readlines()

            result = {"total": None, "cores": []}

            for line in lines:
                if line.startswith("cpu "):
                    # Total CPU: cpu  user nice system idle iowait irq softirq steal guest guest_nice
                    parts = line.split()[1:]
                    result["total"] = {
                        "user": int(parts[0]) + int(parts[1]),  # user + nice
                        "system": int(parts[2]),
                        "idle": int(parts[3]),
                        "iowait": int(parts[4]) if len(parts) > 4 else 0,
                        "total": sum(int(p) for p in parts[:8] if p.isdigit())
                    }
                elif line.startswith("cpu") and line[3].isdigit():
                    # Per-core stats
                    parts = line.split()[1:]
                    result["cores"].append({
                        "user": int(parts[0]) + int(parts[1]),
                        "system": int(parts[2]),
                        "idle": int(parts[3]),
                        "total": sum(int(p) for p in parts[:8] if p.isdigit())
                    })

            return result
        except (FileNotFoundError, PermissionError, IndexError):
            return None

    def _calc_cpu_delta(self, prev: Dict, curr: Dict, delta_time: float) -> Dict:
        """Calculate CPU usage percentages from delta."""
        result = {"user": 0, "system": 0, "iowait": 0, "total": 0, "cores": []}

        if prev.get("total") and curr.get("total"):
            p, c = prev["total"], curr["total"]
            total_delta = c["total"] - p["total"]
            if total_delta > 0:
                result["user"] = 100.0 * (c["user"] - p["user"]) / total_delta
                result["system"] = 100.0 * (c["system"] - p["system"]) / total_delta
                result["iowait"] = 100.0 * (c["iowait"] - p["iowait"]) / total_delta
                result["total"] = 100.0 * (1 - (c["idle"] - p["idle"]) / total_delta)

        # Per-core
        for i, (pc, cc) in enumerate(zip(prev.get("cores", []), curr.get("cores", []))):
            total_delta = cc["total"] - pc["total"]
            if total_delta > 0:
                core_pct = 100.0 * (1 - (cc["idle"] - pc["idle"]) / total_delta)
                result["cores"].append(round(core_pct, 1))

        return result

    def _read_proc_meminfo(self) -> Optional[Dict]:
        """Read /proc/meminfo for memory statistics."""
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()

            mem = {}
            for line in lines:
                parts = line.split()
                key = parts[0].rstrip(":")
                value = int(parts[1]) / 1024  # KB to MB

                if key == "MemTotal":
                    mem["total_mb"] = value
                elif key == "MemFree":
                    mem["free_mb"] = value
                elif key == "Buffers":
                    mem["buffers_mb"] = value
                elif key == "Cached":
                    mem["cached_mb"] = value
                elif key == "SwapTotal":
                    mem["swap_total_mb"] = value
                elif key == "SwapFree":
                    mem["swap_free_mb"] = value

            mem["used_mb"] = mem.get("total_mb", 0) - mem.get("free_mb", 0) - mem.get("buffers_mb", 0) - mem.get("cached_mb", 0)
            mem["swap_used_mb"] = mem.get("swap_total_mb", 0) - mem.get("swap_free_mb", 0)

            return mem
        except (FileNotFoundError, PermissionError, IndexError):
            return None

    def _read_proc_diskstats(self) -> Optional[Dict]:
        """Read /proc/diskstats for I/O statistics."""
        try:
            with open("/proc/diskstats", "r") as f:
                lines = f.readlines()

            total_reads = 0
            total_writes = 0

            for line in lines:
                parts = line.split()
                if len(parts) >= 14:
                    # Skip loop and dm devices, focus on actual disks
                    device = parts[2]
                    if device.startswith(("sd", "nvme", "xvd")):  # AWS uses xvd* or nvme*
                        total_reads += int(parts[3])   # reads completed
                        total_writes += int(parts[7])  # writes completed

            return {"reads": total_reads, "writes": total_writes}
        except (FileNotFoundError, PermissionError, IndexError):
            return None

    def _read_rapl_energy(self) -> Dict:
        """Read Intel RAPL energy counters."""
        result = {"pkg": 0, "dram": 0}

        try:
            # Package energy (CPU + uncore)
            pkg_path = Path("/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj")
            if pkg_path.exists():
                result["pkg"] = int(pkg_path.read_text().strip())

            # DRAM energy (if available)
            dram_path = Path("/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:2/energy_uj")
            if dram_path.exists():
                result["dram"] = int(dram_path.read_text().strip())
        except (FileNotFoundError, PermissionError, ValueError):
            pass

        return result


class ExtendedResourceMonitor:
    """Extended resource monitor combining container and host metrics.

    Usage:
        monitor = ExtendedResourceMonitor("btb_postgres", interval_s=0.5)
        monitor.start()
        # ... run query ...
        metrics = monitor.stop()
    """

    def __init__(self, container_name: str, interval_s: float = 0.5,
                 collect_host: bool = True, collect_energy: bool = True):
        self.container_name = container_name
        self.interval_s = interval_s
        self.collect_host = collect_host
        self.collect_energy = collect_energy

        self.docker_collector = DockerStatsCollector(container_name)
        self.host_collector = HostStatsCollector() if collect_host else None

        self.samples: List[ResourceSample] = []
        self._stop_event: Optional[threading.Event] = None
        self._thread: Optional[threading.Thread] = None
        self._start_time: float = 0
        self._start_energy: Dict = {}

    def _sample_loop(self):
        """Background sampling loop."""
        while not self._stop_event.is_set():
            sample = self.docker_collector.collect_detailed()
            if sample:
                sample.timestamp = time.time() - self._start_time

                # Merge host stats if available
                if self.host_collector:
                    host_sample = self.host_collector.collect()
                    # Use host CPU breakdown if container doesn't provide it
                    if host_sample.cpu_user_pct > 0 and sample.cpu_user_pct == 0:
                        sample.cpu_user_pct = host_sample.cpu_user_pct
                        sample.cpu_system_pct = host_sample.cpu_system_pct
                        sample.cpu_iowait_pct = host_sample.cpu_iowait_pct
                        sample.cpu_cores_pct = host_sample.cpu_cores_pct

                    # Always use host IOPS (container block I/O is cumulative)
                    sample.block_read_iops = host_sample.block_read_iops
                    sample.block_write_iops = host_sample.block_write_iops

                    # Energy from host
                    sample.energy_pkg_uj = host_sample.energy_pkg_uj
                    sample.energy_dram_uj = host_sample.energy_dram_uj

                self.samples.append(sample)

            time.sleep(self.interval_s)

    def start(self):
        """Start background monitoring."""
        self.samples = []
        self._start_time = time.time()

        # Capture initial energy reading
        if self.collect_energy and self.host_collector:
            initial = self.host_collector.collect()
            self._start_energy = {
                "pkg": initial.energy_pkg_uj,
                "dram": initial.energy_dram_uj
            }

        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def stop(self) -> Dict:
        """Stop monitoring and return aggregated metrics."""
        if self._stop_event:
            self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

        return self._aggregate()

    def _aggregate(self) -> Dict:
        """Aggregate samples into summary metrics."""
        if not self.samples:
            return self._empty_metrics()

        duration = self.samples[-1].timestamp if self.samples else 0

        # CPU aggregation
        cpu_total = [s.cpu_pct for s in self.samples if s.cpu_pct > 0]
        cpu_user = [s.cpu_user_pct for s in self.samples if s.cpu_user_pct > 0]
        cpu_system = [s.cpu_system_pct for s in self.samples if s.cpu_system_pct > 0]
        cpu_iowait = [s.cpu_iowait_pct for s in self.samples if s.cpu_iowait_pct > 0]

        # Memory aggregation
        mem_used = [s.mem_used_mb for s in self.samples if s.mem_used_mb > 0]
        mem_rss = [s.mem_rss_mb for s in self.samples if s.mem_rss_mb > 0]
        mem_cache = [s.mem_cache_mb for s in self.samples if s.mem_cache_mb > 0]

        # I/O aggregation (delta between first and last for cumulative metrics)
        first = self.samples[0]
        last = self.samples[-1]
        io_read_mb = last.block_read_mb - first.block_read_mb
        io_write_mb = last.block_write_mb - first.block_write_mb

        # IOPS average
        iops_read = [s.block_read_iops for s in self.samples if s.block_read_iops > 0]
        iops_write = [s.block_write_iops for s in self.samples if s.block_write_iops > 0]

        # Network delta
        net_rx_mb = last.net_rx_mb - first.net_rx_mb
        net_tx_mb = last.net_tx_mb - first.net_tx_mb

        # Energy calculation (delta from start)
        energy_pkg_wh = 0
        energy_dram_wh = 0
        if self._start_energy and last.energy_pkg_uj > 0:
            # Convert microjoules to watt-hours: 1 Wh = 3,600,000,000 µJ
            energy_pkg_uj = last.energy_pkg_uj - self._start_energy.get("pkg", 0)
            energy_dram_uj = last.energy_dram_uj - self._start_energy.get("dram", 0)
            energy_pkg_wh = energy_pkg_uj / 3_600_000_000
            energy_dram_wh = energy_dram_uj / 3_600_000_000

        return {
            "sample_count": len(self.samples),
            "duration_s": duration,
            "cpu": {
                "total_pct": self._stats(cpu_total),
                "user_pct": self._stats(cpu_user),
                "system_pct": self._stats(cpu_system),
                "iowait_pct": self._stats(cpu_iowait),
            },
            "memory": {
                "used_mb": self._stats(mem_used),
                "rss_mb": self._stats(mem_rss),
                "cache_mb": self._stats(mem_cache),
            },
            "io": {
                "read_mb": io_read_mb,
                "write_mb": io_write_mb,
                "read_iops": self._stats(iops_read),
                "write_iops": self._stats(iops_write),
            },
            "network": {
                "rx_mb": net_rx_mb,
                "tx_mb": net_tx_mb,
            },
            "energy": {
                "pkg_wh": energy_pkg_wh,
                "dram_wh": energy_dram_wh,
                "total_wh": energy_pkg_wh + energy_dram_wh,
                "available": self._start_energy.get("pkg", 0) > 0,
            },
            # Keep raw samples for detailed analysis
            "samples": [s.to_dict() for s in self.samples] if len(self.samples) <= 1000 else None,
        }

    @staticmethod
    def _stats(values: List[float]) -> Dict:
        """Compute min/max/avg/median for a list of values."""
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "median": 0}

        sorted_vals = sorted(values)
        return {
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "avg": round(sum(values) / len(values), 2),
            "median": round(sorted_vals[len(sorted_vals) // 2], 2),
        }

    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure."""
        return {
            "sample_count": 0,
            "duration_s": 0,
            "cpu": {"total_pct": {}, "user_pct": {}, "system_pct": {}, "iowait_pct": {}},
            "memory": {"used_mb": {}, "rss_mb": {}, "cache_mb": {}},
            "io": {"read_mb": 0, "write_mb": 0, "read_iops": {}, "write_iops": {}},
            "network": {"rx_mb": 0, "tx_mb": 0},
            "energy": {"pkg_wh": 0, "dram_wh": 0, "total_wh": 0, "available": False},
            "samples": None,
        }


class CloudMetadataCollector:
    """Collect cloud instance metadata (supports multiple providers).

    Currently detects:
    - OVH/OpenStack (primary target)
    - Generic Linux VPS

    Note: Cloud-specific metadata collection is optional.
    The benchmark works on any Linux server with Docker.
    """

    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout
        self._is_cloud: Optional[bool] = None
        self._provider: Optional[str] = None

    def is_cloud(self) -> bool:
        """Check if running on a cloud instance."""
        if self._is_cloud is not None:
            return self._is_cloud

        # Check for common cloud indicators
        try:
            # Check for cloud-init (common on cloud VMs)
            cloud_init = Path("/run/cloud-init")
            if cloud_init.exists():
                self._is_cloud = True
                self._provider = "cloud"
                return True

            # Check DMI for virtualization
            dmi_path = Path("/sys/class/dmi/id/sys_vendor")
            if dmi_path.exists():
                vendor = dmi_path.read_text().strip().lower()
                if any(v in vendor for v in ["ovh", "openstack", "kvm", "qemu"]):
                    self._is_cloud = True
                    self._provider = "ovh" if "ovh" in vendor else "vps"
                    return True
        except Exception:
            pass

        self._is_cloud = False
        return False

    def get_instance_info(self) -> Dict:
        """Get cloud instance information."""
        if not self.is_cloud():
            return {"is_cloud": False}

        info = {
            "is_cloud": True,
            "provider": self._provider,
        }

        # Get hostname
        try:
            info["hostname"] = platform.node()
        except Exception:
            pass

        # Get vCPUs
        try:
            info["vcpus"] = os.cpu_count()
        except Exception:
            pass

        # Get total RAM
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        mem_kb = int(line.split()[1])
                        info["ram_gb"] = round(mem_kb / 1024 / 1024, 1)
                        break
        except Exception:
            pass

        return info

    def get_cpu_options(self) -> Dict:
        """Get vCPU information."""
        try:
            with open("/proc/cpuinfo", "r") as f:
                content = f.read()
                vcpus = content.count("processor")
                return {"vcpus": vcpus}
        except Exception:
            return {}


# Backward compatibility alias
EC2MetadataCollector = CloudMetadataCollector


def get_system_info() -> Dict:
    """Collect comprehensive system information for benchmark context.

    Returns:
        Dict with system, EC2, and Docker information
    """
    import platform

    info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
    }

    # CPU info
    try:
        with open("/proc/cpuinfo", "r") as f:
            content = f.read()
            info["cpu_count"] = content.count("processor")
            # Get model name
            for line in content.split("\n"):
                if "model name" in line:
                    info["cpu_model"] = line.split(":")[1].strip()
                    break
    except Exception:
        pass

    # Memory info
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if "MemTotal" in line:
                    mem_kb = int(line.split()[1])
                    info["total_memory_gb"] = round(mem_kb / 1024 / 1024, 1)
                    break
    except Exception:
        pass

    # Cloud metadata (OVH, VPS, etc.)
    cloud = CloudMetadataCollector()
    cloud_info = cloud.get_instance_info()
    if cloud_info.get("is_cloud"):
        info["cloud"] = cloud_info
        info["cloud"]["cpu_options"] = cloud.get_cpu_options()

    # Docker version
    try:
        result = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            info["docker_version"] = result.stdout.strip()
    except Exception:
        pass

    return info


# Convenience function for backward compatibility
def create_monitor(container_name: str, interval_s: float = 0.5,
                   extended: bool = True) -> ExtendedResourceMonitor:
    """Create a resource monitor (extended or basic).

    Args:
        container_name: Docker container to monitor
        interval_s: Sampling interval in seconds
        extended: If True, collect extended metrics (host CPU, energy, etc.)

    Returns:
        ExtendedResourceMonitor instance
    """
    return ExtendedResourceMonitor(
        container_name,
        interval_s=interval_s,
        collect_host=extended,
        collect_energy=extended
    )
