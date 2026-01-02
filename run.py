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
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Ensure src/ is in path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

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
        "description": "Property Graph in-memory (Cypher)",
        "containers": ["memgraph"],
        "color": MAGENTA,
    },
    "M2": {
        "name": "Memgraph + TimescaleDB",
        "description": "Graphe hybride + TimescaleDB pour séries",
        "containers": ["memgraph", "timescaledb"],
        "color": MAGENTA,
    },
    "O1": {
        "name": "Oxigraph Standalone",
        "description": "Triple Store RDF in-memory (SPARQL)",
        "containers": ["oxigraph"],
        "color": CYAN,
    },
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


def docker_stop_all():
    """Stop all benchmark containers."""
    log("Arrêt de tous les containers...", "step")
    subprocess.run(
        f"{DOCKER_COMPOSE} down -v --remove-orphans",
        shell=True,
        cwd=str(DOCKER_DIR),
        capture_output=True
    )
    log("Tous les containers arrêtés", "ok")


def docker_start(containers: List[str], ram_gb: int, data_dir: Optional[Path] = None) -> bool:
    """Start specified containers with RAM limit."""
    log(f"Démarrage containers: {', '.join(containers)} (limite {ram_gb}GB RAM)...", "step")
    
    env = os.environ.copy()
    env["MEMORY_LIMIT"] = f"{ram_gb}g"
    if data_dir:
        env["BTB_DATA_DIR"] = str(data_dir.resolve())
    
    # Stop first
    subprocess.run(
        f"{DOCKER_COMPOSE} down -v --remove-orphans",
        shell=True,
        cwd=str(DOCKER_DIR),
        env=env,
        capture_output=True
    )
    
    # Start
    container_str = " ".join(containers)
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
    
    # Wait for health
    log("Attente santé des containers...", "step")
    max_wait = 60
    start = time.time()
    
    while time.time() - start < max_wait:
        all_healthy = True
        for container in containers:
            check = subprocess.run(
                f"docker inspect --format='{{{{.State.Health.Status}}}}' btb_{container}",
                shell=True,
                capture_output=True,
                text=True
            )
            status = check.stdout.strip().replace("'", "")
            if status != "healthy":
                all_healthy = False
                break
        
        if all_healthy:
            elapsed = time.time() - start
            log(f"Containers opérationnels ({elapsed:.1f}s)", "ok")
            return True
        
        time.sleep(2)
        print(".", end="", flush=True)
    
    print()
    log(f"Timeout après {max_wait}s", "warn")
    return True  # Continue anyway


