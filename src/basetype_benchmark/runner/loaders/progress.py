"""Rich CLI Progress Display for Bulk Loaders.

Sprint 2 - Benchmark BaseType V3

Affichage interactif avec:
- Multi-progress bars par phase (Schema, Nodes, Edges, Timeseries)
- Speed column (rows/sec) avec formatage K/M
- ETA et temps ecoule
- Summary table finale
- Modes quiet/verbose
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from .base import LoadPhase, LoadProgress, LoadResult
    from basetype_benchmark.exporters.base import ExportPhase, ExportProgress, ExportResult

# Console ASCII-safe pour Windows (cp1252)
console = Console(force_terminal=True, color_system="auto")


# =============================================================================
# CUSTOM COLUMNS
# =============================================================================

class SpeedColumn(ProgressColumn):
    """Colonne custom pour afficher rows/sec avec formatage K/M."""

    def render(self, task: Task) -> Text:
        """Render la vitesse."""
        speed = task.fields.get("speed", 0)
        if speed <= 0:
            return Text("-", style="dim")
        elif speed >= 1_000_000:
            return Text(f"{speed / 1_000_000:.1f}M/s", style="cyan")
        elif speed >= 1_000:
            return Text(f"{speed / 1_000:.1f}K/s", style="cyan")
        else:
            return Text(f"{speed:.0f}/s", style="cyan")


class PhaseColumn(ProgressColumn):
    """Colonne pour le numero de phase [1/4]."""

    def render(self, task: Task) -> Text:
        phase_num = task.fields.get("phase_num", "")
        return Text(phase_num, style="bold blue")


# =============================================================================
# MAIN PROGRESS DISPLAY
# =============================================================================

class LoadProgressDisplay:
    """Affichage interactif multi-phases avec stats live.

    Exemple d'affichage:
    ```
    Benchmark Loader v3 - P1 (PostgreSQL)
    =====================================

    [1/4] Schema      [################] 100%  Done
    [2/4] Nodes       [##########------]  62%  45,231/72,000  12.4K/s  0:02:15
    [3/4] Edges       [----------------]   0%  Waiting...
    [4/4] Timeseries  [----------------]   0%  Waiting...
    ```
    """

    def __init__(self, paradigm: str, total_phases: int = 4):
        """Initialise le display.

        Args:
            paradigm: Nom du paradigme (P1, P2, M1, M2, O2)
            total_phases: Nombre total de phases (default: 4)
        """
        self.paradigm = paradigm
        self.total_phases = total_phases
        self._started = False

        self.progress = Progress(
            SpinnerColumn(),
            PhaseColumn(),
            TextColumn("{task.description:<12}"),
            BarColumn(bar_width=30),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            SpeedColumn(),
            TimeRemainingColumn(),
            console=console,
            refresh_per_second=4,
        )

        # Map phase -> task_id
        self.tasks: dict[str, int] = {}

    def start(self) -> None:
        """Affiche le header et demarre le progress."""
        if self._started:
            return

        console.print()
        console.print(
            Panel(
                f"[bold]Benchmark Loader v3 - {self.paradigm}[/bold]",
                style="blue",
                expand=False,
            )
        )
        console.print()
        self.progress.start()
        self._started = True

    def stop(self) -> None:
        """Arrete le progress display."""
        if self._started:
            self.progress.stop()
            self._started = False

    def add_phase(self, phase: "LoadPhase", total: int, phase_num: int) -> None:
        """Ajoute une phase de chargement.

        Args:
            phase: Phase (SCHEMA, NODES, EDGES, TIMESERIES)
            total: Nombre total d'elements a charger
            phase_num: Numero de la phase (1, 2, 3, 4)
        """
        if not self._started:
            self.start()

        task_id = self.progress.add_task(
            phase.value.capitalize(),
            total=total,
            phase_num=f"[{phase_num}/{self.total_phases}]",
            speed=0,
        )
        self.tasks[phase.value] = task_id

    def update(self, progress: "LoadProgress") -> None:
        """Met a jour une phase depuis un LoadProgress.

        Args:
            progress: LoadProgress avec phase, current, total, rate
        """
        phase_key = progress.phase.value
        if phase_key in self.tasks:
            self.progress.update(
                self.tasks[phase_key],
                completed=progress.current,
                speed=progress.rate,
            )

    def update_phase(
        self,
        phase: "LoadPhase",
        current: int,
        speed: float = 0,
    ) -> None:
        """Met a jour une phase directement.

        Args:
            phase: Phase a mettre a jour
            current: Nombre d'elements charges
            speed: Vitesse en rows/sec
        """
        phase_key = phase.value
        if phase_key in self.tasks:
            self.progress.update(
                self.tasks[phase_key],
                completed=current,
                speed=speed,
            )

    def complete_phase(self, phase: "LoadPhase") -> None:
        """Marque une phase comme terminee.

        Args:
            phase: Phase terminee
        """
        phase_key = phase.value
        if phase_key in self.tasks:
            task = self.progress.tasks[self.tasks[phase_key]]
            self.progress.update(
                self.tasks[phase_key],
                completed=task.total,
                description=f"[green]{phase.value.capitalize()}[/green]",
            )

    def fail_phase(self, phase: "LoadPhase", error: str = "") -> None:
        """Marque une phase comme echouee.

        Args:
            phase: Phase echouee
            error: Message d'erreur optionnel
        """
        phase_key = phase.value
        if phase_key in self.tasks:
            desc = f"[red]{phase.value.capitalize()}[/red]"
            if error:
                desc += f" ({error})"
            self.progress.update(
                self.tasks[phase_key],
                description=desc,
            )

    def print_summary(self, result: "LoadResult") -> None:
        """Affiche le resume final.

        Args:
            result: LoadResult avec statistiques
        """
        self.stop()
        console.print()

        # Table de resume
        table = Table(title="Load Summary", show_header=True, expand=False)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green", justify="right")

        table.add_row("Engine", result.engine)
        table.add_row("Nodes", f"{result.nodes_loaded:,}")
        table.add_row("Edges", f"{result.edges_loaded:,}")
        table.add_row("Timeseries", f"{result.timeseries_loaded:,}")
        table.add_row("Total Rows", f"{result.total_rows:,}")
        table.add_row("Duration", f"{result.duration_seconds:.1f}s")

        # Formatage vitesse
        if result.rate_rows_per_sec >= 1_000_000:
            speed_str = f"{result.rate_rows_per_sec / 1_000_000:.2f}M rows/s"
        elif result.rate_rows_per_sec >= 1_000:
            speed_str = f"{result.rate_rows_per_sec / 1_000:.1f}K rows/s"
        else:
            speed_str = f"{result.rate_rows_per_sec:.0f} rows/s"
        table.add_row("Avg Speed", speed_str)

        # Status
        if result.success:
            status = "[green]OK[/green]"
        else:
            status = "[red]FAILED[/red]"
        table.add_row("Status", status)

        console.print(table)

        # Erreurs si presentes
        if result.errors:
            console.print()
            console.print("[red]Errors:[/red]")
            for error in result.errors:
                console.print(f"  - {error}")

        console.print()

    def __enter__(self) -> "LoadProgressDisplay":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, *args) -> None:
        """Context manager exit."""
        self.stop()


# =============================================================================
# SIMPLE PROGRESS (pour mode quiet/verbose)
# =============================================================================

def print_simple_result(result: "LoadResult") -> None:
    """Affiche un resume simple (mode quiet).

    Args:
        result: LoadResult
    """
    status = "OK" if result.success else "FAILED"
    print(
        f"[{result.engine}] {status}: "
        f"{result.total_rows:,} rows in {result.duration_seconds:.1f}s "
        f"({result.rate_rows_per_sec:,.0f} rows/s)"
    )
    if result.errors:
        for error in result.errors:
            print(f"  ERROR: {error}")


def verbose_callback(progress: "LoadProgress") -> None:
    """Callback verbose pour logging detaille.

    Args:
        progress: LoadProgress
    """
    percent = progress.percent
    rate_str = f"{progress.rate:.0f}/s" if progress.rate > 0 else "-"
    print(
        f"  [{progress.phase.value}] "
        f"{progress.current:,}/{progress.total:,} "
        f"({percent:.1f}%) "
        f"@ {rate_str}"
    )


# =============================================================================
# EXPORT PROGRESS DISPLAY
# =============================================================================

class ExportProgressDisplay:
    """Affichage interactif multi-phases pour l'export.

    Exemple d'affichage:
    ```
    Benchmark Exporter v3 - P1 (PostgreSQL)
    ========================================

    [1/4] Loading     [################] 100%  Done
    [2/4] Nodes       [##########------]  62%  45,231/72,000  12.4K/s  0:00:05
    [3/4] Edges       [----------------]   0%  Waiting...
    [4/4] Timeseries  [----------------]   0%  Waiting...
    ```
    """

    PHASE_ORDER = ["loading", "nodes", "edges", "timeseries"]

    def __init__(self, paradigm: str, total_phases: int = 4):
        """Initialise le display.

        Args:
            paradigm: Nom du paradigme (P1, P2, M1, M2, O2)
            total_phases: Nombre total de phases (default: 4)
        """
        self.paradigm = paradigm
        self.total_phases = total_phases
        self._started = False

        self.progress = Progress(
            SpinnerColumn(),
            PhaseColumn(),
            TextColumn("{task.description:<12}"),
            BarColumn(bar_width=30),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            SpeedColumn(),
            TimeRemainingColumn(),
            console=console,
            refresh_per_second=4,
        )

        # Map phase -> task_id
        self.tasks: dict[str, int] = {}

    def start(self) -> None:
        """Affiche le header et demarre le progress."""
        if self._started:
            return

        console.print()
        console.print(
            Panel(
                f"[bold]Benchmark Exporter v3 - {self.paradigm}[/bold]",
                style="magenta",
                expand=False,
            )
        )
        console.print()
        self.progress.start()
        self._started = True

    def stop(self) -> None:
        """Arrete le progress display."""
        if self._started:
            self.progress.stop()
            self._started = False

    def _get_phase_num(self, phase_key: str) -> int:
        """Retourne le numero de phase (1-based)."""
        try:
            return self.PHASE_ORDER.index(phase_key) + 1
        except ValueError:
            return 0

    def update(self, progress: "ExportProgress") -> None:
        """Met a jour une phase depuis un ExportProgress.

        Args:
            progress: ExportProgress avec phase, current, total, rate
        """
        if not self._started:
            self.start()

        phase_key = progress.phase.value

        # Creer la tache si elle n'existe pas
        if phase_key not in self.tasks:
            phase_num = self._get_phase_num(phase_key)
            task_id = self.progress.add_task(
                phase_key.capitalize(),
                total=progress.total,
                phase_num=f"[{phase_num}/{self.total_phases}]",
                speed=0,
            )
            self.tasks[phase_key] = task_id

        # Mettre a jour
        self.progress.update(
            self.tasks[phase_key],
            completed=progress.current,
            total=progress.total,
            speed=progress.rate,
        )

        # Marquer comme complete si termine
        if progress.is_complete:
            self.progress.update(
                self.tasks[phase_key],
                description=f"[green]{phase_key.capitalize()}[/green]",
            )

    def print_summary(self, result: "ExportResult") -> None:
        """Affiche le resume final.

        Args:
            result: ExportResult avec statistiques
        """
        self.stop()
        console.print()

        # Table de resume
        table = Table(title="Export Summary", show_header=True, expand=False)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green", justify="right")

        table.add_row("Paradigm", result.paradigm.upper())
        table.add_row("Nodes", f"{result.total_nodes:,}")
        table.add_row("Edges", f"{result.total_edges:,}")
        table.add_row("Timeseries", f"{result.total_timeseries:,}")
        table.add_row("Files Created", f"{len(result.files_created)}")

        console.print(table)
        console.print()

    def __enter__(self) -> "ExportProgressDisplay":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, *args) -> None:
        """Context manager exit."""
        self.stop()


def export_verbose_callback(progress: "ExportProgress") -> None:
    """Callback verbose pour logging detaille de l'export.

    Args:
        progress: ExportProgress
    """
    percent = progress.percent
    rate_str = f"{progress.rate:.0f}/s" if progress.rate > 0 else "-"
    msg = f" - {progress.message}" if progress.message else ""
    print(
        f"  [{progress.phase.value}] "
        f"{progress.current:,}/{progress.total:,} "
        f"({percent:.1f}%) "
        f"@ {rate_str}{msg}"
    )
