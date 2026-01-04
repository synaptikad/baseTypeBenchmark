#!/usr/bin/env python3
"""BaseType Benchmark - Interactive Workflow Runner

A verbose, interactive benchmark runner for comparing storage paradigms
for building information systems.

Usage:
    python run.py                    # Interactive mode (recommended)
    python run.py --help             # Show CLI options
"""

import os
import sys
import json
import time
import shutil
import subprocess
from decimal import Decimal
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Ensure src/ is in path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import cgroup-based metrics (precise Linux measurements)
from metrics import Metrics, compute_delta, check_oom


# Custom JSON encoder for Decimal and other types
class BenchmarkEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal, datetime, etc."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)

# ═══════════════════════════════════════════════════════════════════════════════
# ANSI STYLING
# ═══════════════════════════════════════════════════════════════════════════════

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ═══════════════════════════════════════════════════════════════════════════════
# VERBOSE LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

VERBOSE = True  # Global verbosity flag


def log(msg: str, level: str = "info"):
    """Print a log message with timestamp and level."""
    ts = datetime.now().strftime("%H:%M:%S")
    if level == "info":
        print(f"{DIM}[{ts}]{RESET} {BLUE}ℹ{RESET}  {msg}")
    elif level == "ok":
        print(f"{DIM}[{ts}]{RESET} {GREEN}✓{RESET}  {msg}")
    elif level == "warn":
        print(f"{DIM}[{ts}]{RESET} {YELLOW}⚠{RESET}  {msg}")
    elif level == "error":
        print(f"{DIM}[{ts}]{RESET} {RED}✗{RESET}  {msg}")
    elif level == "step":
        print(f"{DIM}[{ts}]{RESET} {CYAN}▸{RESET}  {msg}")
    elif level == "progress":
        print(f"{DIM}[{ts}]{RESET} {MAGENTA}◆{RESET}  {msg}")


def log_section(title: str):
    """Print a section header."""
    width = 70
    print(f"\n{BOLD}{'═' * width}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'═' * width}{RESET}\n")


def log_subsection(title: str):
    """Print a subsection header."""
    print(f"\n{CYAN}── {title} ──{RESET}\n")


def log_box(lines: List[str], color: str = BLUE):
    """Print a boxed message."""
    width = max(len(line) for line in lines) + 4
    print(f"{color}┌{'─' * width}┐{RESET}")
    for line in lines:
        print(f"{color}│{RESET}  {line.ljust(width - 2)}{color}│{RESET}")
    print(f"{color}└{'─' * width}┘{RESET}")


def elapsed_str(seconds: float) -> str:
    """Format elapsed time as human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        m, s = divmod(int(seconds), 60)
        return f"{m}m {s}s"
    else:
        h, rem = divmod(int(seconds), 3600)
        m, s = divmod(rem, 60)
        return f"{h}h {m}m {s}s"


def progress_bar(current: int, total: int, width: int = 40, prefix: str = "") -> str:
    """Generate a progress bar string."""
    pct = current / total if total > 0 else 0
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    return f"{prefix}[{bar}] {current}/{total} ({pct*100:.0f}%)"


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

SCENARIOS = {
    "P1": {
        "name": "PostgreSQL Relational",
        "description": "Tables SQL normalisées + TimescaleDB",
        "containers": ["timescaledb"],
        "color": GREEN,
    },
    "P2": {
        "name": "PostgreSQL JSONB",
        "description": "Documents JSONB + TimescaleDB",
        "containers": ["timescaledb"],
        "color": GREEN,
    },
    "M1": {
        "name": "Memgraph Standalone",
        "description": "Property Graph in-memory avec chunks timeseries (Cypher)",
        "containers": ["memgraph"],
        "color": MAGENTA,
    },
    "M2": {
        "name": "Memgraph + TimescaleDB",
        "description": "Graphe hybride + TimescaleDB pour séries",
        "containers": ["memgraph", "timescaledb"],
        "color": MAGENTA,
    },
    # O1 retiré : Oxigraph ne peut pas embarquer les chunks timeseries en RDF (explosion mémoire)
    # Le benchmark cible M1 vs M2 pour montrer que l'approche hybride est supérieure
    "O2": {
        "name": "Oxigraph + TimescaleDB",
        "description": "RDF hybride + TimescaleDB pour séries",
        "containers": ["oxigraph", "timescaledb"],
        "color": CYAN,
    },
}

QUERIES = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13"]

# ═══════════════════════════════════════════════════════════════════════════════
# DOCKER HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

DOCKER_DIR = Path(__file__).parent / "docker"


def get_docker_compose_cmd() -> str:
    """Get the docker compose command (v2 or v1)."""
    result = subprocess.run(["docker", "compose", "version"], capture_output=True)
    if result.returncode == 0:
        return "docker compose"
    return "docker-compose"


DOCKER_COMPOSE = get_docker_compose_cmd()


def check_postgres_tables_exist() -> bool:
    """Check if PostgreSQL tables exist (nodes, edges, timeseries)."""
    try:
        from src.basetype_benchmark.engines.postgres import PostgresEngine
        engine = PostgresEngine()
        result = engine.execute_query("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name IN ('nodes', 'edges', 'timeseries')
        """)
        count = result[0][0] if result else 0
        engine.close()
        return count >= 3  # All 3 tables exist
    except Exception:
        return False


