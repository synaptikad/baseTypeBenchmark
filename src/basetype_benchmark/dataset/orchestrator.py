#!/usr/bin/env python3
"""Orchestrateur automatique des benchmarks complets."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from basetype_benchmark.dataset.config import PROFILES
from basetype_benchmark.dataset.workflow import DatasetWorkflow


@dataclass
class BenchmarkResult:
    """Résultat d'un benchmark individuel."""
    profile: str
    model: str
    duration_seconds: float
    success: bool
    metrics: Dict
    error: Optional[str] = None


class BenchmarkOrchestrator:
    """Orchestrateur automatique des benchmarks."""

    def __init__(self):
        self.workflow = DatasetWorkflow()
        self.results: List[BenchmarkResult] = []

        # Configuration des modèles
        self.models = ['postgres', 'memgraph', 'oxigraph']
        self.scales = ['small', 'medium', 'large']
        self.durations = ['1w', '1m', '6m', '1y']

        # Répertoire des résultats
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)

    def get_benchmark_profiles(self) -> List[str]:
        """Liste de tous les profils à benchmarker."""
        profiles = []
        for scale in self.scales:
            for duration in self.durations:
                profile = f"{scale}-{duration}"
                if profile in PROFILES:
                    profiles.append(profile)
        return profiles

    def run_single_benchmark(self, profile: str, model: str) -> BenchmarkResult:
        """Exécute un benchmark individuel."""

        print(f"🏃 BENCHMARK: {profile} × {model}")
        print("=" * 50)

        start_time = time.time()

        try:
            # 1. Préparer le dataset
            print("📥 Préparation du dataset...")
            dataset_ready = self.workflow.benchmark_session_workflow(profile)
            if not dataset_ready:
                raise Exception("Impossible de préparer le dataset")

            # 2. Lancer le container approprié
            print(f"🐳 Démarrage {model}...")
            container_id = self.start_container(model, profile)

            # 3. Attendre que le service soit prêt
            print("⏳ Attente initialisation service...")
            self.wait_for_service(model, container_id)

            # 4. Charger les données
            print("📤 Chargement des données...")
            load_success = self.load_data(model, container_id, profile)

            if not load_success:
                raise Exception("Échec du chargement des données")

            # 5. Exécuter les queries de benchmark
            print("⚡ Exécution des benchmarks...")
            metrics = self.run_queries(model, container_id, profile)

            # 6. Nettoyer
            print("🧹 Nettoyage...")
            self.cleanup_container(container_id)

            duration = time.time() - start_time

            result = BenchmarkResult(
                profile=profile,
                model=model,
                duration_seconds=duration,
                success=True,
                metrics=metrics
            )

            print(f"[OK] SUCCÈS: {duration:.1f}s")
            return result

        except Exception as e:
            duration = time.time() - start_time
            print(f"[ERROR] ÉCHEC: {e}")

            result = BenchmarkResult(
                profile=profile,
                model=model,
                duration_seconds=duration,
                success=False,
                metrics={},
                error=str(e)
            )

            # Nettoyer même en cas d'erreur
            try:
                if 'container_id' in locals():
                    self.cleanup_container(container_id)
            except:
                pass

            return result

    def start_container(self, model: str, profile: str) -> str:
        """Démarre le container approprié."""
        if model == 'postgres':
            cmd = [
                'docker-compose', 'up', '-d', 'postgres'
            ]
        elif model == 'memgraph':
            cmd = [
                'docker-compose', 'up', '-d', 'memgraph'
            ]
        elif model == 'oxigraph':
            cmd = [
                'docker-compose', 'up', '-d', 'oxigraph'
            ]
        else:
            raise ValueError(f"Modèle inconnu: {model}")

        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent,
                              capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Échec démarrage {model}: {result.stderr}")

        # Récupérer l'ID du container
        container_name = f"basetypebenchmark_{model}_1"
        result = subprocess.run(['docker', 'ps', '-q', '-f', f"name={container_name}"],
                              capture_output=True, text=True)

        if result.returncode != 0 or not result.stdout.strip():
            raise Exception(f"Container {model} non trouvé")

        return result.stdout.strip()

    def wait_for_service(self, model: str, container_id: str, timeout: int = 60):
        """Attend que le service soit prêt."""
        import time

        if model == 'postgres':
            check_cmd = ['docker', 'exec', container_id, 'pg_isready', '-U', 'postgres']
        elif model == 'memgraph':
            check_cmd = ['docker', 'exec', container_id, 'mgconsole', '--version']
        elif model == 'oxigraph':
            # Vérifier si le port est ouvert
            check_cmd = ['curl', '-f', 'http://localhost:7878/health']
        else:
            raise ValueError(f"Modèle inconnu: {model}")

        start_time = time.time()
        while time.time() - start_time < timeout:
            result = subprocess.run(check_cmd, capture_output=True)
            if result.returncode == 0:
                return
            time.sleep(2)

        raise Exception(f"Service {model} pas prêt après {timeout}s")

    def load_data(self, model: str, container_id: str, profile: str) -> bool:
        """Charge les données dans le système."""
        try:
            if model == 'postgres':
                return self.load_postgres_data(container_id, profile)
            elif model == 'memgraph':
                return self.load_memgraph_data(container_id, profile)
            elif model == 'oxigraph':
                return self.load_oxigraph_data(container_id, profile)
            else:
                raise ValueError(f"Modèle inconnu: {model}")
        except Exception as e:
            print(f"Erreur chargement {model}: {e}")
            return False

    def load_postgres_data(self, container_id: str, profile: str) -> bool:
        """Charge les données PostgreSQL."""
        # Chemin vers les fichiers CSV
        data_dir = Path(__file__).parent / "exports" / profile

        # Commandes COPY pour charger les données
        copy_commands = [
            f"\\COPY nodes FROM '{data_dir}/nodes.csv' WITH CSV HEADER",
            f"\\COPY edges FROM '{data_dir}/edges.csv' WITH CSV HEADER",
            f"\\COPY timeseries FROM '{data_dir}/timeseries.csv' WITH CSV HEADER"
        ]

        for cmd in copy_commands:
            psql_cmd = ['docker', 'exec', '-i', container_id, 'psql', '-U', 'postgres', '-d', 'benchmark']
            result = subprocess.run(psql_cmd, input=cmd, text=True, capture_output=True)

            if result.returncode != 0:
                print(f"Erreur COPY: {result.stderr}")
                return False

        return True

    def load_memgraph_data(self, container_id: str, profile: str) -> bool:
        """Charge les données Memgraph."""
        # Utiliser mgconsole pour charger les données JSON
        data_dir = Path(__file__).parent / "exports" / profile

        # Script de chargement Memgraph
        load_script = f"""
        LOAD DATA LOCAL INFILE '{data_dir}/nodes.json' AS ROW CREATE (n:Node {{id: ROW.id, type: ROW.type}});
        LOAD DATA LOCAL INFILE '{data_dir}/edges.json' AS ROW MATCH (a:Node {{id: ROW.from}}), (b:Node {{id: ROW.to}}) CREATE (a)-[r:RELATION {{type: ROW.type}}]->(b);
        """

        mg_cmd = ['docker', 'exec', '-i', container_id, 'mgconsole']
        result = subprocess.run(mg_cmd, input=load_script, text=True, capture_output=True)

        return result.returncode == 0

    def load_oxigraph_data(self, container_id: str, profile: str) -> bool:
        """Charge les données Oxigraph."""
        data_dir = Path(__file__).parent / "exports" / profile

        # Utiliser curl pour POST le JSON-LD
        with open(data_dir / "graph.jsonld", 'r') as f:
            jsonld_data = f.read()

        curl_cmd = [
            'curl', '-X', 'POST',
            '-H', 'Content-Type: application/ld+json',
            '-d', jsonld_data,
            'http://localhost:7878/store'
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        return result.returncode == 0

    def run_queries(self, model: str, container_id: str, profile: str) -> Dict:
        """Exécute les queries de benchmark."""
        # Pour l'instant, retourner des métriques mock
        # TODO: Implémenter les vraies queries depuis queries/
        return {
            'query_count': 8,
            'total_time': 0.0,
            'avg_time': 0.0,
            'memory_peak': 0,
            'status': 'mock'
        }

    def cleanup_container(self, container_id: str):
        """Nettoie le container."""
        subprocess.run(['docker', 'stop', container_id], capture_output=True)
        subprocess.run(['docker', 'rm', container_id], capture_output=True)

    def run_full_benchmark_suite(self) -> Dict:
        """Exécute la suite complète de benchmarks."""

        print("[START] SUITE DE BENCHMARKS COMPLÈTE")
        print("=" * 60)
        print(f"Modèles: {', '.join(self.models)}")
        print(f"Profils: {len(self.get_benchmark_profiles())} combinaisons")
        print(f"Total: {len(self.models) * len(self.get_benchmark_profiles())} tests")
        print()

        results = {
            'start_time': time.time(),
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'results': [],
            'summary': {}
        }

        profiles = self.get_benchmark_profiles()

        for profile in profiles:
            for model in self.models:
                results['total_tests'] += 1

                result = self.run_single_benchmark(profile, model)
                self.results.append(result)

                if result.success:
                    results['successful_tests'] += 1
                else:
                    results['failed_tests'] += 1

                results['results'].append({
                    'profile': result.profile,
                    'model': result.model,
                    'success': result.success,
                    'duration': result.duration_seconds,
                    'metrics': result.metrics,
                    'error': result.error
                })

                # Sauvegarder les résultats intermédiaires
                self.save_results(results)

                print()

        results['end_time'] = time.time()
        results['total_duration'] = results['end_time'] - results['start_time']

        # Générer le rapport final
        self.generate_report(results)

        return results

    def save_results(self, results: Dict):
        """Sauvegarde les résultats intermédiaires."""
        results_file = self.results_dir / "benchmark_results.json"

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

    def generate_report(self, results: Dict):
        """Génère le rapport final."""
        report_file = self.results_dir / "benchmark_report.md"

        with open(report_file, 'w') as f:
            f.write("# Rapport de Benchmark Complet\n\n")
            f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Durée totale:** {results['total_duration']:.1f}s\n\n")
            f.write(f"**Tests totaux:** {results['total_tests']}\n")
            f.write(f"**Réussis:** {results['successful_tests']}\n")
            f.write(f"**Échoués:** {results['failed_tests']}\n\n")

            # Résumé par modèle
            f.write("## Résumé par Modèle\n\n")
            for model in self.models:
                model_results = [r for r in results['results'] if r['model'] == model]
                success_count = sum(1 for r in model_results if r['success'])
                avg_duration = sum(r['duration'] for r in model_results) / len(model_results)

                f.write(f"### {model.upper()}\n")
                f.write(f"- Tests: {len(model_results)}\n")
                f.write(f"- Réussis: {success_count}\n")
                f.write(f"- Durée moyenne: {avg_duration:.1f}s\n")
                f.write("\n")

            # Détails des échecs
            failed_tests = [r for r in results['results'] if not r['success']]
            if failed_tests:
                f.write("## Échecs\n\n")
                for test in failed_tests:
                    f.write(f"- **{test['profile']} × {test['model']}**: {test['error']}\n")
                f.write("\n")

        print(f"[INFO] Rapport généré: {report_file}")


def main():
    """Interface CLI."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <command>")
        print()
        print("Commands:")
        print("  full-suite    - Exécute la suite complète de benchmarks")
        print("  single <profile> <model> - Test individuel")
        print("  list          - Liste les profils à tester")
        return

    orchestrator = BenchmarkOrchestrator()
    command = sys.argv[1]

    if command == 'full-suite':
        results = orchestrator.run_full_benchmark_suite()
        print("\n[DONE] Suite terminée !")
        print(f"Réussis: {results['successful_tests']}/{results['total_tests']}")

    elif command == 'single':
        if len(sys.argv) < 4:
            print("Usage: python orchestrator.py single <profile> <model>")
            return

        profile = sys.argv[2]
        model = sys.argv[3]

        result = orchestrator.run_single_benchmark(profile, model)
        if result.success:
            print("[OK] Test réussi")
        else:
            print(f"[ERROR] Test échoué: {result.error}")

    elif command == 'list':
        profiles = orchestrator.get_benchmark_profiles()
        print(f"Profils à tester ({len(profiles)}):")
        for profile in profiles:
            print(f"  {profile}")
        print(f"\nTotal combinaisons: {len(profiles) * len(orchestrator.models)}")


if __name__ == "__main__":
    main()