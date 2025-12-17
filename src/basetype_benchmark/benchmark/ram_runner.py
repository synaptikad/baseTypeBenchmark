"""Runner spécialisé pour les tests RAM avec Docker memory limits.

Ce runner exécute les benchmarks avec différentes contraintes RAM pour :
1. Découvrir RAM_min par moteur/profil
2. Générer les courbes latence = f(RAM)
3. Détecter les OOM et dégradations

Intègre :
- ram_config.py pour les bornes adaptatives
- drop_caches entre les runs pour mesures cold-cache
- Docker --memory pour limiter la RAM
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from basetype_benchmark.benchmark.ram_config import (
    EngineType,
    RAMTestConfig,
    RAMTestSequence,
    TestMode,
    generate_test_sequence,
    get_test_config,
    auto_discover_ram_min,
)


@dataclass
class RAMTestResult:
    """Résultat d'un test RAM individuel."""
    engine: str
    profile: str
    ram_limit_mb: int
    success: bool
    oom_killed: bool = False
    ingestion_time_s: float = 0.0
    query_latencies: Dict[str, float] = field(default_factory=dict)
    p95_mean: float = 0.0
    degradation_vs_baseline: float = 0.0
    error_message: str = ""
    memory_stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine": self.engine,
            "profile": self.profile,
            "ram_limit_mb": self.ram_limit_mb,
            "ram_limit_gb": round(self.ram_limit_mb / 1024, 2),
            "success": self.success,
            "oom_killed": self.oom_killed,
            "ingestion_time_s": self.ingestion_time_s,
            "query_latencies": self.query_latencies,
            "p95_mean": self.p95_mean,
            "degradation_vs_baseline": self.degradation_vs_baseline,
            "error_message": self.error_message,
            "memory_stats": self.memory_stats,
        }


@dataclass
class RAMBenchmarkResults:
    """Résultats complets d'une série de tests RAM."""
    engine: str
    profile: str
    results: List[RAMTestResult] = field(default_factory=list)
    ram_min_mb: Optional[int] = None
    baseline_p95: Optional[float] = None
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine": self.engine,
            "profile": self.profile,
            "ram_min_mb": self.ram_min_mb,
            "ram_min_gb": round(self.ram_min_mb / 1024, 2) if self.ram_min_mb else None,
            "baseline_p95": self.baseline_p95,
            "results": [r.to_dict() for r in self.results],
            "timestamp": self.timestamp,
        }


