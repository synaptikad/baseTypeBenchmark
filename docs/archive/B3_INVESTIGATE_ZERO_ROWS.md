# Tâche pour Agent B3: Investiguer les 0 rows dans les résultats

## Problème Observé

Le benchmark quick test sur small-2d retourne **0 rows** pour la plupart des requêtes, ce qui indique un problème de cohérence du dataset:

```
Q2: p50=0.7ms rows=0
Q4: p50=3.0ms rows=0
Q5: p50=21.3ms rows=0
Q7: p50=0.6ms rows=0
Q8: p50=1.9ms rows=0
Q9: p50=1.8ms rows=0
Q10: p50=0.6ms rows=0
Q11: p50=1.3ms rows=0
Q13: p50=2.4ms rows=0
```

Seules Q1, Q3, Q6, Q12 retournent des résultats (1-76 rows).

## Ce qui fonctionne

- Le workflow on-demand fonctionne correctement
- L'export timeseries partagé fonctionne (2393 MB)
- Le chargement des données est OK (48,765 nodes, 54,273 edges, 30M timeseries)
- Les requêtes s'exécutent sans erreur

## Hypothèses à vérifier

### 1. Problème de jointures graph ↔ timeseries

Les requêtes qui retournent 0 rows font probablement des jointures entre:
- Les `point_id` dans la table timeseries
- Les `id` des nodes dans le graphe

**Vérifier:**
```sql
-- Dans PostgreSQL (P1/P2)
SELECT COUNT(*) FROM nodes WHERE type = 'Point';
SELECT COUNT(DISTINCT point_id) FROM timeseries;

-- Les point_id de timeseries existent-ils dans nodes?
SELECT COUNT(*) FROM timeseries t
WHERE NOT EXISTS (SELECT 1 FROM nodes n WHERE n.id = t.point_id);
```

### 2. Problème de format des IDs

Le générateur utilise peut-être un format d'ID différent entre:
- `nodes.parquet` → `id` column
- `timeseries.parquet` → `point_id` column

**Vérifier:**
```python
import pandas as pd
nodes = pd.read_parquet("exports/small-2d_seed42/parquet/nodes.parquet")
ts = pd.read_parquet("exports/small-2d_seed42/parquet/timeseries.parquet")

# Échantillon d'IDs
print("Nodes Point IDs:", nodes[nodes['type'] == 'Point']['id'].head(5).tolist())
print("Timeseries point_ids:", ts['point_id'].unique()[:5].tolist())

# Intersection
node_point_ids = set(nodes[nodes['type'] == 'Point']['id'])
ts_point_ids = set(ts['point_id'].unique())
print(f"Points in nodes: {len(node_point_ids)}")
print(f"Points in timeseries: {len(ts_point_ids)}")
print(f"Intersection: {len(node_point_ids & ts_point_ids)}")
```

### 3. Problème dans les requêtes SQL

Examiner les requêtes qui retournent 0 rows:

```bash
cat queries/p1_p2/Q02_*.sql
cat queries/p1_p2/Q04_*.sql
# etc.
```

Vérifier si les filtres (building_id, equipment_type, etc.) correspondent aux données générées.

### 4. Vérifier la structure du dataset

```python
import pandas as pd
nodes = pd.read_parquet("exports/small-2d_seed42/parquet/nodes.parquet")

# Distribution des types
print(nodes['type'].value_counts())

# Vérifier les propriétés
import json
sample = nodes[nodes['type'] == 'Point'].head(1)
print(json.loads(sample['properties'].iloc[0]))
```

### 5. Problème de variants dans les requêtes

Les requêtes utilisent des "variants" avec des paramètres différents (building_id, dates, etc.).
Si ces paramètres ne correspondent pas aux données générées, on obtient 0 rows.

**Vérifier:**
```bash
# Examiner comment les variants sont générés
grep -r "building_id" queries/
grep -r "variant" src/basetype_benchmark/benchmark/
```

## Actions Recommandées

1. **Lancer le diagnostic Parquet:**
   ```bash
   cd ~/baseTypeBenchmark
   source .venv/bin/activate
   python -c "
   import pandas as pd
   nodes = pd.read_parquet('src/basetype_benchmark/dataset/exports/small-2d_seed42/parquet/nodes.parquet')
   ts = pd.read_parquet('src/basetype_benchmark/dataset/exports/small-2d_seed42/parquet/timeseries.parquet')

   print('=== NODES ===')
   print(nodes['type'].value_counts())

   print('\n=== POINT IDs ===')
   node_points = set(nodes[nodes['type'] == 'Point']['id'])
   ts_points = set(ts['point_id'].unique())
   print(f'Points in nodes: {len(node_points)}')
   print(f'Points in timeseries: {len(ts_points)}')
   print(f'Intersection: {len(node_points & ts_points)}')
   print(f'In nodes but not timeseries: {len(node_points - ts_points)}')
   print(f'In timeseries but not nodes: {len(ts_points - node_points)}')

   if node_points:
       print(f'\nSample node point ID: {list(node_points)[:3]}')
   if ts_points:
       print(f'Sample ts point ID: {list(ts_points)[:3]}')
   "
   ```

2. **Vérifier une requête spécifique en direct:**
   ```bash
   # Lancer le container PostgreSQL
   cd docker && docker compose up -d timescaledb

   # Après chargement, tester manuellement
   docker exec -it btb_timescaledb psql -U postgres -d benchmark -c "
   SELECT n.type, COUNT(*) FROM nodes n GROUP BY n.type ORDER BY COUNT(*) DESC;
   "
   ```

3. **Examiner les requêtes problématiques:**
   ```bash
   cat queries/p1_p2/Q02_find_sensors_by_type.sql
   # Comparer avec les types présents dans le dataset
   ```

## Fichiers à examiner

| Fichier | Contenu |
|---------|---------|
| `src/basetype_benchmark/dataset/generator_v2.py` | Génération des nodes et points |
| `src/basetype_benchmark/dataset/exporter_v2.py` | Export vers Parquet |
| `queries/p1_p2/*.sql` | Requêtes SQL avec leurs paramètres |
| `src/basetype_benchmark/benchmark/runner.py` | Exécution des requêtes et variants |

## Résultat Attendu

Après investigation, identifier:
1. La cause exacte des 0 rows
2. Si c'est un problème de générateur → corriger generator_v2.py
3. Si c'est un problème de requêtes → corriger les SQL ou les variants
4. Si c'est un problème de mapping IDs → corriger l'exporter
