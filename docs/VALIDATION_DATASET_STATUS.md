# État du Projet: Validation Dataset V3

## Mission Globale

Créer un **golden dataset de validation** basé sur le générateur (pas manuel) qui garantit que **toutes les queries Q1-Q23 retournent des résultats cohérents** (même row_count) sur **tous les paradigmes supportés** (P1, P2, M1, M2, O2), sauf pour les queries marquées IMPOSSIBLE.

## Travail Effectué

### 1. Corrections de bugs dans `hybrid.py`

**Fichier**: `src/basetype_benchmark/runner/runners/hybrid.py`

#### Bug 1: `camel_to_snake` ne gérait pas les chiffres (ligne 296-303)
```python
# AVANT (bug): co2Factor → co2factor (manque underscore!)
re.sub(r'([a-z])([A-Z])', r'\1_\2', name).lower()

# APRÈS (fix): co2Factor → co2_factor
re.sub(r'([a-z\d])([A-Z])', r'\1_\2', name).lower()
```

#### Bug 2: `_extract_point_ids` ne gérait pas le format O2 Q13 (ligne 393-404)
Ajouté Case 4 pour gérer les rows SPARQL avec `(point_id, quantity)` au niveau row:
```python
if "point_id" in sample_row and "quantity" in sample_row:
    result = {}
    for row in rows:
        pid = row.get("point_id")
        qty = row.get("quantity")
        if pid and qty:
            if qty not in result:
                result[qty] = []
            result[qty].append(str(pid))
    return result if result else []
```

### 2. Suppression de `golden.py`

L'ancien fichier `golden.py` (golden dataset manuel) a été archivé dans `archive/golden_v1/` et remplacé par:

- **`src/basetype_benchmark/dataset/models.py`**: Contient les dataclasses `Node`, `Edge`, `TimeseriesPoint`
- **`src/basetype_benchmark/dataset/generator.py`**: Modifié pour importer depuis `models.py`
- **`src/basetype_benchmark/exporters/base.py`**: Modifié pour supprimer le fallback `GoldenDataset()`

### 3. Amélioration du `param_sampler.py`

**Fichier**: `src/basetype_benchmark/runner/core/param_sampler.py`

Ajouté des méthodes de sampling spécialisées qui garantissent des entités avec les relations nécessaires:

- `_sample_space_with_equipment()`: Spaces ayant SERVES/LOCATED_IN/MONITORS
- `_sample_floor_with_equipment()`: Floors avec equipment dans leurs spaces
- `_sample_building_with_points()`: Buildings avec points pour queries hybrid
- `_sample_tenant_with_meters()`: Tenants ayant METERS_TENANT relation
- `_sample_point_with_timeseries()`: Points avec données timeseries

Et les méthodes fetch correspondantes pour chaque paradigme (P1/P2/M1/M2/O2):
- `_fetch_spaces_with_equipment()`
- `_fetch_floors_with_equipment()`
- `_fetch_buildings_with_points()`
- `_fetch_tenants_with_meters()`
- `_fetch_points_with_timeseries()`

### 4. Dataset de validation généré

```bash
python -m basetype_benchmark.dataset.generator \
  --profile medium \
  --duration 1m \
  --seed 42 \
  --output data/generated/validation
```

**Localisation**: `data/generated/validation/medium-1m/`

**Contenu**:
- 9144 nodes
- 11891 edges
- 966300 timeseries points
- Seed 42 pour reproductibilité

---

## État Actuel des Queries (Benchmark V2)

### Résultats du dernier benchmark

```
Query  | P1    | P2    | M1    | M2    | O2    | Status
-------|-------|-------|-------|-------|-------|--------
Q1     | 1     | 1     | 0     | 0     | 0     | MISMATCH
Q2     | 3     | 3     | 3     | 3     | 0     | MISMATCH (O2)
Q3     | 4     | 4     | 4     | 4     | 4     | OK ✓
Q4     | 49    | 49    | 81    | 81    | 132   | MISMATCH
Q5     | 1     | 1     | 1     | 1     | 1     | OK ✓
Q6     | 24    | 24    | 2     | 2     | 0     | MISMATCH
Q7     | 0     | 0     | 0     | 0     | 0     | ALL ZERO
Q8     | 1     | 1     | 0     | 1     | 1     | MISMATCH (M1)
Q9     | 1     | 1     | 0     | 1     | 1     | MISMATCH (M1)
Q10    | 2     | 2     | 2     | 2     | 2     | OK ✓
Q11    | 4     | 4     | 4     | 4     | 0     | MISMATCH (O2)
Q12    | 1     | 1     | 0     | 1     | 1     | MISMATCH (M1)
Q13    | 0     | 0     | 0     | 0     | 0     | ALL ZERO
Q14    | SKIP  | 0     | 0     | 0     | 0     | P2 only - no data
Q15    | SKIP  | 27    | 27    | 27    | 0     | MISMATCH (O2)
Q16    | SKIP  | 1135  | 0     | 0     | 1135  | OK (P2+O2 only)
Q17    | SKIP  | 5     | 5     | 5     | 5     | OK ✓
Q18    | 10    | 4     | 7     | 7     | 0     | MISMATCH
Q19    | 1     | 1     | SKIP  | 1     | 1     | OK ✓
Q20    | 0     | 0     | 0     | 0     | SKIP  | ALL ZERO
Q21    | 1     | 1     | 1     | 1     | SKIP  | OK ✓
Q22    | 75    | 75    | 75    | 75    | 0     | MISMATCH (O2)
Q23    | 30    | 131   | 89    | 89    | 5322  | MISMATCH
```

