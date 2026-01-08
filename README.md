# BaseType Benchmark V3

Benchmark academique comparant 5 paradigmes de stockage SGBD pour les systemes d'information batimentaires (middleware smart building).

**Question de recherche** : Un graphe in-memory est-il justifie pour les SI batimentaires ?

**Hypothese** : Les graphes batimentaires sont structurellement simples (degre ~1, profondeur 6-8), donc SQL recursif (CTEs) pourrait suffire.

**Contexte 2025** : Explosion des couts RAM et enjeux energetiques - ce benchmark mesure precisement la consommation memoire de chaque paradigme.

---

## Quick Start

### Installation

```bash
# Cloner et installer
git clone <repo-url>
cd baseTypeBenchmark
pip install -e .

# Verifier l'installation
btb-runner --version
```

### Demarrage Docker (requis)

```bash
# Lancer les conteneurs (TimescaleDB, Memgraph, Oxigraph)
docker compose -f docker/docker-compose.yml up -d

# Verifier le statut
docker compose -f docker/docker-compose.yml ps
```

### Lancer un benchmark

**Option 1 : Menu interactif** (recommande pour debutants)

```bash
python run.py
```

**Option 2 : CLI direct** (utilisateurs avances)

```bash
# Scenario rapide (~10 min)
btb-runner benchmark -s data/generated/small-2d --scenario quick

# Scenario standard (~2h)
btb-runner benchmark -s data/generated/small-2d --scenario standard

# Personnalise
btb-runner benchmark -s data/generated/small-2d -p P1,M1 --ram "32,16,8" --runs 5
```

---

## Paradigmes compares

| ID | Paradigme | Technologie Graph | Timeseries | JSONB |
|----|-----------|-------------------|------------|-------|
| **P1** | PostgreSQL Relational | CTEs recursifs | TimescaleDB | IMPOSSIBLE |
| **P2** | PostgreSQL JSONB | CTEs + JSONB ops | TimescaleDB | NATIVE |
| **M1** | Memgraph Standalone | Cypher natif | Chunks in-memory | DEGRADED |
| **M2** | Memgraph + TimescaleDB | Cypher natif | TimescaleDB (federe) | DEGRADED |
| **O2** | Oxigraph + TimescaleDB | SPARQL RDF | TimescaleDB (federe) | DEGRADED |

### Architecture Option A (partage TimescaleDB)

```
                    ┌─────────────────┐
                    │  TimescaleDB    │  <- Charge UNE SEULE FOIS
                    │  (ts.timeseries)│
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐
    │ P1 (p1.*)   │   │ M2 (Memgraph│   │ O2 (Oxigraph│
    │ P2 (p2.*)   │   │ + ts.*)     │   │ + ts.*)     │
    └─────────────┘   └─────────────┘   └─────────────┘
```

**Avantage** : Pas de biais de mesure du au rechargement des timeseries entre paradigmes.

---

## Scenarios de benchmark

### Scenarios predefinies

| Scenario | Paradigmes | RAM Levels | Runs | Duree estimee |
|----------|------------|------------|------|---------------|
| `quick` | P1, M1 | 32, 16, 8 GB | 3 | ~10 min |
| `standard` | P1, P2, M1, M2, O2 | 128, 64, 32, 16, 8 GB | 10 | ~2h |
| `ram_gradient` | 1 paradigme | 64, 48, 32, 24, 16, 12, 8, 4 GB | 10 | ~30 min |
| `publication` | P1, P2, M1, M2, O2 | 10 niveaux fins | 30 | ~8h |

### Utilisation

```bash
# Scenario predefini
btb-runner benchmark -s data/generated/small-2d --scenario quick

# Scenario YAML personnalise
btb-runner benchmark -s data/generated/small-2d --scenario config/scenarios/custom.yaml

# Parametres individuels
btb-runner benchmark -s data/generated/small-2d \
  -p P1,P2,M1 \
  --ram "64,32,16,8" \
  --runs 10 \
  --variants 3 \
  --cleanup
```

---

## 23 Queries de benchmark

| Categorie | Queries | Description |
|-----------|---------|-------------|
| **Graph-only** | Q1-Q5 | Traversees structurelles (FEEDS, SERVES, CONTAINS) |
| **Timeseries** | Q6 | Agregation horaire |
| **Hybrid** | Q7-Q13 | Selection graph + agregation timeseries |
| **JSONB-specific** | Q14-Q19 | protocol{}, metadata{}, capabilities[], tags[] |
| **Graph-native** | Q20-Q23 | shortestPath, allShortestPaths, siblings, propagation |
| **Write workloads** | QW1-QW3 | Insertion TS, update metadata, mutation relations |

### Matrice de compatibilite

```bash
# Afficher la matrice paradigme/query
btb-runner dry-run --matrix
```

---

## Workflows typiques

### Chercheur academique

```bash
# 1. Generer un dataset reproductible
python -m src.basetype_benchmark.dataset.generator --profile medium --seed 42

# 2. Lancer le benchmark complet
btb-runner benchmark -s data/generated/medium-1w --scenario publication -o results_pub.json

# 3. Valider la reproductibilite
btb-runner golden validate

# 4. Exporter les resultats
# Le fichier results_pub.json contient toutes les metriques
```

### Debug / Developpement

```bash
# Valider les queries sans execution
btb-runner dry-run --all --verbose

# Tester une query specifique
btb-runner run-query Q8 -p M1 --params '{"equipment_id": "eq_123"}'

# Voir les infos d'une query
btb-runner info Q8

# Charger manuellement les donnees
btb-runner load P1 -d data/exports/p1/small-2d --clear
```

