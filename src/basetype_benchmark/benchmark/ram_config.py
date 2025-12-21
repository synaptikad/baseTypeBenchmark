"""Configuration RAM adaptative pour les benchmarks.

Ce module définit les bornes RAM réalistes par configuration (moteur × profil × durée)
et génère automatiquement les séquences de test optimales.

Principes :
- M1 (in-memory) : RAM proportionnelle aux données, risque OOM
- P1/P2 (disk-based) : RAM = cache, dégradation progressive si insuffisant
- M2/O2 (hybrides) : structure in-memory, TS externe
- O1 (RDF disk) : similaire à P1/P2

Modes de test :
- DISCOVERY : trouve RAM_min par dichotomie
- GRADIENT : teste tous les paliers pour courbe complète
- QUICK : teste seulement baseline et RAM contrainte
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math


class EngineType(str, Enum):
    """Types de moteurs avec leurs caractéristiques mémoire."""
    P1 = "P1"  # PostgreSQL Relational - disk-based
    P2 = "P2"  # PostgreSQL JSONB - disk-based
    M1 = "M1"  # Memgraph Standalone - in-memory (données + TS)
    M2 = "M2"  # Memgraph Hybrid - in-memory (structure) + TimescaleDB
    O1 = "O1"  # Oxigraph Standalone - disk-based (RDF)
    O2 = "O2"  # Oxigraph Hybrid - disk-based + TimescaleDB


class TestMode(str, Enum):
    """Modes de test RAM."""
    DISCOVERY = "discovery"    # Dichotomie pour trouver RAM_min
    GRADIENT = "gradient"      # Tous les paliers pour courbe
    QUICK = "quick"            # Baseline + contrainte seulement


@dataclass
class EngineRAMProfile:
    """Profil RAM d'un moteur."""
    engine: EngineType
    is_in_memory: bool  # Tout en RAM vs disk-based
    base_overhead_mb: int  # Overhead minimal du moteur
    structure_multiplier: float  # RAM = structure_size × multiplier
    timeseries_in_memory: bool  # TS stockées en RAM ?
    degradation_threshold: float = 0.2  # Seuil de dégradation acceptable (20%)

    @property
    def can_oom(self) -> bool:
        """Le moteur peut-il OOM si RAM insuffisante ?"""
        return self.is_in_memory


# Profils RAM par moteur
ENGINE_PROFILES: Dict[EngineType, EngineRAMProfile] = {
    EngineType.P1: EngineRAMProfile(
        engine=EngineType.P1,
        is_in_memory=False,
        base_overhead_mb=256,  # PostgreSQL minimal
        structure_multiplier=0.1,  # Cache ~10% des données
        timeseries_in_memory=False,
    ),
    EngineType.P2: EngineRAMProfile(
        engine=EngineType.P2,
        is_in_memory=False,
        base_overhead_mb=256,
        structure_multiplier=0.15,  # JSONB + GIN index = un peu plus
        timeseries_in_memory=False,
    ),
    EngineType.M1: EngineRAMProfile(
        engine=EngineType.M1,
        is_in_memory=True,
        base_overhead_mb=512,  # Memgraph minimal
        structure_multiplier=3.0,  # Graphe in-memory = ~3× taille données
        timeseries_in_memory=True,  # TS aussi en RAM !
    ),
    EngineType.M2: EngineRAMProfile(
        engine=EngineType.M2,
        is_in_memory=True,  # Structure en RAM
        base_overhead_mb=512,
        structure_multiplier=3.0,
        timeseries_in_memory=False,  # TS dans TimescaleDB
    ),
    EngineType.O1: EngineRAMProfile(
        engine=EngineType.O1,
        is_in_memory=False,
        base_overhead_mb=128,  # Oxigraph léger
        structure_multiplier=0.2,
        timeseries_in_memory=False,
    ),
    EngineType.O2: EngineRAMProfile(
        engine=EngineType.O2,
        is_in_memory=False,
        base_overhead_mb=128,
        structure_multiplier=0.2,
        timeseries_in_memory=False,
    ),
}


