# BaseType Benchmark V3

Benchmark orienté **usage middleware smart building** pour comparer 5 paradigmes de base de données sur des charges réalistes.

**Question de recherche** : Un graphe in-memory est-il justifié pour les SI bâtimentaires ?

**Hypothèse** : Les graphes bâtimentaires sont structurellement simples (degré ~1, profondeur 6-8). SQL récursif (CTEs) pourrait suffire. Ce benchmark mesure précisément la consommation mémoire et les latences de chaque paradigme.

---

## Résultats Clés (large-6m : 60k nodes, 2M timeseries)

### Verdict : Hypothèse **SUPPORTÉE**

| Métrique | P2 (PostgreSQL+JSONB) | M1 (Memgraph) | Écart |
|----------|----------------------:|---------------:|------:|
| **RAM Baseline** | 1,566 MB | 2,739 MB | M1 **1.7x** plus |
| **Q6** (timeseries 6 mois) | 22 ms | 2,004 ms | M1 **89x** plus lent |
| **Q7** (variance Top-20) | 119 ms | 1,147 ms | M1 **10x** plus lent |
| **Q20** (shortest path) | 0.8 ms | 0.5 ms | Imperceptible |
| **Q21** (all paths SPOF) | 0.8 ms | 0.6 ms | Imperceptible |

**Conclusion** : M1 (in-memory graph) ne fournit **aucun avantage perceptible** (>500ms) sur les queries graph-native, tandis que P2 est **secondes plus rapide** sur les workloads IoT/timeseries qui représentent 80% des usages middleware.

L'architecture "in-memory graph kernel" (type SpinalCom) n'est pas justifiée pour les middlewares smart building.

→ Voir [data/results/runs/](data/results/runs/) pour les rapports détaillés.

---

## Quickstart

```bash
# 1. Cloner et installer
git clone <repo-url> && cd baseTypeBenchmark
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Lancer le menu interactif
python run.py

# 3. Ou utiliser la CLI directement
btb-runner benchmark -s data/generated/small-2d -p P1,M1 --ram 32,16,8
```

---

## Paradigmes comparés

| ID | Stack | Graph | Timeseries | JSONB |
|----|-------|-------|------------|-------|
| **P1** | PostgreSQL Relational | CTEs récursifs | TimescaleDB | - |
| **P2** | PostgreSQL JSONB | CTEs + JSONB ops | TimescaleDB | NATIVE |
| **M1** | Memgraph Standalone | Cypher natif | Chunks in-memory | - |
| **M2** | Memgraph + TimescaleDB | Cypher natif | TimescaleDB (fédéré) | - |
| **O2** | Oxigraph + TimescaleDB | SPARQL RDF | TimescaleDB (fédéré) | - |

### Architecture (TimescaleDB partagé)

```
                    ┌─────────────────┐
                    │  TimescaleDB    │  <- Chargé UNE SEULE FOIS
                    │  (ts.timeseries)│
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐
    │ P1 (p1.*)   │   │ M2 (Memgraph│   │ O2 (Oxigraph│
    │ P2 (p2.*)   │   │ + ts.*)     │   │ + ts.*)     │
    └─────────────┘   └─────────────┘   └─────────────┘
```

---

## Queries (42 total)

### Reads (Q1-Q34)

| Catégorie | Queries | Description | Avantage |
|-----------|---------|-------------|----------|
| **Graph-only** | Q1-Q5 | Traversées structurelles (FEEDS, SERVES, CONTAINS) | Neutre |
| **Timeseries** | Q6 | Agrégations temporelles (time_bucket) | SQL |
| **Hybrid** | Q7-Q13 | Sélection graph + agrégation TS | Neutre |
| **JSONB** | Q14-Q19 | Requêtes metadata (P2=NATIVE) | P2 |
| **Graph-native** | Q20-Q23 | Algorithmes graphe (shortestPath, allPaths) | M1/M2 |
| **Validation** | Q24-Q26 | Lectures post-écriture | Neutre |
| **Graph-native+** | Q27-Q30 | Weighted paths, cycles, multi-hop | M1/M2 |
| **SQL-native** | Q31-Q34 | Window functions, LATERAL, materialized views | P1/P2 |

