#!/usr/bin/env python3
"""Workflow optimisé pour génération séquentielle des datasets (Codespace-friendly)."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import List

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from basetype_benchmark.dataset.config import PROFILES
from basetype_benchmark.dataset.release_manager import DatasetReleaser


class DatasetWorkflow:
    """Workflow optimisé pour génération séquentielle avec nettoyage automatique."""
    
    def __init__(self):
        self.releaser = DatasetReleaser()
        
        # Vérifier la configuration
        self.github_token = os.environ.get("GITHUB_TOKEN")
        if not self.github_token:
            print("[WARN]  GITHUB_TOKEN non configuré - mode local uniquement")
    
    def get_codespace_storage_info(self) -> dict:
        """Informations sur le stockage du Codespace."""
        try:
            import subprocess
            # Utiliser df pour obtenir les infos de stockage
            result = subprocess.run(['df', '-BG', '/'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        total_gb = int(parts[1].rstrip('G'))
                        used_gb = int(parts[2].rstrip('G'))
                        free_gb = int(parts[3].rstrip('G'))
                        usage_percent = int(parts[4].rstrip('%'))
                        
                        return {
                            'total_gb': total_gb,
                            'used_gb': used_gb,
                            'free_gb': free_gb,
                            'usage_percent': usage_percent
                        }
        except Exception as e:
            pass
        
        # Fallback: essayer statvfs
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
        except:
            return {'error': 'Impossible de récupérer les infos stockage'}
    
    def sequential_generation_workflow(self, profiles: List[str], 
                                     max_parallel: int = 1,
                                     delay_between: int = 5) -> dict:
        """Génération séquentielle avec nettoyage automatique."""
        
        print("[START] WORKFLOW DE GÉNÉRATION SÉQUENTIELLE")
        print("=" * 60)
        print(f"Profils à traiter: {', '.join(profiles)}")
        print(f"Parallélisation: {max_parallel}")
        print(f"Délai entre générations: {delay_between}s")
        print()
        
        results = {
            'total': len(profiles),
            'successful': 0,
            'failed': 0,
            'storage_before': self.get_codespace_storage_info(),
            'storage_after': None,
            'details': []
        }
        
        for i, profile in enumerate(profiles, 1):
            print(f"\n🔄 [{i}/{len(profiles)}] Traitement {profile}")
            print("-" * 40)
            
            # Vérifier l'espace disponible
            storage = self.get_codespace_storage_info()
            if 'error' not in storage:
                print(f"💾 Stockage: {storage['used_gb']}/{storage['total_gb']} GB ({storage['usage_percent']}%)")
            
            try:
                # Workflow complet
                start_time = time.time()
                success = self.releaser.release_and_clean_workflow(profile, keep_local=False)
                duration = time.time() - start_time
                
                if success:
                    results['successful'] += 1
                    status = "[OK] SUCCÈS"
                else:
                    results['failed'] += 1
                    status = "[ERROR] ÉCHEC"
                
                results['details'].append({
                    'profile': profile,
                    'success': success,
                    'duration': round(duration, 1),
                    'storage_after': self.get_codespace_storage_info()
                })
                
                print(f"{status} - {profile} ({duration:.1f}s)")
                
            except Exception as e:
                print(f"[ERROR] ERREUR - {profile}: {e}")
                results['failed'] += 1
                results['details'].append({
                    'profile': profile,
                    'success': False,
                    'error': str(e)
                })
            
            # Délai entre générations (sauf dernière)
            if i < len(profiles):
                print(f"⏳ Pause de {delay_between}s...")
                time.sleep(delay_between)
        
        # Résumé final
        results['storage_after'] = self.get_codespace_storage_info()
        
        print("\n" + "=" * 60)
        print("[DONE] RÉSULTATS FINAUX")
        print("=" * 60)
        print(f"Total: {results['total']}")
        print(f"Réussis: {results['successful']}")
        print(f"Échoués: {results['failed']}")
        
        if 'error' not in results['storage_before'] and 'error' not in results['storage_after']:
            before = results['storage_before']
            after = results['storage_after']
            print(f"Stockage avant: {before['used_gb']}/{before['total_gb']} GB")
            print(f"Stockage après: {after['used_gb']}/{after['total_gb']} GB")
            print(f"Évolution: {after['used_gb'] - before['used_gb']:+.1f} GB")
        
        return results
    
    def smart_profile_selection(self, max_storage_gb: float = 10.0) -> List[str]:
        """Sélection intelligente des profils selon l'espace disponible."""
        
        print(f"🎯 SÉLECTION PROFILS (max {max_storage_gb} GB)")
        print("-" * 40)
        
        # Estimation des tailles (approximative)
        profile_sizes = {
            'small-1w': 1.0,    # ~951 MB cache + exports
            'small-1m': 4.5,    # ~4077 MB
            'small-6m': 27.0,   # ~24462 MB
            'small-1y': 55.0,   # ~49603 MB
            'medium-1w': 2.0,   # ~1903 MB
            'medium-1m': 9.0,   # ~8154 MB
            'medium-6m': 54.0,  # ~48923 MB
            'medium-1y': 110.0, # ~99206 MB
            'large-1w': 11.0,   # ~9513 MB
            'large-1m': 45.0,   # ~40770 MB
            'large-6m': 270.0,  # ~244617 MB
            'large-1y': 550.0   # ~496030 MB
        }
        
        # Profils par priorité (du plus petit au plus grand)
        priority_profiles = [
            'small-1w', 'small-1m', 'medium-1w', 'medium-1m',
            'small-6m', 'large-1w', 'medium-6m', 'large-1m',
            'small-1y', 'medium-1y', 'large-6m', 'large-1y'
        ]
        
        selected = []
        total_size = 0
        
        for profile in priority_profiles:
            if profile in PROFILES and profile in profile_sizes:
                size = profile_sizes[profile]
                if total_size + size <= max_storage_gb:
                    selected.append(profile)
                    total_size += size
                    print(f"✓ {profile}: {size:.1f} GB (total: {total_size:.1f} GB)")
                else:
                    print(f"✗ {profile}: {size:.1f} GB (dépasserait {total_size + size:.1f} GB)")
        
        print(f"\n[INFO] Sélection finale: {len(selected)} profils, {total_size:.1f} GB")
        return selected
    
    def benchmark_session_workflow(self, profile_name: str, seed: int = 42) -> bool:
        """Workflow pour une session de benchmark: téléchargement + préparation."""
        
        print(f"🏃 WORKFLOW SESSION BENCHMARK: {profile_name}")
        print("=" * 50)
        
        # Vérifier si disponible en cache local
        if self.releaser.manager.is_cached(profile_name, seed):
            print("✓ Dataset trouvé en cache local")
            return True
        
        # Télécharger depuis GitHub
        print("📥 Téléchargement depuis GitHub...")
        download_path = self.releaser.download_dataset_from_release(profile_name, seed)
        
        if download_path:
            print("[OK] Dataset prêt pour benchmark")
            return True
        else:
            print("[ERROR] Impossible de récupérer le dataset")
            return False


