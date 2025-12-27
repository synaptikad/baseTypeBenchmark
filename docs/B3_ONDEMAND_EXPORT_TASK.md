# Tâche pour Agent B3: Export On-Demand

## Contexte

Le workflow actuel exporte TOUS les formats cibles (P1, P2, M1, M2, O1, O2) pendant la phase de génération du dataset, ce qui:
- Duplique `timeseries.csv` dans chaque répertoire (~40GB+ au lieu de ~10-15GB)
- Consomme trop d'espace disque sur B3
- Ralentit la génération initiale

## Objectif

Implémenter un workflow **on-demand** où:
1. `python run.py generate` génère UNIQUEMENT le Parquet pivot
2. Chaque format cible est exporté JUSTE AVANT son benchmark
3. Après le benchmark, le répertoire du scénario est nettoyé
4. Pas de modes multiples - c'est LE workflow par défaut

## Analyse: Timeseries Partagé

### Confirmation: P1, P2, M2, O2 partagent le même format timeseries

| Scénario | Fichier attendu | Format CSV | Destination |
|----------|-----------------|------------|-------------|
| P1 | `p1/pg_timeseries.csv` | `point_id,time,value` | TimescaleDB |
| P2 | `p2/pg_timeseries.csv` | `point_id,time,value` | TimescaleDB |
| M2 | `m2/timeseries.csv` | `point_id,time,value` | TimescaleDB |
| O2 | `o2/timeseries.csv` | `point_id,time,value` | TimescaleDB |
| **M1** | `m1/mg_chunks.csv` | chunks JSON | Memgraph nodes |
| **O1** | `o1/chunks.nt` | N-Triples | Oxigraph |

**Conclusion**: Un seul `timeseries.csv` partagé peut servir P1, P2, M2, O2. M1 et O1 n'en ont pas besoin.

### Code de chargement (run.py ligne 2601-2604)

```python
cur.copy_expert(
    "COPY timeseries (point_id, time, value) FROM STDIN WITH CSV HEADER",
    f
)
```

Le format est identique pour tous les scénarios hybrides.

## Ordre Recommandé des Benchmarks

```
Phase 1 - Scénarios hybrides (partagent timeseries.csv):
  0. Export timeseries.csv UNE FOIS → exports/{profile}/timeseries.csv
  1. P1: export → symlink p1/pg_timeseries.csv → benchmark → cleanup p1/
  2. P2: export → symlink p2/pg_timeseries.csv → benchmark → cleanup p2/
  3. M2: export → symlink m2/timeseries.csv → benchmark → cleanup m2/
  4. O2: export → symlink o2/timeseries.csv → benchmark → cleanup o2/
  5. Supprimer timeseries.csv partagé

Phase 2 - Scénarios graph-only (pas de timeseries.csv):
  6. M1: export (chunks) → benchmark → cleanup m1/
  7. O1: export (chunks+aggregates) → benchmark → cleanup o1/
```

## Ce qui a été tenté (commit f980aad)

### Fonctions ajoutées dans `exporter_v2.py`:

```python
def export_timeseries_csv_shared(parquet_dir, shared_ts_path, force=False) -> bool:
    """Export timeseries.csv UNE FOIS depuis Parquet."""

def get_shared_timeseries_path(export_dir) -> Path:
    """Retourne exports/{profile}/timeseries.csv"""

def symlink_or_copy_timeseries(shared_ts_path, scenario_dir, filename="timeseries.csv"):
    """Crée symlink (Unix) ou copie (Windows) vers le scénario."""
```

### Paramètre `skip_timeseries` ajouté:

```python
def export_postgresql_csv(..., skip_timeseries=False)
def export_postgresql_jsonb_csv(..., skip_timeseries=False)
def export_memgraph_csv(..., skip_timeseries=False)
def export_for_target(..., skip_timeseries=False)
```

### Fonctions ajoutées dans `run.py`:

```python
def run_scenario_with_ondemand_export(scenario, export_dir, profile, ram_gb=8, cleanup_after=True):
    """Export on-demand + benchmark + cleanup."""

def run_all_scenarios_ondemand(export_dir, profile, ram_gb=8, scenarios=None, cleanup_between=True):
    """Workflow complet on-demand."""
```

### Fonction dans `dataset_manager.py`:

```python
def export_scenario_only(self, profile_name, scenario, seed=DEFAULT_SEED, skip_timeseries=False):
    """Exporte UN scénario depuis Parquet, avec option skip_timeseries."""
```

## PROBLÈME: Ce qui n'a PAS été modifié