@dataclass
class DatasetSizeEstimate:
    """Estimation de la taille d'un dataset."""
    scale: str  # small, medium, large
    duration: str  # 1w, 1m, 6m, 1y
    structure_mb: int  # Taille structure (nodes + edges)
    timeseries_mb: int  # Taille séries temporelles

    @property
    def total_mb(self) -> int:
        return self.structure_mb + self.timeseries_mb

    @property
    def profile_name(self) -> str:
        return f"{self.scale}-{self.duration}"


# =============================================================================
# Configuration serveur OVH B3-256
# =============================================================================
OVH_MAX_RAM_GB = 256  # OVH B3-256 : 256 Go RAM (32 vCPU, 400 Go NVMe)
"""RAM maximale disponible sur l'instance OVH B3-256."""

# Alias pour compatibilité
MAX_RAM_GB = OVH_MAX_RAM_GB
AWS_MAX_RAM_GB = OVH_MAX_RAM_GB  # Legacy alias

# =============================================================================
# Paliers RAM pour tests (max 256GB sur OVH B3-256)
# =============================================================================
# Objectif : Trouver le plateau PostgreSQL et le seuil OOM Memgraph/Oxigraph
#
# PostgreSQL (P1/P2) : disk-based, plateau attendu entre 8-32GB
# Memgraph (M1/M2)   : in-memory, OOM attendu selon taille dataset
# Oxigraph (O1/O2)   : disk-based mais RDF overhead, OOM possible sur gros datasets

# Paliers fins pour trouver les seuils critiques
RAM_LEVELS_DISCOVERY = [
    1024,    # 1 GB  - minimum absolu
    2048,    # 2 GB  - très contraint
    4096,    # 4 GB  - contraint
    8192,    # 8 GB  - baseline laptop
    16384,   # 16 GB - serveur léger
    32768,   # 32 GB - serveur standard
    65536,   # 64 GB - serveur confortable
    131072,  # 128 GB - serveur large
    196608,  # 192 GB - near-max
    262144,  # 256 GB - max disponible
]

# Paliers par échelle de dataset
RAM_LEVELS_SMALL = [1024, 2048, 4096, 8192, 16384, 32768]  # 1-32 GB
RAM_LEVELS_MEDIUM = [2048, 4096, 8192, 16384, 32768, 65536, 131072]  # 2-128 GB
RAM_LEVELS_LARGE = [4096, 8192, 16384, 32768, 65536, 131072, 196608, 262144]  # 4-256 GB
RAM_LEVELS_XLARGE = [8192, 16384, 32768, 65536, 131072, 196608, 262144]  # 8-256 GB

# =============================================================================
# Estimations de taille par profil (échelle × fenêtre temporelle)
# =============================================================================
# La RAM nécessaire dépend de :
#   1. Échelle (small/medium/large) → nombre de nodes/edges (structure)
#   2. Fenêtre temporelle (2d/1m/6m/1y) → volume de séries temporelles
#   3. Type de moteur (in-memory vs disk-based)
#
# Formules d'estimation :
#   - Structure MB = nodes × 0.5KB + edges × 0.3KB (approximation)
#   - TimeSeries MB = points × samples × 16 bytes (timestamp + value + overhead)
#
# Pour M1 (Memgraph tout in-memory) :
#   RAM_M1 ≈ (Structure + TimeSeries) × 3 (overhead index/structures Memgraph)
#
# Pour P1/P2/O1/O2 (disk-based) :
#   RAM ≈ Structure × 0.5 + overhead moteur (cache efficace)
#
# =============================================================================

# Échelles de projet (inspiré papier.md Section 3.2)
# | Échelle | Bâtiments | Étages | Espaces | Équipements | Points TS |
# |---------|-----------|--------|---------|-------------|-----------|
# | small   | 10        | 25     | 1,250   | 6,250       | 50,000    |
# | medium  | 100       | 50     | 2,500   | 12,500      | 100,000   |
# | large   | 1000      | 100    | 5,000   | 25,000      | 500,000   |

# Fenêtres temporelles et leur impact sur le volume TS
# | Fenêtre | Jours | Samples/point (15min) | Multiplicateur |
# |---------|-------|----------------------|----------------|
# | 2d      | 2     | 192                  | 1×             |
# | 1w      | 7     | 672                  | 3.5×           |
# | 1m      | 30    | 2,880                | 15×            |
# | 6m      | 180   | 17,280               | 90×            |
# | 1y      | 365   | 35,040               | 182×           |

