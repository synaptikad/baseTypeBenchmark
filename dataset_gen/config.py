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
    "small": ScaleProfile(
        floors=10,
        spaces=800,
        equipments=3000,
        points=15000,
        meters=200,
    ),
    "large": ScaleProfile(
        floors=20,
        spaces=2000,
        equipments=8000,
        points=50000,
        meters=500,
    ),
}

ALIASES = {"laptop": "small", "server": "large"}
"""Alias historiques conservés pour rétrocompatibilité."""


DEFAULT_SEED = 42
"""Graine par défaut pour garantir la reproductibilité."""


def get_profile(mode: str) -> ScaleProfile:
    """Retourne le profil associé au mode ou déclenche une erreur claire."""

    normalized = ALIASES.get(mode.lower(), mode.lower())

    try:
        return PROFILES[normalized]
    except KeyError as exc:
        allowed = ", ".join(sorted(PROFILES))
        aliases = ", ".join(f"{src}->{dst}" for src, dst in sorted(ALIASES.items()))
        raise ValueError(
            f"Mode de volumétrie inconnu: {mode}. Profils attendus: {allowed}. Alias: {aliases}."
        ) from exc
