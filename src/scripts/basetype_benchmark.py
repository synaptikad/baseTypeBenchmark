#!/usr/bin/env python3
"""Script principal de lancement du benchmark BaseType."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ajouter src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from basetype_benchmark.dataset.workflow import DatasetWorkflow
from basetype_benchmark.dataset.orchestrator import BenchmarkOrchestrator


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="BaseType Benchmark - Comparaison des paradigmes de BD pour données bâtimentaires"
    )

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Commande dataset
    dataset_parser = subparsers.add_parser('dataset', help='Gestion des datasets')
    dataset_parser.add_argument('action', choices=['generate', 'list', 'clean', 'storage'],
                               help='Action à effectuer')
    dataset_parser.add_argument('--profile', help='Profil de dataset')
    dataset_parser.add_argument('--seed', type=int, default=42, help='Seed pour génération')

    # Commande benchmark
    benchmark_parser = subparsers.add_parser('benchmark', help='Exécution des benchmarks')
    benchmark_parser.add_argument('action', choices=['run', 'full-suite', 'single'],
                                 help='Type de benchmark')
    benchmark_parser.add_argument('--profile', help='Profil pour test unique')
    benchmark_parser.add_argument('--model', choices=['postgres', 'memgraph', 'oxigraph'],
                                 help='Modèle pour test unique')

    # Commande workflow
    workflow_parser = subparsers.add_parser('workflow', help='Workflows automatisés')
    workflow_parser.add_argument('action', choices=['sequential', 'smart-select', 'session'],
                                help='Type de workflow')
    workflow_parser.add_argument('--profiles', nargs='*', help='Profils pour génération séquentielle')
    workflow_parser.add_argument('--max-gb', type=float, default=10, help='Espace max pour sélection')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'dataset':
            handle_dataset_command(args)
        elif args.command == 'benchmark':
            handle_benchmark_command(args)
        elif args.command == 'workflow':
            handle_workflow_command(args)
        else:
            parser.print_help()

    except Exception as e:
        print(f"[ERROR] Erreur: {e}")
        sys.exit(1)


def handle_dataset_command(args):
    """Gestion des commandes dataset."""
    workflow = DatasetWorkflow()

    if args.action == 'generate':
        if not args.profile:
            print("[ERROR] Profil requis pour génération")
            return
        success = workflow.benchmark_session_workflow(args.profile, args.seed)
        print(f"[OK] Génération {'réussie' if success else 'échouée'}")

    elif args.action == 'list':
        # TODO: Implémenter listing des datasets
        print("📋 Listing des datasets (TODO)")

    elif args.action == 'clean':
        # TODO: Implémenter nettoyage
        print("🧹 Nettoyage (TODO)")

    elif args.action == 'storage':
        storage = workflow.get_codespace_storage_info()
        if 'error' in storage:
            print(f"[ERROR] {storage['error']}")
        else:
            print("💾 STOCKAGE CODESPACE")
            print(f"Total: {storage['total_gb']} GB")
            print(f"Utilisé: {storage['used_gb']} GB")
            print(f"Libre: {storage['free_gb']} GB")
            print(f"Usage: {storage['usage_percent']}%")


def handle_benchmark_command(args):
    """Gestion des commandes benchmark."""
    orchestrator = BenchmarkOrchestrator()

    if args.action == 'run':
        print("🏃 Exécution benchmark (TODO)")
    elif args.action == 'full-suite':
        results = orchestrator.run_full_benchmark_suite()
        print(f"[DONE] Suite terminée: {results['successful_tests']}/{results['total_tests']} réussis")
    elif args.action == 'single':
        if not args.profile or not args.model:
            print("[ERROR] Profil et modèle requis pour test unique")
            return
        result = orchestrator.run_single_benchmark(args.profile, args.model)
        status = "[OK] RÉUSSI" if result.success else "[ERROR] ÉCHEC"
        print(f"{status}: {result.profile} × {result.model} ({result.duration_seconds:.1f}s)")


def handle_workflow_command(args):
    """Gestion des commandes workflow."""
    workflow = DatasetWorkflow()

    if args.action == 'sequential':
        if not args.profiles:
            # Sélection automatique
            storage = workflow.get_codespace_storage_info()
            if 'free_gb' in storage:
                max_gb = min(storage['free_gb'] * 0.8, 10.0)
                args.profiles = workflow.smart_profile_selection(max_gb)
            else:
                args.profiles = ['small-1w', 'small-1m']

        print(f"[START] Génération séquentielle: {', '.join(args.profiles)}")
        results = workflow.sequential_generation_workflow(args.profiles)
        print(f"[OK] Terminé: {results['successful']}/{results['total']} réussis")

    elif args.action == 'smart-select':
        selected = workflow.smart_profile_selection(args.max_gb)
        print(f"🎯 Profils sélectionnés ({args.max_gb} GB max): {', '.join(selected)}")

    elif args.action == 'session':
        if not args.profiles or len(args.profiles) != 1:
            print("[ERROR] Un seul profil requis pour session")
            return
        success = workflow.benchmark_session_workflow(args.profiles[0])
        print(f"[OK] Session {'réussie' if success else 'échouée'}")


if __name__ == "__main__":
    main()