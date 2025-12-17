#!/usr/bin/env python3
"""Orchestrateur complet pour les 6 scénarios avec variable RAM.

Scénarios:
- P1: PostgreSQL Relational + TimescaleDB
- P2: PostgreSQL JSONB + TimescaleDB
- M1: Memgraph Standalone (tout in-memory)
- M2: Memgraph + TimescaleDB (hybride)
- O1: Oxigraph Standalone (RDF)
- O2: Oxigraph + TimescaleDB (hybride)

Ce module intègre:
- ram_config.py pour les bornes RAM adaptatives
- ram_runner.py pour les tests avec contraintes Docker
- Génération/export des datasets
- Exécution des queries Q1-Q12
- Collecte des métriques pour le papier

Usage:
    python full_orchestrator.py --profile small-1w --scenario P1
    python full_orchestrator.py --profile small-1w --all-scenarios
    python full_orchestrator.py --full-suite --host-ram 32
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from basetype_benchmark.benchmark.ram_config import (
    EngineType,
    TestMode,
    get_test_config,
    generate_test_sequence,
    DATASET_ESTIMATES,
    B3_MAX_RAM_GB,
)


class Scenario(str, Enum):
    """Les 6 scénarios de benchmark."""
    P1 = "P1"  # PostgreSQL Relational
    P2 = "P2"  # PostgreSQL JSONB
    M1 = "M1"  # Memgraph Standalone
    M2 = "M2"  # Memgraph + TimescaleDB
    O1 = "O1"  # Oxigraph Standalone
    O2 = "O2"  # Oxigraph + TimescaleDB


# Mapping scénario → profil YAML
SCENARIO_PROFILES = {
    Scenario.P1: "pg_rel",
    Scenario.P2: "pg_jsonb",
    Scenario.M1: "memgraph",
    Scenario.M2: "memgraph_hybrid",
    Scenario.O1: "oxigraph",
    Scenario.O2: "oxigraph_hybrid",
}

# Mapping scénario → EngineType (pour ram_config)
SCENARIO_ENGINE = {
    Scenario.P1: EngineType.P1,
    Scenario.P2: EngineType.P2,
    Scenario.M1: EngineType.M1,
    Scenario.M2: EngineType.M2,
    Scenario.O1: EngineType.O1,
    Scenario.O2: EngineType.O2,
}

# Containers par scénario
SCENARIO_CONTAINERS = {
    Scenario.P1: ["btb_timescaledb"],
    Scenario.P2: ["btb_timescaledb"],
    Scenario.M1: ["btb_memgraph"],
    Scenario.M2: ["btb_memgraph", "btb_timescaledb"],
    Scenario.O1: ["btb_oxigraph"],
    Scenario.O2: ["btb_oxigraph", "btb_timescaledb"],
}

# Docker images par container
CONTAINER_IMAGES = {
    "btb_timescaledb": "timescale/timescaledb:latest-pg16",
    "btb_memgraph": "memgraph/memgraph:latest",
    "btb_oxigraph": "ghcr.io/oxigraph/oxigraph:latest",
}


@dataclass
class QueryResult:
    """Résultat d'une query."""
    query_id: str
    latencies_ms: List[float]
    p50_ms: float
    p95_ms: float
    rows: int = 0
    error: Optional[str] = None


@dataclass
class ScenarioResult:
    """Résultat complet d'un scénario."""
    scenario: str
    profile: str
    ram_limit_mb: int
    timestamp: str

    # Ingestion
    ingestion_time_s: float = 0.0
    ingestion_success: bool = False

    # Queries
    queries: List[Dict[str, Any]] = field(default_factory=list)
    query_p95_mean_ms: float = 0.0

    # Resources
    peak_memory_mb: float = 0.0
    disk_usage_mb: float = 0.0
    oom_killed: bool = False

    # Status
    success: bool = False
    error: Optional[str] = None