def docker_get_memory_usage(container: str) -> Optional[float]:
    """Get current memory usage of a container in MB."""
    result = subprocess.run(
        f"docker stats --no-stream --format '{{{{.MemUsage}}}}' btb_{container}",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        usage = result.stdout.strip().split("/")[0].strip()
        if "GiB" in usage:
            return float(usage.replace("GiB", "").strip()) * 1024
        elif "MiB" in usage:
            return float(usage.replace("MiB", "").strip())
    return None


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
            
            datasets.append({
                "name": d.name,
                "path": d,
                "size_mb": size_mb,
                "nodes": fingerprint.get("nodes_count", "?"),
                "edges": fingerprint.get("edges_count", "?"),
                "timeseries": fingerprint.get("timeseries_count", "?"),
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


def prompt_choice(question: str, options: List[str], default: int = 1) -> int:
    """Prompt user to choose from numbered options."""
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
        print(f"    Nœuds:          {fingerprint.get('nodes_count', 'N/A'):,}")
        print(f"    Arêtes:         {fingerprint.get('edges_count', 'N/A'):,}")
        print(f"    Points mesure:  {fingerprint.get('timeseries_count', 'N/A'):,}")
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
    
    ds_idx = prompt_choice("\nChoisir le dataset", [ds['name'] for ds in datasets], default=1)
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
    sc_choice = prompt("Scénario(s)", "ALL", ["P1", "P2", "M1", "M2", "O1", "O2", "ALL"])
    
    if sc_choice.upper() == "ALL":
        scenarios = scenario_list
    else:
        scenarios = [sc_choice.upper()]
    
    log(f"Scénarios: {', '.join(scenarios)}", "ok")
    
    # RAM selection
    log_subsection("Allocation mémoire")
    print("  RAM allouée à chaque container Docker:\n")
    ram_options = ["4 GB", "8 GB (recommandé)", "16 GB", "32 GB"]
    ram_idx = prompt_choice("Choisir la RAM", ram_options, default=2)
    ram_values = [4, 8, 16, 32]
    ram_gb = ram_values[ram_idx - 1]
    log(f"RAM allouée: {ram_gb} GB", "ok")
    
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
    
    total_runs = len(scenarios) * len(queries)
    print(f"  Dataset:    {BOLD}{selected_ds['name']}{RESET}")
    print(f"  Scénarios:  {', '.join(scenarios)}")
    print(f"  Requêtes:   {len(queries)} ({queries[0]}...{queries[-1]})")
    print(f"  RAM:        {ram_gb} GB")
    print(f"  Total:      {len(scenarios)} scénarios × {len(queries)} requêtes = {total_runs} exécutions")
    
    est_time = len(scenarios) * 120 + total_runs * 3  # ~2min load + 3s/query
    print(f"  Durée est.: ~{elapsed_str(est_time)}")
    
    print()
    if not confirm("Lancer le benchmark?"):
        docker_stop_all()
        return
    
    # Execute benchmark
    log_section("EXÉCUTION DU BENCHMARK")
    
    results_dir = get_results_dir()
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = results_dir / f"{timestamp}_{selected_ds['name']}"
    run_dir.mkdir(exist_ok=True)
    
    log(f"Résultats → {run_dir}", "info")
    
    all_results = {}
    t0_total = time.time()
    
    for sc_idx, scenario in enumerate(scenarios, 1):
        sc_info = SCENARIOS[scenario]
        
        log_subsection(f"[{sc_idx}/{len(scenarios)}] Scénario {sc_info['color']}{scenario}{RESET}: {sc_info['name']}")
        
        # Start containers
        if not docker_start(sc_info["containers"], ram_gb, selected_ds["path"]):
            log(f"Échec démarrage containers pour {scenario}", "error")
            all_results[scenario] = {"status": "container_error", "queries": {}}
            continue
        
        # Load data
        log(f"Chargement des données ({scenario})...", "step")
        t0_load = time.time()
        
        try:
            load_result = load_data_for_scenario(
                scenario, 
                selected_ds["path"], 
                ram_gb
            )
            load_time = time.time() - t0_load
            log(f"Données chargées en {elapsed_str(load_time)}", "ok")
            
            # Show memory after load
            for container in sc_info["containers"]:
                mem_mb = docker_get_memory_usage(container)
                if mem_mb:
                    log(f"  RAM {container}: {mem_mb:.0f} MB", "info")
                    
        except Exception as e:
            log(f"Erreur chargement: {e}", "error")
            all_results[scenario] = {"status": "load_error", "error": str(e), "queries": {}}
            docker_stop_all()
            continue
        
        # Execute queries
        scenario_results = {"scenario": scenario, "load_time_s": load_time, "queries": {}}
        
        print()
        for q_idx, query in enumerate(queries, 1):
            progress = progress_bar(q_idx, len(queries), width=30, prefix=f"  {scenario} ")
            print(f"\r{progress} {query}...", end="", flush=True)
            
            try:
                row_count, latency_ms = execute_query_for_scenario(scenario, query, selected_ds["path"])
                
                mem_mb = None
                for container in sc_info["containers"]:
                    m = docker_get_memory_usage(container)
                    if m:
                        mem_mb = m if mem_mb is None else max(mem_mb, m)
                
                scenario_results["queries"][query] = {
                    "row_count": row_count,
                    "latency_ms": latency_ms,
                    "memory_mb": mem_mb,
                    "status": "ok"
                }
                
            except Exception as e:
                scenario_results["queries"][query] = {"error": str(e), "status": "error"}
        
        print(f"\r{progress_bar(len(queries), len(queries), width=30, prefix=f'  {scenario} ')} Terminé")
        
        # Summary for this scenario
        ok_count = sum(1 for q in scenario_results["queries"].values() if q.get("status") == "ok")
        print()
        
        for query, data in scenario_results["queries"].items():
            if data.get("status") == "ok":
                mem_str = f", {data.get('memory_mb', 0):.0f}MB" if data.get('memory_mb') else ""
                print(f"    {GREEN}✓{RESET} {query}: {data['row_count']} rows, {data['latency_ms']:.1f}ms{mem_str}")
            else:
                print(f"    {RED}✗{RESET} {query}: {data.get('error', 'Unknown error')}")
        
        all_results[scenario] = scenario_results
        
        # Save intermediate results
        result_file = run_dir / f"{scenario}.json"
        result_file.write_text(json.dumps(scenario_results, indent=2))
        log(f"Résultats {scenario} sauvegardés", "ok")
        
        docker_stop_all()
        print()
    
    # Final summary
    elapsed_total = time.time() - t0_total
    
    log_section("BENCHMARK TERMINÉ")
    
    log(f"Durée totale: {elapsed_str(elapsed_total)}", "ok")
    log(f"Résultats: {run_dir}", "info")
    
    print()
    print(f"  {BOLD}Résumé par scénario:{RESET}")
    print()
    
    for scenario, results in all_results.items():
        sc_info = SCENARIOS[scenario]
        if "queries" in results:
            ok_count = sum(1 for q in results["queries"].values() if q.get("status") == "ok")
            total_count = len(results["queries"])
            
            if ok_count == total_count:
                status = f"{GREEN}✓{RESET}"
            elif ok_count > 0:
                status = f"{YELLOW}⚠{RESET}"
            else:
                status = f"{RED}✗{RESET}"
            
            # Calculate avg latency
            latencies = [q["latency_ms"] for q in results["queries"].values() if q.get("latency_ms")]
            avg_lat = sum(latencies) / len(latencies) if latencies else 0
            
            print(f"  {status} {sc_info['color']}{scenario}{RESET}: {ok_count}/{total_count} OK, avg {avg_lat:.1f}ms")
        else:
            print(f"  {RED}✗{RESET} {sc_info['color']}{scenario}{RESET}: {results.get('status', 'error')}")
    
    # Save summary
    summary = {
        "timestamp": timestamp,
        "dataset": selected_ds["name"],
        "ram_gb": ram_gb,
        "scenarios": scenarios,
        "queries": queries,
        "elapsed_s": elapsed_total,
        "results": all_results,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    
    print()
    input("Appuyez sur Entrée pour continuer...")


def load_data_for_scenario(scenario: str, dataset_path: Path, ram_gb: int) -> Dict:
    """Load data for a specific scenario."""
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
            
            # Timeseries
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
            
            if scenario == "M1":
                chunks_file = m1_dir / "mg_chunks.csv"
                if chunks_file.exists():
                    log("  Chargement chunks timeseries (M1)...", "step")
                    engine.load_chunks(chunks_file)
        else:
            log("  Export M1 non trouvé", "warn")
        
        engine.close()
        return {"status": "ok"}
    
    elif scenario in ("O1", "O2"):
        engine = OxigraphEngine(scenario)
        engine.connect()
        engine.clear()
        
        o1_dir = dataset_path / "o1"
        if o1_dir.exists():
            nt_file = o1_dir / "graph.nt"
            if nt_file.exists():
                engine.load_ntriples(nt_file)
        else:
            log("  Export O1 non trouvé", "warn")
        
        engine.close()
        return {"status": "ok"}
    
    return {"status": "unknown_scenario"}


def execute_query_for_scenario(scenario: str, query: str, dataset_path: Path) -> tuple:
    """Execute a query for a specific scenario. Returns (row_count, latency_ms)."""
    from basetype_benchmark.runner.engines.postgres import PostgresEngine
    from basetype_benchmark.runner.engines.memgraph import MemgraphEngine
    from basetype_benchmark.runner.engines.oxigraph import OxigraphEngine
    from basetype_benchmark.runner.params import resolve_params
    
    queries_dir = Path(__file__).parent / "queries"
    
    if scenario in ("P1", "P2"):
        matches = list(queries_dir.glob(f"p1_p2/{query}_*.sql"))
        if not matches:
            raise FileNotFoundError(f"Query {query} not found for P1/P2")
        query_text = matches[0].read_text()
        
        params = resolve_params(dataset_path, scenario)
        for key, value in params.items():
            query_text = query_text.replace(f"${key}", str(value))
        
        lines = [l for l in query_text.split("\n") if not l.strip().startswith("--")]
        query_text = "\n".join(lines)
        
        engine = PostgresEngine(scenario)
        engine.connect()
        row_count, latency_ms = engine.execute_query(query_text)
        engine.close()
        return row_count, latency_ms
    
    elif scenario in ("M1", "M2"):
        query_dir = "m1" if scenario == "M1" else "m2/graph"
        matches = list(queries_dir.glob(f"{query_dir}/{query}_*.cypher"))
        if not matches:
            raise FileNotFoundError(f"Query {query} not found for {scenario}")
        query_text = matches[0].read_text()
        
        params = resolve_params(dataset_path, scenario)
        for key, value in params.items():
            query_text = query_text.replace(f"${key}", str(value))
        
        lines = [l for l in query_text.split("\n") if not l.strip().startswith("//")]
        query_text = "\n".join(lines)
        
        engine = MemgraphEngine(scenario)
        engine.connect()
        row_count, latency_ms = engine.execute_query(query_text)
        engine.close()
        return row_count, latency_ms
    
    elif scenario in ("O1", "O2"):
        query_dir = "o1" if scenario == "O1" else "o2/graph"
        matches = list(queries_dir.glob(f"{query_dir}/{query}_*.sparql"))
        if not matches:
            raise FileNotFoundError(f"Query {query} not found for {scenario}")
        query_text = matches[0].read_text()
        
        params = resolve_params(dataset_path, scenario)
        for key, value in params.items():
            query_text = query_text.replace(f"${key}", str(value))
        
        lines = [l for l in query_text.split("\n") if not l.strip().startswith("#")]
        query_text = "\n".join(lines)
        
        engine = OxigraphEngine(scenario)
        engine.connect()
        row_count, latency_ms = engine.execute_query(query_text)
        engine.close()
        return row_count, latency_ms
    
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
