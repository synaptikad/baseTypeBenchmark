"""Base types and protocols for Bulk Loaders.

Sprint 2 - Benchmark BaseType V3
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Callable, Protocol, runtime_checkable

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================

class LoadPhase(str, Enum):
    """Phases du chargement bulk."""
    SCHEMA = "schema"
    NODES = "nodes"
    EDGES = "edges"
    TIMESERIES = "timeseries"


class TimeseriesDependencyStatus(str, Enum):
    """Status de la dépendance aux timeseries."""
    NOT_NEEDED = "not_needed"     # Engine doesn't need timeseries (M1)
    AVAILABLE = "available"       # Timeseries data is available
    MISSING = "missing"           # Timeseries data is missing, needs loading
    CONNECTION_ERROR = "error"    # Cannot connect to TimescaleDB


# =============================================================================
# PROGRESS MODELS
# =============================================================================

class LoadProgress(BaseModel):
    """Progress update pour callback."""
    phase: LoadPhase
    current: int = Field(ge=0, description="Nombre d'elements charges")
    total: int = Field(ge=0, description="Nombre total d'elements")
    rate: float = Field(default=0.0, ge=0, description="Vitesse en rows/sec")
    message: str = Field(default="", description="Message optionnel")

    @property
    def percent(self) -> float:
        """Pourcentage de completion."""
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100

    @property
    def is_complete(self) -> bool:
        """Phase terminee."""
        return self.current >= self.total


# Callback type pour progress updates
ProgressCallback = Callable[[LoadProgress], None]


# =============================================================================
# RESULT MODEL
# =============================================================================

class TimeseriesDependencyResult(BaseModel):
    """Résultat de la vérification de dépendance timeseries."""
    status: TimeseriesDependencyStatus
    row_count: int = Field(default=0, ge=0, description="Nombre de rows si AVAILABLE")
    message: str = Field(default="", description="Message explicatif")
    can_load: bool = Field(default=False, description="True si on peut charger les TS")

    @property
    def needs_user_action(self) -> bool:
        """True si l'utilisateur doit décider (TS manquantes)."""
        return self.status == TimeseriesDependencyStatus.MISSING


class LoadResult(BaseModel):
    """Resultat d'un chargement bulk."""
    engine: str = Field(description="P1, P2, M1, M2")
    success: bool = Field(default=True)
    nodes_loaded: int = Field(default=0, ge=0)
    edges_loaded: int = Field(default=0, ge=0)
    timeseries_loaded: int = Field(default=0, ge=0)
    duration_seconds: float = Field(default=0.0, ge=0)
    rate_rows_per_sec: float = Field(default=0.0, ge=0)
    errors: list[str] = Field(default_factory=list)

    @property
    def total_rows(self) -> int:
        """Total de lignes chargees."""
        return self.nodes_loaded + self.edges_loaded + self.timeseries_loaded

    def add_error(self, error: str) -> None:
        """Ajoute une erreur et marque comme echec."""
        self.errors.append(error)
        self.success = False


# =============================================================================
# PROTOCOL
# =============================================================================

@runtime_checkable
class BulkLoader(Protocol):
    """Protocol pour tous les loaders.

    Chaque loader (PostgresLoader, MemgraphLoader)
    doit implementer cette interface.
    """

    def load_all(
        self,
        data_dir: Path,
        progress_callback: ProgressCallback | None = None,
        workers: int = 4,
    ) -> LoadResult:
        """Charge toutes les donnees depuis un repertoire d'export.

        Args:
            data_dir: Repertoire contenant les fichiers exportes (CSV, NT, etc.)
            progress_callback: Callback pour progress updates (optional)
            workers: Nombre de workers paralleles

        Returns:
            LoadResult avec statistiques et status
        """
        ...

    def clear_database(self) -> bool:
        """Vide la base de donnees pour un reload propre.

        Returns:
            True si succes, False si erreur
        """
        ...

    def check_connection(self) -> bool:
        """Verifie la connexion a la base.

        Returns:
            True si connecte, False sinon
        """
        ...


# =============================================================================
# BASE CLASS (optional, for shared logic)
# =============================================================================

class BaseLoader:
    """Classe de base avec logique partagee pour les loaders."""

    def __init__(self, engine: str):
        self.engine = engine
        self._start_time: float = 0.0

    def _count_csv_rows(self, csv_path: Path) -> int:
        """Compte les lignes d'un CSV (sans le header)."""
        if not csv_path.exists():
            return 0
        with open(csv_path, "r", encoding="utf-8") as f:
            # -1 pour le header
            return sum(1 for _ in f) - 1

    def _count_nt_lines(self, nt_path: Path) -> int:
        """Compte les triples d'un fichier N-Triples."""
        if not nt_path.exists():
            return 0
        with open(nt_path, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip() and not line.startswith("#"))

    def _make_progress(
        self,
        phase: LoadPhase,
        current: int,
        total: int,
        rate: float = 0.0,
        message: str = "",
    ) -> LoadProgress:
        """Factory pour LoadProgress."""
        return LoadProgress(
            phase=phase,
            current=current,
            total=total,
            rate=rate,
            message=message,
        )

    def _emit_progress(
        self,
        callback: ProgressCallback | None,
        phase: LoadPhase,
        current: int,
        total: int,
        rate: float = 0.0,
    ) -> None:
        """Emet un progress update si callback fourni."""
        if callback:
            callback(self._make_progress(phase, current, total, rate))
