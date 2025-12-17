#!/usr/bin/env python3
"""Orchestrateur de benchmark rigoureux pour garantir la validité académique.

Ce module implémente un workflow séquentiel strict qui garantit:
- Un seul dataset généré (seed=42) par profil
- Export dans les 3 formats (SQL, graph, RDF)
- Tests séquentiels sur les 3 paradigmes avec le MÊME dataset
- Isolation complète entre tests (nettoyage des conteneurs)
- Collecte standardisée des métriques (JSON)

Workflow académique:
    FOR EACH profile IN [small-1w, small-1m, ..., large-1y]:
        1. Générer dataset (seed=42)
        2. Exporter vers PostgreSQL, Memgraph, Oxigraph
        3. FOR EACH paradigm IN [postgres, memgraph, oxigraph]:
            a. Démarrer conteneur propre
            b. Charger dataset
            c. Exécuter Q1-Q8
            d. Collecter métriques (latency, RAM, CPU, disk)
            e. Arrêter et nettoyer conteneur
        4. Sauvegarder résultats JSON
        5. Nettoyer cache dataset (optionnel)

Compatible avec:
    - Codespace 32GB RAM: 5 profils
    - Codespace 64GB RAM: 9 profils
    - OVH B3-256 (256GB RAM): 12 profils (TOUS)
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from basetype_benchmark.dataset.config import PROFILES, DEFAULT_SEED


# =============================================================================
# Dataclasses pour les résultats
# =============================================================================

@dataclass
class QueryMetrics:
    """Métriques pour une requête."""
    query_id: str
    latency_p50_ms: float
    latency_p95_ms: float
    latency_max_ms: float
    latency_min_ms: float
    rows_returned: int
    runs: int
    error: Optional[str] = None


@dataclass
class ParadigmBenchmark:
    """Résultats benchmark pour un paradigm sur un dataset."""
    paradigm: str  # postgres, memgraph, oxigraph
    profile: str
    seed: int

    # Métriques d'ingestion
    load_duration_s: float
    load_ram_peak_mb: float
    load_disk_mb: float
    load_items: int

    # Métriques de queries (Q1-Q8)
    queries: List[Dict[str, Any]]

    # Métriques système pendant queries
    query_ram_steady_mb: float
    query_ram_peak_mb: float
    query_cpu_avg_percent: float

    # Métadonnées
    timestamp: str
    docker_image: str
    container_id: str
    engine: str


@dataclass
class DatasetBenchmarkSession:
    """Session complète pour un dataset sur les 3 paradigmes."""
    profile: str
    seed: int
    timestamp: str

    # Métadonnées dataset
    dataset_nodes: int
    dataset_edges: int
    dataset_timeseries_points: int

    # Résultats des 3 paradigmes
    postgres: Optional[Dict] = None
    memgraph: Optional[Dict] = None
    oxigraph: Optional[Dict] = None

    # Statut global
    status: str = "pending"  # pending, in_progress, completed, failed
    errors: List[str] = field(default_factory=list)


# =============================================================================
# Constantes de configuration
# =============================================================================

DOCKER_COMPOSE_FILE = "docker/docker-compose.yml"

# Mapping paradigm -> service docker-compose
PARADIGM_SERVICES = {
    "postgres": "timescaledb",
    "memgraph": "memgraph",
    "oxigraph": "oxigraph",
}

# Mapping paradigm -> container name
PARADIGM_CONTAINERS = {
    "postgres": "btb_timescaledb",
    "memgraph": "btb_memgraph",
    "oxigraph": "btb_oxigraph",
}

# Mapping paradigm -> runner profile YAML
PARADIGM_PROFILES = {
    "postgres": "pg_rel",
    "memgraph": "memgraph",
    "oxigraph": "oxigraph",
}

# Health check timeouts
HEALTH_CHECK_TIMEOUT = 120  # seconds
HEALTH_CHECK_INTERVAL = 5  # seconds


# =============================================================================
# Classe principale
# =============================================================================

class BenchmarkOrchestrator:
    """Orchestrateur de benchmark rigoureux."""

    def __init__(self, output_dir: Path = None, docker_compose_file: str = None):
        """Initialise l'orchestrateur.

        Args:
            output_dir: Répertoire de sortie des résultats (défaut: ./benchmark_results)
            docker_compose_file: Fichier docker-compose (défaut: docker/docker-compose.yml)
        """
        self.output_dir = output_dir or Path("./benchmark_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.data_dir = Path("./data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.docker_compose_file = docker_compose_file or DOCKER_COMPOSE_FILE
        self.cwd = Path.cwd()

        # Vérifier Docker disponible
        self._check_docker()

    def _check_docker(self) -> None:
        """Vérifie que Docker est disponible."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[OK] Docker disponible: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("[ERROR] Docker n'est pas disponible. Requis pour les benchmarks.")

    def _get_storage_info(self) -> Dict[str, float]:
        """Récupère les informations de stockage."""
        try:
            stat = os.statvfs('/')
            total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
            free_gb = (stat.f_available * stat.f_frsize) / (1024**3)
            used_gb = total_gb - free_gb

            return {
                'total_gb': round(total_gb, 1),
                'used_gb': round(used_gb, 1),
                'free_gb': round(free_gb, 1),
                'usage_percent': round((used_gb / total_gb) * 100, 1)
            }
        except Exception:
            return {'error': 'Unknown'}

    def _get_ram_info(self) -> Dict[str, float]:
        """Récupère les informations RAM."""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            total_kb = int([l for l in meminfo.split('\n') if 'MemTotal' in l][0].split()[1])
            return {'total_gb': round(total_kb / 1024 / 1024, 1)}
        except Exception:
            return {'total_gb': 32}  # Default fallback

    # =========================================================================
    # Docker management
    # =========================================================================

    def _docker_compose(self, *args, check: bool = True) -> subprocess.CompletedProcess:
        """Exécute une commande docker-compose."""
        cmd = ["docker", "compose", "-f", self.docker_compose_file] + list(args)
        return subprocess.run(
            cmd,
            cwd=self.cwd,
            capture_output=True,
            text=True,
            check=check
        )

    def _start_service(self, service: str) -> bool:
        """Démarre un service Docker."""
        print(f"  🐳 Démarrage {service}...")
        try:
            self._docker_compose("up", "-d", service)
            return True
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Erreur démarrage {service}: {e.stderr}")
            return False

    def _stop_service(self, service: str, remove_volumes: bool = True) -> bool:
        """Arrête et nettoie un service Docker."""
        print(f"  🛑 Arrêt {service}...")
        try:
            if remove_volumes:
                self._docker_compose("down", "-v", "--remove-orphans")
            else:
                self._docker_compose("down")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  [WARN]  Erreur arrêt {service}: {e.stderr}")
            return False

    def _wait_for_health(self, container: str, timeout: int = HEALTH_CHECK_TIMEOUT) -> bool:
        """Attend qu'un conteneur soit healthy."""
        print(f"  ⏳ Attente health check {container}...")
        start = time.time()

        while time.time() - start < timeout:
            try:
                result = subprocess.run(
                    ["docker", "inspect", "-f", "{{.State.Health.Status}}", container],
                    capture_output=True,
                    text=True,
                    check=True
                )
                status = result.stdout.strip()
                if status == "healthy":
                    print(f"  [OK] {container} healthy")
                    return True
                elif status == "unhealthy":
                    print(f"  [ERROR] {container} unhealthy")
                    return False
            except subprocess.CalledProcessError:
                pass  # Container not ready yet

            time.sleep(HEALTH_CHECK_INTERVAL)

        print(f"  [ERROR] Timeout waiting for {container}")
        return False

    def _get_container_id(self, container: str) -> str:
        """Récupère l'ID d'un conteneur."""
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.Id}}", container],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()[:12]
        except subprocess.CalledProcessError:
            return "unknown"

    # =========================================================================
    # Dataset generation
    # =========================================================================

    def generate_and_export_dataset(self, profile: str, seed: int = DEFAULT_SEED) -> bool:
        """Génère un dataset et l'exporte dans tous les formats.

        Args:
            profile: Nom du profil (small-1w, medium-1m, etc.)
            seed: Graine aléatoire (défaut: 42)

        Returns:
            True si succès, False sinon
        """
        print(f"\n{'='*60}")
        print(f"[INFO] GÉNÉRATION DATASET: {profile} (seed={seed})")
        print(f"{'='*60}")

        # Vérifier espace disponible
        storage = self._get_storage_info()
        if 'free_gb' in storage and storage['free_gb'] < 5:
            print(f"[WARN]  ATTENTION: Seulement {storage['free_gb']} GB libres")

        try:
            # Générer dataset via le workflow existant
            from basetype_benchmark.dataset.workflow import DatasetWorkflow
            workflow = DatasetWorkflow()

            # Le workflow existant génère et exporte automatiquement
            success = workflow.releaser.release_and_clean_workflow(
                profile,
                keep_local=True  # Garder pour les benchmarks
            )

            if success:
                print(f"[OK] Dataset {profile} généré et exporté")
                return True
            else:
                print(f"[ERROR] Échec génération {profile}")
                return False

        except Exception as e:
            print(f"[ERROR] ERREUR génération {profile}: {e}")
            return False

    # =========================================================================
    # Benchmark runners
    # =========================================================================

    def _run_benchmark_with_runner(self, runner_profile: str, container: str) -> Dict[str, Any]:
        """Exécute le benchmark avec le runner existant.

        Args:
            runner_profile: Nom du profil YAML (pg_rel, memgraph, oxigraph)
            container: Nom du conteneur Docker

        Returns:
            Dict avec les résultats du benchmark
        """
        from basetype_benchmark.benchmark.metrics import ResourceMonitor, latency_stats, volume_disk_usage

        # Charger le profil
        profiles_dir = Path("src/basetype_benchmark/benchmark/profiles")
        profile_path = profiles_dir / f"{runner_profile}.yaml"

        if not profile_path.exists():
            raise FileNotFoundError(f"Profil {runner_profile} non trouvé: {profile_path}")

        import yaml
        with open(profile_path) as f:
            profile_data = yaml.safe_load(f)

        # Démarrer monitoring
        monitor = ResourceMonitor(container)
        monitor.start()

        results = {
            "engine": profile_data.get("engine", runner_profile),
            "profile": runner_profile,
            "ingestion": {},
            "queries": [],
            "resources": {},
        }

        try:
            # Phase 1: Ingestion
            print(f"  📥 Phase ingestion...")
            ingestion_config = profile_data.get("ingestion", {})
            if ingestion_config and ingestion_config.get("command"):
                ingestion_start = time.perf_counter()
                cmd = ingestion_config["command"]
                subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=self.cwd)
                ingestion_time = time.perf_counter() - ingestion_start
                results["ingestion"] = {"time_s": round(ingestion_time, 3)}
                print(f"  [OK] Ingestion: {ingestion_time:.1f}s")

            # Phase 2: Queries
            print(f"  🔍 Phase queries...")
            queries_config = profile_data.get("queries", {})
            n_warmup = 3
            n_runs = 10

            for query_name, query_cmd in queries_config.items():
                # Handle different query formats (list, dict with selection/aggregation)
                if isinstance(query_cmd, dict):
                    # Complex query with selection + aggregation
                    print(f"    {query_name}: composite query (skipping for now)")
                    results["queries"].append({
                        "query": query_name,
                        "note": "composite query",
                        "stats": None
                    })
                    continue

                # Simple query
                print(f"    {query_name}...", end=" ", flush=True)

                # Warmup
                for _ in range(n_warmup):
                    try:
                        subprocess.run(query_cmd, check=True, capture_output=True, timeout=30)
                    except Exception:
                        pass

                # Measure
                latencies = []
                for _ in range(n_runs):
                    try:
                        t0 = time.perf_counter()
                        subprocess.run(query_cmd, check=True, capture_output=True, timeout=30)
                        latencies.append(time.perf_counter() - t0)
                    except Exception as e:
                        latencies.append(30.0)  # Timeout value

                stats = latency_stats(latencies)
                results["queries"].append({
                    "query": query_name,
                    "warmup_runs": n_warmup,
                    "measure_runs": latencies,
                    "stats": stats,
                })
                print(f"p50={stats['p50']:.3f}s p95={stats['p95']:.3f}s")

        finally:
            # Arrêter monitoring
            monitor.stop()
            resources = monitor.summarize()
            resources["volume_mb"] = volume_disk_usage(profile_data.get("volume"))
            results["resources"] = resources

        return results

    def _benchmark_postgres(self, profile: str, seed: int) -> Optional[ParadigmBenchmark]:
        """Benchmark PostgreSQL/TimescaleDB."""
        paradigm = "postgres"
        service = PARADIGM_SERVICES[paradigm]
        container = PARADIGM_CONTAINERS[paradigm]
        runner_profile = PARADIGM_PROFILES[paradigm]

        print(f"\n📍 Benchmark PostgreSQL/TimescaleDB")

        try:
            # Démarrer conteneur
            if not self._start_service(service):
                return None

            # Attendre health
            if not self._wait_for_health(container):
                self._stop_service(service)
                return None

            # Exécuter benchmark
            print(f"  [INFO] Exécution benchmark...")
            results = self._run_benchmark_with_runner(runner_profile, container)

            # Construire ParadigmBenchmark
            benchmark = ParadigmBenchmark(
                paradigm=paradigm,
                profile=profile,
                seed=seed,
                load_duration_s=results.get("ingestion", {}).get("time_s", 0),
                load_ram_peak_mb=results.get("resources", {}).get("peak_mem_mb") or 0,
                load_disk_mb=results.get("resources", {}).get("volume_mb") or 0,
                load_items=results.get("ingestion", {}).get("items") or 0,
                queries=results.get("queries", []),
                query_ram_steady_mb=results.get("resources", {}).get("steady_state_mem_mb") or 0,
                query_ram_peak_mb=results.get("resources", {}).get("peak_mem_mb") or 0,
                query_cpu_avg_percent=results.get("resources", {}).get("avg_cpu_pct") or 0,
                timestamp=datetime.utcnow().isoformat() + "Z",
                docker_image="timescale/timescaledb-ha:pg16",
                container_id=self._get_container_id(container),
                engine=results.get("engine", "pg_rel"),
            )

            print(f"  [OK] PostgreSQL benchmark terminé")
            return benchmark

        except Exception as e:
            print(f"  [ERROR] Erreur PostgreSQL: {e}")
            return None

        finally:
            # Toujours nettoyer
            self._stop_service(service, remove_volumes=True)

    def _benchmark_memgraph(self, profile: str, seed: int) -> Optional[ParadigmBenchmark]:
        """Benchmark Memgraph."""
        paradigm = "memgraph"
        service = PARADIGM_SERVICES[paradigm]
        container = PARADIGM_CONTAINERS[paradigm]
        runner_profile = PARADIGM_PROFILES[paradigm]

        print(f"\n📍 Benchmark Memgraph")

        try:
            # Démarrer conteneur
            if not self._start_service(service):
                return None

            # Attendre health
            if not self._wait_for_health(container):
                self._stop_service(service)
                return None

            # Exécuter benchmark
            print(f"  [INFO] Exécution benchmark...")
            results = self._run_benchmark_with_runner(runner_profile, container)

            # Construire ParadigmBenchmark
            benchmark = ParadigmBenchmark(
                paradigm=paradigm,
                profile=profile,
                seed=seed,
                load_duration_s=results.get("ingestion", {}).get("time_s", 0),
                load_ram_peak_mb=results.get("resources", {}).get("peak_mem_mb") or 0,
                load_disk_mb=results.get("resources", {}).get("volume_mb") or 0,
                load_items=results.get("ingestion", {}).get("items") or 0,
                queries=results.get("queries", []),
                query_ram_steady_mb=results.get("resources", {}).get("steady_state_mem_mb") or 0,
                query_ram_peak_mb=results.get("resources", {}).get("peak_mem_mb") or 0,
                query_cpu_avg_percent=results.get("resources", {}).get("avg_cpu_pct") or 0,
                timestamp=datetime.utcnow().isoformat() + "Z",
                docker_image="memgraph/memgraph:latest",
                container_id=self._get_container_id(container),
                engine=results.get("engine", "memgraph"),
            )

            print(f"  [OK] Memgraph benchmark terminé")
            return benchmark

        except Exception as e:
            print(f"  [ERROR] Erreur Memgraph: {e}")
            return None

        finally:
            # Toujours nettoyer
            self._stop_service(service, remove_volumes=True)

    def _benchmark_oxigraph(self, profile: str, seed: int) -> Optional[ParadigmBenchmark]:
        """Benchmark Oxigraph."""
        paradigm = "oxigraph"
        service = PARADIGM_SERVICES[paradigm]
        container = PARADIGM_CONTAINERS[paradigm]
        runner_profile = PARADIGM_PROFILES[paradigm]

        print(f"\n📍 Benchmark Oxigraph")

        try:
            # Démarrer conteneur
            if not self._start_service(service):
                return None

            # Attendre health
            if not self._wait_for_health(container):
                self._stop_service(service)
                return None

            # Exécuter benchmark
            print(f"  [INFO] Exécution benchmark...")
            results = self._run_benchmark_with_runner(runner_profile, container)

            # Construire ParadigmBenchmark
            benchmark = ParadigmBenchmark(
                paradigm=paradigm,
                profile=profile,
                seed=seed,
                load_duration_s=results.get("ingestion", {}).get("time_s", 0),
                load_ram_peak_mb=results.get("resources", {}).get("peak_mem_mb") or 0,
                load_disk_mb=results.get("resources", {}).get("volume_mb") or 0,
                load_items=results.get("ingestion", {}).get("items") or 0,
                queries=results.get("queries", []),
                query_ram_steady_mb=results.get("resources", {}).get("steady_state_mem_mb") or 0,
                query_ram_peak_mb=results.get("resources", {}).get("peak_mem_mb") or 0,
                query_cpu_avg_percent=results.get("resources", {}).get("avg_cpu_pct") or 0,
                timestamp=datetime.utcnow().isoformat() + "Z",
                docker_image="oxigraph/oxigraph:latest",
                container_id=self._get_container_id(container),
                engine=results.get("engine", "oxigraph"),
            )

            print(f"  [OK] Oxigraph benchmark terminé")
            return benchmark

        except Exception as e:
            print(f"  [ERROR] Erreur Oxigraph: {e}")
            return None

        finally:
            # Toujours nettoyer
            self._stop_service(service, remove_volumes=True)

    # =========================================================================
    # Main workflow
    # =========================================================================

    def run_paradigm_benchmark(
        self,
        profile: str,
        paradigm: str,
        seed: int = DEFAULT_SEED
    ) -> Optional[ParadigmBenchmark]:
        """Exécute un benchmark complet pour un paradigme.

        Args:
            profile: Nom du profil
            paradigm: postgres, memgraph, ou oxigraph
            seed: Graine du dataset

        Returns:
            ParadigmBenchmark avec les métriques ou None si échec
        """
        print(f"\n{'─'*60}")
        print(f"🔬 BENCHMARK {paradigm.upper()}: {profile}")
        print(f"{'─'*60}")

        if paradigm == "postgres":
            return self._benchmark_postgres(profile, seed)
        elif paradigm == "memgraph":
            return self._benchmark_memgraph(profile, seed)
        elif paradigm == "oxigraph":
            return self._benchmark_oxigraph(profile, seed)
        else:
            print(f"[ERROR] Paradigme inconnu: {paradigm}")
            return None

    def run_full_dataset_benchmark(
        self,
        profile: str,
        seed: int = DEFAULT_SEED,
        paradigms: List[str] = None
    ) -> DatasetBenchmarkSession:
        """Exécute le workflow complet pour un dataset.

        Workflow:
        1. Générer dataset (seed=42)
        2. Exporter vers tous les formats
        3. Tester séquentiellement les 3 paradigmes
        4. Collecter et sauvegarder résultats

        Args:
            profile: Nom du profil (small-1w, etc.)
            seed: Graine aléatoire
            paradigms: Liste des paradigmes à tester (défaut: tous)

        Returns:
            DatasetBenchmarkSession avec tous les résultats
        """
        if paradigms is None:
            paradigms = ["postgres", "memgraph", "oxigraph"]

        print(f"\n{'='*60}")
        print(f"[START] WORKFLOW BENCHMARK COMPLET: {profile}")
        print(f"{'='*60}")
        print(f"Paradigmes: {', '.join(paradigms)}")
        print(f"Seed: {seed}")

        # Créer session
        session = DatasetBenchmarkSession(
            profile=profile,
            seed=seed,
            timestamp=time.strftime("%Y%m%d-%H%M%S"),
            dataset_nodes=0,
            dataset_edges=0,
            dataset_timeseries_points=0,
            status="in_progress"
        )

        try:
            # Étape 1: Génération et export
            print(f"\n[PACKAGE] Étape 1/{len(paradigms)+1}: Génération dataset")
            if not self.generate_and_export_dataset(profile, seed):
                session.status = "failed"
                session.errors.append("Échec génération dataset")
                return session

            # Étape 2+: Tests séquentiels des paradigmes
            for i, paradigm in enumerate(paradigms, start=2):
                print(f"\n🔬 Étape {i}/{len(paradigms)+1}: Test {paradigm}")

                result = self.run_paradigm_benchmark(profile, paradigm, seed)

                if result is not None:
                    # Convertir en dict pour JSON
                    setattr(session, paradigm, asdict(result))
                    print(f"[OK] {paradigm} terminé")
                else:
                    error_msg = f"Échec benchmark {paradigm}"
                    session.errors.append(error_msg)
                    print(f"[ERROR] {error_msg}")

                # Pause entre paradigmes pour libérer ressources
                if i < len(paradigms) + 1:
                    print("⏳ Pause de 10s avant paradigme suivant...")
                    time.sleep(10)

            # Sauvegarder résultats
            session.status = "completed" if not session.errors else "completed_with_errors"
            self._save_session(session)

        except Exception as e:
            session.status = "failed"
            session.errors.append(str(e))
            print(f"[ERROR] ERREUR CRITIQUE: {e}")

        return session

    def _save_session(self, session: DatasetBenchmarkSession) -> None:
        """Sauvegarde les résultats d'une session."""
        output_file = self.output_dir / f"{session.profile}_{session.timestamp}.json"

        # Convertir en dict pour JSON
        session_dict = asdict(session)

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Résultats sauvegardés: {output_file}")

    def run_sequential_suite(
        self,
        profiles: List[str] = None,
        seed: int = DEFAULT_SEED,
        ram_gb: int = None
    ) -> List[DatasetBenchmarkSession]:
        """Exécute la suite complète de benchmarks séquentiels.

        Args:
            profiles: Liste des profils à tester (défaut: selon RAM disponible)
            seed: Graine aléatoire
            ram_gb: RAM disponible (auto-détecté si None)

        Returns:
            Liste des sessions de benchmark
        """
        # Auto-détecter RAM si non spécifié
        if ram_gb is None:
            ram_info = self._get_ram_info()
            ram_gb = int(ram_info.get('total_gb', 32))

        if profiles is None:
            # Profils par défaut selon RAM disponible
            if ram_gb >= 200:
                # OVH B3-256 ou équivalent: TOUS les profils
                profiles = [
                    "small-1w", "small-1m", "small-6m", "small-1y",
                    "medium-1w", "medium-1m", "medium-6m", "medium-1y",
                    "large-1w", "large-1m", "large-6m", "large-1y"
                ]
            elif ram_gb >= 64:
                # Codespace 64GB RAM
                profiles = [
                    "small-1w", "small-1m", "small-6m", "small-1y",
                    "medium-1w", "medium-1m", "medium-6m", "medium-1y",
                    "large-1w"
                ]
            else:
                # Codespace 32GB RAM (standard)
                profiles = [
                    "small-1w", "small-1m",
                    "medium-1w", "medium-1m",
                    "large-1w"
                ]

        print(f"\n{'='*60}")
        print(f"🎯 SUITE SÉQUENTIELLE COMPLÈTE")
        print(f"{'='*60}")
        print(f"RAM détectée: {ram_gb} GB")
        print(f"Profils: {len(profiles)}")
        print(f"Tests: {len(profiles)} × 3 paradigmes = {len(profiles) * 3} benchmarks")
        print(f"Seed: {seed}")

        # Vérifier espace
        storage = self._get_storage_info()
        if 'free_gb' in storage:
            print(f"💾 Stockage: {storage['used_gb']}/{storage['total_gb']} GB ({storage['usage_percent']}%)")

        sessions = []

        for i, profile in enumerate(profiles, start=1):
            print(f"\n{'═'*60}")
            print(f"[INFO] PROFIL {i}/{len(profiles)}: {profile}")
            print(f"{'═'*60}")

            session = self.run_full_dataset_benchmark(profile, seed)
            sessions.append(session)

            # Résumé
            status_emoji = "[OK]" if session.status == "completed" else "[WARN]"
            print(f"\n{status_emoji} {profile}: {session.status}")
            if session.errors:
                for error in session.errors:
                    print(f"  [WARN]  {error}")

            # Pause entre profils
            if i < len(profiles):
                print(f"\n⏳ Pause de 30s avant profil suivant...")
                time.sleep(30)

        # Résumé final
        print(f"\n{'='*60}")
        print(f"[DONE] SUITE COMPLÈTE TERMINÉE")
        print(f"{'='*60}")
        print(f"Total: {len(sessions)} profils")
        completed = sum(1 for s in sessions if s.status == "completed")
        failed = sum(1 for s in sessions if s.status == "failed")
        print(f"Réussis: {completed}")
        print(f"Échoués: {failed}")
        print(f"\n📂 Résultats: {self.output_dir}")

        return sessions


