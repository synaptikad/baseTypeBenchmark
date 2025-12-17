#!/usr/bin/env python3
"""Gestionnaire de releases GitHub pour les datasets."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from basetype_benchmark.dataset.config import PROFILES, ALIASES
from basetype_benchmark.dataset.dataset_manager import DatasetManager


class DatasetReleaser:
    """Gestionnaire de releases GitHub pour les datasets."""
    
    def __init__(self, repo_owner: str = "synaptikad", repo_name: str = "baseTypeBenchmark-datasets"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.manager = DatasetManager()
        
        # Token GitHub (doit être configuré)
        self.github_token = os.environ.get("GITHUB_TOKEN")
        if not self.github_token:
            print("[WARN]  GITHUB_TOKEN non configuré - mode lecture seule")
    
    def create_release(self, tag_name: str, name: str, body: str, 
                      draft: bool = True) -> Optional[Dict]:
        """Crée une release GitHub."""
        if not self.github_token:
            print("[ERROR] GITHUB_TOKEN requis pour créer des releases")
            return None
        
        url = f"{self.api_base}/releases"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "tag_name": tag_name,
            "name": name,
            "body": body,
            "draft": draft
        }
        
        import requests
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"✓ Release créée: {tag_name}")
            return response.json()
        else:
            print(f"[ERROR] Erreur création release: {response.status_code}")
            print(response.text)
            return None
    
    def upload_asset(self, release_id: str, file_path: Path, label: str) -> bool:
        """Upload un asset vers une release."""
        if not self.github_token:
            print("[ERROR] GITHUB_TOKEN requis pour uploader des assets")
            return False
        
        filename = file_path.name
        url = f"{self.api_base}/releases/{release_id}/assets?name={filename}"
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Content-Type": "application/octet-stream"
        }
        
        print(f"📤 Upload {filename} ({file_path.stat().st_size / (1024*1024):.1f} MB)...")
        
        import requests
        with open(file_path, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
        
        if response.status_code == 201:
            print(f"✓ Asset uploadé: {filename}")
            return True
        else:
            print(f"[ERROR] Erreur upload asset: {response.status_code}")
            return False
    
    def prepare_dataset_release(self, profile_name: str, seed: int = 42) -> Optional[Path]:
        """Prépare un dataset pour release (archive optimisée)."""
        
        print(f"[PACKAGE] Préparation release pour {profile_name}")
        
        # Générer le dataset si nécessaire
        dataset, summary = self.manager.generate_dataset(profile_name, seed)
        
        # Créer répertoire temporaire pour l'archive
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_name = f"dataset_{profile_name}_seed{seed}"
            archive_path = temp_path / archive_name
            
            # Exporter dans tous les formats
            export_path = self.manager.export_dataset(
                profile_name, 
                formats=['postgres', 'graph', 'rdf'], 
                seed=seed
            )
            
            # Créer archive compressée
            import shutil
            print(f"🗜️  Création archive {archive_name}.tar.gz...")
            shutil.make_archive(str(archive_path), 'gztar', export_path)
            
            final_archive = Path(f"{archive_name}.tar.gz")
            shutil.move(f"{archive_path}.tar.gz", final_archive)
            
            size_mb = final_archive.stat().st_size / (1024*1024)
            print(f"✓ Archive créée: {final_archive.name} ({size_mb:.1f} MB)")
            
            return final_archive
    
    def release_dataset(self, profile_name: str, seed: int = 42, 
                       upload: bool = False) -> bool:
        """Crée une release complète pour un dataset."""
        
        # Informations du profil
        resolved_profile = ALIASES.get(profile_name, profile_name)
        profile = PROFILES.get(resolved_profile)
        if not profile:
            print(f"[ERROR] Profil {profile_name} inconnu")
            return False
        
        # Préparer l'archive
        archive_path = self.prepare_dataset_release(profile_name, seed)
        if not archive_path:
            return False
        
        # Créer la release
        tag_name = f"dataset-{resolved_profile}-seed{seed}"
        release_name = f"Dataset {resolved_profile} (seed {seed})"
        
        # Description détaillée
        body = f"""# Dataset {resolved_profile}