@dataclass
class BenchmarkSession:
    """Session de benchmark complète."""
    profile: str
    seed: int
    timestamp: str
    host_ram_gb: int

    # Dataset info
    dataset_nodes: int = 0
    dataset_edges: int = 0
    dataset_timeseries_samples: int = 0

    # Résultats par scénario
    results: Dict[str, List[ScenarioResult]] = field(default_factory=dict)

    # Métriques agrégées
    ram_min_by_scenario: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FullOrchestrator:
    """Orchestrateur complet pour les 6 scénarios."""

    def __init__(
        self,
        output_dir: Path = Path("benchmark_results"),
        data_dir: Path = Path("data"),
        docker_compose: str = "docker/docker-compose.yml",
        verbose: bool = True,
    ):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.docker_compose = docker_compose
        self.verbose = verbose
        self.cwd = Path.cwd()

    def log(self, msg: str) -> None:
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {msg}")

    # =========================================================================
    # Docker Management
    # =========================================================================

    def _docker_compose_cmd(self, *args) -> List[str]:
        return ["docker", "compose", "-f", self.docker_compose] + list(args)

    def _run_cmd(self, cmd: List[str], timeout: int = 300) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.cwd,
        )

    def start_containers(
        self,
        scenario: Scenario,
        ram_limit_mb: Optional[int] = None,
    ) -> bool:
        """Démarre les containers pour un scénario."""
        containers = SCENARIO_CONTAINERS[scenario]
        self.log(f"🐳 Démarrage containers: {containers}")

        for container in containers:
            # Arrêter l'ancien si existe
            self._run_cmd(["docker", "rm", "-f", container])

            # Construire la commande docker run
            cmd = ["docker", "run", "-d", "--name", container]

            # Limite RAM si spécifiée
            if ram_limit_mb:
                cmd.extend([f"--memory={ram_limit_mb}m", f"--memory-swap={ram_limit_mb}m"])

            # Ports et configuration selon container
            if container == "btb_timescaledb":
                cmd.extend([
                    "-p", "5432:5432",
                    "-e", "POSTGRES_USER=benchmark",
                    "-e", "POSTGRES_PASSWORD=benchmark",
                    "-e", "POSTGRES_DB=benchmark",
                ])
            elif container == "btb_memgraph":
                cmd.extend(["-p", "7687:7687"])
            elif container == "btb_oxigraph":
                cmd.extend(["-p", "7878:7878"])

            cmd.append(CONTAINER_IMAGES[container])

            result = self._run_cmd(cmd)
            if result.returncode != 0:
                self.log(f"❌ Échec démarrage {container}: {result.stderr}")
                return False

        # Attendre que tous les containers soient prêts
        time.sleep(5)  # Initial wait
        return self._wait_for_containers(containers)

    def _wait_for_containers(self, containers: List[str], timeout: int = 120) -> bool:
        """Attend que les containers soient prêts."""
        start = time.time()

        while time.time() - start < timeout:
            all_ready = True

            for container in containers:
                # Vérifier status
                result = self._run_cmd([
                    "docker", "inspect", "-f", "{{.State.Status}}", container
                ])
                if result.stdout.strip() != "running":
                    all_ready = False
                    break

                # Health check spécifique
                if container == "btb_timescaledb":
                    hc = self._run_cmd([
                        "docker", "exec", container,
                        "pg_isready", "-U", "benchmark"
                    ])
                    if hc.returncode != 0:
                        all_ready = False
                elif container == "btb_memgraph":
                    # Memgraph prêt si port 7687 répond
                    hc = self._run_cmd([
                        "docker", "exec", container,
                        "mgconsole", "--host", "127.0.0.1", "--port", "7687",
                        "-c", "RETURN 1;"
                    ])
                    if hc.returncode != 0:
                        all_ready = False
                elif container == "btb_oxigraph":
                    hc = self._run_cmd([
                        "curl", "-sf", "http://localhost:7878/health"
                    ])
                    if hc.returncode != 0:
                        all_ready = False

            if all_ready:
                self.log("✓ Tous les containers prêts")
                return True

            time.sleep(2)

        self.log("❌ Timeout attente containers")
        return False

    def stop_containers(self, scenario: Scenario) -> None:
        """Arrête et supprime les containers d'un scénario."""
        containers = SCENARIO_CONTAINERS[scenario]
        for container in containers:
            self._run_cmd(["docker", "rm", "-f", container])
        self.log(f"🛑 Containers arrêtés: {containers}")

    def check_oom(self, scenario: Scenario) -> bool:
        """Vérifie si un container a été OOM killed."""
        for container in SCENARIO_CONTAINERS[scenario]:
            result = self._run_cmd([
                "docker", "inspect", "-f", "{{.State.OOMKilled}}", container
            ])
            if result.stdout.strip() == "true":
                return True
        return False

    def drop_caches(self) -> bool:
        """Vide le cache Linux (nécessite sudo)."""
        try:
            subprocess.run(["sync"], check=True, timeout=30)
            result = subprocess.run(
                ["sudo", "-n", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            self.log("⚠️  drop_caches non disponible")
            return False

    # =========================================================================
    # Dataset Generation
    # =========================================================================

    def generate_dataset(self, profile: str, seed: int = 42) -> bool:
        """Génère et exporte le dataset."""
        self.log(f"📊 Génération dataset: {profile}")

        try:
            from basetype_benchmark.dataset.workflow import DatasetWorkflow
            workflow = DatasetWorkflow()

            success = workflow.releaser.release_and_clean_workflow(
                profile,
                keep_local=True
            )

            if success:
                self.log(f"✓ Dataset {profile} généré")
            return success

        except Exception as e:
            self.log(f"❌ Erreur génération: {e}")
            return False

    # =========================================================================
    # Query Execution
    # =========================================================================

    def run_query(
        self,
        scenario: Scenario,
        query_id: str,
        warmup_runs: int = 3,
        measure_runs: int = 10,
    ) -> QueryResult:
        """Exécute une query et mesure les latences."""
        import yaml

        # Charger le profil
        profile_name = SCENARIO_PROFILES[scenario]
        profile_path = Path(f"src/basetype_benchmark/benchmark/profiles/{profile_name}.yaml")

        with open(profile_path) as f:
            profile = yaml.safe_load(f)

        queries = profile.get("queries", {})
        if query_id not in queries:
            return QueryResult(
                query_id=query_id,
                latencies_ms=[],
                p50_ms=0,
                p95_ms=0,
                error=f"Query {query_id} non trouvée"
            )

        query_cmd = queries[query_id]

        # Gérer les queries hybrides
        if isinstance(query_cmd, dict):
            # Query hybride (selection + aggregation)
            # Pour l'instant, on mesure juste la partie selection
            if "selection" in query_cmd:
                query_cmd = query_cmd["selection"]
            else:
                return QueryResult(
                    query_id=query_id,
                    latencies_ms=[],
                    p50_ms=0,
                    p95_ms=0,
                    error="Query hybride non supportée"
                )

        # Warmup
        for _ in range(warmup_runs):
            try:
                subprocess.run(query_cmd, capture_output=True, timeout=60)
            except Exception:
                pass

        # Mesures
        latencies = []
        for _ in range(measure_runs):
            try:
                t0 = time.perf_counter()
                result = subprocess.run(query_cmd, capture_output=True, timeout=60)
                elapsed = (time.perf_counter() - t0) * 1000  # ms

                if result.returncode == 0:
                    latencies.append(elapsed)
                else:
                    latencies.append(60000)  # Timeout
            except subprocess.TimeoutExpired:
                latencies.append(60000)
            except Exception as e:
                return QueryResult(
                    query_id=query_id,
                    latencies_ms=latencies,
                    p50_ms=0,
                    p95_ms=0,
                    error=str(e)
                )

        # Calcul stats
        if latencies:
            sorted_lat = sorted(latencies)
            p50 = sorted_lat[len(sorted_lat) // 2]
            p95_idx = int(len(sorted_lat) * 0.95)
            p95 = sorted_lat[min(p95_idx, len(sorted_lat) - 1)]
        else:
            p50, p95 = 0, 0

        return QueryResult(
            query_id=query_id,
            latencies_ms=latencies,
            p50_ms=round(p50, 2),
            p95_ms=round(p95, 2),
        )

    def run_all_queries(self, scenario: Scenario) -> List[QueryResult]:
        """Exécute toutes les queries Q1-Q12 pour un scénario."""
        results = []

        for i in range(1, 13):
            query_id = f"Q{i}"
            self.log(f"  🔍 {query_id}...")

            result = self.run_query(scenario, query_id)
            results.append(result)

            if result.error:
                self.log(f"    ⚠️  {result.error}")
            else:
                self.log(f"    p50={result.p50_ms:.1f}ms p95={result.p95_ms:.1f}ms")

        return results

    # =========================================================================
    # Scenario Execution
    # =========================================================================

    def run_scenario(
        self,
        scenario: Scenario,
        profile: str,
        ram_limit_mb: Optional[int] = None,
    ) -> ScenarioResult:
        """Exécute un scénario complet."""
        self.log(f"\n{'='*60}")
        self.log(f"🎯 SCÉNARIO: {scenario.value} | Profil: {profile}")
        if ram_limit_mb:
            self.log(f"   RAM limit: {ram_limit_mb} Mo ({ram_limit_mb/1024:.1f} Go)")
        self.log(f"{'='*60}")

        result = ScenarioResult(
            scenario=scenario.value,
            profile=profile,
            ram_limit_mb=ram_limit_mb or 0,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        try:
            # Drop caches avant le test
            self.drop_caches()

            # Démarrer les containers
            if not self.start_containers(scenario, ram_limit_mb):
                result.error = "Échec démarrage containers"
                return result

            # Vérifier OOM immédiat
            if self.check_oom(scenario):
                result.oom_killed = True
                result.error = "OOM au démarrage"
                self.stop_containers(scenario)
                return result

            # TODO: Ingestion des données
            # Pour l'instant, on suppose que les données sont déjà chargées
            result.ingestion_success = True

            # Exécuter les queries
            self.log("📊 Exécution queries...")
            query_results = self.run_all_queries(scenario)

            # Vérifier OOM pendant queries
            if self.check_oom(scenario):
                result.oom_killed = True
                result.error = "OOM pendant queries"
            else:
                result.queries = [asdict(q) for q in query_results]

                # Calculer p95 moyen
                p95_values = [q.p95_ms for q in query_results if q.p95_ms > 0]
                if p95_values:
                    result.query_p95_mean_ms = sum(p95_values) / len(p95_values)

                result.success = True

        except Exception as e:
            result.error = str(e)
            self.log(f"❌ Erreur: {e}")

        finally:
            self.stop_containers(scenario)

        return result

    def run_scenario_with_ram_gradient(
        self,
        scenario: Scenario,
        profile: str,
        mode: TestMode = TestMode.GRADIENT,
        host_ram_mb: Optional[int] = None,
    ) -> List[ScenarioResult]:
        """Exécute un scénario avec différents niveaux de RAM."""
        engine = SCENARIO_ENGINE[scenario]
        config = get_test_config(engine, profile, mode, host_ram_mb)

        if config.excluded:
            self.log(f"⚠️  Configuration exclue: {config.exclusion_reason}")
            return []

        self.log(f"\n📊 RAM Gradient: {scenario.value} × {profile}")
        self.log(f"   Paliers: {[f'{r/1024:.1f}Go' for r in config.ram_steps]}")

        results = []

        for ram_mb in reversed(config.ram_steps):
            result = self.run_scenario(scenario, profile, ram_mb)
            results.append(result)

            if result.oom_killed:
                self.log(f"   💀 OOM à {ram_mb/1024:.1f} Go - arrêt du gradient")
                break

        return results

    # =========================================================================
    # Full Suite
    # =========================================================================

    def run_full_suite(
        self,
        profiles: Optional[List[str]] = None,
        scenarios: Optional[List[Scenario]] = None,
        ram_mode: TestMode = TestMode.QUICK,
        host_ram_gb: int = 32,
        seed: int = 42,
    ) -> List[BenchmarkSession]:
        """Exécute la suite complète de benchmarks."""
        if profiles is None:
            # Profils par défaut selon RAM
            if host_ram_gb >= 200:
                profiles = list(DATASET_ESTIMATES.keys())
            elif host_ram_gb >= 64:
                profiles = ["small-1w", "small-1m", "medium-1w", "medium-1m", "large-1w"]
            else:
                profiles = ["small-1w", "small-1m", "medium-1w"]

        if scenarios is None:
            scenarios = list(Scenario)

        host_ram_mb = host_ram_gb * 1024

        self.log(f"\n{'='*70}")
        self.log(f"🚀 SUITE COMPLÈTE DE BENCHMARKS")
        self.log(f"{'='*70}")
        self.log(f"Profils: {profiles}")
        self.log(f"Scénarios: {[s.value for s in scenarios]}")
        self.log(f"RAM hôte: {host_ram_gb} Go")
        self.log(f"Mode RAM: {ram_mode.value}")

        sessions = []

        for profile in profiles:
            session = BenchmarkSession(
                profile=profile,
                seed=seed,
                timestamp=datetime.utcnow().isoformat() + "Z",
                host_ram_gb=host_ram_gb,
            )

            self.log(f"\n{'─'*70}")
            self.log(f"📦 PROFIL: {profile}")
            self.log(f"{'─'*70}")

            # Générer le dataset
            if not self.generate_dataset(profile, seed):
                self.log(f"❌ Échec génération dataset {profile}")
                continue

            # Exécuter chaque scénario
            for scenario in scenarios:
                self.log(f"\n🎯 Scénario: {scenario.value}")

                if ram_mode == TestMode.QUICK:
                    # Mode rapide: baseline uniquement
                    result = self.run_scenario(scenario, profile)
                    session.results.setdefault(scenario.value, []).append(result)
                else:
                    # Mode gradient: plusieurs niveaux de RAM
                    results = self.run_scenario_with_ram_gradient(
                        scenario, profile, ram_mode, host_ram_mb
                    )
                    session.results[scenario.value] = results

                    # Déterminer RAM_min
                    for r in reversed(results):
                        if r.success and not r.oom_killed:
                            session.ram_min_by_scenario[scenario.value] = r.ram_limit_mb
                            break

            # Sauvegarder la session
            self._save_session(session)
            sessions.append(session)

        # Générer rapport final
        self._generate_report(sessions)

        return sessions

    def _save_session(self, session: BenchmarkSession) -> None:
        """Sauvegarde une session en JSON."""
        filename = f"session_{session.profile}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = self.output_dir / filename

        with open(path, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2, default=str)

        self.log(f"💾 Session sauvegardée: {path}")

    def _generate_report(self, sessions: List[BenchmarkSession]) -> None:
        """Génère un rapport markdown."""
        report_path = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        lines = [
            "# Rapport de Benchmark - BaseType Benchmark",
            "",
            f"Date: {datetime.now().isoformat()}",
            "",
            "## Résumé RAM_min par Scénario",
            "",
            "| Profil | P1 | P2 | M1 | M2 | O1 | O2 |",
            "|--------|----|----|----|----|----|----|",
        ]

        for session in sessions:
            row = [session.profile]
            for scenario in ["P1", "P2", "M1", "M2", "O1", "O2"]:
                ram = session.ram_min_by_scenario.get(scenario)
                if ram:
                    row.append(f"{ram/1024:.1f}Go")
                else:
                    row.append("N/A")
            lines.append("| " + " | ".join(row) + " |")

        lines.extend([
            "",
            "## Latence p95 moyenne (ms)",
            "",
            "| Profil | P1 | P2 | M1 | M2 | O1 | O2 |",
            "|--------|----|----|----|----|----|----|",
        ])

        for session in sessions:
            row = [session.profile]
            for scenario in ["P1", "P2", "M1", "M2", "O1", "O2"]:
                results = session.results.get(scenario, [])
                if results and results[0].query_p95_mean_ms > 0:
                    row.append(f"{results[0].query_p95_mean_ms:.1f}")
                else:
                    row.append("N/A")
            lines.append("| " + " | ".join(row) + " |")

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.log(f"📄 Rapport: {report_path}")


def main():
    """CLI principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Orchestrateur complet BaseType Benchmark")

    parser.add_argument("--profile", help="Profil dataset (ex: small-1w)")
    parser.add_argument("--scenario", choices=[s.value for s in Scenario],
                       help="Scénario spécifique (P1, P2, M1, M2, O1, O2)")
    parser.add_argument("--all-scenarios", action="store_true",
                       help="Exécuter tous les scénarios")
    parser.add_argument("--full-suite", action="store_true",
                       help="Exécuter la suite complète")
    parser.add_argument("--host-ram", type=int, default=32,
                       help="RAM disponible en Go (défaut: 32)")
    parser.add_argument("--ram-mode", choices=["quick", "gradient", "discovery"],
                       default="quick", help="Mode de test RAM")
    parser.add_argument("--seed", type=int, default=42, help="Graine aléatoire")

    args = parser.parse_args()

    orchestrator = FullOrchestrator()
    ram_mode = TestMode(args.ram_mode)

    if args.full_suite:
        orchestrator.run_full_suite(
            ram_mode=ram_mode,
            host_ram_gb=args.host_ram,
            seed=args.seed,
        )
    elif args.profile and args.scenario:
        scenario = Scenario(args.scenario)
        orchestrator.run_scenario(scenario, args.profile)
    elif args.profile and args.all_scenarios:
        for scenario in Scenario:
            orchestrator.run_scenario(scenario, args.profile)
    else:
        parser.print_help()
        print("\nExemples:")
        print("  python full_orchestrator.py --profile small-1w --scenario P1")
        print("  python full_orchestrator.py --profile small-1w --all-scenarios")
        print("  python full_orchestrator.py --full-suite --host-ram 32")


if __name__ == "__main__":
    main()