DATASET_ESTIMATES: Dict[str, DatasetSizeEstimate] = {
    # ==========================================================================
    # SMALL (10 bâtiments, ~60K nodes, ~50K points TS)
    # Structure : ~15 MB
    # ==========================================================================
    "small-2d": DatasetSizeEstimate("small", "2d", 15, 150),      # ~10M samples
    "small-1w": DatasetSizeEstimate("small", "1w", 15, 500),      # ~34M samples
    "small-1m": DatasetSizeEstimate("small", "1m", 15, 2200),     # ~144M samples
    "small-6m": DatasetSizeEstimate("small", "6m", 15, 13000),    # ~864M samples
    "small-1y": DatasetSizeEstimate("small", "1y", 15, 26000),    # ~1.75B samples

    # ==========================================================================
    # MEDIUM (100 bâtiments, ~600K nodes, ~100K points TS)
    # Structure : ~150 MB
    # ==========================================================================
    "medium-2d": DatasetSizeEstimate("medium", "2d", 150, 300),    # ~19M samples
    "medium-1w": DatasetSizeEstimate("medium", "1w", 150, 1000),   # ~67M samples
    "medium-1m": DatasetSizeEstimate("medium", "1m", 150, 4500),   # ~288M samples
    "medium-6m": DatasetSizeEstimate("medium", "6m", 150, 27000),  # ~1.7B samples
    "medium-1y": DatasetSizeEstimate("medium", "1y", 150, 55000),  # ~3.5B samples

    # ==========================================================================
    # LARGE (1000 bâtiments, ~6M nodes, ~500K points TS)
    # Structure : ~1.5 GB
    # ==========================================================================
    "large-2d": DatasetSizeEstimate("large", "2d", 1500, 1500),    # ~96M samples
    "large-1w": DatasetSizeEstimate("large", "1w", 1500, 5000),    # ~336M samples
    "large-1m": DatasetSizeEstimate("large", "1m", 1500, 22000),   # ~1.4B samples
    "large-6m": DatasetSizeEstimate("large", "6m", 1500, 130000),  # ~8.6B samples
    "large-1y": DatasetSizeEstimate("large", "1y", 1500, 265000),  # ~17.5B samples

    # ==========================================================================
    # Profils legacy (pour compatibilité avec anciens scripts)
    # ==========================================================================
    "medium-10w": DatasetSizeEstimate("medium", "10w", 150, 7500),  # ~10 semaines
    "large-100w": DatasetSizeEstimate("large", "100w", 1500, 190000),  # ~100 semaines
}


@dataclass
class RAMTestConfig:
    """Configuration de test RAM pour une combinaison moteur × profil."""
    engine: EngineType
    profile: str
    ram_min_mb: int  # RAM minimale estimée
    ram_max_mb: int  # RAM maximale utile
    ram_steps: List[int]  # Paliers à tester (en Mo)
    excluded: bool = False  # Configuration exclue (OOM garanti)
    exclusion_reason: str = ""

    # Estimations détaillées
    estimated_structure_mb: int = 0
    estimated_timeseries_mb: int = 0
    estimated_total_mb: int = 0

    @property
    def ram_steps_gb(self) -> List[float]:
        """Paliers en Go pour affichage."""
        return [r / 1024 for r in self.ram_steps]


# =============================================================================
# Matrice de faisabilité M1 (Memgraph in-memory)
# =============================================================================
# Prédiction OOM pour M1 basée sur :
#   RAM_M1 = (structure_mb + timeseries_mb) × 3
#
# Avec 256GB max :
#   - small-* : toujours OK (max ~80GB pour 1y)
#   - medium-2d/1w/1m : OK
#   - medium-6m : ~81GB → OK
#   - medium-1y : ~165GB → OK
#   - large-2d/1w : OK
#   - large-1m : ~70GB → OK
#   - large-6m : ~394GB → OOM !
#   - large-1y : ~800GB → OOM !

def estimate_m1_ram_mb(profile: str) -> int:
    """Estime la RAM nécessaire pour M1 (tout in-memory)."""
    if profile not in DATASET_ESTIMATES:
        return -1

    dataset = DATASET_ESTIMATES[profile]
    # M1 : structure × 3 + timeseries × 3 (overhead Memgraph)
    return int((dataset.structure_mb + dataset.timeseries_mb) * 3)


