"""Paramètres de volumétrie pour le générateur de dataset."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ScaleProfile:
    """Profil de génération contrôlé."""

    floors: int
    spaces: int
    equipments: int
    points: int
    meters: int


PROFILES: Dict[str, ScaleProfile] = {
    "laptop": ScaleProfile(
        floors=10,
        spaces=800,
        equipments=3000,
        points=15000,
        meters=200,
    ),
    "server": ScaleProfile(
        floors=20,
        spaces=2000,
        equipments=8000,
        points=50000,
        meters=500,
    ),
}


DEFAULT_SEED = 42
"""Graine par défaut pour garantir la reproductibilité."""


def get_profile(mode: str) -> ScaleProfile:
    """Retourne le profil associé au mode ou déclenche une erreur claire."""

    try:
        return PROFILES[mode]
    except KeyError as exc:
        raise ValueError(f"Mode de scale inconnu: {mode}") from exc