class RAMBenchmarkRunner:
    """Runner pour benchmarks avec contraintes RAM."""

    # Mapping des noms de moteurs vers les commandes Docker
    ENGINE_DOCKER_CONFIG = {
        "P1": {
            "image": "timescale/timescaledb:latest-pg16",
            "container_name": "benchmark_postgres_ram",
            "env": {
                "POSTGRES_USER": "benchmark",
                "POSTGRES_PASSWORD": "benchmark",
                "POSTGRES_DB": "benchmark",
            },
            "ports": {"5432": "5432"},
            "healthcheck_cmd": ["pg_isready", "-U", "benchmark"],
        },
        "P2": {
            "image": "timescale/timescaledb:latest-pg16",
            "container_name": "benchmark_postgres_ram",
            "env": {
                "POSTGRES_USER": "benchmark",
                "POSTGRES_PASSWORD": "benchmark",
                "POSTGRES_DB": "benchmark",
            },
            "ports": {"5432": "5432"},
            "healthcheck_cmd": ["pg_isready", "-U", "benchmark"],
        },
        "M1": {
            "image": "memgraph/memgraph:latest",
            "container_name": "benchmark_memgraph_ram",
            "env": {},
            "ports": {"7687": "7687"},
            "healthcheck_cmd": ["mgconsole", "--version"],
        },
        "M2": {
            "image": "memgraph/memgraph:latest",
            "container_name": "benchmark_memgraph_ram",
            "env": {},
            "ports": {"7687": "7687"},
            "healthcheck_cmd": ["mgconsole", "--version"],
        },
        "O1": {
            "image": "ghcr.io/oxigraph/oxigraph:latest",
            "container_name": "benchmark_oxigraph_ram",
            "env": {},
            "ports": {"7878": "7878"},
            "healthcheck_cmd": ["curl", "-f", "http://localhost:7878/health"],
        },
        "O2": {
            "image": "ghcr.io/oxigraph/oxigraph:latest",
            "container_name": "benchmark_oxigraph_ram",
            "env": {},
            "ports": {"7878": "7878"},
            "healthcheck_cmd": ["curl", "-f", "http://localhost:7878/health"],
        },
    }

    def __init__(
        self,
        results_dir: Path = Path("bench/results/ram"),
        data_dir: Optional[Path] = None,
        drop_caches: bool = True,
        verbose: bool = True,
    ):
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = data_dir
        self.drop_caches = drop_caches
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Log avec timestamp."""
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {message}")

    def _drop_caches(self) -> bool:
        """Vide le cache Linux (nécessite sudo sans mot de passe)."""
        if not self.drop_caches:
            return True

        try:
            # Sync d'abord
            subprocess.run(["sync"], check=True, timeout=30)
            # Drop caches (nécessite privilèges)
            result = subprocess.run(
                ["sudo", "-n", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            self.log("⚠️  drop_caches non disponible (sudo requis)")
            return False

    def _start_container(
        self,
        engine: str,
        ram_limit_mb: int,
        timeout: int = 120,
    ) -> Optional[str]:
        """Démarre un container avec limite RAM."""
        config = self.ENGINE_DOCKER_CONFIG.get(engine)
        if not config:
            self.log(f"❌ Engine inconnu: {engine}")
            return None

        container_name = config["container_name"]

        # Arrêter l'ancien container si existe
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
        )

        # Construire la commande docker run
        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            f"--memory={ram_limit_mb}m",
            "--memory-swap", f"{ram_limit_mb}m",  # Pas de swap
        ]

        # Ports
        for host_port, container_port in config["ports"].items():
            cmd.extend(["-p", f"{host_port}:{container_port}"])

        # Variables d'environnement
        for key, value in config["env"].items():
            cmd.extend(["-e", f"{key}={value}"])

        # Image
        cmd.append(config["image"])

        self.log(f"🐳 Démarrage {engine} avec {ram_limit_mb}Mo RAM...")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                self.log(f"❌ Erreur démarrage: {result.stderr}")
                return None

            # Attendre que le service soit prêt
            return self._wait_for_health(container_name, config["healthcheck_cmd"], timeout)

        except subprocess.TimeoutExpired:
            self.log("❌ Timeout au démarrage")
            return None

    def _wait_for_health(
        self,
        container_name: str,
        healthcheck_cmd: List[str],
        timeout: int = 120,
    ) -> Optional[str]:
        """Attend que le container soit healthy."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                # Vérifier si le container est toujours running
                status = subprocess.run(
                    ["docker", "inspect", "-f", "{{.State.Status}}", container_name],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if status.returncode != 0 or status.stdout.strip() != "running":
                    # Vérifier si OOM killed
                    oom = subprocess.run(
                        ["docker", "inspect", "-f", "{{.State.OOMKilled}}", container_name],
                        capture_output=True,
                        text=True,
                    )
                    if oom.stdout.strip() == "true":
                        self.log("💀 Container OOM killed")
                        return None
                    self.log(f"❌ Container non running: {status.stdout.strip()}")
                    return None

                # Vérifier la santé
                health = subprocess.run(
                    ["docker", "exec", container_name] + healthcheck_cmd,
                    capture_output=True,
                    timeout=10,
                )
                if health.returncode == 0:
                    self.log("✓ Service prêt")
                    return container_name

            except subprocess.TimeoutExpired:
                pass

            time.sleep(2)

        self.log(f"❌ Timeout healthcheck après {timeout}s")
        return None

    def _stop_container(self, container_name: str) -> None:
        """Arrête et supprime un container."""
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
        )

    def _get_container_stats(self, container_name: str) -> Dict[str, Any]:
        """Récupère les stats mémoire du container."""
        try:
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format",
                 "{{.MemUsage}},{{.MemPerc}},{{.CPUPerc}}",
                 container_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(",")
                if len(parts) >= 3:
                    mem_usage = parts[0].strip()
                    mem_perc = parts[1].strip().rstrip("%")
                    cpu_perc = parts[2].strip().rstrip("%")
                    return {
                        "memory_usage": mem_usage,
                        "memory_percent": float(mem_perc) if mem_perc else 0,
                        "cpu_percent": float(cpu_perc) if cpu_perc else 0,
                    }
        except (subprocess.TimeoutExpired, ValueError):
            pass
        return {}

    def _check_oom_killed(self, container_name: str) -> bool:
        """Vérifie si le container a été OOM killed."""
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.OOMKilled}}", container_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip() == "true"
        except:
            return False

    def run_single_test(
        self,
        engine: str,
        profile: str,
        ram_limit_mb: int,
        run_queries_fn: Optional[Callable] = None,
    ) -> RAMTestResult:
        """Exécute un test avec une limite RAM spécifique.

        Args:
            engine: Type de moteur (P1, M1, etc.)
            profile: Profil dataset (small-1w, etc.)
            ram_limit_mb: Limite RAM en Mo
            run_queries_fn: Fonction optionnelle pour exécuter les queries
                           Signature: (container_name) -> Dict[str, float]

        Returns:
            RAMTestResult avec les métriques
        """
        result = RAMTestResult(
            engine=engine,
            profile=profile,
            ram_limit_mb=ram_limit_mb,
            success=False,
        )

        # Drop caches avant le test
        self._drop_caches()

        # Démarrer le container
        container = self._start_container(engine, ram_limit_mb)
        if not container:
            result.oom_killed = self._check_oom_killed(
                self.ENGINE_DOCKER_CONFIG[engine]["container_name"]
            )
            result.error_message = "OOM au démarrage" if result.oom_killed else "Échec démarrage"
            self._stop_container(self.ENGINE_DOCKER_CONFIG[engine]["container_name"])
            return result

        try:
            # TODO: Ingestion des données
            # Pour l'instant, simuler
            result.ingestion_time_s = 0.0

            # Exécuter les queries si fonction fournie
            if run_queries_fn:
                result.query_latencies = run_queries_fn(container)
                if result.query_latencies:
                    p95_values = [v for v in result.query_latencies.values() if v is not None]
                    result.p95_mean = sum(p95_values) / len(p95_values) if p95_values else 0

            # Stats mémoire
            result.memory_stats = self._get_container_stats(container)

            # Vérifier OOM
            result.oom_killed = self._check_oom_killed(container)
            result.success = not result.oom_killed

        except Exception as e:
            result.error_message = str(e)
            result.oom_killed = self._check_oom_killed(container)

        finally:
            self._stop_container(container)

        return result

    def run_ram_gradient(
        self,
        engine: EngineType,
        profile: str,
        mode: TestMode = TestMode.GRADIENT,
        host_ram_mb: Optional[int] = None,
        run_queries_fn: Optional[Callable] = None,
    ) -> RAMBenchmarkResults:
        """Exécute une série de tests RAM pour une configuration.

        Args:
            engine: Type de moteur
            profile: Profil dataset
            mode: Mode de test (GRADIENT, DISCOVERY, QUICK)
            host_ram_mb: RAM disponible sur l'hôte
            run_queries_fn: Fonction pour exécuter les queries

        Returns:
            RAMBenchmarkResults avec tous les résultats
        """
        config = get_test_config(engine, profile, mode, host_ram_mb)

        benchmark_results = RAMBenchmarkResults(
            engine=engine.value,
            profile=profile,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        if config.excluded:
            self.log(f"⚠️  Configuration exclue: {config.exclusion_reason}")
            return benchmark_results

        self.log(f"📊 Test RAM gradient: {engine.value} × {profile}")
        self.log(f"   Paliers: {[f'{r/1024:.1f}Go' for r in config.ram_steps]}")

        baseline_p95 = None

        # Tester du plus grand au plus petit pour établir baseline d'abord
        for ram_mb in reversed(config.ram_steps):
            self.log(f"\n🔧 Test avec {ram_mb/1024:.1f} Go RAM...")

            result = self.run_single_test(
                engine.value,
                profile,
                ram_mb,
                run_queries_fn,
            )

            # Établir baseline sur le premier succès (RAM max)
            if result.success and baseline_p95 is None:
                baseline_p95 = result.p95_mean
                benchmark_results.baseline_p95 = baseline_p95
                self.log(f"   📏 Baseline p95: {baseline_p95:.3f}s")

            # Calculer dégradation
            if baseline_p95 and result.p95_mean > 0:
                result.degradation_vs_baseline = (result.p95_mean - baseline_p95) / baseline_p95

            benchmark_results.results.append(result)

            # Log résultat
            if result.success:
                deg_str = f" (dégradation: {result.degradation_vs_baseline*100:.1f}%)" if baseline_p95 else ""
                self.log(f"   ✓ Succès - p95: {result.p95_mean:.3f}s{deg_str}")

                # Mettre à jour RAM_min si pas trop de dégradation
                if result.degradation_vs_baseline <= 0.2:  # < 20%
                    benchmark_results.ram_min_mb = ram_mb
            else:
                status = "OOM" if result.oom_killed else "Échec"
                self.log(f"   ❌ {status}: {result.error_message}")

        # Sauvegarder les résultats
        self._save_results(benchmark_results)

        return benchmark_results

    def _save_results(self, results: RAMBenchmarkResults) -> Path:
        """Sauvegarde les résultats en JSON."""
        filename = f"ram_{results.engine}_{results.profile}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = self.results_dir / filename

        with open(path, "w", encoding="utf-8") as f:
            json.dump(results.to_dict(), f, indent=2)

        self.log(f"💾 Résultats sauvegardés: {path}")
        return path

    def run_full_sequence(
        self,
        engines: Optional[List[EngineType]] = None,
        profiles: Optional[List[str]] = None,
        mode: TestMode = TestMode.GRADIENT,
        host_ram_mb: Optional[int] = None,
        run_queries_fn: Optional[Callable] = None,
    ) -> Dict[str, RAMBenchmarkResults]:
        """Exécute la séquence complète de tests RAM."""
        sequence = generate_test_sequence(engines, profiles, mode, host_ram_mb)

        self.log("=" * 60)
        self.log("SÉQUENCE DE TESTS RAM")
        self.log("=" * 60)
        self.log(f"Tests totaux: {sequence.total_tests}")
        self.log(f"Durée estimée: {sequence.estimated_duration_min} min")

        all_results = {}

        for config in sequence.get_runnable():
            key = f"{config.engine.value}_{config.profile}"
            results = self.run_ram_gradient(
                config.engine,
                config.profile,
                mode,
                host_ram_mb,
                run_queries_fn,
            )
            all_results[key] = results

        # Générer rapport récapitulatif
        self._generate_summary_report(all_results)

        return all_results

    def _generate_summary_report(self, all_results: Dict[str, RAMBenchmarkResults]) -> None:
        """Génère un rapport récapitulatif."""
        report_path = self.results_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        lines = [
            "# Rapport RAM Benchmark",
            "",
            f"Date: {datetime.now().isoformat()}",
            "",
            "## RAM Minimale par Configuration",
            "",
            "| Engine | Profile | RAM_min | Baseline p95 |",
            "|--------|---------|---------|--------------|",
        ]

        for key, results in sorted(all_results.items()):
            ram_min = f"{results.ram_min_mb/1024:.1f} Go" if results.ram_min_mb else "N/A"
            baseline = f"{results.baseline_p95:.3f}s" if results.baseline_p95 else "N/A"
            lines.append(f"| {results.engine} | {results.profile} | {ram_min} | {baseline} |")

        lines.extend([
            "",
            "## Détails par Test",
            "",
        ])

        for key, results in sorted(all_results.items()):
            lines.append(f"### {results.engine} × {results.profile}")
            lines.append("")
            lines.append("| RAM | Succès | p95 | Dégradation |")
            lines.append("|-----|--------|-----|-------------|")

            for r in sorted(results.results, key=lambda x: x.ram_limit_mb, reverse=True):
                status = "✓" if r.success else ("OOM" if r.oom_killed else "❌")
                p95 = f"{r.p95_mean:.3f}s" if r.p95_mean else "N/A"
                deg = f"{r.degradation_vs_baseline*100:.1f}%" if r.degradation_vs_baseline else "N/A"
                lines.append(f"| {r.ram_limit_mb/1024:.1f} Go | {status} | {p95} | {deg} |")

            lines.append("")

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.log(f"📄 Rapport: {report_path}")


def main():
    """CLI pour les tests RAM."""
    import argparse

    parser = argparse.ArgumentParser(description="Runner benchmark RAM")
    parser.add_argument("--engine", help="Moteur spécifique (P1, M1, etc.)")
    parser.add_argument("--profile", help="Profil dataset (small-1w, etc.)")
    parser.add_argument("--host-ram", type=int, help="RAM hôte en Go")
    parser.add_argument("--mode", choices=["gradient", "discovery", "quick"],
                       default="gradient", help="Mode de test")
    parser.add_argument("--no-drop-caches", action="store_true",
                       help="Désactiver drop_caches")
    args = parser.parse_args()

    runner = RAMBenchmarkRunner(
        drop_caches=not args.no_drop_caches,
    )

    host_ram_mb = args.host_ram * 1024 if args.host_ram else None
    mode = TestMode(args.mode)

    if args.engine and args.profile:
        # Test unique
        engine = EngineType(args.engine)
        runner.run_ram_gradient(engine, args.profile, mode, host_ram_mb)
    elif args.engine:
        # Tous les profils pour un moteur
        engines = [EngineType(args.engine)]
        runner.run_full_sequence(engines, None, mode, host_ram_mb)
    elif args.profile:
        # Tous les moteurs pour un profil
        runner.run_full_sequence(None, [args.profile], mode, host_ram_mb)
    else:
        print("Spécifiez --engine et/ou --profile")
        print("Exemple: python ram_runner.py --engine P1 --profile small-1w --host-ram 16")


if __name__ == "__main__":
    main()