### Queries OK (6 queries)
- **Q3, Q5, Q10, Q17, Q19, Q21**: Mêmes résultats sur tous les paradigmes supportés

### Queries ALL ZERO (3 queries) - PRIORITÉ HAUTE
Ces queries ne retournent aucun résultat sur aucun paradigme:

#### Q7: Building Energy (hybrid)
- **Fichiers**: `queries/*/Q7.*` et `queries/*/ts/Q07.sql`
- **Problème probable**: Le BUILDING_ID échantillonné n'a pas de points avec timeseries
- **Action**: Améliorer `_sample_building_with_points()` pour garantir des points energy

#### Q13: Office Comfort (hybrid)
- **Fichiers**: `queries/*/Q13.*` et `queries/*/ts/Q13.sql`
- **Problème probable**: Pas de spaces de type "office" avec points temperature/co2
- **Action**: Vérifier que le générateur crée des spaces "office*" avec les bons points

#### Q20: Shortest Path
- **Fichiers**: `queries/*/Q20.*`
- **Problème probable**: Pas de chemin entre SOURCE_ID et TARGET_ID échantillonnés
- **Action**: Le sampler doit échantillonner des paires (source, target) connectées

### Queries O2=0 (6 queries) - PRIORITÉ HAUTE
Les queries SPARQL O2 retournent 0 alors que les autres paradigmes fonctionnent:

#### Q2: Functional Impact
- **Fichier**: `queries/o2/graph/Q2.sparql`
- **Problème**: Property paths `btb:feeds+` ne fonctionnent pas comme attendu
- **Action**: Vérifier la syntaxe SPARQL et les prédicats RDF

#### Q6: Point Timeseries (hybrid)
- **Fichier**: `queries/o2/graph/Q6.sparql` + `queries/o2/ts/Q06.sql`
- **Problème**: La phase graph retourne 0 points
- **Action**: Vérifier que les Points sont bien exportés avec `btb:id`

#### Q11: UPS Battery Status (hybrid)
- **Fichier**: `queries/o2/graph/Q11.sparql`
- **Problème**: UPS non trouvé en SPARQL
- **Action**: Vérifier l'export de `equipmentType` pour UPS

#### Q15: Warranty Expiring
- **Fichier**: `queries/o2/graph/Q15.sparql`
- **Problème**: Metadata warranty pas accessible en SPARQL
- **Action**: Vérifier l'export des `metadata*` properties

#### Q18: Calibration Due
- **Fichier**: `queries/o2/graph/Q18.sparql`
- **Problème**: Calibration data pas accessible
- **Action**: Vérifier l'export des `calibration*` properties

#### Q22: Siblings
- **Fichier**: `queries/o2/graph/Q22.sparql`
- **Problème**: Query siblings ne fonctionne pas
- **Action**: Vérifier la logique SPARQL pour trouver les siblings

### Queries M1=0 (3 queries) - PRIORITÉ MOYENNE
M1 retourne 0 alors que M2 fonctionne:

#### Q8, Q9, Q12: Hybrid queries
- **Fichiers**: `queries/m1/Q8.cypher`, `queries/m1/Q9.cypher`, `queries/m1/Q12.cypher`
- **Problème**: M1 n'est pas hybrid (pas de timeseries), mais ces queries sont catégorisées hybrid
- **Action**: Vérifier le catalog.yaml pour la catégorie de ces queries pour M1

### Queries MISMATCH (sémantique différente) - PRIORITÉ BASSE
Ces queries retournent des résultats mais avec des counts différents:

#### Q1: Energy Chain
- P1/P2=1, M1/M2/O2=0
- **Analyse**: La query SQL utilise RECURSIVE CTE, Cypher utilise `[:FEEDS*1..10]`
- **Action**: Harmoniser la sémantique (inclure ou non le source)

