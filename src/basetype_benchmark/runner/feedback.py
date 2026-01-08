"""Rich-based feedback system for benchmark execution.

Provides 4 verbosity levels:
- QUIET: Minimal output (final result only)
- NORMAL: Progress bars + key events
- VERBOSE: Detailed logs with timestamps
- DASHBOARD: Live dashboard with real-time updates
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TaskID
from rich.table import Table


class FeedbackLevel(Enum):
    """Verbosity levels for feedback."""
    QUIET = 0      # Minimal: final result only
    NORMAL = 1     # Progress bars + key events
    VERBOSE = 2    # Detailed logs
    DASHBOARD = 3  # Live dashboard


@dataclass
class BenchmarkProgress:
    """Track benchmark progress state."""
    # Overall
    total_paradigms: int = 0
    current_paradigm_idx: int = 0
    current_paradigm: str = ""

    # Per paradigm
    total_ram_levels: int = 0
    current_ram_level_idx: int = 0
    current_ram_mb: int = 0

    # Per RAM level
    total_queries: int = 0
    current_query_idx: int = 0
    current_query: str = ""

    # Per query
    total_runs: int = 0
    current_run: int = 0

    # Phase
    phase: str = "init"  # init, export, load, warmup, run, cleanup

    # Results so far
    completed_results: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Timing
    start_time: datetime = field(default_factory=datetime.now)

    @property
    def eta_seconds(self) -> float:
        """Estimate time remaining based on work done."""
        elapsed = (datetime.now() - self.start_time).total_seconds()

        total_work = self.total_paradigms * self.total_ram_levels * max(self.total_queries, 1) * max(self.total_runs, 1)
        done_work = (
            self.current_paradigm_idx * self.total_ram_levels * max(self.total_queries, 1) * max(self.total_runs, 1) +
            self.current_ram_level_idx * max(self.total_queries, 1) * max(self.total_runs, 1) +
            self.current_query_idx * max(self.total_runs, 1) +
            self.current_run
        )

        if done_work == 0 or total_work == 0:
            return 0.0

        rate = elapsed / done_work
        remaining = total_work - done_work
        return rate * remaining

    @property
    def progress_percent(self) -> float:
        """Overall progress percentage."""
        total_work = self.total_paradigms * self.total_ram_levels * max(self.total_queries, 1)
        done_work = (
            self.current_paradigm_idx * self.total_ram_levels * max(self.total_queries, 1) +
            self.current_ram_level_idx * max(self.total_queries, 1) +
            self.current_query_idx
        )

        if total_work == 0:
            return 0.0
        return (done_work / total_work) * 100


class FeedbackManager:
    """Manage benchmark feedback based on verbosity level.

    Usage:
        feedback = FeedbackManager(level=FeedbackLevel.NORMAL)
        feedback.start(config)

        feedback.on_paradigm_start("P1", 0)
        feedback.on_phase("export")
        feedback.on_phase("load")
        feedback.on_ram_level(32768, 0)
        feedback.on_query("Q1", 0)
        feedback.on_run(1, "success", 12.3)
        feedback.on_level_complete(32768, "success", 245.3)
        feedback.on_paradigm_complete("P1", 8192, 20, 23)

        feedback.stop()
    """

    PHASE_ICONS = {
        "init": ".",
        "export": "P",  # Package
        "load": "L",    # Load
        "warmup": "W",  # Warmup
        "run": ">",     # Run
        "cleanup": "C", # Cleanup
    }

    def __init__(self, level: FeedbackLevel = FeedbackLevel.NORMAL):
        self.level = level
        self.console = Console()
        self.progress = BenchmarkProgress()
        self._live: Live | None = None
        self._progress_bar: Progress | None = None
        self._tasks: dict[str, TaskID] = {}

    def start(self, paradigms: list[str], ram_levels: list[int], queries: list[str] | None, n_runs: int, n_variants: int) -> None:
        """Initialize feedback for benchmark run.

        Args:
            paradigms: List of paradigm IDs
            ram_levels: List of RAM levels in MB
            queries: List of query IDs (or None for all)
            n_runs: Number of timed runs
            n_variants: Number of parameter variants
        """
        self.progress.total_paradigms = len(paradigms)
        self.progress.total_ram_levels = len(ram_levels)
        self.progress.total_queries = len(queries) if queries else 23
        self.progress.total_runs = n_runs * n_variants
        self.progress.start_time = datetime.now()

        if self.level == FeedbackLevel.DASHBOARD:
            self._start_dashboard()
        elif self.level == FeedbackLevel.NORMAL:
            self._start_progress()
        elif self.level == FeedbackLevel.VERBOSE:
            self._log(f"Starting benchmark: {len(paradigms)} paradigms, {len(ram_levels)} RAM levels")

    def _start_progress(self) -> None:
        """Start progress bar mode."""
        self._progress_bar = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console,
        )
        self._tasks = {
            "paradigm": self._progress_bar.add_task("Paradigm", total=self.progress.total_paradigms),
            "ram": self._progress_bar.add_task("RAM Level", total=self.progress.total_ram_levels, visible=False),
            "query": self._progress_bar.add_task("Query", total=self.progress.total_queries, visible=False),
        }
        self._progress_bar.start()

    def _start_dashboard(self) -> None:
        """Start live dashboard mode."""
        self._live = Live(self._build_dashboard(), refresh_per_second=4, console=self.console)
        self._live.start()

    def _build_dashboard(self) -> Panel:
        """Build dashboard panel."""
        # Progress section
        progress_table = Table(show_header=False, box=None, padding=(0, 1))
        progress_table.add_column("Label", style="cyan")
        progress_table.add_column("Value")

        paradigm_str = f"{self.progress.current_paradigm} ({self.progress.current_paradigm_idx + 1}/{self.progress.total_paradigms})"
        ram_str = f"{self.progress.current_ram_mb // 1024} GB ({self.progress.current_ram_level_idx + 1}/{self.progress.total_ram_levels})" if self.progress.current_ram_mb else "-"
        query_str = f"{self.progress.current_query} ({self.progress.current_query_idx + 1}/{self.progress.total_queries})" if self.progress.current_query else "-"
        run_str = f"{self.progress.current_run}/{self.progress.total_runs}"

        progress_table.add_row("Paradigm:", paradigm_str)
        progress_table.add_row("RAM Level:", ram_str)
        progress_table.add_row("Query:", query_str)
        progress_table.add_row("Run:", run_str)
        progress_table.add_row("Phase:", self.progress.phase)

        # Results section
        results_table = Table(title="Completed", show_header=True, box=None)
        results_table.add_column("Paradigm", style="cyan")
        results_table.add_column("RAM Viable")
        results_table.add_column("OK")

        for p, result in self.progress.completed_results.items():
            ram = f"{result.get('ram_viable')} GB" if result.get('ram_viable') else "[red]FAIL[/red]"
            ok = f"{result.get('ok_count', 0)}/{result.get('total', 0)}"
            results_table.add_row(p, ram, ok)

        # ETA
        eta = self.progress.eta_seconds
        if eta > 3600:
            eta_str = f"{int(eta // 3600)}h {int((eta % 3600) // 60)}m"
        elif eta > 60:
            eta_str = f"{int(eta // 60)}m {int(eta % 60)}s"
        elif eta > 0:
            eta_str = f"{int(eta)}s"
        else:
            eta_str = "calculating..."

        progress_pct = f"{self.progress.progress_percent:.1f}%"

        content = f"{progress_table}\n\nProgress: {progress_pct} | ETA: {eta_str}"
        if self.progress.completed_results:
            content += f"\n\n{results_table}"

        return Panel(
            content,
            title="[bold blue]Benchmark Progress[/bold blue]",
            border_style="blue",
        )

    def _log(self, message: str) -> None:
        """Print timestamped log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(f"[dim][{timestamp}][/dim] {message}")

    def on_paradigm_start(self, paradigm: str, idx: int) -> None:
        """Called when starting a new paradigm."""
        self.progress.current_paradigm = paradigm
        self.progress.current_paradigm_idx = idx
        self.progress.current_ram_level_idx = 0
        self.progress.current_ram_mb = 0
        self.progress.current_query = ""
        self.progress.current_query_idx = 0
        self.progress.current_run = 0

        if self.level >= FeedbackLevel.NORMAL:
            self.console.print(f"\n[bold cyan]===== {paradigm} ({idx + 1}/{self.progress.total_paradigms}) =====[/bold cyan]")

        if self.level == FeedbackLevel.DASHBOARD:
            self._live.update(self._build_dashboard())
        elif self.level == FeedbackLevel.NORMAL and self._progress_bar:
            self._progress_bar.update(self._tasks["paradigm"], completed=idx)
            self._progress_bar.update(self._tasks["ram"], completed=0, visible=True)

    def on_phase(self, phase: str) -> None:
        """Called when entering a phase."""
        self.progress.phase = phase

        if self.level >= FeedbackLevel.VERBOSE:
            icon = self.PHASE_ICONS.get(phase, ".")
            self._log(f"  [{icon}] {phase.capitalize()}...")

        if self.level == FeedbackLevel.DASHBOARD and self._live:
            self._live.update(self._build_dashboard())

    def on_ram_level(self, level_mb: int, idx: int) -> None:
        """Called when starting a new RAM level."""
        self.progress.current_ram_mb = level_mb
        self.progress.current_ram_level_idx = idx
        self.progress.current_query_idx = 0
        self.progress.current_query = ""
        self.progress.current_run = 0

        if self.level >= FeedbackLevel.VERBOSE:
            self._log(f"    RAM: {level_mb // 1024} GB ({idx + 1}/{self.progress.total_ram_levels})")

        if self.level == FeedbackLevel.DASHBOARD and self._live:
            self._live.update(self._build_dashboard())
        elif self.level == FeedbackLevel.NORMAL and self._progress_bar:
            self._progress_bar.update(self._tasks["ram"], completed=idx)
            self._progress_bar.update(self._tasks["query"], completed=0, visible=True)

    def on_query(self, query_id: str, idx: int) -> None:
        """Called when starting a new query."""
        self.progress.current_query = query_id
        self.progress.current_query_idx = idx
        self.progress.current_run = 0

        if self.level == FeedbackLevel.DASHBOARD and self._live:
            self._live.update(self._build_dashboard())
        elif self.level == FeedbackLevel.NORMAL and self._progress_bar:
            self._progress_bar.update(self._tasks["query"], completed=idx)

    def on_run(self, run_id: int, status: str, latency_ms: float = 0) -> None:
        """Called after a query run."""
        self.progress.current_run = run_id

        if self.level >= FeedbackLevel.VERBOSE:
            icon = "+" if status == "success" else "x" if status == "error" else "?"
            color = "green" if status == "success" else "red" if status == "error" else "yellow"
            self.console.print(f"        [{color}]{icon}[/{color}] Run {run_id}: {latency_ms:.1f}ms", highlight=False)

        if self.level == FeedbackLevel.DASHBOARD and self._live:
            self._live.update(self._build_dashboard())

    def on_level_complete(self, level_mb: int, status: str, peak_mb: float) -> None:
        """Called when a RAM level completes."""
        if self.level >= FeedbackLevel.NORMAL:
            icon = "+" if status == "success" else "!" if status == "oom" else "x"
            color = "green" if status == "success" else "yellow" if status == "oom" else "red"
            self.console.print(f"  [{color}]{icon}[/{color}] {level_mb // 1024}GB: {status} (peak: {peak_mb:.0f}MB)")

    def on_paradigm_complete(self, paradigm: str, ram_viable_mb: int | None, ok_count: int, total: int) -> None:
        """Called when a paradigm completes."""
        self.progress.completed_results[paradigm] = {
            "ram_viable": ram_viable_mb // 1024 if ram_viable_mb else None,
            "ok_count": ok_count,
            "total": total,
        }

        if self.level >= FeedbackLevel.NORMAL:
            if ram_viable_mb:
                self.console.print(f"  [green]+[/green] RAM viable: {ram_viable_mb // 1024} GB ({ok_count}/{total} queries OK)")
            else:
                self.console.print(f"  [red]x[/red] All OOM or ERROR ({ok_count}/{total} queries OK)")

        if self.level == FeedbackLevel.DASHBOARD and self._live:
            self._live.update(self._build_dashboard())

    def on_error(self, message: str) -> None:
        """Called when an error occurs."""
        if self.level >= FeedbackLevel.NORMAL:
            self.console.print(f"  [red]ERROR: {message}[/red]")

    def stop(self) -> None:
        """Stop feedback display."""
        if self._live:
            self._live.stop()
            self._live = None
        if self._progress_bar:
            self._progress_bar.stop()
            self._progress_bar = None

    def print_summary(self, results: dict[str, Any]) -> None:
        """Print final benchmark summary."""
        if self.level == FeedbackLevel.QUIET:
            # Minimal output
            for paradigm, data in self.progress.completed_results.items():
                ram = data.get("ram_viable")
                if ram:
                    self.console.print(f"{paradigm}: {ram}GB")
                else:
                    self.console.print(f"{paradigm}: FAIL")
            return

        # Full summary
        self.console.print("\n" + "=" * 60)
        self.console.print("[bold]Benchmark Summary[/bold]")
        self.console.print("=" * 60)

        # Results table
        table = Table(show_header=True)
        table.add_column("Paradigm", style="cyan")
        table.add_column("RAM Viable")
        table.add_column("Queries OK")

        for paradigm, data in self.progress.completed_results.items():
            ram = f"{data.get('ram_viable')} GB" if data.get('ram_viable') else "[red]FAIL[/red]"
            ok = f"{data.get('ok_count', 0)}/{data.get('total', 0)}"
            table.add_row(paradigm, ram, ok)

        self.console.print(table)

        # Duration
        duration = (datetime.now() - self.progress.start_time).total_seconds()
        if duration > 3600:
            duration_str = f"{int(duration // 3600)}h {int((duration % 3600) // 60)}m"
        else:
            duration_str = f"{int(duration // 60)}m {int(duration % 60)}s"

        self.console.print(f"\n[dim]Total duration: {duration_str}[/dim]")


# Callback type for integration with existing code
FeedbackCallback = Callable[[str, str, float], None]


def create_feedback_callback(manager: FeedbackManager) -> FeedbackCallback:
    """Create a callback function compatible with existing progress API.

    Args:
        manager: FeedbackManager instance

    Returns:
        Callback function with signature (paradigm, message, progress)
    """
    def callback(paradigm: str, message: str, progress: float) -> None:
        # Parse message to determine event type
        msg_lower = message.lower()

        if "export" in msg_lower:
            manager.on_phase("export")
        elif "load" in msg_lower:
            manager.on_phase("load")
        elif "warmup" in msg_lower:
            manager.on_phase("warmup")
        elif "run" in msg_lower or "query" in msg_lower:
            manager.on_phase("run")
        elif "cleanup" in msg_lower:
            manager.on_phase("cleanup")

    return callback
