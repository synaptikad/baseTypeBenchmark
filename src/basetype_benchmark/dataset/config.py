"""Configuration des profils de volumétrie pour le générateur de dataset.

Ce module définit les profils de scale pour le benchmark d'un BOS (Building Operating System)
ou Digital Twin de bâtiment/campus, inspiré des ontologies Haystack, Brick et RealEstateCore.

VOLUMÉTRIE - Total de nœuds dans le graphe:
- Small  (~60k nœuds):  Bâtiment tertiaire standard (25 étages, 1250 espaces)
- Medium (~120k nœuds): Grand bâtiment ou petit campus (50 étages, 2500 espaces)
- Large  (~540k nœuds): Campus universitaire, hôpital ou quartier d'affaires

Composition des nœuds (exemple Large ~540k):
- Spatial:      ~5k   (Site, Building, Floor, Space, Zone)
- Équipements:  ~25k  (Equipment, System, Controller)
- Points:       ~500k (Point, Sensor, Actuator) - capteurs/commandes
- Énergie:      ~2.5k (Meter, EnergyZone)
- IT:           ~1.5k (Datacenter, Rack, Server, NetworkDevice, Storage)
- AV:           ~500  (AVSystem, Display, Projector, Speaker)
- Parking:      ~2.5k (ParkingZone, ParkingLevel, ParkingSpot, ChargingStation)
- Sécurité:     ~1.2k (SecurityZone, AccessPoint, Camera, Alarm)
- Organisation: ~5k   (Organization, Department, Team, Person, Tenant)
- Contractuel:  ~300  (Contract, Provider, Lease, WorkOrder)

TIMESERIES - Comportement réaliste type SCADA/BMS:
Les points de mesure ont des comportements temporels très différents:
- Points fixes (~30%):     Config, setpoints, seuils → PAS de timeseries
- Événements rares (~25%): Alarmes, accès, états → quelques événements/jour
- Mesures lentes (~20%):   Compteurs énergie → 1 sample/heure
- Mesures 15min (~20%):    Températures, CO2 → 96 samples/jour
- Mesures rapides (~5%):   Puissance élec → 1 sample/minute (SCADA)

DURÉES TEMPORELLES:
- 2d: Court terme (tests rapides, comparable solutions in-memory)
- 1w: Une semaine (opérationnel quotidien)
- 1m: Un mois (analyse mensuelle)
- 6m: Six mois (analyse saisonnière)
- 1y: Un an (reporting annuel, analytics long terme)

Estimation timeseries Large-1y:
- Points avec TS continues: ~350k (70% des 500k points)
- Mix de fréquences: moyenne ~40 samples/jour (vs 96 si tous 15min)
- Total samples: 350k × 40 × 365 ≈ 5.1 milliards samples
- Taille estimée: ~350 GB (format JSON lines)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ScaleProfile:
    """Profil de génération contrôlé pour un dataset.

    Attributes:
        name: Nom du profil pour référence
        floors: Nombre d'étages (détermine la hiérarchie spatiale)
        spaces: Nombre total d'espaces (bureaux, salles, etc.)
        equipments: Nombre d'équipements techniques
        points: Nombre total de points de mesure
        meters: Nombre de compteurs (arbre de distribution)
        duration_days: Durée des séries temporelles en jours

        # Nouveaux domaines (complexité maximale)
        it_devices: Nombre de devices IT (serveurs, switches, storage)
        av_systems: Nombre de systèmes audiovisuels
        parking_spots: Nombre de places de parking
        security_devices: Nombre de dispositifs de sécurité
        persons: Nombre de personnes dans l'organisation
        contracts: Nombre de contrats (maintenance, énergie)
    """
    name: str
    floors: int
    spaces: int
    equipments: int
    points: int
    meters: int
    duration_days: int

    # Domaines étendus
    it_devices: int = 0
    av_systems: int = 0
    parking_spots: int = 0
    security_devices: int = 0
    persons: int = 0
    contracts: int = 0

    def __post_init__(self):
        """Validation des paramètres."""
        if self.points < self.equipments:
            raise ValueError("points doit être >= equipments")


# =============================================================================
# Profils de base (structure uniquement, sans durée)
# =============================================================================

# Small: Bâtiment de bureaux standard (~25 étages, 1250 espaces)
_SMALL_BASE = {
    "floors": 25,
    "spaces": 1250,          # ~50 espaces/étage
    "equipments": 6250,      # ~5 équipements/espace
    "points": 50000,         # ~8 points/équipement
    "meters": 500,           # Arbre de distribution ~8 niveaux
    # Domaines étendus (proportionnels)
    "it_devices": 200,       # 1 datacenter, ~10 racks, serveurs/switches
    "av_systems": 100,       # Salles de réunion équipées
    "parking_spots": 300,    # Parking souterrain
    "security_devices": 150, # Lecteurs badges, caméras
    "persons": 500,          # Effectif du bâtiment
    "contracts": 50,         # Contrats maintenance/énergie
}

# Medium: Grand bâtiment ou petit campus (~50 étages équivalent)
_MEDIUM_BASE = {
    "floors": 50,
    "spaces": 2500,
    "equipments": 12500,
    "points": 100000,
    "meters": 1000,
    # Domaines étendus
    "it_devices": 500,
    "av_systems": 200,
    "parking_spots": 800,
    "security_devices": 400,
    "persons": 1500,
    "contracts": 120,
}

# Large: Campus ou quartier d'affaires (~100 étages équivalent)
_LARGE_BASE = {
    "floors": 100,
    "spaces": 5000,
    "equipments": 25000,
    "points": 500000,
    "meters": 2500,
    # Domaines étendus
    "it_devices": 1500,
    "av_systems": 500,
    "parking_spots": 2500,
    "security_devices": 1200,
    "persons": 5000,
    "contracts": 300,
}


# =============================================================================
# Profils complets avec durées temporelles
# =============================================================================

PROFILES: Dict[str, ScaleProfile] = {
    # =========================================================================
    # SMALL (50k points) - Bâtiment standard
    # =========================================================================
    "small-2d": ScaleProfile(
        name="small-2d",
        duration_days=2,
        **_SMALL_BASE
    ),
    "small-1w": ScaleProfile(
        name="small-1w",
        duration_days=7,
        **_SMALL_BASE
    ),
    "small-1m": ScaleProfile(
        name="small-1m",
        duration_days=30,
        **_SMALL_BASE
    ),
    "small-6m": ScaleProfile(
        name="small-6m",
        duration_days=180,
        **_SMALL_BASE
    ),
    "small-1y": ScaleProfile(
        name="small-1y",
        duration_days=365,
        **_SMALL_BASE
    ),

    # =========================================================================
    # MEDIUM (100k points) - Grand bâtiment / petit campus
    # =========================================================================
    "medium-2d": ScaleProfile(
        name="medium-2d",
        duration_days=2,
        **_MEDIUM_BASE
    ),
    "medium-1w": ScaleProfile(
        name="medium-1w",
        duration_days=7,
        **_MEDIUM_BASE
    ),
    "medium-1m": ScaleProfile(
        name="medium-1m",
        duration_days=30,
        **_MEDIUM_BASE
    ),
    "medium-6m": ScaleProfile(
        name="medium-6m",
        duration_days=180,
        **_MEDIUM_BASE
    ),
    "medium-1y": ScaleProfile(
        name="medium-1y",
        duration_days=365,
        **_MEDIUM_BASE
    ),

    # =========================================================================
    # LARGE (500k points) - Campus / quartier d'affaires
    # =========================================================================
    "large-2d": ScaleProfile(
        name="large-2d",
        duration_days=2,
        **_LARGE_BASE
    ),
    "large-1w": ScaleProfile(
        name="large-1w",
        duration_days=7,
        **_LARGE_BASE
    ),
    "large-1m": ScaleProfile(
        name="large-1m",
        duration_days=30,
        **_LARGE_BASE
    ),
    "large-6m": ScaleProfile(
        name="large-6m",
        duration_days=180,
        **_LARGE_BASE
    ),
    "large-1y": ScaleProfile(
        name="large-1y",
        duration_days=365,
        **_LARGE_BASE
    ),
}


# =============================================================================
# Estimations de taille (GB) par profil
# =============================================================================

SIZE_ESTIMATES_GB = {
    "small-2d": 0.5, "small-1w": 1, "small-1m": 5, "small-6m": 27, "small-1y": 55,
    "medium-2d": 1, "medium-1w": 2, "medium-1m": 10, "medium-6m": 54, "medium-1y": 110,
    "large-2d": 5, "large-1w": 11, "large-1m": 45, "large-6m": 270, "large-1y": 550,
}


# =============================================================================
# Alias pour compatibilité et raccourcis
# =============================================================================

ALIASES = {
    # Environnements de test
    "laptop": "small-1w",
    "desktop": "small-1m",
    "server": "medium-6m",
    "cluster": "large-1y",

    # Scénarios de benchmark
    "market-baseline": "small-2d",   # Comparable aux solutions in-memory
    "operational": "medium-1m",       # Usage opérationnel typique
    "analytics": "large-1y",          # Analyse long terme complète
}


# =============================================================================
# Constantes
# =============================================================================

DEFAULT_SEED = 42
"""Graine par défaut pour garantir la reproductibilité."""

# =============================================================================
# Distribution des comportements temporels des points (réaliste BMS/SCADA)
# =============================================================================

POINT_TEMPORAL_DISTRIBUTION = {
    "fixed": 0.30,        # Config, setpoints, seuils → PAS de timeseries
    "event_rare": 0.25,   # Alarmes, accès, états → ~5 événements/jour
    "hourly": 0.20,       # Compteurs énergie → 24 samples/jour
    "quarter_hour": 0.20, # Températures, CO2, humidity → 96 samples/jour
    "minute": 0.05,       # Puissance élec, SCADA critique → 1440 samples/jour
}

# Samples par jour selon le type de point
SAMPLES_PER_DAY = {
    "fixed": 0,
    "event_rare": 5,
    "hourly": 24,
    "quarter_hour": 96,
    "minute": 1440,
}

# Ratio de points avec timeseries (tous sauf fixed)
TIMESERIES_RATIO = 0.70
"""70% des points génèrent des timeseries (event_rare + hourly + quarter_hour + minute)."""

# Moyenne pondérée de samples/jour pour estimation
AVERAGE_SAMPLES_PER_DAY = (
    0.25 * 5 +      # event_rare
    0.20 * 24 +     # hourly
    0.20 * 96 +     # quarter_hour
    0.05 * 1440     # minute
) / 0.70  # Normalisé sur les 70% qui ont des TS
# = (1.25 + 4.8 + 19.2 + 72) / 0.70 ≈ 139 samples/jour/point avec TS


# =============================================================================
# Configuration chunking par scénario (optimisation M1)
# =============================================================================

# Taille des chunks timeseries pour Memgraph standalone (M1)
# Petits chunks = meilleure gestion mémoire, garbage collection efficace
MEMGRAPH_CHUNK_SIZE = 50
"""Nombre max de samples par chunk pour M1 (Memgraph in-memory)."""

# Taille des chunks pour PostgreSQL (timeseries_chunks.json)
# Plus grands chunks OK car stockage sur disque avec compression
POSTGRES_CHUNK_SIZE = 1000
"""Nombre max de samples par chunk pour P1/P2 (utilisé pour export JSON)."""

# Configuration export par scénario
SCENARIO_CONFIG = {
    "P1": {
        "name": "PostgreSQL Relational + TimescaleDB",
        "timeseries_storage": "hypertable",
        "chunk_size": POSTGRES_CHUNK_SIZE,
        "uses_external_ts": False,
    },
    "P2": {
        "name": "PostgreSQL JSONB + TimescaleDB",
        "timeseries_storage": "hypertable",
        "chunk_size": POSTGRES_CHUNK_SIZE,
        "uses_external_ts": False,
    },
    "M1": {
        "name": "Memgraph Standalone",
        "timeseries_storage": "property_array",
        "chunk_size": MEMGRAPH_CHUNK_SIZE,
        "uses_external_ts": False,
    },
    "M2": {
        "name": "Memgraph + TimescaleDB Hybrid",
        "timeseries_storage": "external_hypertable",
        "chunk_size": POSTGRES_CHUNK_SIZE,
        "uses_external_ts": True,
    },
    "O1": {
        "name": "Oxigraph Standalone (RDF)",
        "timeseries_storage": "rdf_aggregates",
        "chunk_size": 0,  # Pas de chunks, agrégats pré-calculés
        "uses_external_ts": False,
    },
    "O2": {
        "name": "Oxigraph + TimescaleDB Hybrid",
        "timeseries_storage": "external_hypertable",
        "chunk_size": POSTGRES_CHUNK_SIZE,
        "uses_external_ts": True,
    },
}


# =============================================================================
# Fonctions utilitaires
# =============================================================================

def get_profile(mode: str) -> ScaleProfile:
    """Retourne le profil associé au mode ou déclenche une erreur claire.

    Args:
        mode: Nom du profil ou alias

    Returns:
        ScaleProfile correspondant

    Raises:
        ValueError: Si le mode n'existe pas
    """
    normalized = ALIASES.get(mode.lower(), mode.lower())

    try:
        return PROFILES[normalized]
    except KeyError as exc:
        allowed = ", ".join(sorted(PROFILES))
        aliases = ", ".join(f"{src}->{dst}" for src, dst in sorted(ALIASES.items()))
        raise ValueError(
            f"Mode de volumétrie inconnu: {mode}. "
            f"Profils attendus: {allowed}. "
            f"Alias: {aliases}."
        ) from exc


def get_profile_metrics(profile: ScaleProfile) -> Dict[str, any]:
    """Calcule les métriques estimées pour un profil.

    Utile pour estimer la taille du dataset avant génération.

    Args:
        profile: Profil de scale

    Returns:
        Dict avec estimations détaillées de nodes, edges, timeseries
    """
    # Estimation du nombre de nœuds par domaine
    nodes_spatial = 1 + 1 + profile.floors + profile.spaces  # Site, Building, Floors, Spaces
    nodes_equipment = profile.equipments + profile.points + profile.meters
    nodes_it = profile.it_devices
    nodes_av = profile.av_systems
    nodes_parking = profile.parking_spots
    nodes_security = profile.security_devices
    nodes_org = profile.persons + profile.contracts

    nodes_estimate = (
        nodes_spatial +
        nodes_equipment +
        nodes_it +
        nodes_av +
        nodes_parking +
        nodes_security +
        nodes_org
    )

    # Estimation des edges (approximation basée sur les ratios typiques)
    edges_estimate = int(nodes_estimate * 2.5)  # ~2.5 relations par nœud en moyenne

    # Estimation des timeseries avec distribution réaliste
    ts_points_by_type = {
        "fixed": int(profile.points * POINT_TEMPORAL_DISTRIBUTION["fixed"]),
        "event_rare": int(profile.points * POINT_TEMPORAL_DISTRIBUTION["event_rare"]),
        "hourly": int(profile.points * POINT_TEMPORAL_DISTRIBUTION["hourly"]),
        "quarter_hour": int(profile.points * POINT_TEMPORAL_DISTRIBUTION["quarter_hour"]),
        "minute": int(profile.points * POINT_TEMPORAL_DISTRIBUTION["minute"]),
    }

    # Calcul des samples par type
    ts_samples_by_type = {
        k: v * SAMPLES_PER_DAY[k] * profile.duration_days
        for k, v in ts_points_by_type.items()
    }

    ts_points_total = sum(v for k, v in ts_points_by_type.items() if k != "fixed")
    ts_samples_total = sum(ts_samples_by_type.values())

    # Estimation taille en GB (environ 70 bytes par sample JSON)
    size_gb = ts_samples_total * 70 / 1e9

    return {
        # Graphe
        "nodes_estimate": nodes_estimate,
        "nodes_by_domain": {
            "spatial": nodes_spatial,
            "equipment": nodes_equipment,
            "it": nodes_it,
            "av": nodes_av,
            "parking": nodes_parking,
            "security": nodes_security,
            "organization": nodes_org,
        },
        "edges_estimate": edges_estimate,
        # Timeseries détaillées
        "points_total": profile.points,
        "points_by_type": ts_points_by_type,
        "timeseries_points": ts_points_total,
        "timeseries_samples": ts_samples_total,
        "samples_by_type": ts_samples_by_type,
        # Métadonnées
        "duration_days": profile.duration_days,
        "estimated_size_gb": round(size_gb, 1),
    }


def list_profiles_by_scale() -> Dict[str, list]:
    """Liste les profils groupés par échelle.

    Returns:
        Dict avec scales (small, medium, large) et leurs profils
    """
    result = {"small": [], "medium": [], "large": []}
    for name in PROFILES:
        scale = name.split("-")[0]
        if scale in result:
            result[scale].append(name)
    return result


def list_profiles_by_duration() -> Dict[str, list]:
    """Liste les profils groupés par durée.

    Returns:
        Dict avec durées (2d, 1w, 1m, 6m, 1y) et leurs profils
    """
    result = {"2d": [], "1w": [], "1m": [], "6m": [], "1y": []}
    for name in PROFILES:
        duration = name.split("-")[1]
        if duration in result:
            result[duration].append(name)
    return result