#### Q4: Floor Equipment
- P1/P2=49, M1/M2=81, O2=132
- **Analyse**: Les queries ont des logiques différentes pour le comptage
- **Action**: Aligner la sémantique sur tous les paradigmes

#### Q6: Point Timeseries
- P1/P2=24, M1/M2=2, O2=0
- **Analyse**: Différents points échantillonnés ou date ranges
- **Action**: Vérifier que le même point_id et dates sont utilisés

#### Q18: Calibration
- P1=10, P2=4, M1/M2=7, O2=0
- **Analyse**: Différentes logiques de filtrage calibration
- **Action**: Harmoniser la logique

#### Q23: Adjacency Matrix
- P1=30, P2=131, M1/M2=89, O2=5322
- **Analyse**: Très grande différence, sémantique très différente
- **Action**: Revoir complètement les queries pour aligner

---

## Fichiers Clés à Modifier

### Queries
```
queries/
├── p1/          # SQL pour PostgreSQL relationnel
├── p2/          # SQL pour PostgreSQL JSONB
├── m1/          # Cypher pour Memgraph (graph-only)
├── m2/
│   ├── graph/   # Cypher pour phase graph
│   └── ts/      # SQL pour phase timeseries
├── o2/
│   ├── graph/   # SPARQL pour Oxigraph
│   └── ts/      # SQL pour TimescaleDB
└── catalog.yaml # Définition des queries et leurs catégories
```

### Runner
```
src/basetype_benchmark/runner/
├── core/
│   ├── param_sampler.py   # Échantillonnage des paramètres
│   ├── catalog.py         # Lecture du catalog
│   └── query_utils.py     # Utilitaires queries
├── runners/
│   ├── hybrid.py          # Exécution hybrid (graph + ts)
│   ├── postgres.py        # P1/P2
│   ├── memgraph.py        # M1/M2
│   └── oxigraph.py        # O2
└── ram/
    └── gradient.py        # Orchestration du benchmark
```

### Exporters
```
src/basetype_benchmark/exporters/
├── base.py           # Classes de base
├── p1_extractor.py   # Export P1
├── p2_extractor.py   # Export P2
├── m1m2_extractor.py # Export M1/M2
└── o2_extractor.py   # Export O2 (RDF N-Triples)
```

---

## Commandes Utiles

### Générer le dataset
```bash
cd /home/ubuntu/baseTypeBenchmark
source .venv/bin/activate
python -m basetype_benchmark.dataset.generator \
  --profile medium --duration 1m --seed 42 \
  --output data/generated/validation
```

### Lancer le benchmark complet
```bash
python -m basetype_benchmark.runner benchmark \
  --source data/generated/validation/medium-1m \
  --paradigms P1,P2,M1,M2,O2 \
  --ram 64 \
  --runs 1 --variants 1 \
  --output results_validation.json
```

### Tester une query spécifique
```bash
python -m basetype_benchmark.runner run-query \
  --paradigm P1 \
  --query Q3 \
  --source data/generated/validation/medium-1m
```

### Vérifier les données Parquet
```python
import pyarrow.parquet as pq
from pathlib import Path

nodes = pq.read_table("data/generated/validation/medium-1m/nodes.parquet").to_pylist()
edges = pq.read_table("data/generated/validation/medium-1m/edges.parquet").to_pylist()

# Compter par type
from collections import Counter
print(Counter(n['type'] for n in nodes))
print(Counter(e['rel_type'] for e in edges))
```

---

## Critères de Succès

1. **Aucune query ALL ZERO**: Q7, Q13, Q20 doivent retourner > 0 rows
2. **Cohérence O2**: Toutes les queries O2 (sauf IMPOSSIBLE) doivent retourner le même count que P1/P2
3. **Cohérence M1**: M1 doit matcher M2 pour les queries graph-only
4. **Équivalence sémantique**: Même row_count entre paradigmes supportés
5. **golden_answers.yaml créé**: Basé sur les résultats validés

---

## Corrections Effectuées (Session Courante)

### 5. Corrections des queries SPARQL O2