def get_m1_feasibility_matrix() -> Dict[str, Dict[str, str]]:
    """Retourne la matrice de faisabilité M1 pour toutes les configurations.

    Returns:
        Dict[scale][duration] = "OK (XXX GB)" ou "OOM (XXX GB > 256)"
    """
    matrix = {}
    max_ram_mb = OVH_MAX_RAM_GB * 1024

    scales = ["small", "medium", "large"]
    durations = ["2d", "1w", "1m", "6m", "1y"]

    for scale in scales:
        matrix[scale] = {}
        for duration in durations:
            profile = f"{scale}-{duration}"
            if profile in DATASET_ESTIMATES:
                ram_mb = estimate_m1_ram_mb(profile)
                ram_gb = ram_mb / 1024
                if ram_mb <= max_ram_mb:
                    matrix[scale][duration] = f"OK ({ram_gb:.0f} GB)"
                else:
                    matrix[scale][duration] = f"OOM ({ram_gb:.0f} GB > {OVH_MAX_RAM_GB})"
            else:
                matrix[scale][duration] = "N/A"

    return matrix


def print_m1_feasibility_matrix() -> None:
    """Affiche la matrice de faisabilité M1."""
    matrix = get_m1_feasibility_matrix()

    print("\n" + "=" * 80)
    print("MATRICE DE FAISABILITÉ M1 (Memgraph tout in-memory)")
    print("=" * 80)
    print(f"RAM disponible : {OVH_MAX_RAM_GB} GB")
    print(f"Formule : RAM = (structure + timeseries) × 3")
    print()

    # Header
    durations = ["2d", "1w", "1m", "6m", "1y"]
    header = f"{'Scale':<10}" + "".join(f"{d:>18}" for d in durations)
    print(header)
    print("-" * 80)

    # Rows
    for scale in ["small", "medium", "large"]:
        row = f"{scale:<10}"
        for duration in durations:
            cell = matrix.get(scale, {}).get(duration, "N/A")
            # Colorer OOM en rouge conceptuellement
            if "OOM" in cell:
                row += f"{cell:>18}"
            else:
                row += f"{cell:>18}"
        print(row)

    print()
    print("Légende : OK = faisable, OOM = Out Of Memory garanti")
    print("=" * 80)


