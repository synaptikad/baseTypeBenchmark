#!/usr/bin/env python3
"""Script principal pour lancer le workflow séquentiel académique.

Ce script orchestre le benchmark complet avec la rigueur académique requise:
- Génération déterministe (seed=42)
- Tests séquentiels sur même dataset
- Isolation complète entre paradigmes
- Métriques standardisées

Usage:
    # Tester un seul profil
    python run_sequential_benchmark.py single small-1w

    # Suite complète (profils compatibles 128GB)
    python run_sequential_benchmark.py suite

    # Suite personnalisée
    python run_sequential_benchmark.py suite small-1w medium-1w

    # Tester un seul paradigm
    python run_sequential_benchmark.py paradigm small-1w postgres
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from basetype_benchmark.benchmark.orchestrator import BenchmarkOrchestrator


def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 2:
        print("Usage: python run_sequential_benchmark.py <command> [args...]")
        print()
        print("Commands:")
        print("  single <profile>             - Workflow complet pour un profil")
        print("  paradigm <profile> <paradigm> - Test d'un seul paradigm")
        print("  suite [profiles...]          - Suite séquentielle complète")
        print("  info                         - Afficher les profils compatibles")
        print()
        print("Exemples:")
        print("  python run_sequential_benchmark.py single small-1w")
        print("  python run_sequential_benchmark.py paradigm small-1w postgres")
        print("  python run_sequential_benchmark.py suite")
        print("  python run_sequential_benchmark.py suite small-1w medium-1w")
        return 1

    orchestrator = BenchmarkOrchestrator()
    command = sys.argv[1]

    if command == "info":
        print("\n[INFO] PROFILS COMPATIBLES CODESPACE 128GB / 64GB RAM")
        print("=" * 60)
        print("\nProfiles avec tous les paradigmes (PostgreSQL + Memgraph + Oxigraph):")
        print("RAM 32GB (standard):")
        compatible_32gb = ["small-1w", "small-1m", "medium-1w", "medium-1m", "large-1w"]
        for profile in compatible_32gb:
            print(f"  [OK] {profile}")

        print("\nRAM 64GB (upgraded) - NOUVEAUX PROFILS DÉBLOQUÉS:")
        compatible_64gb = ["small-6m", "small-1y", "medium-6m", "medium-1y"]
        for profile in compatible_64gb:
            print(f"  ✨ {profile} (nécessite 64GB RAM)")

        print("\nProfiles PostgreSQL uniquement (RAM Memgraph >64GB):")
        postgres_only = ["large-1m"]
        for profile in postgres_only:
            print(f"  🔵 {profile} (Memgraph: 146GB RAM requis)")

        print("\nProfiles non compatibles (>128GB disk):")
        incompatible = ["large-6m", "large-1y"]
        for profile in incompatible:
            print(f"  [ERROR] {profile}")

        print(f"\n💡 Recommandation:")
        print(f"   • RAM 32GB: Suite standard (5 profils)")
        print(f"   • RAM 64GB: Suite étendue (9 profils × 3 paradigmes = 27 benchmarks)")
        return 0

    elif command == "single":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: run_sequential_benchmark.py single <profile>")
            return 1

        profile = sys.argv[2]
        print(f"\n[START] BENCHMARK COMPLET: {profile}")
        print("=" * 60)

        session = orchestrator.run_full_dataset_benchmark(profile)

        if session.status == "completed":
            print(f"\n[OK] SUCCESS: {profile}")
            return 0
        else:
            print(f"\n[ERROR] FAILED: {profile}")
            for error in session.errors:
                print(f"   {error}")
            return 1

    elif command == "paradigm":
        if len(sys.argv) < 4:
            print("[ERROR] Usage: run_sequential_benchmark.py paradigm <profile> <paradigm>")
            return 1

        profile = sys.argv[2]
        paradigm = sys.argv[3]

        if paradigm not in ["postgres", "memgraph", "oxigraph"]:
            print(f"[ERROR] Paradigm invalide: {paradigm}")
            print("   Choix: postgres, memgraph, oxigraph")
            return 1

        print(f"\n🔬 BENCHMARK UNIQUE: {paradigm} sur {profile}")
        print("=" * 60)

        result = orchestrator.run_paradigm_benchmark(profile, paradigm)

        if result is not None:
            print(f"\n[OK] SUCCESS: {paradigm} sur {profile}")
            return 0
        else:
            print(f"\n[ERROR] FAILED: {paradigm} sur {profile}")
            return 1

    elif command == "suite":
        profiles = sys.argv[2:] if len(sys.argv) > 2 else None

        print(f"\n🎯 SUITE SÉQUENTIELLE ACADÉMIQUE")
        print("=" * 60)

        sessions = orchestrator.run_sequential_suite(profiles)

        # Résumé
        completed = sum(1 for s in sessions if s.status == "completed")
        failed = sum(1 for s in sessions if s.status == "failed")

        print(f"\n{'=' * 60}")
        print(f"RÉSUMÉ FINAL")
        print(f"{'=' * 60}")
        print(f"Total: {len(sessions)} profils")
        print(f"Réussis: {completed}")
        print(f"Échoués: {failed}")

        if completed == len(sessions):
            print(f"\n[OK] SUITE COMPLÈTE: 100% SUCCESS")
            return 0
        else:
            print(f"\n[WARN]  SUITE PARTIELLE: {failed} échecs")
            return 1

    else:
        print(f"[ERROR] Commande inconnue: {command}")
        print("   Utilisez 'info', 'single', 'paradigm', ou 'suite'")
        return 1


if __name__ == "__main__":
    sys.exit(main())