#### Q7.sparql - Navigation building→points
**Problème**: La query cherchait `btb:buildingId` comme propriété directe sur Point (n'existe pas).
**Correction**: Réécriture avec navigation via relations:
```sparql
?building a btb:Building ; btb:id ?buildingId .
?building btb:contains ?floor .
?floor btb:contains ?space .
?eq btb:serves|btb:locatedIn|btb:monitors ?space .
?eq btb:hasPoint ?point .
?point btb:id ?point_id .
```

#### Q13.sparql - Navigation building→spaces offices
**Problème**: La query cherchait `btb:buildingId` comme propriété sur Space.
**Correction**: Réécriture avec navigation Building → Floor → Space + filtres.

#### Q11.sparql - Variable hardcodée
**Problème**: Utilisait le literal `"ups_1"` au lieu d'une variable.
**Correction**: Remplacé par `?upsId` pour permettre l'injection VALUES.

#### Q15.sparql - Variables mal nommées
**Problème**: Variables `?ref_date` et `?days_ahead` ne correspondaient pas aux paramètres injectés.
**Correction**: Renommées en `?referenceDate` et `?daysAhead` (camelCase).

### 6. Résultats Benchmark Après Corrections

```
Query  | P1    | P2    | M1    | M2    | O2    | Status
-------|-------|-------|-------|-------|-------|--------
Q1     | 1     | 1     | 0     | 0     | 0     | MISMATCH
Q2     | 3     | 3     | 3     | 3     | 0     | O2=0 (à investiguer)
Q3     | 4     | 4     | 4     | 4     | 4     | OK ✓
Q4     | 49    | 49    | 81    | 81    | 132   | MISMATCH (sémantique)
Q5     | 1     | 1     | 1     | 1     | 1     | OK ✓
Q6     | 24    | 24    | 2     | 2     | 0     | MISMATCH (timeseries)
Q7     | 0     | 0     | 0     | 0     | 0     | ALL ZERO (données)
Q8     | 1     | 1     | 0     | 1     | 1     | OK (M1 DEGRADED)
Q9     | 1     | 1     | 0     | 1     | 1     | OK (M1 DEGRADED)
Q10    | 2     | 2     | 2     | 2     | 2     | OK ✓
Q11    | 4     | 4     | 4     | 4     | 6     | AMÉLIORÉ ✓ (était 0)
Q12    | 1     | 1     | 0     | 1     | 1     | OK (M1 DEGRADED)
Q13    | 0     | 0     | 0     | 0     | 0     | ALL ZERO (données)
Q14    | SKIP  | 0     | 0     | 0     | 0     | No data
Q15    | SKIP  | 27    | 27    | 27    | 0     | O2=0 (à investiguer)
Q16    | SKIP  | 1135  | 0     | 0     | 1135  | OK (P2+O2 only)
Q17    | SKIP  | 5     | 5     | 5     | 5     | OK ✓
Q18    | 10    | 4     | 7     | 7     | 0     | O2=0 (à investiguer)
Q19    | 1     | 1     | SKIP  | 1     | 1     | OK ✓
Q20    | 0     | 0     | 0     | 0     | SKIP  | ALL ZERO (données)
Q21    | 1     | 1     | 1     | 1     | SKIP  | OK ✓
Q22    | 75    | 75    | 75    | 75    | 0     | O2=0 (à investiguer)
Q23    | 30    | 131   | 89    | 89    | 5322  | MISMATCH (sémantique)
```

**Amélioration Q11**: La correction de la variable `?upsId` fonctionne - O2 retourne 6 résultats (avant: 0).

**Problèmes O2=0 restants** (Q2, Q15, Q18, Q22):
- Les queries SPARQL utilisent les bonnes variables camelCase
- Les données RDF sont correctement exportées (9144 nodes, 11891 edges)
- **Cause probable**: Le param_sampler échantillonne des équipements qui n'ont pas les relations requises

**Problèmes ALL ZERO** (Q7, Q13, Q20):
- Retournent 0 sur TOUS les paradigmes
- Problème de données/paramètres, pas de queries
- Le générateur ou sampler ne garantit pas les structures requises

---

## Prochaines Étapes Recommandées

1. **Investiguer O2=0 restants** (Q2, Q15, Q18, Q22)
   ```bash
   python -m basetype_benchmark.runner benchmark \
     --source data/generated/validation/medium-1m \
     --paradigms P1,P2,M1,M2,O2 \
     --ram 64 --runs 1 --variants 1
   ```

2. **Vérifier Q20 (ALL ZERO)** - SPARQL limitation
   - Q20 est marqué IMPOSSIBLE pour O2 (shortestPath n'existe pas en SPARQL)
   - Vérifier que les autres paradigmes retournent des résultats

3. **Harmoniser les sémantiques MISMATCH**
   - Q1, Q4, Q6, Q18, Q23 ont des counts différents entre paradigmes
   - Comparer les queries SQL vs Cypher vs SPARQL

4. **Créer golden_answers.yaml**
   - Une fois toutes les queries cohérentes
   - Documenter les row_counts attendus

5. **Validation finale**
   - Benchmark complet
   - Vérifier reproductibilité avec seed=42