#### Nouvelles queries d'équilibrage (Q27-Q34)

| Query | Nom | Graph Status | SQL Status |
|-------|-----|--------------|------------|
| **Q27** | Evacuation Path | NATIVE (Dijkstra) | DEGRADED (CTE récursif) |
| **Q28** | Tenant Impact Chain | NATIVE (var-length) | DEGRADED (5 JOINs) |
| **Q29** | All Power Paths | NATIVE (allPaths) | DEGRADED (ARRAY explosion) |
| **Q30** | Cycle Detection | NATIVE (O(V+E)) | DEGRADED (O(n²)) |
| **Q31** | Rolling Aggregation | DEGRADED (UNWIND) | NATIVE (window functions) |
| **Q32** | JSON Schema Validation | DEGRADED | NATIVE (JSONB operators) |
| **Q33** | Latest Value per Space | IMPOSSIBLE | NATIVE (LATERAL JOIN) |
| **Q34** | Materialized Energy | IMPOSSIBLE | NATIVE (mat. views) |

### Writes (QW1-QW8)

| Query | Nom | Description |
|-------|-----|-------------|
| QW1 | Timeseries Append | Ingestion IoT batch |
| QW2 | Metadata Update | Mise à jour tags |
| QW3 | Relation Mutation | Ajout/suppression edges |
| QW4-QW8 | JSONB Writes | Opérations JSONB avancées (P2) |

Voir [queries/catalog.yaml](queries/catalog.yaml) pour les 42 définitions complètes.

---

## Métriques

| Métrique | Description |
|----------|-------------|
| `p50_ms`, `p95_ms` | Latence médiane et 95e percentile |
| `avg_ms`, `min_ms`, `max_ms` | Statistiques latence |
| `memory_peak_mb` | Pic mémoire via cgroups v2 |
| `row_count` | Nombre de lignes retournées |
| `success_rate` | Taux de succès des exécutions |

### Mesure mémoire (cgroups v2)

Le benchmark utilise `memory.peak` de cgroups v2 pour mesurer précisément la consommation mémoire **par query**. Ceci nécessite Linux avec kernel >= 5.10.

**Important** : Pour des mesures per-query précises, le benchmark doit être exécuté avec `sudo` :

```bash
# Métriques mémoire précises (reset memory.peak entre chaque query)
sudo btb-runner benchmark -s data/generated/small-2d -p P1,M1 --ram 32,16,8

# Sans sudo : métriques mémoire en mode "fallback" (moins précis)
btb-runner benchmark -s data/generated/small-2d -p P1,M1 --ram 32,16,8
```

**Pourquoi sudo ?** Les fichiers `memory.peak` dans `/sys/fs/cgroup/` appartiennent à root. Le reset du compteur peak (écriture de "0") nécessite les droits root. Sans ces droits, le benchmark fonctionne mais utilise le peak global du container (moins granulaire).

**Sécurité** : Le code n'exécute aucun subprocess via sudo. L'utilisateur choisit explicitement de lancer le processus Python avec les droits root.

---

## Validation Cross-Paradigme

Le benchmark inclut un système de validation pour garantir l'équivalence sémantique des résultats entre paradigmes.

```bash
# Après un benchmark multi-paradigme
btb-runner validate results.json --reference P1 --verbose

# Générer un rapport HTML pour publication
btb-runner validate results.json --html validation_report.html
```

### Statuts de validation

| Statut | Description |
|--------|-------------|
| **EQUIVALENT** | Résultats identiques (tolérance 1% pour floats) |
| **DEGRADED** | Limitation connue (ex: M1 sans TimescaleDB) |
| **SKIP** | Query impossible pour ce paradigme |
| **MISMATCH** | Différence inattendue à investiguer |

### Règles d'équivalence