### CI/CD / Automatisation

```bash
# Verification rapide
btb-runner benchmark -s data/generated/small-2d --scenario quick -o ci_results.json

# Avec fichier de config
btb-runner benchmark --scenario config/scenarios/ci.yaml
```

---

## Structure du projet

```
baseTypeBenchmark/
├── run.py                    # Menu interactif Rich
├── README.md                 # Ce fichier
│
├── config/
│   ├── equipment/            # 32 types d'equipements
│   ├── profiles/             # Profils volumetrie (small, medium, large)
│   └── scenarios/            # Scenarios YAML predefinies
│
├── data/
│   ├── generated/            # Datasets Parquet generes
│   ├── exports/              # Exports par paradigme
│   └── results/              # Resultats JSON
│
├── queries/
│   ├── catalog.yaml          # Definition des 23 queries
│   ├── golden_answers.yaml   # Reponses attendues (reproductibilite)
│   ├── p1/*.sql              # Implementations P1
│   ├── p2/*.sql              # Implementations P2
│   ├── m1/*.cypher           # Implementations M1
│   ├── m2/                   # Implementations M2 (hybrid)
│   └── o2/                   # Implementations O2 (hybrid)
│
├── docker/
│   └── docker-compose.yml    # TimescaleDB, Memgraph, Oxigraph
│
├── src/basetype_benchmark/
│   ├── dataset/              # Generateur + golden dataset
│   ├── exporters/            # Transformateurs par paradigme
│   └── runner/               # Execution et benchmarking
│       ├── cli.py            # CLI btb-runner
│       ├── benchmark/        # Orchestration
│       ├── loaders/          # Chargement bulk
│       ├── runners/          # Execution queries
│       ├── ram/              # RAM gradient
│       └── monitoring/       # Metriques cgroups v2
│
└── refactor/                 # Documentation technique
```

---

## Mesure RAM (Methodologie)

### Protocole RAM-Gradient

1. **Test avec RAM decroissante** : 128 → 64 → 32 → 16 → 8 GB
2. **Mesure via cgroups v2** : `memory.peak` du kernel (le plus precis)
3. **Detection OOM** : Exit codes Docker, syslog
4. **Reset entre niveaux** : Restart containers, preserve volumes

### Metriques collectees

- **RAM_viable** : Plus petit niveau sans OOM
- **RAM_baseline** : Pic memoire a charge nominale
- **Latences** : p50, p95, p99 par query
- **Success rate** : Taux de reussite par query/niveau

### Exclusions

- **Load time** : Non mesure (n'affecte pas l'usage)
- **Warmup** : 3 runs exclus avant mesure

---

## Commandes CLI (btb-runner)

```bash
# Benchmark
btb-runner benchmark -s <source> [options]    # Lancer un benchmark complet
btb-runner gradient <paradigm> -d <data>      # Test RAM gradient seul

# Validation
btb-runner dry-run [--matrix|--all]           # Valider queries sans execution
btb-runner info <query_id>                    # Infos detaillees d'une query
btb-runner golden validate                    # Valider reproductibilite

# Data
btb-runner generate --profile <name>          # Generer dataset
btb-runner export <paradigm> -s <source>      # Exporter vers paradigme
btb-runner load <paradigm> -d <data>          # Charger dans DB

# Systeme
btb-runner status                             # Etat Docker, datasets, exports
btb-runner profiles                           # Infos profils et engines
```

---

## Formats de sortie

### Resultats JSON

```json
{
  "config": {
    "paradigms": ["P1", "P2", "M1", "M2", "O2"],
    "ram_levels_mb": [131072, 65536, 32768, 16384, 8192],
    "n_runs": 10
  },
  "summary": {
    "ram_viable": {"P1": 8192, "M1": 16384, ...},
    "ram_baseline": {"P1": 245.3, "M1": 412.7, ...}
  },
  "results": {
    "P1": {
      "levels": [
        {"limit_mb": 32768, "status": "success", "actual_peak_mb": 245.3, ...}
      ]
    }
  }
}
```

---

## Dependances

```
Python >= 3.11
Docker avec cgroups v2
```

**Packages Python** :
- `typer`, `rich` : CLI et affichage
- `pyarrow`, `polars` : Manipulation Parquet
- `psycopg`, `neo4j`, `httpx` : Connecteurs DB
- `pyyaml` : Configuration

---

## Reproductibilite

Ce benchmark est concu pour la recherche academique :

1. **Datasets Parquet** : Source immuable avec seed
2. **Golden answers** : Resultats attendus pour validation
3. **Scenarios YAML** : Configuration reproductible
4. **Logs detailles** : Traçabilite complete

```bash
# Valider que les resultats sont corrects
btb-runner golden validate

# Rejouer un scenario exact
btb-runner benchmark --scenario config/scenarios/paper_v1.yaml
```

---

## Documentation supplementaire

- [refactor/00_INDEX.md](refactor/00_INDEX.md) - Index documentation technique
- [refactor/06_ram_gradient_protocol.md](refactor/06_ram_gradient_protocol.md) - Protocole RAM detaille
- [refactor/07_todo_tracker.md](refactor/07_todo_tracker.md) - Etat d'avancement
- [queries/catalog.yaml](queries/catalog.yaml) - Definition des 23 queries

---

## Licence

Projet academique - Usage recherche uniquement.