def get_full_feasibility_matrix() -> Dict[str, Dict[str, Dict[str, str]]]:
    """Retourne la matrice de faisabilité complète pour tous les moteurs.

    Returns:
        Dict[engine][scale][duration] = "XX GB" ou "OOM"
    """
    matrix = {}
    max_ram_mb = OVH_MAX_RAM_GB * 1024

    scales = ["small", "medium", "large"]
    durations = ["2d", "1w", "1m", "6m", "1y"]

    for engine in EngineType:
        matrix[engine.value] = {}
        profile_engine = ENGINE_PROFILES[engine]

        for scale in scales:
            matrix[engine.value][scale] = {}

            for duration in durations:
                profile = f"{scale}-{duration}"
                if profile not in DATASET_ESTIMATES:
                    matrix[engine.value][scale][duration] = "N/A"
                    continue

                dataset = DATASET_ESTIMATES[profile]

                # Calcul RAM selon type de moteur
                if profile_engine.is_in_memory and profile_engine.timeseries_in_memory:
                    # M1 : tout en RAM
                    ram_mb = int((dataset.structure_mb + dataset.timeseries_mb) * 3)
                elif profile_engine.is_in_memory:
                    # M2 : structure en RAM, TS externe
                    ram_mb = int(dataset.structure_mb * 3) + profile_engine.base_overhead_mb
                else:
                    # P1/P2/O1/O2 : disk-based
                    ram_mb = int(dataset.structure_mb * profile_engine.structure_multiplier)
                    ram_mb += profile_engine.base_overhead_mb
                    # Ajouter un peu pour le cache des TS
                    ram_mb += min(dataset.timeseries_mb // 10, 4096)  # Max 4GB cache TS

                ram_gb = ram_mb / 1024

                if ram_mb <= max_ram_mb:
                    matrix[engine.value][scale][duration] = f"{ram_gb:.0f}"
                else:
                    matrix[engine.value][scale][duration] = f"OOM"

    return matrix


def print_full_feasibility_matrix() -> None:
    """Affiche la matrice de faisabilité complète pour tous les moteurs."""
    matrix = get_full_feasibility_matrix()

    print("\n" + "=" * 100)
    print("MATRICE DE FAISABILITÉ - TOUS LES MOTEURS")
    print("=" * 100)
    print(f"RAM disponible : {OVH_MAX_RAM_GB} GB | OOM = dépassement garanti")
    print()

    scales = ["small", "medium", "large"]
    durations = ["2d", "1w", "1m", "6m", "1y"]

    # Pour chaque échelle
    for scale in scales:
        print(f"\n{'-' * 100}")
        print(f"  {scale.upper()} SCALE")
        print(f"{'-' * 100}")

        # Header avec durées
        header = f"{'Moteur':<12}"
        for d in durations:
            header += f"{d:>12}"
        print(header)
        print("-" * 72)

        # Une ligne par moteur
        for engine in ["P1", "P2", "M1", "M2", "O1", "O2"]:
            row = f"{engine:<12}"
            for duration in durations:
                val = matrix.get(engine, {}).get(scale, {}).get(duration, "N/A")
                if val == "OOM":
                    row += f"{'X OOM':>12}"
                elif val == "N/A":
                    row += f"{'N/A':>12}"
                else:
                    row += f"{val + ' GB':>12}"
            print(row)

    print("\n" + "=" * 100)
    print("ANALYSE CRITIQUE :")
    print("-" * 100)
    print("* P1/P2 (PostgreSQL) : disk-based, RAM = cache -> toujours OK, plateau perf attendu ~8-32GB")
    print("* M1 (Memgraph full) : in-memory total -> OOM sur large-6m et large-1y")
    print("* M2 (Memgraph hybrid) : structure in-memory, TS externe -> OK partout")
    print("* O1/O2 (Oxigraph) : disk-based RDF -> OK partout, mais performances a valider")
    print("=" * 100)


def estimate_ram_requirements(
    engine: EngineType,
    profile: str
) -> Tuple[int, int]:
    """Estime RAM min et max pour une configuration.

    Returns:
        (ram_min_mb, ram_max_mb)
    """
    if profile not in DATASET_ESTIMATES:
        raise ValueError(f"Profil inconnu: {profile}")

    dataset = DATASET_ESTIMATES[profile]
    engine_profile = ENGINE_PROFILES[engine]

    # RAM minimale = overhead + structure (+ TS si in-memory)
    ram_min = engine_profile.base_overhead_mb
    ram_min += int(dataset.structure_mb * engine_profile.structure_multiplier)

    if engine_profile.timeseries_in_memory:
        # M1 : TS en RAM avec overhead ~3× pour index/structures
        ram_min += int(dataset.timeseries_mb * 3)

    # RAM maximale utile (au-delà = gain marginal)
    if engine_profile.is_in_memory:
        # In-memory : besoin de tout + marge GC
        ram_max = int(ram_min * 1.5)
    else:
        # Disk-based : shared_buffers optimal ~25% des données
        ram_max = max(
            engine_profile.base_overhead_mb * 4,
            int(dataset.total_mb * 0.5)
        )

    # Minimum absolu
    ram_min = max(ram_min, 512)  # 512 Mo minimum
    ram_max = max(ram_max, ram_min * 2)

    return ram_min, ram_max


def generate_ram_steps(
    ram_min_mb: int,
    ram_max_mb: int,
    num_steps: int = 5
) -> List[int]:
    """Génère des paliers RAM logarithmiques entre min et max.

    Paliers arrondis à des valeurs "rondes" (512, 1024, 2048, etc.)
    """
    if ram_max_mb <= ram_min_mb:
        return [ram_min_mb]

    # Générer paliers logarithmiques
    log_min = math.log2(ram_min_mb)
    log_max = math.log2(ram_max_mb)

    steps = []
    for i in range(num_steps):
        log_val = log_min + (log_max - log_min) * i / (num_steps - 1)
        val = 2 ** log_val

        # Arrondir à la puissance de 2 la plus proche ou multiple de 1024
        if val < 1024:
            rounded = 512 if val < 768 else 1024
        elif val < 2048:
            rounded = 1024 if val < 1536 else 2048
        else:
            # Arrondir au Go le plus proche
            rounded = round(val / 1024) * 1024

        if rounded not in steps:
            steps.append(rounded)

    # Toujours inclure min et max
    if ram_min_mb not in steps:
        steps.insert(0, ram_min_mb)
    if ram_max_mb not in steps:
        steps.append(ram_max_mb)

    return sorted(set(steps))


def get_test_config(
    engine: EngineType,
    profile: str,
    mode: TestMode = TestMode.GRADIENT,
    host_ram_mb: Optional[int] = None
) -> RAMTestConfig:
    """Génère la configuration de test RAM pour une combinaison.

    Args:
        engine: Type de moteur
        profile: Nom du profil (ex: "small-1w")
        mode: Mode de test
        host_ram_mb: RAM disponible sur l'hôte (pour filtrer les tests impossibles)

    Returns:
        RAMTestConfig avec les paliers à tester
    """
    ram_min, ram_max = estimate_ram_requirements(engine, profile)

    # Vérifier si la configuration est réaliste
    excluded = False
    exclusion_reason = ""

    # M1 avec gros datasets : vérifier contre limite B3 (256 Go)
    if engine == EngineType.M1:
        dataset = DATASET_ESTIMATES[profile]
        # M1 nécessite ~3× la taille des TS en RAM
        estimated_ram_gb = (ram_min / 1024)
        if estimated_ram_gb > B3_MAX_RAM_GB:
            excluded = True
            exclusion_reason = f"M1 + {profile}: RAM estimée {estimated_ram_gb:.0f} Go > B3 max ({B3_MAX_RAM_GB} Go)"

    # Vérifier contre RAM hôte
    if host_ram_mb and ram_min > host_ram_mb:
        excluded = True
        exclusion_reason = f"RAM min ({ram_min/1024:.1f} Go) > RAM hôte ({host_ram_mb/1024:.1f} Go)"

    # Générer les paliers selon le mode
    if excluded:
        steps = []
    elif mode == TestMode.QUICK:
        # Juste baseline (max) et contrainte (min)
        steps = [ram_min, ram_max]
    elif mode == TestMode.DISCOVERY:
        # Plus de paliers pour dichotomie précise
        steps = generate_ram_steps(ram_min, ram_max, num_steps=7)
    else:  # GRADIENT
        steps = generate_ram_steps(ram_min, ram_max, num_steps=5)

    # Filtrer selon RAM hôte si spécifiée
    if host_ram_mb:
        steps = [s for s in steps if s <= host_ram_mb]

    return RAMTestConfig(
        engine=engine,
        profile=profile,
        ram_min_mb=ram_min,
        ram_max_mb=ram_max,
        ram_steps=steps,
        excluded=excluded,
        exclusion_reason=exclusion_reason
    )


@dataclass
class RAMTestSequence:
    """Séquence complète de tests RAM."""
    configs: List[RAMTestConfig]
    total_tests: int
    estimated_duration_min: int  # Estimation durée totale

    def get_runnable(self) -> List[RAMTestConfig]:
        """Retourne uniquement les configurations non exclues."""
        return [c for c in self.configs if not c.excluded]

    def get_excluded(self) -> List[RAMTestConfig]:
        """Retourne les configurations exclues."""
        return [c for c in self.configs if c.excluded]


def generate_test_sequence(
    engines: Optional[List[EngineType]] = None,
    profiles: Optional[List[str]] = None,
    mode: TestMode = TestMode.GRADIENT,
    host_ram_mb: Optional[int] = None
) -> RAMTestSequence:
    """Génère une séquence de tests RAM complète.

    Args:
        engines: Liste des moteurs (défaut: tous)
        profiles: Liste des profils (défaut: tous)
        mode: Mode de test
        host_ram_mb: RAM disponible sur l'hôte

    Returns:
        RAMTestSequence avec toutes les configurations
    """
    if engines is None:
        engines = list(EngineType)
    if profiles is None:
        profiles = list(DATASET_ESTIMATES.keys())

    configs = []
    total_tests = 0

    for profile in profiles:
        for engine in engines:
            config = get_test_config(engine, profile, mode, host_ram_mb)
            configs.append(config)
            total_tests += len(config.ram_steps)

    # Estimation durée : ~2 min par test (ingestion + queries)
    estimated_duration = total_tests * 2

    return RAMTestSequence(
        configs=configs,
        total_tests=total_tests,
        estimated_duration_min=estimated_duration
    )


def auto_discover_ram_min(
    engine: EngineType,
    profile: str,
    run_test_fn,  # Callable[[int], Tuple[bool, float]] -> (success, p95_latency)
    tolerance: float = 0.2
) -> Tuple[int, Dict]:
    """Découvre automatiquement RAM_min par dichotomie.

    Args:
        engine: Type de moteur
        profile: Profil à tester
        run_test_fn: Fonction qui exécute le test et retourne (succès, p95)
        tolerance: Dégradation acceptable vs baseline

    Returns:
        (ram_min_mb, results_dict)
    """
    config = get_test_config(engine, profile, TestMode.DISCOVERY)

    if config.excluded:
        return -1, {"error": config.exclusion_reason}

    results = {}
    baseline_p95 = None
    ram_min = config.ram_max_mb

    # Tester du plus grand au plus petit
    for ram_mb in reversed(config.ram_steps):
        success, p95 = run_test_fn(ram_mb)
        results[ram_mb] = {"success": success, "p95": p95}

        if not success:
            # OOM ou échec
            continue

        if baseline_p95 is None:
            baseline_p95 = p95

        # Vérifier dégradation
        degradation = (p95 - baseline_p95) / baseline_p95 if baseline_p95 > 0 else 0
        results[ram_mb]["degradation"] = degradation

        if degradation <= tolerance:
            ram_min = ram_mb
        else:
            # Dégradation trop importante, arrêter
            break

    return ram_min, results


# =============================================================================
# Utilitaires CLI
# =============================================================================

def print_test_matrix(
    engines: Optional[List[EngineType]] = None,
    profiles: Optional[List[str]] = None,
    host_ram_mb: Optional[int] = None
) -> None:
    """Affiche la matrice des tests RAM."""
    sequence = generate_test_sequence(engines, profiles, TestMode.GRADIENT, host_ram_mb)

    print("=" * 80)
    print("MATRICE DE TESTS RAM")
    print("=" * 80)

    if host_ram_mb:
        print(f"RAM hôte: {host_ram_mb/1024:.1f} Go")
    print(f"Tests totaux: {sequence.total_tests}")
    print(f"Durée estimée: {sequence.estimated_duration_min} min")
    print()

    # Grouper par profil
    by_profile = {}
    for config in sequence.configs:
        if config.profile not in by_profile:
            by_profile[config.profile] = []
        by_profile[config.profile].append(config)

    for profile in sorted(by_profile.keys()):
        print(f"\n📊 {profile}")
        print("-" * 60)

        for config in by_profile[profile]:
            if config.excluded:
                print(f"  ❌ {config.engine.value}: EXCLU - {config.exclusion_reason}")
            else:
                steps_str = ", ".join(f"{s/1024:.1f}Go" for s in config.ram_steps)
                print(f"  ✓ {config.engine.value}: [{steps_str}]")
                print(f"      RAM estimée: {config.ram_min_mb/1024:.1f} - {config.ram_max_mb/1024:.1f} Go")

    # Résumé des exclusions
    excluded = sequence.get_excluded()
    if excluded:
        print(f"\n⚠️  {len(excluded)} configurations exclues")


def main():
    """CLI pour visualiser les configurations RAM."""
    import argparse

    parser = argparse.ArgumentParser(description="Configuration RAM pour benchmarks")
    parser.add_argument("--host-ram", type=int, help="RAM hôte en Go")
    parser.add_argument("--profile", help="Profil spécifique (ex: small-1w)")
    parser.add_argument("--engine", help="Moteur spécifique (ex: M1)")
    args = parser.parse_args()

    host_ram_mb = args.host_ram * 1024 if args.host_ram else None
    engines = [EngineType(args.engine)] if args.engine else None
    profiles = [args.profile] if args.profile else None

    print_test_matrix(engines, profiles, host_ram_mb)


if __name__ == "__main__":
    main()