- **P1** = référence (ground truth)
- Comparaison row-by-row avec alignement par clés (id, point_id, etc.)
- Hash SHA256 pour vérification intégrité complète
- Tolérance configurable pour les floats

---

## Dataset

### Génération

```bash
# Via menu interactif
python run.py  # → Dataset → Generate

# Via CLI
python -m src.basetype_benchmark.dataset.generator \
  --profile small --duration 2d --seed 42
```

### Profils

| Profil | Bâtiments | Points estimés | Usage |
|--------|-----------|----------------|-------|
| `small` | 1 | ~12k | Tests rapides |
| `medium` | 2-3 | ~50k | Développement |
| `large` | 5-10 | ~200k | Validation |
| `xlarge` | 20+ | ~1M | Publication |

### Timeseries

Le générateur respecte la propriété `frequency` des points :

| Fréquence | Pas | Usage |
|-----------|-----|-------|
| `fast` | 1 min | Températures, CO2 |
| `normal` | 5 min | Puissance |
| `slow` | 15 min | Humidité |
| `energy` | 15 min | Compteurs |

### queries_params.yaml

Le générateur produit un fichier `queries_params.yaml` avec des IDs validés extraits du dataset. Cela garantit que tous les paradigmes utilisent des paramètres identiques.

---

## Scénarios de benchmark

### Prédéfinis

| Scénario | Paradigmes | Queries | RAM | Durée |
|----------|------------|---------|-----|-------|
| `quick` | P1, M1 | Q1, Q6, Q8 | 32-16-8 GB | ~5 min |
| `standard` | Tous | Tous | 64-32-16-8 GB | ~2h |
| `ram_gradient` | M1 | Q1, Q6, Q8 | 64→4 GB | ~30 min |
| `publication` | Tous | Tous | 128→4 GB | ~8h |

### YAML personnalisé

```yaml
# config/scenarios/custom.yaml
name: Custom Scenario
paradigms: [P1, M1, M2]
queries: [Q1, Q7, Q8, Q12]

dataset:
  profile: small

ram_gradient:
  levels_gb: [32, 16, 8]

execution:
  warmup_runs: 0
  timed_runs: 5
  variants: 1
  timeout_seconds: 120
```

---

## CLI Reference

```bash
# Benchmark complet
btb-runner benchmark -s data/generated/small-2d \
  -p P1,P2,M1,M2,O2 --ram 64,32,16,8 --runs 10

# Query unique (debug)
btb-runner run-query Q8 -p M1

# Validation cross-paradigme
btb-runner validate results.json -r P1 --html report.html

# Dry-run (vérification sans exécution)
btb-runner dry-run --matrix

# Liste des scénarios
btb-runner scenarios

# Export manuel
btb-runner export P1 -s data/generated/small-2d -o data/exports/p1
```

---

## Structure du projet

```
baseTypeBenchmark/
├── run.py                    # Menu interactif Rich
├── config/
│   ├── equipment/            # 34 types d'équipements
│   ├── profiles/             # Profils volumétrie (small, medium, large)
│   └── scenarios/            # Scénarios YAML (quick, standard, etc.)
├── queries/
│   ├── catalog.yaml          # Définition des 34 queries
│   ├── p1/, p2/, m1/, m2/, o2/  # Implémentations par paradigme
├── src/basetype_benchmark/
│   ├── dataset/              # Générateur + modèles
│   │   ├── generator.py      # Génère nodes, edges, timeseries, queries_params
│   │   └── models.py         # Dataclasses Node, Edge, TimeseriesPoint
│   ├── exporters/            # Export Parquet → format paradigme
│   └── runner/
│       ├── cli.py            # Commandes Typer (benchmark, validate, etc.)
│       ├── benchmark/        # Orchestration, résultats
│       ├── core/             # Query runner, validation, param sampler
│       │   └── cross_validator.py  # Validation cross-paradigme
│       ├── ram/              # RAM gradient executor
│       └── loaders/          # Chargement par paradigme
├── docker/
│   └── docker-compose.yml    # PostgreSQL, Memgraph, Oxigraph
├── data/
│   ├── generated/            # Datasets Parquet
│   └── results/              # Résultats JSON + validation
└── docs/
    └── SPEC_WORKLOAD_SCENARIOS.md  # Spec pour load testing (futur)
```