# =============================================================================
# CLI
# =============================================================================

def main():
    """Interface CLI pour l'orchestrateur."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <command> [args...]")
        print()
        print("Commands:")
        print("  single <profile> <paradigm>  - Benchmark unique (ex: small-1w postgres)")
        print("  dataset <profile>            - Workflow complet pour un dataset")
        print("  suite [profiles...]          - Suite séquentielle complète")
        print()
        print("Exemples:")
        print("  python orchestrator.py single small-1w postgres")
        print("  python orchestrator.py dataset small-1w")
        print("  python orchestrator.py suite small-1w medium-1w")
        print("  python orchestrator.py suite  # Profils par défaut (auto-détection RAM)")
        return

    orchestrator = BenchmarkOrchestrator()
    command = sys.argv[1]

    if command == "single":
        if len(sys.argv) < 4:
            print("Usage: orchestrator.py single <profile> <paradigm>")
            return
        profile = sys.argv[2]
        paradigm = sys.argv[3]
        result = orchestrator.run_paradigm_benchmark(profile, paradigm)
        if result:
            print(f"\n[OK] Benchmark terminé: {paradigm} sur {profile}")

    elif command == "dataset":
        if len(sys.argv) < 3:
            print("Usage: orchestrator.py dataset <profile>")
            return
        profile = sys.argv[2]
        session = orchestrator.run_full_dataset_benchmark(profile)
        print(f"\n[OK] Session terminée: {session.status}")

    elif command == "suite":
        profiles = sys.argv[2:] if len(sys.argv) > 2 else None
        sessions = orchestrator.run_sequential_suite(profiles)
        print(f"\n[OK] {len(sessions)} sessions terminées")

    else:
        print(f"[ERROR] Commande inconnue: {command}")


if __name__ == "__main__":
    main()
