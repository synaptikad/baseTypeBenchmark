"""RAM Calibration Cache - Benchmark BaseType V3

Manages the ram_calibration.json file stored with each generated dataset.
The calibration is dataset-specific: different data sizes require different RAM minimums.

File location: data/generated/<dataset>/ram_calibration.json
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ParadigmCalibration:
    """Calibration result for a single paradigm."""
    ram_minimum_viable_mb: int
    levels_tested: list[int]
    crash_level_mb: int | None = None  # Level that caused OOM crash

    def to_dict(self) -> dict[str, Any]:
        return {
            "ram_minimum_viable_mb": self.ram_minimum_viable_mb,
            "levels_tested": self.levels_tested,
            "crash_level_mb": self.crash_level_mb,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParadigmCalibration":
        return cls(
            ram_minimum_viable_mb=data["ram_minimum_viable_mb"],
            levels_tested=data["levels_tested"],
            crash_level_mb=data.get("crash_level_mb"),
        )


@dataclass
class RAMCalibration:
    """Complete calibration data for a dataset."""
    dataset: str
    calibrated_at: str
    paradigms: dict[str, ParadigmCalibration] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "calibrated_at": self.calibrated_at,
            "paradigms": {k: v.to_dict() for k, v in self.paradigms.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RAMCalibration":
        return cls(
            dataset=data["dataset"],
            calibrated_at=data["calibrated_at"],
            paradigms={
                k: ParadigmCalibration.from_dict(v)
                for k, v in data.get("paradigms", {}).items()
            },
        )

    def get_minimum_viable(self, paradigm: str) -> int | None:
        """Get minimum viable RAM for a paradigm.

        Args:
            paradigm: P1, P2, M1, M2, or O2

        Returns:
            RAM in MB, or None if not calibrated
        """
        paradigm = paradigm.upper()
        if paradigm in self.paradigms:
            return self.paradigms[paradigm].ram_minimum_viable_mb
        return None

    def set_calibration(
        self,
        paradigm: str,
        minimum_viable_mb: int,
        levels_tested: list[int],
        crash_level_mb: int | None = None,
    ) -> None:
        """Set calibration result for a paradigm."""
        paradigm = paradigm.upper()
        self.paradigms[paradigm] = ParadigmCalibration(
            ram_minimum_viable_mb=minimum_viable_mb,
            levels_tested=levels_tested,
            crash_level_mb=crash_level_mb,
        )


CALIBRATION_FILENAME = "ram_calibration.json"


def load_calibration(data_path: Path) -> RAMCalibration | None:
    """Load calibration cache from dataset directory.

    Args:
        data_path: Path to dataset directory (e.g., data/generated/medium-1w)

    Returns:
        RAMCalibration if file exists, None otherwise
    """
    calibration_file = Path(data_path) / CALIBRATION_FILENAME

    if not calibration_file.exists():
        logger.debug(f"No calibration cache at {calibration_file}")
        return None

    try:
        with open(calibration_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        calibration = RAMCalibration.from_dict(data)
        logger.info(f"Loaded calibration cache from {calibration_file}")
        return calibration
    except Exception as e:
        logger.warning(f"Failed to load calibration cache: {e}")
        return None


def save_calibration(data_path: Path, calibration: RAMCalibration) -> bool:
    """Save calibration cache to dataset directory.

    Args:
        data_path: Path to dataset directory
        calibration: Calibration data to save

    Returns:
        True if saved successfully
    """
    calibration_file = Path(data_path) / CALIBRATION_FILENAME

    try:
        # Update timestamp
        calibration.calibrated_at = datetime.utcnow().isoformat() + "Z"

        with open(calibration_file, "w", encoding="utf-8") as f:
            json.dump(calibration.to_dict(), f, indent=2)

        logger.info(f"Saved calibration cache to {calibration_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to save calibration cache: {e}")
        return False


def get_or_create_calibration(data_path: Path) -> RAMCalibration:
    """Load existing calibration or create new one.

    Args:
        data_path: Path to dataset directory

    Returns:
        RAMCalibration (loaded or new)
    """
    existing = load_calibration(data_path)
    if existing:
        return existing

    # Create new calibration for this dataset
    dataset_name = Path(data_path).name
    return RAMCalibration(
        dataset=dataset_name,
        calibrated_at=datetime.utcnow().isoformat() + "Z",
        paradigms={},
    )


def needs_calibration(
    data_path: Path,
    paradigms: list[str],
    force: bool = False,
) -> list[str]:
    """Check which paradigms need calibration.

    Args:
        data_path: Path to dataset directory
        paradigms: List of paradigms to check (e.g., ["P1", "M1"])
        force: If True, return all paradigms (force re-calibration)

    Returns:
        List of paradigms that need calibration
    """
    if force:
        return [p.upper() for p in paradigms]

    calibration = load_calibration(data_path)
    if calibration is None:
        return [p.upper() for p in paradigms]

    # Check which paradigms are missing
    missing = []
    for paradigm in paradigms:
        paradigm = paradigm.upper()
        if paradigm not in calibration.paradigms:
            missing.append(paradigm)

    return missing