---

## Dépendances

```
Python >= 3.11
Docker avec cgroups v2
```

**Packages** : `typer`, `rich`, `pyarrow`, `polars`, `psycopg`, `neo4j`, `httpx`, `pyyaml`

---

## Développement

### Ajouter une query

1. Définir dans `queries/catalog.yaml`
2. Implémenter dans `queries/{paradigm}/Q{N}.{ext}`
3. Ajouter status IMPOSSIBLE/DEGRADED si applicable

### Debug

```bash
# Exécuter une query avec verbose
btb-runner run-query Q8 -p M1 --verbose

# Vérifier la matrice de support
btb-runner dry-run --matrix

# Logs Docker
docker compose -f docker/docker-compose.yml logs -f memgraph
```

---

## Évolutions récentes

### v3.2 (Janvier 2026)

- **Analyse d'efficience critique** : Nouveau système de conclusion basé sur les écarts perceptibles
  - Comparaison P2 vs M1 (focus sur l'architecture "in-memory graph kernel" type SpinalCom)
  - Seuil de 500ms pour distinguer les différences perceptibles vs imperceptibles
  - Exclusion automatique des queries avec 0 résultats (pas significatives)
  - Verdict automatique : SUPPORTED / REFUTED / MIXED
- **Rapport benchmark enrichi** : Section "Critical Findings" avec tableaux comparatifs
- **Config `efficiency_thresholds.yaml`** : Paramètres de conclusion configurables

### v3.1 (Janvier 2026)

- **Équilibrage benchmark** : 8 nouvelles queries (Q27-Q34) pour balance graph/SQL
  - Q27-Q30 : Graph-native (weighted paths, cycles) - avantage M1/M2
  - Q31-Q34 : SQL-native (window functions, LATERAL) - avantage P1/P2
- **Analyse d'efficience** : Rapport automatique avec validation d'hypothèse
  - Seuils d'acceptabilité latence par catégorie d'usage (realtime, analytics, navigation)
  - Ratio ressources (RAM) par paradigme
  - Conclusion automatique sur l'hypothèse "M1/M2 vs P2"
  - Référence scalabilité PostgreSQL (~50k QPS)
- **Enrichissement dataset** : Nouveaux types d'entités et relations
  - Node types : Technician, WorkOrder, Alarm, Schedule, Lease, Contract, Zone
  - Equipment types : 35 types (Lighting, FireSafety, Parking, HVAC, Electrical, BMS)
  - Relations : 26 types incluant EMERGENCY_EXIT, TRIGGERS, FOLLOWS, ASSIGNED_TO
- **Propriétés graph-native** : `is_exit`, `distance`, `critical` pour Q27-Q30
- **Expected answers** : Génération automatique des réponses attendues pour validation
- **Archivage résultats** : Replay et reproductibilité des benchmarks

### v3.0 (Janvier 2026)

- **Validation cross-paradigme** : Comparaison P1 vs autres avec rapport HTML
- **Validation sémantique** : Comparaison avec expected answers générés
- **queries_params.yaml** : Paramètres identiques garantis entre paradigmes
- **Timeseries par fréquence** : Respect de la propriété `frequency` des points
- **O2 (Oxigraph)** : Queries SPARQL corrigées (Q14, Q15, Q23)
- **M1 hybrid** : Chemins de traversée corrigés pour TimeseriesChunk
- **Write workloads** : QW1-QW8 implémentés avec cycle write-read

### Documentation technique

- [queries/catalog.yaml](queries/catalog.yaml) - Définition des 42 queries
- [config/validation_rules.yaml](config/validation_rules.yaml) - Règles DEGRADED/IMPOSSIBLE
- [config/efficiency_thresholds.yaml](config/efficiency_thresholds.yaml) - Seuils d'efficience et conclusion
