"""Environment diagnostics for BaseType Benchmark.

Goal: quickly validate that Linux/Docker metrics collection will be reliable on
an instance before running a full benchmark campaign.

This script is designed to be safe: read-only except for an optional
memory.peak reset test (best-effort).

Usage (Linux host):
  python scripts/diagnose_env.py --containers btb_timescaledb btb_memgraph btb_oxigraph

Exit code:
  0: diagnostics ran (even if some checks failed)
  2: fatal error (unexpected exception)
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _docker_version() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        r = _run(["docker", "version", "--format", "{{json .}}"], timeout=10)
        out["returncode"] = r.returncode
        out["stderr"] = r.stderr.strip()
        if r.returncode == 0 and r.stdout.strip():
            try:
                out["version"] = json.loads(r.stdout)
            except json.JSONDecodeError:
                out["raw"] = r.stdout.strip()
    except Exception as e:
        out["error"] = repr(e)
    return out


def _compose_version() -> Dict[str, Any]:
    # Try docker compose
    for cmd in (["docker", "compose", "version"], ["docker-compose", "version"]):
        try:
            r = _run(cmd, timeout=10)
            if r.returncode == 0:
                return {"cmd": " ".join(cmd), "stdout": r.stdout.strip()}
        except Exception:
            continue
    return {"cmd": None}


def _is_linux() -> bool:
    return sys.platform.startswith("linux")


def _resolve_cgroup_path(container_name: str) -> Dict[str, Any]:
    """Resolve cgroup v2 path for a Docker container.

    Mirrors the logic currently embedded in run.py, but returns structured
    diagnostics instead of None.
    """
    result: Dict[str, Any] = {"container": container_name, "cgroup_path": None}

    if not _is_linux():
        result["error"] = "not_linux"
        return result

    try:
        r = _run(["docker", "inspect", "--format", "{{.Id}}", container_name], timeout=10)
        if r.returncode != 0:
            result["inspect_error"] = r.stderr.strip() or r.stdout.strip()
            return result

        container_id = r.stdout.strip()
        if not container_id:
            result["inspect_error"] = "empty_container_id"
            return result

        systemd_path = f"/sys/fs/cgroup/system.slice/docker-{container_id}.scope"
        if os.path.exists(systemd_path):
            result["cgroup_path"] = systemd_path
            result["driver"] = "systemd"
            return result

        cgroupfs_path = f"/sys/fs/cgroup/docker/{container_id}"
        if os.path.exists(cgroupfs_path):
            result["cgroup_path"] = cgroupfs_path
            result["driver"] = "cgroupfs"
            return result

        result["inspect_id"] = container_id
        result["error"] = "cgroup_path_not_found"
        return result

    except Exception as e:
        result["error"] = repr(e)
        return result


def _read_int(path: Path) -> Optional[int]:
    try:
        if not path.exists():
            return None
        return int(path.read_text().strip())
    except Exception:
        return None


def _read_text(path: Path) -> Optional[str]:
    try:
        if not path.exists():
            return None
        return path.read_text().strip()
    except Exception:
        return None


def _read_cpu_stat(path: Path) -> Dict[str, int]:
    data: Dict[str, int] = {}
    try:
        if not path.exists():
            return data
        for line in path.read_text().strip().splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1].isdigit():
                data[parts[0]] = int(parts[1])
    except Exception:
        return data
    return data


def _test_reset_memory_peak(cgroup_path: str) -> Dict[str, Any]:
    """Best-effort test: try to reset memory.peak and observe change.

    Note: On some setups, memory.peak may not be writable. We report that.
    """
    out: Dict[str, Any] = {"supported": False, "reset_attempted": False, "reset_ok": False}
    p = Path(cgroup_path) / "memory.peak"
    if not p.exists():
        return out

    before = _read_int(p)
    out["supported"] = True
    out["before"] = before

    out["reset_attempted"] = True
    try:
        p.write_text("0")
        time.sleep(0.05)
        after = _read_int(p)
        out["after"] = after
        # Different kernels behave differently; we accept any successful write.
        out["reset_ok"] = True
    except Exception as e:
        out["error"] = repr(e)
        out["reset_ok"] = False

    return out


def _check_drop_caches() -> Dict[str, Any]:
    """Check whether drop_caches is possible (requires root).

    We do not execute it by default; we only detect if it would likely work.
    """
    if not _is_linux():
        return {"available": False, "reason": "not_linux"}

    target = Path("/proc/sys/vm/drop_caches")
    if not target.exists():
        return {"available": False, "reason": "missing_proc_file"}

    writable = os.access(str(target), os.W_OK)
    return {"available": True, "writable": writable}


def diagnose(containers: List[str]) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "is_linux": _is_linux(),
            "uname": " ".join(platform.uname()),
        },
        "docker": _docker_version(),
        "compose": _compose_version(),
        "cgroup": {
            "is_cgroup_v2": Path("/sys/fs/cgroup/cgroup.controllers").exists() if _is_linux() else False,
        },
        "drop_caches": _check_drop_caches(),
        "containers": [],
    }

    for name in containers:
        item = _resolve_cgroup_path(name)
        cpath = item.get("cgroup_path")
        if cpath:
            p = Path(cpath)
            item["files"] = {
                "memory.current": _read_int(p / "memory.current"),
                "memory.peak": _read_int(p / "memory.peak"),
                "cpu.stat": _read_cpu_stat(p / "cpu.stat"),
                "io.stat": _read_text(p / "io.stat"),
            }
            item["memory_peak_reset_test"] = _test_reset_memory_peak(cpath)
        report["containers"].append(item)

    return report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Diagnose Linux/Docker metrics prerequisites.")
    p.add_argument(
        "--containers",
        nargs="*",
        default=["btb_timescaledb", "btb_memgraph", "btb_oxigraph"],
        help="Docker container names to inspect",
    )
    p.add_argument(
        "--out",
        default=str(REPO_ROOT / "benchmark_results" / "diagnostics.json"),
        help="Output JSON path",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        report = diagnose(args.containers)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Wrote diagnostics: {out_path}")

        # Print a short summary
        if not report["host"]["is_linux"]:
            print("[WARN] Not running on Linux; cgroup metrics will be unavailable.")
        if report["docker"].get("returncode") != 0:
            print("[WARN] Docker not available or not running.")

        cgv2 = report["cgroup"].get("is_cgroup_v2")
        print(f"cgroup v2: {cgv2}")
        for c in report["containers"]:
            name = c["container"]
            path = c.get("cgroup_path")
            if not path:
                print(f"- {name}: no cgroup path ({c.get('error')})")
                continue
            reset = c.get("memory_peak_reset_test", {})
            print(f"- {name}: cgroup ok, memory.peak reset_ok={reset.get('reset_ok', False)}")

        return 0

    except Exception as e:
        print(f"[FATAL] {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
