#!/usr/bin/env python3
"""Script de pré-génération des datasets pour les benchmarks."""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from basetype_benchmark.dataset.config import DEFAULT_SEED

def pregenerate_datasets():
    """Pré-génère les datasets les plus utilisés."""
    
    manager = DatasetManager()
    
    # Liste des datasets à pré-générer (les plus utilisés)
    datasets_to_generate = [
        ('small-1w', DEFAULT_SEED),    # Test rapide
        ('small-1m', DEFAULT_SEED),    # Test standard
        ('medium-1m', DEFAULT_SEED),   # Test moyen
        # ('large-1w', DEFAULT_SEED), # Désactivé car très volumineux
    ]
    
    print("[START] PRÉ-GÉNÉRATION DES DATASETS")
    print("=" * 50)
    
    total_start = time.time()
    
    for profile, seed in datasets_to_generate:
        print(f"\n[INFO] Génération {profile} (seed={seed})")
        start_time = time.time()
        
        try:
            # Générer et mettre en cache
            dataset, summary = manager.generate_dataset(profile, seed, force_regen=True)
            
            # Calculer les métriques
            duration = time.time() - start_time
            cache_info = manager.get_dataset_info(profile, seed)
            
            print(f"  ✓ Terminé en {duration:.1f}s")
            print(f"  [STATS] {summary.node_count:,} nœuds, {len(dataset.timeseries):,} séries TS")
            print(f"  💾 Cache: {cache_info['size_mb']:.1f} MB")
            
        except Exception as e:
            print(f"  [ERROR] Erreur: {e}")
            continue
    
    total_duration = time.time() - total_start
    print(f"\n[DONE] Pré-génération terminée en {total_duration:.1f}s")
    
    # Afficher l'état du cache
    print("\n📂 État du cache:")
    cached = manager.list_cached_datasets()
    for ds in cached:
        print(f"  {ds['name']}: {ds['size_mb']:.1f} MB")


def export_benchmark_datasets():
    """Exporte les datasets pour les benchmarks."""
    
    manager = DatasetManager()
    
    # Datasets à exporter pour les benchmarks
    exports = [
        ('small-1w', ['postgres']),      # PostgreSQL only pour tests rapides
        ('small-1m', ['postgres', 'graph']), # PostgreSQL + Memgraph
        ('medium-1m', ['postgres']),     # PostgreSQL pour tests moyens
    ]
    
    print("📤 EXPORT DES DATASETS POUR BENCHMARKS")
    print("=" * 50)
    
    for profile, formats in exports:
        print(f"\n[INFO] Export {profile} -> {', '.join(formats)}")
        start_time = time.time()
        
        try:
            export_path = manager.export_dataset(profile, formats)
            duration = time.time() - start_time
            print(f"  ✓ Terminé en {duration:.1f}s -> {export_path}")
            
        except Exception as e:
            print(f"  [ERROR] Erreur: {e}")
            continue


def main():
    """Point d'entrée principal."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pregenerate.py <command>")
        print("Commands:")
        print("  generate  - Pré-génère les datasets principaux")
        print("  export    - Exporte les datasets pour benchmarks")
        print("  all       - Fait les deux")
        return
    
    command = sys.argv[1]
    
    if command in ['generate', 'all']:
        pregenerate_datasets()
    
    if command in ['export', 'all']:
        export_benchmark_datasets()


if __name__ == "__main__":
    main()