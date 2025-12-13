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


# Volumétries Smart Building réalistes
# Les vendors BOS mettent TOUT en RAM (graphe + time-series)
# Ce benchmark démontre qu'une architecture hybride fait pareil avec 8x moins de RAM
PROFILES: Dict[str, ScaleProfile] = {
    "small": ScaleProfile(
        floors=20,
        spaces=4_000,
        equipments=10_000,
        points=50_000,        # Petit smart building
        meters=500,
    ),
    "large": ScaleProfile(
        floors=40,
        spaces=8_000,
        equipments=20_000,
        points=100_000,       # Smart building standard
        meters=1_000,
    ),
    "xl": ScaleProfile(
        floors=100,
        spaces=20_000,
        equipments=100_000,
        points=500_000,       # Grand smart building
        meters=5_000,
    ),
}

ALIASES = {"laptop": "small", "server": "large", "enterprise": "xl", "prod": "xl"}
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