**Profil:** {resolved_profile}
**Seed:** {seed}
**Points:** {profile.points:,}
**Équipements:** {profile.equipments:,}
**Espaces:** {profile.spaces:,}
**Étages:** {profile.floors}
**Durée TS:** {profile.duration_days} jours

## Contenu
- Export PostgreSQL (nodes.csv, edges.csv, timeseries.csv)
- Export Property Graph (nodes.json, edges.json)
- Export RDF (graph.jsonld)

## Génération
```bash
python dataset_gen/dataset_manager.py export {profile_name} postgres,graph,rdf {seed}
```

## Statistiques
- Nœuds: {len(dataset.nodes) if 'dataset' in locals() else 'N/A'}
- Relations: {len(dataset.edges) if 'dataset' in locals() else 'N/A'}
- Séries temporelles: {len(dataset.timeseries) if 'dataset' in locals() else 'N/A'}
"""
        
        release = self.create_release(tag_name, release_name, body, draft=True)
        if not release:
            return False
        
        # Uploader l'archive si demandé
        if upload:
            success = self.upload_asset(release['id'], archive_path, f"dataset_{resolved_profile}.tar.gz")
            if success:
                print(f"[DONE] Release complète: https://github.com/{self.repo_owner}/{self.repo_name}/releases/tag/{tag_name}")
            return success
        
        return True
    
    def list_releases(self) -> List[Dict]:
        """Liste les releases existantes."""
        import requests
        
        response = requests.get(f"{self.api_base}/releases")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] Erreur récupération releases: {response.status_code}")
            return []
    
    def batch_release_datasets(self, profiles: List[str] = None, upload: bool = False):
        """Crée des releases pour plusieurs datasets."""
        
        if profiles is None:
            # Profils par défaut pour release
            profiles = ['small-1w', 'small-1m', 'medium-1m']
        
        print(f"[START] BATCH RELEASE - {len(profiles)} datasets")
        print("=" * 50)
        
        successful = 0
        for profile in profiles:
            print(f"\n[INFO] Release {profile}")
            if self.release_dataset(profile, upload=upload):
                successful += 1
            time.sleep(2)  # Éviter rate limiting
        
        print(f"\n[DONE] {successful}/{len(profiles)} releases créées avec succès")
    
    def release_and_clean_workflow(self, profile_name: str, seed: int = 42, 
                                  keep_local: bool = False) -> bool:
        """Workflow complet: générer → release → nettoyer (optimisé pour Codespace)."""
        
        print(f"🔄 WORKFLOW OPTIMISÉ: {profile_name} (seed {seed})")
        print("=" * 60)
        
        # 1. Générer et créer release
        print("[PACKAGE] Phase 1: Génération et release...")
        success = self.release_dataset(profile_name, seed, upload=True)
        if not success:
            print("[ERROR] Échec génération/release")
            return False
        
        if keep_local:
            print("✓ Dataset gardé localement")
            return True
        
        # 2. Nettoyer le cache local
        print("\n🧹 Phase 2: Nettoyage local...")
        
        # Supprimer le cache
        cache_path = self.manager.get_cache_path(profile_name, seed)
        if cache_path.exists():
            cache_size = cache_path.stat().st_size / (1024*1024)
            cache_path.unlink()
            print(f"✓ Cache supprimé: {cache_path.name} ({cache_size:.1f} MB)")
        
        # Supprimer les exports locaux
        resolved_profile = ALIASES.get(profile_name, profile_name)
        export_subdir = self.manager.export_dir / resolved_profile
        if export_subdir.exists():
            export_size = sum(f.stat().st_size for f in export_subdir.rglob('*') if f.is_file()) / (1024*1024)
            shutil.rmtree(export_subdir)
            print(f"✓ Exports supprimés: {export_subdir.name} ({export_size:.1f} MB)")
        
        # Nettoyer les archives temporaires
        for archive in self.manager.export_dir.glob(f"dataset_{profile_name}_seed{seed}.tar.gz"):
            archive_size = archive.stat().st_size / (1024*1024)
            archive.unlink()
            print(f"✓ Archive temporaire supprimée: {archive.name} ({archive_size:.1f} MB)")
        
        print("\n[OK] Workflow terminé - dataset disponible sur GitHub")
        return True
    
    def download_dataset_from_release(self, profile_name: str, seed: int = 42, 
                                     target_dir: Path = None) -> Optional[Path]:
        """Télécharge un dataset depuis une release GitHub."""
        
        if not target_dir:
            target_dir = self.manager.export_dir
        
        resolved_profile = ALIASES.get(profile_name, profile_name)
        tag_name = f"dataset-{resolved_profile}-seed{seed}"
        
        # Trouver la release
        releases = self.list_releases()
        release = next((r for r in releases if r['tag_name'] == tag_name), None)
        
        if not release:
            print(f"[ERROR] Release {tag_name} non trouvée")
            return None
        
        # Trouver l'asset d'archive
        assets = release.get('assets', [])
        archive_asset = next((a for a in assets if a['name'].endswith('.tar.gz')), None)
        
        if not archive_asset:
            print(f"[ERROR] Archive non trouvée dans release {tag_name}")
            return None
        
        # Télécharger l'archive
        download_url = archive_asset['browser_download_url']
        archive_name = archive_asset['name']
        archive_path = target_dir / archive_name
        
        print(f"📥 Téléchargement {archive_name}...")
        
        import requests
        response = requests.get(download_url)
        if response.status_code != 200:
            print(f"[ERROR] Erreur téléchargement: {response.status_code}")
            return None
        
        with open(archive_path, 'wb') as f:
            f.write(response.content)
        
        # Extraire l'archive
        extract_dir = target_dir / resolved_profile
        extract_dir.mkdir(exist_ok=True)
        
        print(f"[PACKAGE] Extraction vers {extract_dir}...")
        shutil.unpack_archive(archive_path, extract_dir, 'gztar')
        
        # Supprimer l'archive
        archive_path.unlink()
        
        print(f"✓ Dataset téléchargé et extrait: {extract_dir}")
        return extract_dir


def main():
    """Interface CLI pour les releases."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python release_manager.py <command> [args...]")
        print()
        print("Commands:")
        print("  release <profile> [seed] [--upload]  - Crée release pour un dataset")
        print("  workflow <profile> [seed] [--keep]   - Workflow complet: générer→release→nettoyer")
        print("  download <profile> [seed]            - Télécharge dataset depuis release")
        print("  batch [--upload]                     - Batch release des datasets principaux")
        print("  list                                  - Liste les releases existantes")
        print("  prepare <profile> [seed]              - Prépare archive sans release")
        print()
        print("Options:")
        print("  --upload: Upload l'archive vers la release")
        print("  --keep: Garde le dataset local après workflow")
        return
    
    releaser = DatasetReleaser()
    command = sys.argv[1]
    
    if command == 'release':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 42
        upload = '--upload' in sys.argv
        releaser.release_dataset(profile, seed, upload)
    
    elif command == 'workflow':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 42
        keep_local = '--keep' in sys.argv
        releaser.release_and_clean_workflow(profile, seed, keep_local)
    
    elif command == 'download':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 42
        releaser.download_dataset_from_release(profile, seed)
    
    elif command == 'batch':
        upload = '--upload' in sys.argv
        releaser.batch_release_datasets(upload=upload)
    
    elif command == 'list':
        releases = releaser.list_releases()
        if releases:
            print(f"Releases ({len(releases)}):")
            for release in releases[:10]:  # Limiter à 10
                draft = " [DRAFT]" if release.get('draft') else ""
                print(f"  {release['tag_name']}: {release['name']}{draft}")
        else:
            print("Aucune release trouvée")
    
    elif command == 'prepare':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 42
        archive = releaser.prepare_dataset_release(profile, seed)
        if archive:
            print(f"✓ Archive préparée: {archive}")


if __name__ == "__main__":
    main()