def main():
    """Interface CLI pour le workflow."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python workflow.py <command> [args...]")
        print()
        print("Commands:")
        print("  sequential [profiles...]     - Génération séquentielle (défaut: auto-sélection)")
        print("  smart-select [max_gb]        - Sélection intelligente des profils")
        print("  session <profile> [seed]     - Préparation session benchmark")
        print("  storage                      - Infos stockage Codespace")
        print()
        print("Exemples:")
        print("  python workflow.py sequential small-1w small-1m")
        print("  python workflow.py smart-select 5")
        print("  python workflow.py session small-1w")
        return
    
    workflow = DatasetWorkflow()
    command = sys.argv[1]
    
    if command == 'sequential':
        if len(sys.argv) > 2:
            profiles = sys.argv[2:]
        else:
            # Auto-sélection selon stockage disponible
            storage = workflow.get_codespace_storage_info()
            if 'free_gb' in storage:
                max_gb = min(storage['free_gb'] * 0.8, 10.0)  # 80% de l'espace libre, max 10GB
                profiles = workflow.smart_profile_selection(max_gb)
            else:
                profiles = ['small-1w', 'small-1m']  # Défaut
        
        workflow.sequential_generation_workflow(profiles)
    
    elif command == 'smart-select':
        max_gb = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
        selected = workflow.smart_profile_selection(max_gb)
        print(f"Profils sélectionnés: {', '.join(selected)}")
    
    elif command == 'session':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42
        workflow.benchmark_session_workflow(profile, seed)
    
    elif command == 'storage':
        storage = workflow.get_codespace_storage_info()
        if 'error' in storage:
            print(f"Erreur: {storage['error']}")
        else:
            print("💾 STOCKAGE CODESPACE")
            print(f"Total: {storage['total_gb']} GB")
            print(f"Utilisé: {storage['used_gb']} GB")
            print(f"Libre: {storage['free_gb']} GB")
            print(f"Usage: {storage['usage_percent']}%")


if __name__ == "__main__":
    main()