### `dataset_manager.py` - Phase 3 toujours active (lignes 203-237)

```python
# PHASE 3: Exporter vers les formats cibles   <-- CECI DOIT ÊTRE SUPPRIMÉ
print(f"    [3/3] Exporting to target formats...")
for fmt in formats:
    ...
    exporter_v2.export_for_target(parquet_dir, target, output_dir)  # <-- EXPORTE TOUT
```

Cette Phase 3 exporte TOUS les formats pendant `generate_and_export()`, ce qui annule le workflow on-demand.

## Modifications à Effectuer

### 1. Supprimer Phase 3 dans `dataset_manager.py`

Fichier: `src/basetype_benchmark/dataset/dataset_manager.py`
Lignes: 202-237

**Supprimer ou commenter ce bloc:**

```python
        # =====================================================================
        # PHASE 3: Exporter vers les formats cibles   <-- SUPPRIMER TOUT CE BLOC
        # =====================================================================
        print(f"    [3/3] Exporting to target formats...")
        export_start = time_module.time()

        target_mapping = {
            'postgresql': ('postgresql', 'P1'),
            ...
        }

        for fmt in formats:
            ...
            exporter_v2.export_for_target(parquet_dir, target, output_dir)
        ...
```

### 2. Modifier le workflow benchmark dans `run.py`

Le workflow de benchmark doit:

1. Vérifier que Parquet existe
2. Exporter `timeseries.csv` partagé UNE FOIS
3. Pour chaque scénario P1/P2/M2/O2:
   - Exporter le format (sans timeseries)
   - Créer symlink/copie du timeseries partagé
   - Lancer le benchmark
   - Nettoyer le répertoire du scénario
4. Supprimer `timeseries.csv` partagé
5. Pour M1/O1:
   - Exporter le format (avec chunks)
   - Lancer le benchmark
   - Nettoyer

### 3. Utiliser `symlink_or_copy_timeseries()` correctement

Pour P1/P2, le fichier doit être nommé `pg_timeseries.csv`:
```python
exporter_v2.symlink_or_copy_timeseries(shared_ts_path, p1_dir, filename="pg_timeseries.csv")
exporter_v2.symlink_or_copy_timeseries(shared_ts_path, p2_dir, filename="pg_timeseries.csv")
```

Pour M2/O2, le fichier reste `timeseries.csv`:
```python
exporter_v2.symlink_or_copy_timeseries(shared_ts_path, m2_dir, filename="timeseries.csv")
exporter_v2.symlink_or_copy_timeseries(shared_ts_path, o2_dir, filename="timeseries.csv")
```

## Vérification Après Modification

### Test 1: Génération ne doit créer QUE Parquet

```bash
python run.py generate medium-1w
ls exports/medium-1w_seed42/
# Attendu: parquet/ fingerprint.json (PAS de p1/ p2/ m1/ m2/ o1/ o2/)
```

### Test 2: Benchmark doit exporter on-demand

```bash
python run.py benchmark
# Observer:
# - Export P1 → benchmark P1 → cleanup p1/
# - Export P2 → benchmark P2 → cleanup p2/
# - etc.
```

### Test 3: Espace disque maîtrisé

```bash
du -sh exports/medium-1w_seed42/
# Attendu: ~10-15GB max pendant le benchmark (au lieu de 40GB+)
```

## Fichiers Concernés

| Fichier | Modification |
|---------|--------------|
| `src/basetype_benchmark/dataset/dataset_manager.py` | Supprimer Phase 3 (lignes 202-237) |
| `run.py` | Modifier workflow benchmark pour on-demand |

## Fonctions Existantes à Utiliser

```python
# Dans exporter_v2.py (déjà implémenté):
exporter_v2.export_timeseries_csv_shared(parquet_dir, shared_ts_path)
exporter_v2.symlink_or_copy_timeseries(shared_ts_path, scenario_dir, filename)
exporter_v2.export_for_target(parquet_dir, target, output_dir, skip_timeseries=True)

# Dans dataset_manager.py (déjà implémenté):
manager.export_scenario_only(profile, scenario, seed, skip_timeseries=True)
manager.prune_scenario(profile, scenario, seed)
```

## Résumé

1. **Supprimer Phase 3** dans `generate_and_export()` - c'est la cause du problème
2. **Modifier le benchmark** pour utiliser l'export on-demand avec le workflow:
   - timeseries.csv partagé → P1, P2, M2, O2 (symlinks) → cleanup → M1, O1
3. Les fonctions helper existent déjà, il faut juste les utiliser correctement
