"""Checkpoint system for resumable benchmarks.

Allows benchmark runs to be interrupted and resumed without losing progress.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class BenchmarkRun:
    """Single benchmark run configuration and status."""
    scenario: str
    profile: str
    ram_mb: int
    status: str = "pending"  # pending, running, completed, failed, skipped
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_s: Optional[float] = None
    error: Optional[str] = None
    result_file: Optional[str] = None

    @property
    def run_id(self) -> str:
        """Unique identifier for this run."""
        return f"{self.scenario}_{self.profile}_{self.ram_mb}MB"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkRun":
        return cls(**data)


@dataclass
class BenchmarkCheckpoint:
    """Checkpoint state for a benchmark session."""
    session_id: str
    created_at: str
    updated_at: str
    config: Dict[str, Any]
    runs: List[BenchmarkRun] = field(default_factory=list)

    # Stats
    total_runs: int = 0
    completed_runs: int = 0
    failed_runs: int = 0
    skipped_runs: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "config": self.config,
            "runs": [r.to_dict() for r in self.runs],
            "stats": {
                "total": self.total_runs,
                "completed": self.completed_runs,
                "failed": self.failed_runs,
                "skipped": self.skipped_runs,
                "pending": self.total_runs - self.completed_runs - self.failed_runs - self.skipped_runs
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkCheckpoint":
        runs = [BenchmarkRun.from_dict(r) for r in data.get("runs", [])]
        stats = data.get("stats", {})
        return cls(
            session_id=data["session_id"],
            created_at=data["created_at"],
            updated_at=data.get("updated_at", data["created_at"]),
            config=data.get("config", {}),
            runs=runs,
            total_runs=stats.get("total", len(runs)),
            completed_runs=stats.get("completed", 0),
            failed_runs=stats.get("failed", 0),
            skipped_runs=stats.get("skipped", 0)
        )

    def update_stats(self):
        """Recalculate stats from runs."""
        self.total_runs = len(self.runs)
        self.completed_runs = sum(1 for r in self.runs if r.status == "completed")
        self.failed_runs = sum(1 for r in self.runs if r.status == "failed")
        self.skipped_runs = sum(1 for r in self.runs if r.status == "skipped")


class CheckpointManager:
    """Manages benchmark checkpoints for resumable runs."""

    def __init__(self, results_dir: Path | str = "benchmark_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoint: Optional[BenchmarkCheckpoint] = None
        self._checkpoint_file: Optional[Path] = None

    def create_session(
        self,
        scenarios: List[str],
        profiles: List[str],
        ram_levels: List[int],
        config: Optional[Dict[str, Any]] = None
    ) -> BenchmarkCheckpoint:
        """Create a new benchmark session with checkpoint."""
        # Generate session ID from config hash
        config_str = f"{sorted(scenarios)}_{sorted(profiles)}_{sorted(ram_levels)}"
        session_id = hashlib.md5(config_str.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{timestamp}_{session_id}"

        # Create session directory
        session_dir = self.results_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Create runs
        runs = []
        for scenario in scenarios:
            for profile in profiles:
                for ram in ram_levels:
                    runs.append(BenchmarkRun(
                        scenario=scenario,
                        profile=profile,
                        ram_mb=ram
                    ))

        # Create checkpoint
        now = datetime.now().isoformat()
        checkpoint = BenchmarkCheckpoint(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            config=config or {
                "scenarios": scenarios,
                "profiles": profiles,
                "ram_levels": ram_levels
            },
            runs=runs,
            total_runs=len(runs)
        )

        self._checkpoint = checkpoint
        self._checkpoint_file = session_dir / "checkpoint.json"
        self._save()

        return checkpoint

    def load_session(self, session_id: str) -> Optional[BenchmarkCheckpoint]:
        """Load an existing session from checkpoint."""
        session_dir = self.results_dir / session_id
        checkpoint_file = session_dir / "checkpoint.json"

        if not checkpoint_file.exists():
            return None

        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self._checkpoint = BenchmarkCheckpoint.from_dict(data)
        self._checkpoint_file = checkpoint_file
        return self._checkpoint

    def find_latest_session(self) -> Optional[str]:
        """Find the most recent session ID."""
        sessions = sorted(
            [d.name for d in self.results_dir.iterdir() if d.is_dir()],
            reverse=True
        )
        return sessions[0] if sessions else None

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions with their status."""
        sessions = []
        for session_dir in sorted(self.results_dir.iterdir(), reverse=True):
            if not session_dir.is_dir():
                continue

            checkpoint_file = session_dir / "checkpoint.json"
            if checkpoint_file.exists():
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                stats = data.get("stats", {})
                sessions.append({
                    "session_id": session_dir.name,
                    "created_at": data.get("created_at"),
                    "total": stats.get("total", 0),
                    "completed": stats.get("completed", 0),
                    "failed": stats.get("failed", 0),
                    "pending": stats.get("pending", 0)
                })
            else:
                sessions.append({
                    "session_id": session_dir.name,
                    "status": "no checkpoint"
                })

        return sessions

    def get_next_run(self) -> Optional[BenchmarkRun]:
        """Get the next pending run."""
        if not self._checkpoint:
            return None

        for run in self._checkpoint.runs:
            if run.status == "pending":
                return run

        return None

    def get_pending_runs(self) -> List[BenchmarkRun]:
        """Get all pending runs."""
        if not self._checkpoint:
            return []
        return [r for r in self._checkpoint.runs if r.status == "pending"]

    def mark_running(self, run: BenchmarkRun):
        """Mark a run as currently running."""
        run.status = "running"
        run.started_at = datetime.now().isoformat()
        self._save()

    def mark_completed(self, run: BenchmarkRun, result_file: Optional[str] = None, duration_s: Optional[float] = None):
        """Mark a run as completed."""
        run.status = "completed"
        run.completed_at = datetime.now().isoformat()
        run.result_file = result_file
        run.duration_s = duration_s
        self._checkpoint.completed_runs += 1
        self._save()

    def mark_failed(self, run: BenchmarkRun, error: str):
        """Mark a run as failed."""
        run.status = "failed"
        run.completed_at = datetime.now().isoformat()
        run.error = error
        self._checkpoint.failed_runs += 1
        self._save()

    def mark_skipped(self, run: BenchmarkRun, reason: str):
        """Mark a run as skipped (e.g., OOM prediction)."""
        run.status = "skipped"
        run.error = reason
        self._checkpoint.skipped_runs += 1
        self._save()

    def _save(self):
        """Save checkpoint to disk."""
        if not self._checkpoint or not self._checkpoint_file:
            return

        self._checkpoint.updated_at = datetime.now().isoformat()
        self._checkpoint.update_stats()

        with open(self._checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(self._checkpoint.to_dict(), f, indent=2)

    def get_session_dir(self) -> Optional[Path]:
        """Get current session directory."""
        if self._checkpoint_file:
            return self._checkpoint_file.parent
        return None

    def get_progress(self) -> Dict[str, Any]:
        """Get current progress summary."""
        if not self._checkpoint:
            return {"error": "No active session"}

        return {
            "session_id": self._checkpoint.session_id,
            "total": self._checkpoint.total_runs,
            "completed": self._checkpoint.completed_runs,
            "failed": self._checkpoint.failed_runs,
            "skipped": self._checkpoint.skipped_runs,
            "pending": self._checkpoint.total_runs - self._checkpoint.completed_runs - self._checkpoint.failed_runs - self._checkpoint.skipped_runs,
            "progress_pct": round(
                (self._checkpoint.completed_runs + self._checkpoint.failed_runs + self._checkpoint.skipped_runs)
                / self._checkpoint.total_runs * 100, 1
            ) if self._checkpoint.total_runs > 0 else 0
        }

    def generate_report(self) -> str:
        """Generate a text report of the session."""
        if not self._checkpoint:
            return "No active session"

        lines = [
            f"Benchmark Session: {self._checkpoint.session_id}",
            f"Created: {self._checkpoint.created_at}",
            f"Updated: {self._checkpoint.updated_at}",
            "",
            "Progress:",
            f"  Total:     {self._checkpoint.total_runs}",
            f"  Completed: {self._checkpoint.completed_runs}",
            f"  Failed:    {self._checkpoint.failed_runs}",
            f"  Skipped:   {self._checkpoint.skipped_runs}",
            f"  Pending:   {self._checkpoint.total_runs - self._checkpoint.completed_runs - self._checkpoint.failed_runs - self._checkpoint.skipped_runs}",
            "",
            "Runs:"
        ]

        for run in self._checkpoint.runs:
            status_symbol = {
                "completed": "[OK]",
                "failed": "[FAIL]",
                "skipped": "[SKIP]",
                "running": "[...]",
                "pending": "[   ]"
            }.get(run.status, "[???]")

            line = f"  {status_symbol} {run.run_id}"
            if run.duration_s:
                line += f" ({run.duration_s:.1f}s)"
            if run.error:
                line += f" - {run.error}"
            lines.append(line)

        return "\n".join(lines)


def resume_or_create(
    results_dir: str = "benchmark_results",
    scenarios: Optional[List[str]] = None,
    profiles: Optional[List[str]] = None,
    ram_levels: Optional[List[int]] = None
) -> CheckpointManager:
    """Resume latest session or create a new one.

    Args:
        results_dir: Directory for results and checkpoints
        scenarios: List of scenarios (required if creating new)
        profiles: List of profiles (required if creating new)
        ram_levels: List of RAM levels in MB (required if creating new)

    Returns:
        CheckpointManager with loaded or created session
    """
    manager = CheckpointManager(results_dir)

    # Try to resume latest
    latest = manager.find_latest_session()
    if latest:
        checkpoint = manager.load_session(latest)
        if checkpoint:
            pending = manager.get_pending_runs()
            if pending:
                print(f"Resuming session {latest} ({len(pending)} pending runs)")
                return manager

    # Create new session
    if scenarios and profiles and ram_levels:
        manager.create_session(scenarios, profiles, ram_levels)
        print(f"Created new session: {manager._checkpoint.session_id}")
    else:
        raise ValueError("Cannot resume - no pending sessions and no config provided for new session")

    return manager