def docker_update_memory(containers: List[str], ram_gb: int, clear_cache: bool = True) -> bool:
    """Update memory limit on containers and optionally restart to clear caches.
    
    This preserves PostgreSQL/TimescaleDB data between RAM level iterations
    while ensuring cache isolation for accurate benchmarking.
    
    Uses 'docker update --memory' + 'docker restart' to:
    - Change RAM limit dynamically
    - Clear PostgreSQL shared_buffers and OS page cache (restart)
    - Preserve data on named volumes
    
    Args:
        containers: List of container names to update
        ram_gb: New RAM limit in GB
        clear_cache: If True, restart containers to clear caches (default True for benchmark accuracy)
        
    Returns:
        True if all containers updated successfully
    """
    memory_limit = f"{ram_gb}g"
    success = True
    
    for container in containers:
        container_name = f"btb_{container}"
        
        # Check if container exists (running or stopped)
        check = subprocess.run(
            f"docker ps -aq --filter 'name={container_name}'",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if not check.stdout.strip():
            log(f"Container {container_name} n'existe pas, skip update", "warn")
            continue
            
        # Update memory limit
        result = subprocess.run(
            f"docker update --memory {memory_limit} --memory-swap {memory_limit} {container_name}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            log(f"Échec update RAM {container_name}: {result.stderr}", "error")
            success = False
            continue
        
        if clear_cache:
            # Restart to clear caches (PostgreSQL shared_buffers, OS page cache)
            # This ensures fair comparison between RAM levels
            log(f"Restart {container_name} pour vider les caches...", "step")
            restart = subprocess.run(
                f"docker restart {container_name}",
                shell=True,
                capture_output=True,
                text=True
            )
            if restart.returncode != 0:
                log(f"Échec restart {container_name}: {restart.stderr}", "error")
                success = False
                continue
                
        log(f"RAM {container_name} → {ram_gb}GB ✓" + (" (cache vidé)" if clear_cache else ""), "ok")
    
    # Wait for containers to be healthy after restart
    if clear_cache and success:
        log("Attente santé des containers après restart...", "step")
        time.sleep(3)  # Initial delay
        max_wait = 60
        start = time.time()
        
        while time.time() - start < max_wait:
            all_healthy = True
            for container in containers:
                container_name = f"btb_{container}"
                # Check health status
                hc_check = subprocess.run(
                    f"docker inspect --format='{{{{.State.Health.Status}}}}' {container_name}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                status = hc_check.stdout.strip().replace("'", "")
                if status not in ("healthy", ""):  # "" means no healthcheck
                    all_healthy = False
                    break
            
            if all_healthy:
                break
            time.sleep(2)
        else:
            log("Timeout attente santé après restart", "warn")
    
    return success


def docker_stop_all(preserve_volumes: bool = False):
    """Stop all benchmark containers.
    
    Args:
        preserve_volumes: If True, keep volumes (for reuse across RAM levels)
    """
    log("Arrêt de tous les containers benchmark...", "step")
    
    if preserve_volumes:
        # Just stop and remove containers, keep volumes
        subprocess.run(
            f"{DOCKER_COMPOSE} stop",
            shell=True,
            cwd=str(DOCKER_DIR),
            capture_output=True
        )
        subprocess.run(
            f"{DOCKER_COMPOSE} rm -f",
            shell=True,
            cwd=str(DOCKER_DIR),
            capture_output=True
        )
    else:
        # Full cleanup with volumes
        subprocess.run(
            f"{DOCKER_COMPOSE} down -v --remove-orphans",
            shell=True,
            cwd=str(DOCKER_DIR),
            capture_output=True
        )
    
    # Force stop any remaining btb_ containers
    result = subprocess.run(
        "docker ps -q --filter 'name=btb_'",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        log("Containers résiduels détectés, arrêt forcé...", "warn")
        subprocess.run(
            "docker ps -q --filter 'name=btb_' | xargs -r docker stop",
            shell=True,
            capture_output=True
        )
        rm_flag = "" if preserve_volumes else "-v"
        subprocess.run(
            f"docker ps -aq --filter 'name=btb_' | xargs -r docker rm -f {rm_flag}",
            shell=True,
            capture_output=True
        )
    
    log("Environnement nettoyé", "ok")


def docker_verify_isolation(expected_containers: List[str]) -> bool:
    """Verify only expected containers are running (academic rigor)."""
    result = subprocess.run(
        "docker ps --filter 'name=btb_' --format '{{.Names}}'",
        shell=True,
        capture_output=True,
        text=True
    )
    running = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
    expected = set(f"btb_{c}" for c in expected_containers)
    
    unexpected = running - expected
    if unexpected:
        log(f"ISOLATION VIOLATION: containers inattendus: {unexpected}", "error")
        return False
    
    missing = expected - running
    if missing:
        log(f"Containers manquants: {missing}", "warn")
        return False
    
    return True


def docker_start(containers: List[str], ram_gb: int, data_dir: Optional[Path] = None, preserve_volumes: bool = False) -> bool:
    """Start ONLY specified containers with RAM limit (strict isolation).
    
    Args:
        containers: List of container names to start
        ram_gb: RAM limit in GB
        data_dir: Dataset directory path
        preserve_volumes: If True, don't delete volumes (for RAM variance on persistent storage)
                         If containers are already running, just update RAM limit
    """
    log(f"Démarrage containers: {', '.join(containers)} (limite {ram_gb}GB RAM)...", "step")
    
    env = os.environ.copy()
    env["MEMORY_LIMIT"] = f"{ram_gb}g"
    if data_dir:
        env["BTB_DATA_DIR"] = str(data_dir.resolve())
    
    if preserve_volumes:
        # Check if all required containers exist (running or stopped)
        all_exist = True
        for container in containers:
            check = subprocess.run(
                f"docker ps -aq --filter 'name=btb_{container}'",
                shell=True,
                capture_output=True,
                text=True
            )
            if not check.stdout.strip():
                all_exist = False
                break
        
        if all_exist:
            # Containers exist - update RAM limit and restart (clears cache, preserves data)
            log("Containers existants → update RAM + restart (cache vidé, données préservées)", "step")
            if docker_update_memory(containers, ram_gb, clear_cache=True):
                # docker_update_memory already waits for health after restart
                if docker_verify_isolation(containers):
                    log(f"RAM mise à jour avec succès → {ram_gb}GB (cache vidé)", "ok")
                    return True
                else:
                    log("Containers non sains après update, recréation...", "warn")
            else:
                log("Échec update RAM, recréation containers...", "warn")
        
        # Containers don't exist or update failed - just start (volumes persist)
        log("Démarrage containers avec volumes existants...", "step")
    else:
        # CRITICAL: Full cleanup for isolation
        log("Nettoyage environnement (isolation académique)...", "step")
        subprocess.run(
            f"{DOCKER_COMPOSE} down -v --remove-orphans",
            shell=True,
            cwd=str(DOCKER_DIR),
            env=env,
            capture_output=True
        )
        
        # Force cleanup any residual
        subprocess.run(
            "docker ps -aq --filter 'name=btb_' | xargs -r docker rm -fv 2>/dev/null",
            shell=True,
            capture_output=True
        )
    
    # Small delay to ensure resources are released
    time.sleep(1)
    
    # Start ONLY requested containers
    container_str = " ".join(containers)
    log(f"Démarrage strict: {container_str} uniquement", "step")
    
    result = subprocess.run(
        f"{DOCKER_COMPOSE} up -d {container_str}",
        shell=True,
        cwd=str(DOCKER_DIR),
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        log(f"Échec démarrage containers: {result.stderr}", "error")
        return False
    
    # Wait for health/running state
    log("Attente santé des containers...", "step")
    max_wait = 60
    start = time.time()
    
    while time.time() - start < max_wait:
        all_ready = True
        for container in containers:
            # First check if container has healthcheck
            hc_check = subprocess.run(
                f"docker inspect --format='{{{{.State.Health}}}}' btb_{container}",
                shell=True,
                capture_output=True,
                text=True
            )
            has_healthcheck = hc_check.returncode == 0 and "<nil>" not in hc_check.stdout
            
            if has_healthcheck:
                # Container has healthcheck - wait for healthy
                check = subprocess.run(
                    f"docker inspect --format='{{{{.State.Health.Status}}}}' btb_{container}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                status = check.stdout.strip().replace("'", "")
                if status != "healthy":
                    all_ready = False
                    break
            else:
                # No healthcheck (e.g., Oxigraph) - just check if running
                check = subprocess.run(
                    f"docker inspect --format='{{{{.State.Running}}}}' btb_{container}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                is_running = check.stdout.strip().replace("'", "").lower() == "true"
                if not is_running:
                    all_ready = False
                    break
        
        if all_ready:
            # Extra wait for containers without healthcheck to ensure service is up
            no_hc_containers = [c for c in containers if c == "oxigraph"]
            if no_hc_containers:
                time.sleep(3)  # Give services time to start
            
            elapsed = time.time() - start
            log(f"Containers opérationnels ({elapsed:.1f}s)", "ok")
            
            # CRITICAL: Verify isolation before proceeding
            if not docker_verify_isolation(containers):
                log("Échec vérification isolation - abandon", "error")
                return False
            
            log(f"Isolation vérifiée: seuls {containers} actifs ✓", "ok")
            return True
        
        time.sleep(2)
        print(".", end="", flush=True)
    
    print()
    log(f"Timeout après {max_wait}s", "warn")
    return True  # Continue anyway


def get_container_metrics(container: str) -> Metrics:
    """Get metrics for a container using cgroups (precise) or docker stats (fallback)."""
    return Metrics.capture(f"btb_{container}")


def docker_get_memory_usage(container: str) -> Optional[float]:
    """Get current memory usage of a container in MB (via cgroups)."""
    m = get_container_metrics(container)
    return m.memory_mb if m.memory_mb > 0 else None


# ═══════════════════════════════════════════════════════════════════════════════
# DATASET MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def get_exports_dir() -> Path:
    return Path(__file__).parent / "src" / "basetype_benchmark" / "dataset" / "exports"


def get_results_dir() -> Path:
    return Path(__file__).parent / "benchmark_results"


def get_available_datasets() -> List[Dict[str, Any]]:
    """Get list of available datasets with metadata."""
    exports = get_exports_dir()
    if not exports.exists():
        return []
    
    datasets = []
    for d in sorted(exports.iterdir()):
        if d.is_dir() and (d / "parquet").exists():
            fingerprint_file = d / "fingerprint.json"
            fingerprint = {}
            if fingerprint_file.exists():
                try:
                    fingerprint = json.loads(fingerprint_file.read_text())
                except:
                    pass
            
            size_mb = sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) / (1024 * 1024)
            
            # Extract counts (handle both old and new fingerprint formats)
            counts = fingerprint.get("counts", {})
            nodes = counts.get("nodes") or fingerprint.get("nodes_count", "?")
            edges = counts.get("edges") or fingerprint.get("edges_count", "?")
            timeseries = counts.get("timeseries") or fingerprint.get("timeseries_count", "?")
            
            datasets.append({
                "name": d.name,
                "path": d,
                "size_mb": size_mb,
                "nodes": nodes,
                "edges": edges,
                "timeseries": timeseries,
            })
    
    return datasets


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def prompt(question: str, default: str = "", choices: List[str] = None) -> str:
    """Prompt user for input with optional default and validation."""
    suffix = f" [{default}]" if default else ""
    if choices:
        suffix = f" ({'/'.join(choices)}){suffix}"
    
    while True:
        answer = input(f"{question}{suffix}: ").strip()
        if not answer and default:
            return default
        if choices and answer.upper() not in [c.upper() for c in choices]:
            print(f"  {YELLOW}Entrez l'une des options: {', '.join(choices)}{RESET}")
            continue
        return answer if answer else default


def prompt_choice(question: str, options: List[str], default: int = 1, show_options: bool = True) -> int:
    """Prompt user to choose from numbered options."""
    if show_options:
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
    
    while True:
        answer = input(f"\n{question} [1-{len(options)}, défaut={default}]: ").strip()
        if not answer:
            return default
        try:
            idx = int(answer)
            if 1 <= idx <= len(options):
                return idx
        except ValueError:
            pass
        print(f"  {YELLOW}Entrez un nombre entre 1 et {len(options)}{RESET}")


def confirm(question: str, default: bool = True) -> bool:
    """Ask for confirmation."""
    suffix = "[O/n]" if default else "[o/N]"
    answer = input(f"{question} {suffix}: ").strip().lower()
    if not answer:
        return default
    return answer in ("o", "y", "oui", "yes")


# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW: GENERATE DATASET
# ═══════════════════════════════════════════════════════════════════════════════

def workflow_generate():
    """Generate a new dataset."""
    log_section("GÉNÉRATION DE DATASET")
    
    from basetype_benchmark.dataset.dataset_manager import DatasetManager
    
    # Recommended profile
    log_box([
        "Profil recommandé pour ce benchmark:",
        "",
        f"  {BOLD}large-1w{RESET} (1 semaine, ~1.2M points)",
        "",
        "Ce profil offre un bon équilibre entre:",
        "  • Taille suffisante pour stresser les moteurs",
        "  • Temps de génération raisonnable (~5-10 min)",
        "  • Taille disque modérée (~14 GB)",
        "",
        "Pour un test rapide, utilisez small-2d.",
    ])
    
    print()
    
    # Scale selection
    log_subsection("Échelle du dataset")
    print("  L'échelle détermine le nombre de bâtiments et équipements:\n")
    scales = [
        "small  - 1 bâtiment, ~50K nœuds (tests rapides)",
        "medium - 5 bâtiments, ~250K nœuds (validation)",
        f"{BOLD}large  - 25 bâtiments, ~1.2M nœuds (benchmark complet){RESET}",
    ]
    scale_idx = prompt_choice("Choisir l'échelle", scales, default=3)
    scale = ["small", "medium", "large"][scale_idx - 1]
    log(f"Échelle sélectionnée: {scale}", "ok")
    
    # Duration selection
    log_subsection("Fenêtre temporelle")
    print("  La durée détermine la quantité de séries temporelles:\n")
    durations = [
        "2d - 2 jours (~500 MB, test rapide)",
        f"{BOLD}1w - 1 semaine (~2 GB, recommandé){RESET}",
        "1m - 1 mois (~8 GB, patterns mensuels)",
    ]
    duration_idx = prompt_choice("Choisir la durée", durations, default=2)
    duration = ["2d", "1w", "1m"][duration_idx - 1]
    log(f"Durée sélectionnée: {duration}", "ok")
    
    profile = f"{scale}-{duration}"
    
    # Seed
    print()
    seed_str = prompt("Seed aléatoire (reproductibilité)", "42")
    seed = int(seed_str)
    
    # Check if exists
    exports = get_exports_dir()
    target = exports / f"{profile}_seed{seed}"
    
    if target.exists():
        print()
        log(f"Dataset {profile}_seed{seed} existe déjà", "warn")
        if not confirm("Régénérer (supprime l'existant)?", default=False):
            return
        log("Suppression dataset existant...", "step")
        shutil.rmtree(target)
        log("Supprimé", "ok")
    
    # Summary and confirmation
    log_subsection("Récapitulatif")
    print(f"  Profil:      {BOLD}{profile}{RESET}")
    print(f"  Seed:        {seed}")
    print(f"  Destination: {target}")
    print()
    
    if not confirm("Lancer la génération?"):
        return
    
    # Generate
    print()
    log_section("GÉNÉRATION EN COURS")
    
    t0 = time.time()
    
    log("Initialisation du générateur...", "step")
    manager = DatasetManager()
    
    log(f"Génération du profil {profile} (seed={seed})...", "progress")
    log("Cette opération peut prendre plusieurs minutes.", "info")
    print()
    
    try:
        parquet_dir, fingerprint = manager.generate_parquet_only(profile, seed)
        elapsed = time.time() - t0
        
        print()
        log_section("GÉNÉRATION TERMINÉE")
        
        log(f"Dataset généré en {elapsed_str(elapsed)}", "ok")
        print()
        print(f"  {BOLD}Statistiques:{RESET}")
        # Handle both old and new fingerprint formats
        counts = fingerprint.get("counts", {})
        nodes = counts.get("nodes") or fingerprint.get('nodes_count')
        edges = counts.get("edges") or fingerprint.get('edges_count')
        points = counts.get("timeseries") or fingerprint.get('timeseries_count')
        print(f"    Nœuds:          {nodes:,}" if nodes else "    Nœuds:          N/A")
        print(f"    Arêtes:         {edges:,}" if edges else "    Arêtes:         N/A")
        print(f"    Points mesure:  {points:,}" if points else "    Points mesure:  N/A")
        print(f"    Destination:    {parquet_dir}")
        
    except Exception as e:
        log(f"Erreur lors de la génération: {e}", "error")
        import traceback
        traceback.print_exc()
    
    print()
    input("Appuyez sur Entrée pour continuer...")


# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW: RUN BENCHMARK
# ═══════════════════════════════════════════════════════════════════════════════

def workflow_benchmark():
    """Run benchmark on selected dataset."""
    log_section("EXÉCUTION DU BENCHMARK")
    
    # Check datasets
    datasets = get_available_datasets()
    if not datasets:
        log("Aucun dataset disponible. Générez-en un d'abord (option 1).", "error")
        input("\nAppuyez sur Entrée...")
        return
    
    # Dataset selection
    log_subsection("Sélection du dataset")
    print("  Datasets disponibles:\n")
    for i, ds in enumerate(datasets, 1):
        size_str = f"{ds['size_mb']:.0f} MB" if ds['size_mb'] < 1024 else f"{ds['size_mb']/1024:.1f} GB"
        print(f"  {i}. {BOLD}{ds['name']}{RESET} ({size_str})")
        if isinstance(ds['nodes'], int):
            print(f"     {DIM}{ds['nodes']:,} nœuds, {ds['edges']:,} arêtes{RESET}")
    
    ds_idx = prompt_choice("\nChoisir le dataset", [ds['name'] for ds in datasets], default=1, show_options=False)
    selected_ds = datasets[ds_idx - 1]
    log(f"Dataset sélectionné: {selected_ds['name']}", "ok")
    
    # Scenario selection
    log_subsection("Sélection des scénarios")
    print("  Scénarios disponibles:\n")
    
    scenario_list = list(SCENARIOS.keys())
    for sc_id in scenario_list:
        sc = SCENARIOS[sc_id]
        print(f"  • {sc['color']}{BOLD}{sc_id}{RESET}: {sc['name']}")
        print(f"    {DIM}{sc['description']}{RESET}")
    
    print(f"\n  • {BOLD}ALL{RESET}: Exécuter les 6 scénarios")
    
    print()
    sc_choice = prompt("Scénario(s)", "ALL", ["P1", "P2", "M1", "M2", "O2", "ALL"])
    
    if sc_choice.upper() == "ALL":
        scenarios = scenario_list
    else:
        scenarios = [sc_choice.upper()]
    
    log(f"Scénarios: {', '.join(scenarios)}", "ok")
    
    # RAM selection - RAM Gradient protocol
    log_subsection("Protocole RAM-Gradient")
    print("  Le benchmark teste chaque scénario avec différents niveaux de RAM")
    print("  pour identifier les seuils OOM et mesurer l'efficience (perf/GB).\n")
    
    print("  Niveaux disponibles:\n")
    all_ram_levels = [4, 8, 16, 32, 64, 128, 256]
    
    print("  Mode de sélection:\n")
    ram_modes = [
        "SINGLE   - Un seul niveau (test rapide)",
        "GRADIENT - Plusieurs niveaux (protocole complet)",
        "AUTO     - Niveaux adaptés au dataset"
    ]
    ram_mode_idx = prompt_choice("Choisir le mode", ram_modes, default=2)
    
    if ram_mode_idx == 1:  # SINGLE
        print("\n  Niveaux RAM:\n")
        ram_options = [f"{r} GB" for r in all_ram_levels]
        ram_idx = prompt_choice("Choisir la RAM", ram_options, default=2)
        ram_levels = [all_ram_levels[ram_idx - 1]]
    elif ram_mode_idx == 2:  # GRADIENT
        print("\n  Niveaux à tester (ex: 8,16,32,64 ou ALL):\n")
        for i, r in enumerate(all_ram_levels):
            print(f"    {r} GB")
        ram_input = prompt("\n  Niveaux", "8,16,32,64")
        if ram_input.upper() == "ALL":
            ram_levels = all_ram_levels
        else:
            ram_levels = [int(x.strip()) for x in ram_input.split(",")]
    else:  # AUTO
        # Estimate based on dataset size
        ds_size_gb = selected_ds['size_mb'] / 1024
        if ds_size_gb < 1:
            ram_levels = [4, 8, 16]
            log(f"Dataset petit ({ds_size_gb:.1f}GB) → RAM: 4, 8, 16 GB", "info")
        elif ds_size_gb < 5:
            ram_levels = [8, 16, 32]
            log(f"Dataset moyen ({ds_size_gb:.1f}GB) → RAM: 8, 16, 32 GB", "info")
        else:
            ram_levels = [16, 32, 64, 128]
            log(f"Dataset large ({ds_size_gb:.1f}GB) → RAM: 16, 32, 64, 128 GB", "info")
    
    log(f"Niveaux RAM: {ram_levels} GB", "ok")
    
    # Query selection
    log_subsection("Sélection des requêtes")
    print("  Requêtes benchmark (Q1-Q13):\n")
    print("  • Q1-Q5:   Traversées de graphe (structure)")
    print("  • Q6-Q7:   Agrégations séries temporelles")
    print("  • Q8-Q13:  Requêtes hybrides (graphe + séries)")
    
    print()
    query_choice = prompt("Requêtes (ALL ou liste: Q1,Q4,Q6)", "ALL")
    
    if query_choice.upper() == "ALL":
        queries = QUERIES
    else:
        queries = [q.strip().upper() for q in query_choice.split(",")]
    
    log(f"Requêtes: {', '.join(queries)}", "ok")
    
    # Summary
    log_subsection("Récapitulatif")
    
    total_combinations = len(scenarios) * len(ram_levels)
    total_runs = total_combinations * len(queries)
    print(f"  Dataset:    {BOLD}{selected_ds['name']}{RESET}")
    print(f"  Scénarios:  {', '.join(scenarios)} ({len(scenarios)})")
    print(f"  RAM:        {', '.join(str(r) for r in ram_levels)} GB ({len(ram_levels)} niveaux)")
    print(f"  Requêtes:   {len(queries)} ({queries[0]}...{queries[-1]})")
    print()
    print(f"  {BOLD}Total:      {len(scenarios)} × {len(ram_levels)} × {len(queries)} = {total_runs} exécutions{RESET}")
    
    est_time = total_combinations * 120 + total_runs * 3  # ~2min load + 3s/query
    print(f"  Durée est.: ~{elapsed_str(est_time)}")
    
    print()
    if not confirm("Lancer le benchmark?"):
        docker_stop_all()
        return
    
    # Helper function for loading with error handling
    def _do_load(scenario: str, path: Path, ram: int, graph_only: bool = False) -> Optional[float]:
        """Load data, return elapsed time or None on error."""
        what = "graphe" if graph_only else "données"
        log(f"Chargement {what} ({scenario})...", "step")
        t0 = time.time()
        try:
            load_data_for_scenario(scenario, path, ram, graph_only=graph_only)
            elapsed = time.time() - t0
            log(f"Chargé en {elapsed_str(elapsed)}", "ok")
            return elapsed
        except Exception as e:
            log(f"Erreur chargement: {e}", "error")
            is_oom = "OOM" in str(e) or "memory" in str(e).lower()
            if is_oom:
                log(f"{RED}OOM détecté{RESET}", "warn")
            docker_stop_all()
            return None
    
    # Execute benchmark
    log_section("EXÉCUTION DU BENCHMARK")
    
    results_dir = get_results_dir()
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = results_dir / f"{timestamp}_{selected_ds['name']}"
    run_dir.mkdir(exist_ok=True)
    
    log(f"Résultats → {run_dir}", "info")
    
    # Optimize scenario order: group TimescaleDB users together
    # P1 → P2 → M2 → O2 (share TimescaleDB) then M1 (standalone with chunks)
    OPTIMAL_ORDER = ["P1", "P2", "M2", "O2", "M1"]
    scenarios_ordered = sorted(scenarios, key=lambda s: OPTIMAL_ORDER.index(s) if s in OPTIMAL_ORDER else 99)
    
    if scenarios_ordered != scenarios:
        log(f"Ordre optimisé: {' → '.join(scenarios_ordered)} (partage TimescaleDB)", "info")
    
    all_results = {}  # {scenario: {ram_gb: {queries...}}}
    t0_total = time.time()
    
    total_combinations = len(scenarios) * len(ram_levels)
    combo_idx = 0
    
    # Track TimescaleDB state across scenarios
    timescale_loaded_for_ram = {}  # {ram_gb: True} when timeseries loaded
    
    for scenario in scenarios_ordered:
        sc_info = SCENARIOS[scenario]
        all_results[scenario] = {}
        first_ram_run = True
        prev_ram_avg_latency = None  # For plateau detection
        skip_remaining_ram = False  # Set True if plateau detected
        
        for ram_gb in ram_levels:
            # Skip if plateau was detected
            if skip_remaining_ram:
                log(f"Plateau détecté → skip {scenario}@{ram_gb}GB", "info")
                combo_idx += 1
                continue
            
            combo_idx += 1
            
            log_subsection(f"[{combo_idx}/{total_combinations}] {sc_info['color']}{scenario}{RESET} @ {ram_gb}GB RAM")
            
            # Determine container and loading strategy
            # - P1/P2: preserve TimescaleDB volumes across RAM levels
            # - M2/O2: can reuse TimescaleDB if already loaded at this RAM level
            # - M1: always full reload (standalone in-memory with chunks)
            
            uses_timescale = scenario in ("P1", "P2", "M2", "O2")
            timescale_ready = timescale_loaded_for_ram.get(ram_gb, False)
            can_preserve = uses_timescale and (not first_ram_run or timescale_ready)
            
            # Start containers with specific RAM
            if not docker_start(sc_info["containers"], ram_gb, selected_ds["path"], preserve_volumes=can_preserve):
                log(f"Échec démarrage containers pour {scenario}@{ram_gb}GB", "error")
                all_results[scenario][ram_gb] = {"status": "container_error", "queries": {}}
                continue
            
            # Smart loading strategy
            load_time = 0
            
            if scenario in ("P1", "P2"):
                # PostgreSQL: check if tables actually exist before skipping
                tables_exist = check_postgres_tables_exist() if not first_ram_run else False
                
                if not first_ram_run and tables_exist:
                    log(f"PostgreSQL persistant → skip rechargement", "ok")
                elif timescale_ready and tables_exist:
                    log(f"TimescaleDB déjà chargé (RAM {ram_gb}GB) → skip", "ok")
                else:
                    if not first_ram_run and not tables_exist:
                        log(f"Tables manquantes → rechargement nécessaire", "warn")
                    load_time = _do_load(scenario, selected_ds["path"], ram_gb)
                    if load_time is None:
                        all_results[scenario][ram_gb] = {"status": "load_error", "queries": {}}
                        continue
                    timescale_loaded_for_ram[ram_gb] = True
                    
            elif scenario in ("M2", "O2"):
                # Hybrid: need to load graph, but TimescaleDB may be ready
                if timescale_ready:
                    log(f"TimescaleDB déjà chargé → chargement graphe uniquement", "info")
                    load_time = _do_load(scenario, selected_ds["path"], ram_gb, graph_only=True)
                else:
                    load_time = _do_load(scenario, selected_ds["path"], ram_gb)
                    timescale_loaded_for_ram[ram_gb] = True
                if load_time is None:
                    all_results[scenario][ram_gb] = {"status": "load_error", "queries": {}}
                    continue
                    
            else:  # M1 - standalone with chunks
                load_time = _do_load(scenario, selected_ds["path"], ram_gb)
                if load_time is None:
                    all_results[scenario][ram_gb] = {"status": "load_error", "queries": {}}
                    continue
            
            first_ram_run = False
            
            # Capture metrics after load and RESET peak for query-only measurement
            metrics_after_load = {}
            total_mem_after_load = 0
            for container in sc_info["containers"]:
                m = get_container_metrics(container)
                metrics_after_load[container] = {
                    "memory_mb": m.memory_mb,
                    "memory_peak_mb": m.memory_peak_mb,
                }
                total_mem_after_load += m.memory_mb
                # Reset peak to measure query-only RAM usage
                reset_ok = m.reset_peak()
                pct = (m.memory_mb / 1024) / ram_gb * 100
                color = GREEN if pct < 70 else YELLOW if pct < 90 else RED
                reset_str = " (peak reset ✓)" if reset_ok else ""
                log(f"  RAM {container}: {m.memory_mb:.0f}MB ({color}{pct:.0f}%{RESET}){reset_str}", "info")
            
            # Show total for multi-container scenarios
            if len(sc_info["containers"]) > 1:
                total_pct = (total_mem_after_load / 1024) / ram_gb * 100
                color = GREEN if total_pct < 70 else YELLOW if total_pct < 90 else RED
                log(f"  RAM TOTAL: {total_mem_after_load:.0f}MB ({color}{total_pct:.0f}%{RESET})", "info")
            
            # Execute queries with precise metrics
            scenario_results = {
                "scenario": scenario, 
                "ram_gb": ram_gb,
                "load_time_s": load_time, 
                "mem_after_load_mb": metrics_after_load,
                "mem_after_load_total_mb": total_mem_after_load,
                "queries": {},
                "responses": {},  # Store actual results for cross-engine validation
            }
            
            print()
            for q_idx, query in enumerate(queries, 1):
                progress = progress_bar(q_idx, len(queries), width=30, prefix=f"  {scenario}@{ram_gb}GB ")
                print(f"\r{progress} {query}...", end="", flush=True)
                
                try:
                    # Capture metrics before query
                    m_before = {c: get_container_metrics(c) for c in sc_info["containers"]}
                    
                    row_count, latency_ms, rows_data = execute_query_for_scenario(
                        scenario, query, selected_ds["path"], return_rows=True
                    )
                    
                    # Capture metrics after query (includes peak since reset)
                    m_after = {c: get_container_metrics(c) for c in sc_info["containers"]}
                    
                    # Aggregate RAM across all containers (sum, not max)
                    query_mem_mb = sum(m_after[c].memory_mb for c in sc_info["containers"])
                    query_peak_mb = sum(m_after[c].memory_peak_mb for c in sc_info["containers"])
                    
                    # Per-container breakdown for detailed analysis
                    mem_breakdown = {c: {
                        "memory_mb": m_after[c].memory_mb,
                        "peak_mb": m_after[c].memory_peak_mb,
                    } for c in sc_info["containers"]}
                    
                    scenario_results["queries"][query] = {
                        "row_count": row_count,
                        "latency_ms": latency_ms,
                        "memory_mb": query_mem_mb,
                        "memory_peak_mb": query_peak_mb,
                        "memory_by_container": mem_breakdown,
                        "status": "ok"
                    }
                    
                    # Store response fingerprint for cross-engine validation
                    if rows_data:
                        scenario_results["responses"][query] = {
                            "row_count": row_count,
                            "sample": rows_data[:5] if len(rows_data) > 5 else rows_data,
                            "hash": hash(str(sorted(str(r) for r in rows_data))) if rows_data else 0,
                        }
                    
                except Exception as e:
                    scenario_results["queries"][query] = {"error": str(e), "status": "error"}
            
            print(f"\r{progress_bar(len(queries), len(queries), width=30, prefix=f'  {scenario}@{ram_gb}GB ')} Terminé")
            
            # Summary for this scenario/RAM combination
            print()
            for query, data in scenario_results["queries"].items():
                if data.get("status") == "ok":
                    peak_str = f", peak:{data.get('memory_peak_mb', 0):.0f}MB" if data.get('memory_peak_mb') else ""
                    print(f"    {GREEN}✓{RESET} {query}: {data['row_count']} rows, {data['latency_ms']:.1f}ms{peak_str}")
                else:
                    print(f"    {RED}✗{RESET} {query}: {data.get('error', 'Unknown error')}")
            
            all_results[scenario][ram_gb] = scenario_results
            
            # Save intermediate results
            result_file = run_dir / f"{scenario}_{ram_gb}GB.json"
            result_file.write_text(json.dumps(scenario_results, indent=2, cls=BenchmarkEncoder))
            log(f"Résultats {scenario}@{ram_gb}GB sauvegardés", "ok")
            
            # Plateau detection: compare with previous RAM level
            ok_queries = [q for q in scenario_results["queries"].values() if q.get("status") == "ok"]
            if ok_queries:
                curr_avg_latency = sum(q["latency_ms"] for q in ok_queries) / len(ok_queries)
                
                if prev_ram_avg_latency is not None:
                    improvement = (prev_ram_avg_latency - curr_avg_latency) / prev_ram_avg_latency
                    if improvement < 0.10:  # Less than 10% improvement
                        log(f"Plateau détecté: {prev_ram_avg_latency:.0f}ms → {curr_avg_latency:.0f}ms ({improvement*100:+.1f}%)", "info")
                        skip_remaining_ram = True
                    else:
                        log(f"Amélioration: {prev_ram_avg_latency:.0f}ms → {curr_avg_latency:.0f}ms ({improvement*100:+.1f}%)", "ok")
                
                prev_ram_avg_latency = curr_avg_latency
            
            # Preserve volumes for PostgreSQL scenarios (P1/P2) across RAM levels
            # This allows reuse of loaded data when only RAM limit changes
            preserve = scenario in ("P1", "P2")
            docker_stop_all(preserve_volumes=preserve)
            print()
        
        # Full cleanup after each scenario completes (or when switching scenarios)
        if scenario in ("P1", "P2"):
            docker_stop_all(preserve_volumes=False)  # Now cleanup volumes
    
    # Final summary
    elapsed_total = time.time() - t0_total
    
    log_section("BENCHMARK TERMINÉ")
    
    log(f"Durée totale: {elapsed_str(elapsed_total)}", "ok")
    log(f"Résultats: {run_dir}", "info")
    
    print()
    print(f"  {BOLD}Résumé par scénario × RAM:{RESET}")
    print()
    
    # Table header
    ram_header = "  " + "Scénario".ljust(12) + "".join(f"{r}GB".rjust(10) for r in ram_levels)
    print(ram_header)
    print("  " + "─" * (12 + 10 * len(ram_levels)))
    
    for scenario in scenarios:
        sc_info = SCENARIOS[scenario]
        row = f"  {sc_info['color']}{scenario.ljust(12)}{RESET}"
        
        for ram_gb in ram_levels:
            results = all_results.get(scenario, {}).get(ram_gb, {})
            if results.get("status") == "OOM":
                cell = f"{RED}OOM{RESET}"
            elif "queries" in results:
                ok_count = sum(1 for q in results["queries"].values() if q.get("status") == "ok")
                total_count = len(results["queries"])
                latencies = [q["latency_ms"] for q in results["queries"].values() if q.get("latency_ms")]
                avg_lat = sum(latencies) / len(latencies) if latencies else 0
                
                if ok_count == total_count:
                    cell = f"{GREEN}{avg_lat:.0f}ms{RESET}"
                elif ok_count > 0:
                    cell = f"{YELLOW}{ok_count}/{total_count}{RESET}"
                else:
                    cell = f"{RED}FAIL{RESET}"
            else:
                cell = f"{DIM}---{RESET}"
            
            row += cell.rjust(10 + len(cell) - len(cell.replace(RESET, "").replace(GREEN, "").replace(RED, "").replace(YELLOW, "").replace(DIM, "")))
        
        print(row)
    
    # Save summary
    summary = {
        "timestamp": timestamp,
        "dataset": selected_ds["name"],
        "ram_levels": ram_levels,
        "scenarios": scenarios,
        "queries": queries,
        "elapsed_s": elapsed_total,
        "results": all_results,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, cls=BenchmarkEncoder))
    
    print()
    input("Appuyez sur Entrée pour continuer...")


def load_data_for_scenario(scenario: str, dataset_path: Path, ram_gb: int, graph_only: bool = False) -> Dict:
    """Load data for a specific scenario.
    
    Args:
        scenario: P1, P2, M1, M2, O1, O2
        dataset_path: Path to dataset export directory
        ram_gb: RAM limit (for logging)
        graph_only: If True, only load graph structure (skip timeseries for M2/O2)
    """
    from basetype_benchmark.runner.engines.postgres import PostgresEngine
    from basetype_benchmark.runner.engines.memgraph import MemgraphEngine
    from basetype_benchmark.runner.engines.oxigraph import OxigraphEngine
    
    parquet_dir = dataset_path / "parquet"
    
    if scenario in ("P1", "P2"):
        engine = PostgresEngine(scenario)
        engine.connect()
        engine.clear()
        engine.create_schema()
        
        log("  Conversion Parquet → chargement...", "step")
        
        import pyarrow.parquet as pq
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Nodes
            nodes_df = pq.read_table(parquet_dir / "nodes.parquet").to_pandas()
            nodes_csv = Path(tmpdir) / "nodes.csv"
            nodes_df.to_csv(nodes_csv, index=False)
            engine.load_nodes(nodes_csv)
            
            # Edges
            edges_df = pq.read_table(parquet_dir / "edges.parquet").to_pandas()
            edges_csv = Path(tmpdir) / "edges.csv"
            edges_df.to_csv(edges_csv, index=False)
            engine.load_edges(edges_csv)
            
            # Timeseries (skip if graph_only)
            if not graph_only:
                ts_file = parquet_dir / "timeseries.parquet"
                if ts_file.exists():
                    log("  Chargement séries temporelles...", "step")
                    engine.load_timeseries_from_parquet(ts_file)
        
        engine.close()
        return {"status": "ok"}
    
    elif scenario in ("M1", "M2"):
        engine = MemgraphEngine(scenario)
        engine.connect()
        engine.clear()
        
        m1_dir = dataset_path / "m1"
        if m1_dir.exists():
            engine.load_nodes(m1_dir / "mg_nodes.csv")
            engine.load_edges(m1_dir / "mg_edges.csv")
            
            # M1: load chunks in-memory
            # M2: TimescaleDB handled separately (skip if graph_only or if already loaded)
            if scenario == "M1":
                chunks_file = m1_dir / "mg_chunks.csv"
                if chunks_file.exists():
                    log("  Chargement chunks timeseries (M1)...", "step")
                    engine.load_chunks(chunks_file)
            elif scenario == "M2" and not graph_only:
                # M2 needs TimescaleDB - load via PostgresEngine
                log("  Chargement TimescaleDB pour M2...", "step")
                pg_engine = PostgresEngine("P1")  # Reuse P1 schema for timeseries
                pg_engine.connect()
                pg_engine.create_schema()
                ts_file = parquet_dir / "timeseries.parquet"
                if ts_file.exists():
                    pg_engine.load_timeseries_from_parquet(ts_file)
                pg_engine.close()
        else:
            log("  Export M1 non trouvé", "warn")
        
        engine.close()
        return {"status": "ok"}
    
    elif scenario == "O2":
        # O2 hybride: graphe RDF + TimescaleDB pour séries
        # (O1 standalone retiré: ne peut pas embarquer les chunks RDF)
        engine = OxigraphEngine(scenario)
        engine.connect()
        engine.clear()
        
        o1_dir = dataset_path / "o1"
        nt_file = o1_dir / "graph.nt"
        
        # Generate O1 export if not exists
        if not nt_file.exists():
            log("  Génération export N-Triples...", "step")
            o1_dir.mkdir(parents=True, exist_ok=True)
            try:
                from basetype_benchmark.dataset.exporter_v2 import export_ntriples
                export_ntriples(parquet_dir, o1_dir)
            except Exception as e:
                log(f"  Échec génération export: {e}", "error")
                engine.close()
                return {"status": "error", "error": str(e)}
        
        if nt_file.exists():
            engine.load_ntriples(nt_file)
        else:
            log("  Export N-Triples non trouvé après génération", "warn")
        
        # O2 needs TimescaleDB for timeseries
        if not graph_only:
            log("  Chargement TimescaleDB pour O2...", "step")
            pg_engine = PostgresEngine("P1")
            pg_engine.connect()
            pg_engine.create_schema()
            ts_file = parquet_dir / "timeseries.parquet"
            if ts_file.exists():
                pg_engine.load_timeseries_from_parquet(ts_file)
            pg_engine.close()
        
        engine.close()
        return {"status": "ok"}
    
    return {"status": "unknown_scenario"}


def execute_query_for_scenario(scenario: str, query: str, dataset_path: Path, return_rows: bool = False) -> tuple:
    """Execute a query for a specific scenario.
    
    Returns:
        If return_rows=False: (row_count, latency_ms)
        If return_rows=True: (row_count, latency_ms, rows_data)
    """
    from basetype_benchmark.runner.engines.postgres import PostgresEngine
    from basetype_benchmark.runner.engines.memgraph import MemgraphEngine
    from basetype_benchmark.runner.engines.oxigraph import OxigraphEngine
    from basetype_benchmark.runner.params import (
        extract_dataset_info_from_parquet,
        extract_timeseries_range_from_parquet,
        get_query_variants,
        substitute_params,
    )
    
    queries_dir = Path(__file__).parent / "queries"
    parquet_dir = dataset_path / "parquet"
    
    # Extract dataset info for parameter substitution
    dataset_info = extract_dataset_info_from_parquet(parquet_dir / "nodes.parquet")
    ts_range = extract_timeseries_range_from_parquet(parquet_dir / "timeseries.parquet")
    dataset_info.update(ts_range)
    
    # Get profile name from path
    profile = dataset_path.name.split("_seed")[0] if "_seed" in dataset_path.name else "small-2d"
    
    # Generate one variant of parameters
    variants = get_query_variants(query, profile, dataset_info, seed=42, scenario=scenario, n_variants=1)
    params = variants[0] if variants else {}
    
    if scenario in ("P1", "P2"):
        matches = list(queries_dir.glob(f"p1_p2/{query}_*.sql"))
        if not matches:
            raise FileNotFoundError(f"Query {query} not found for P1/P2")
        query_text = matches[0].read_text()
        
        # Substitute params
        query_text = substitute_params(query_text, params)
        
        # Remove comments
        lines = [l for l in query_text.split("\n") if not l.strip().startswith("--")]
        query_text = "\n".join(lines)
        
        engine = PostgresEngine(scenario)
        engine.connect()
        if return_rows:
            rows, latency_ms = engine.execute_query_with_results(query_text)
            engine.close()
            return len(rows), latency_ms, rows
        else:
            row_count, latency_ms = engine.execute_query(query_text)
            engine.close()
            return row_count, latency_ms, None
    
    elif scenario in ("M1", "M2"):
        query_dir = "m1" if scenario == "M1" else "m2/graph"
        matches = list(queries_dir.glob(f"{query_dir}/{query}_*.cypher"))
        if not matches:
            raise FileNotFoundError(f"Query {query} not found for {scenario}")
        query_text = matches[0].read_text()
        
        # Substitute params
        query_text = substitute_params(query_text, params)
        
        # Remove comments
        lines = [l for l in query_text.split("\n") if not l.strip().startswith("//")]
        query_text = "\n".join(lines)
        
        engine = MemgraphEngine(scenario)
        engine.connect()
        if return_rows:
            rows, latency_ms = engine.execute_query_with_results(query_text)
            engine.close()
            return len(rows), latency_ms, rows
        else:
            row_count, latency_ms = engine.execute_query(query_text)
            engine.close()
            return row_count, latency_ms, None
    
    elif scenario == "O2":
        # O2 only (O1 removed from benchmark)
        query_dir = "o2/graph"
        matches = list(queries_dir.glob(f"{query_dir}/{query}_*.sparql"))
        if not matches:
            raise FileNotFoundError(f"Query {query} not found for {scenario}")
        query_text = matches[0].read_text()
        
        # Substitute params
        query_text = substitute_params(query_text, params)
        
        # Remove comments
        lines = [l for l in query_text.split("\n") if not l.strip().startswith("#")]
        query_text = "\n".join(lines)
        
        engine = OxigraphEngine(scenario)
        engine.connect()
        if return_rows:
            rows, latency_ms = engine.execute_query_with_results(query_text)
            engine.close()
            return len(rows), latency_ms, rows
        else:
            row_count, latency_ms = engine.execute_query(query_text)
            engine.close()
            return row_count, latency_ms, None
    
    raise ValueError(f"Unknown scenario: {scenario}")


# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW: PURGE DATASETS
# ═══════════════════════════════════════════════════════════════════════════════

def workflow_purge():
    """Purge datasets."""
    log_section("SUPPRESSION DES DATASETS")
    
    datasets = get_available_datasets()
    if not datasets:
        log("Aucun dataset à supprimer.", "info")
        input("\nAppuyez sur Entrée...")
        return
    
    log(f"{YELLOW}ATTENTION: Suppression définitive!{RESET}", "warn")
    
    print("\n  Datasets exportés:\n")
    total_mb = 0
    for i, ds in enumerate(datasets, 1):
        size_str = f"{ds['size_mb']:.0f} MB" if ds['size_mb'] < 1024 else f"{ds['size_mb']/1024:.1f} GB"
        print(f"  {i}. {ds['name']}: {size_str}")
        total_mb += ds['size_mb']
    
    total_str = f"{total_mb:.0f} MB" if total_mb < 1024 else f"{total_mb/1024:.1f} GB"
    print(f"\n  Total: {total_str}")
    
    print("\n  Options:")
    print("    A. Supprimer TOUS")
    print("    S. Sélectionner")
    print("    0. Annuler")
    
    choice = prompt("\nChoix", "0", ["A", "S", "0"]).upper()
    
    if choice == "0":
        return
    elif choice == "A":
        if confirm(f"Supprimer {len(datasets)} datasets ({total_str})?", default=False):
            for ds in datasets:
                log(f"Suppression {ds['name']}...", "step")
                shutil.rmtree(ds['path'])
            log(f"{len(datasets)} datasets supprimés", "ok")
    elif choice == "S":
        idx_str = prompt(f"Numéro (1-{len(datasets)})", "1")
        try:
            idx = int(idx_str)
            ds = datasets[idx - 1]
            if confirm(f"Supprimer {ds['name']}?", default=False):
                shutil.rmtree(ds['path'])
                log(f"{ds['name']} supprimé", "ok")
        except (ValueError, IndexError):
            log("Sélection invalide", "error")
    
    input("\nAppuyez sur Entrée...")


# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW: VIEW RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

def workflow_results():
    """View benchmark results."""
    log_section("RÉSULTATS DU BENCHMARK")
    
    results_dir = get_results_dir()
    if not results_dir.exists():
        log("Aucun résultat disponible.", "info")
        input("\nAppuyez sur Entrée...")
        return
    
    runs = sorted([d for d in results_dir.iterdir() if d.is_dir()], reverse=True)
    
    if not runs:
        log("Aucun résultat disponible.", "info")
        input("\nAppuyez sur Entrée...")
        return
    
    print("  Exécutions récentes:\n")
    for i, run in enumerate(runs[:10], 1):
        summary_file = run / "summary.json"
        if summary_file.exists():
            summary = json.loads(summary_file.read_text())
            elapsed = elapsed_str(summary.get('elapsed_s', 0))
            print(f"  {i}. {run.name}")
            print(f"     {DIM}Dataset: {summary.get('dataset', '?')}, RAM: {summary.get('ram_gb', '?')}GB, Durée: {elapsed}{RESET}")
        else:
            print(f"  {i}. {run.name}")
    
    print("\n  0. Retour")
    
    choice = prompt("\nVoir détails", "0")
    
    if choice == "0":
        return
    
    try:
        idx = int(choice)
        run = runs[idx - 1]
        summary_file = run / "summary.json"
        
        if summary_file.exists():
            summary = json.loads(summary_file.read_text())
            
            log_subsection(f"Détails: {run.name}")
            
            print(f"  Dataset:  {summary.get('dataset', '?')}")
            print(f"  RAM:      {summary.get('ram_gb', '?')} GB")
            print(f"  Durée:    {elapsed_str(summary.get('elapsed_s', 0))}")
            
            print(f"\n  {BOLD}Résultats:{RESET}\n")
            
            for scenario, results in summary.get("results", {}).items():
                sc_info = SCENARIOS.get(scenario, {})
                print(f"  {sc_info.get('color', '')}{BOLD}{scenario}{RESET}:")
                for query, data in results.get("queries", {}).items():
                    if data.get("status") == "ok":
                        print(f"    {query}: {data.get('row_count', '?')} rows, {data.get('latency_ms', 0):.1f}ms")
                    else:
                        print(f"    {query}: {RED}ERROR{RESET} - {data.get('error', '?')}")
                print()
    
    except (ValueError, IndexError):
        log("Sélection invalide", "error")
    
    input("\nAppuyez sur Entrée...")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════════════════════════════

def main_menu():
    """Main interactive menu."""
    while True:
        log_section("BASETYPE BENCHMARK")
        
        # Show status
        datasets = get_available_datasets()
        if datasets:
            total_mb = sum(d['size_mb'] for d in datasets)
            total_str = f"{total_mb:.0f} MB" if total_mb < 1024 else f"{total_mb/1024:.1f} GB"
            print(f"  {DIM}Datasets disponibles: {len(datasets)} ({total_str}){RESET}")
            for ds in datasets[:3]:
                nodes_str = f"{ds['nodes']:,}" if isinstance(ds['nodes'], int) else "?"
                print(f"    • {ds['name']} ({nodes_str} nœuds)")
            if len(datasets) > 3:
                print(f"    • ... et {len(datasets) - 3} autres")
        else:
            print(f"  {DIM}Aucun dataset généré{RESET}")
        
        print()
        print(f"  {BOLD}Actions:{RESET}\n")
        print("  1. Générer un dataset")
        print("  2. Lancer le benchmark")
        print("  3. Voir les résultats")
        print(f"  4. {RED}Supprimer des datasets{RESET}")
        print()
        print("  0. Quitter")
        
        print()
        choice = prompt("Choix", "1")
        
        if choice == "1":
            workflow_generate()
        elif choice == "2":
            workflow_benchmark()
        elif choice == "3":
            workflow_results()
        elif choice == "4":
            workflow_purge()
        elif choice == "0":
            docker_stop_all()
            print(f"\n  {GREEN}Au revoir!{RESET}\n")
            break


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("--help", "-h"):
            print(__doc__)
            print("\nPour le mode CLI, utilisez:")
            print("  python run.py generate <profile>")
            print("  python run.py benchmark")
            return
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Interruption utilisateur{RESET}")
        docker_stop_all()


if __name__ == "__main__":
    main()
