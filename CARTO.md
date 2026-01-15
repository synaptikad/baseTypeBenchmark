# Cartographie Code - BaseType Benchmark v3

> **Dernière mise à jour**: 2026-01-15 par Claude Opus 4.5
> **Status**: Analyse complète - Document de référence architecture

## Vue d'ensemble

```
Total lignes de code: ~30,000
├── runner/           20,246 lignes (benchmark execution)
├── dataset/           2,681 lignes (data generation)
├── validation/        1,296 lignes (result validation)
└── exporters/         2,077 lignes (format conversion)
```

> **Note sur les métriques**: Le nombre de lignes n'est pas un indicateur de qualité.
> C'est un **warning** quand un fichier est très long (>500 lignes) = probable violation Single Responsibility.

## Contexte Métier

### Objectif du Benchmark
Comparer **4 paradigmes** de bases de données pour un middleware smart building/city (BOS):
- **P1**: PostgreSQL relationnel pur (tables normalisées)
- **P2**: PostgreSQL avec JSONB (semi-structuré) - **GAGNANT PROBABLE**
- **M1**: Memgraph standalone (graphe pur, tout en RAM)
- **M2**: Memgraph + TimescaleDB (hybride graphe + timeseries)

> **O2 (Oxigraph)**: Retiré du benchmark actif. Voir [CONTRIBUTING.md](CONTRIBUTING.md#notes-sur-o2-oxigraph).

### Hypothèse validée
> PostgreSQL JSONB (P2) offre le meilleur compromis performance/flexibilité
> pour les cas d'usage BOS, surpassant Memgraph même sur les traversées graphe
> (profondeur 6-8, degré moyen ~1 dans un bâtiment)

### Utilisateurs
- Équipes techniques internes (choix architecture)
- Publication académique (benchmark reproductible)
- Conseil client (aide à la décision stack)

---

## Modules Dataset & Validation

### dataset/ (2,681 lignes)

| Fichier | Lignes | Rôle | Verdict |
|---------|--------|------|---------|
| generator.py | 2,440 | Génération données synthétiques | Core, OK |
| expected_answers.py | 2,393 | Réponses attendues par query | Core, OK |
| calibration.py | 204 | Cache RAM calibration | Core, NOUVEAU |
| models.py | 42 | Node/Edge dataclasses | OK |

**generator.py** - Structure:
- `EquipmentConfig/ProfileConfig`: Config YAML
- `EquipmentRegistry`: Chargement équipements
- `ProtocolGenerator`: BACnet, Modbus, SNMP...
- `MetadataGenerator`: Métadonnées équipements
- `CapabilitiesGenerator`: Capacités/tags
- `CalibrationGenerator`: Calibration points
- `RangeGenerator`: Plages valeurs
- `DatasetGenerator`: Classe principale (60+ méthodes)

**expected_answers.py** - Structure:
- `ExpectedAnswer`: Dataclass résultat attendu
- `ExpectedAnswerGenerator`: 41 méthodes `_gen_qX()`
  - Chaque query a sa logique de calcul
  - Utilise les index nodes/edges
  - Génère hash pour comparaison

### validation/ (1,296 lignes)

| Fichier | Lignes | Rôle | Verdict |
|---------|--------|------|---------|
| validator.py | 796 | Validation réponses | OK |
| normalizer.py | 797 | Normalisation types | OK |
| expected_store.py | 278 | Chargement expected | OK |
| models.py | 183 | ValidationResult etc | OK |

### exporters/ (2,077 lignes)

| Fichier | Lignes | Rôle | Verdict |
|---------|--------|------|---------|
| o2_extractor.py | 607 | Export RDF/Turtle | **DEPRECATED** (O2 retiré) |
| m1m2_extractor.py | 416 | Export Cypher/CSV | OK |
| base.py | 405 | Classe base | OK |
| p1_extractor.py | 344 | Export SQL P1 | OK |
| p2_extractor.py | 293 | Export SQL P2 | OK |

---

## Résumé Statistiques Runner

| Module | Lignes | Utilisé | Verdict |
|--------|--------|---------|---------|
| cli.py | 3,126 | Partiellement | 17 commandes, ~5 utilisées |
| gradient.py | 1,318 | Oui | Core, mais trop complexe |
| archive.py | 1,112 | Oui | Utile pour replay |
| postgres.py (loader) | 1,061 | Oui | OK |
| semantic_validator.py | 1,036 | Via cli | Complexe |
| cross_validator.py | 970 | Via cli | Complexe |
| memgraph.py (loader) | 922 | Oui | OK |
| scenario.py | 833 | Oui | Core |
| param_sampler.py | 606 | Oui | OK |
| oxigraph.py (loader) | 544 | Oui | **DEPRECATED** (O2 retiré) |
| hybrid.py (runner) | 530 | Oui | OK |
| progress.py | 481 | Oui | UI |
| executor.py (workload) | 465 | Partiellement | ? |
| cgroups.py | 429 | **Oui (via __init__)** | **ESSENTIEL** |
| oxigraph.py (runner) | 428 | Oui | **DEPRECATED** (O2 retiré) |
| isolation.py | 416 | Oui | Core |
| **feedback.py** | **411** | **Non (mais utile)** | **À INTÉGRER** |
| core/query.py | 392 | Oui | OK |
| scenarios.py | 389 | Via cli | OK |
| workload/models.py | 386 | Partiellement | ? |
| postgres.py (runner) | 374 | Oui | OK |
| workload/loader.py | 372 | Partiellement | ? |
| core/catalog.py | 353 | Oui | OK |
| config.py | 349 | Oui | OK |
| memgraph.py (runner) | 345 | Oui | OK |
| results.py | 345 | Oui | OK |
| docker_client.py | 329 | Oui | OK |
| sampler.py | 322 | Oui | OK |
| core/params.py | 297 | Oui | OK |
| runners/base.py | 248 | Oui | OK |
| loaders/base.py | 202 | Oui | OK |

**TOTAL: 20,246 lignes**

---

## Code Mort / À Intégrer

### 1. feedback.py (411 lignes) - À INTÉGRER
```
Status: Non importé mais UTILE
Contenu: Système Rich de feedback (progress bars, dashboard live)
Usage: Pourrait améliorer le feedback de run.py qui est basique

VERDICT: NE PAS SUPPRIMER - À intégrer dans run.py pour meilleure UX
```

### 2. cgroups.py (429 lignes) - ESSENTIEL
```
Status: BIEN UTILISÉ via monitoring/__init__.py
Imports:
  - monitoring/__init__.py: "from .cgroups import ..."
  - Exporté dans __all__

Rôle: Lecture memory.peak via cgroups v2 (métrique RAM précise)
Requis: sudo -E (pour préserver venv) car /sys/fs/cgroup nécessite root

VERDICT: NE PAS SUPPRIMER - C'est le cœur de la mesure mémoire!
```

### 3. Code O2 (Oxigraph) - DEPRECATED → À SUPPRIMER
```
Status: Retiré du benchmark actif, À SUPPRIMER
Fichiers concernés (~1,600 lignes):
  - exporters/o2_extractor.py (607 lignes)
  - runners/oxigraph.py (428 lignes)
  - loaders/oxigraph.py (544 lignes)
  - queries/o2/* (tous les fichiers SPARQL/SQL)
  - config.py: OxigraphConfig, EngineType.O2, ENGINE_PROFILES[O2]
  - runners/__init__.py: imports O2
  - loaders/__init__.py: imports O2
  - hybrid.py: O2HybridRunner
  - docker/docker-compose.yml: service oxigraph
  - tests/test_*.py: références O2

Raison suppression:
  - Exploratoire uniquement, jamais en production
  - Performances non compétitives pour BOS
  - SPARQL trop complexe vs SQL/Cypher
  - ~1,600 lignes de code mort à maintenir

ACTION: Supprimer complètement O2 (pas de backward compat nécessaire)
QUAND: Prochaine session de nettoyage
```

---

## cli.py - Analyse des Commandes

### Commandes CORE (utilisées par run.py)
| Commande | Lignes | Appels run.py | Verdict |
|----------|--------|---------------|---------|
| `benchmark` | 505-795 | L472, L890, L1000, L1199, L1294 | **CORE** |
| `validate` | 1509-2386 | L563 | **CORE** |
| `dry-run` | 97-191 | L614 | **CORE** |
| `run-query` | 403-503 | L946 | **CORE** |
| `workload` | 2423-2563 | L897, L907 | Utilisé |

### Commandes DEPRECATED
| Commande | Lignes | Raison | Action |
|----------|--------|--------|--------|
| `gradient` | 797-895 | Remplacé par `benchmark` | Marquer deprecated |
| `load` | 897-1285 | Intégré dans `benchmark` | Marquer deprecated |
| `generate` | 1367-1430 | Fait par wizard (run.py) | Marquer deprecated |
| `export` | 1432-1507 | Intégré dans `benchmark` | Marquer deprecated |

### Commandes UTILITAIRES (garder)
| Commande | Lignes | Usage |
|----------|--------|-------|
| `status` | 1287-1365 | Debug système |
| `info` | 273-345 | Info query spécifique |
| `profiles` | 347-401 | Liste profils data |
| `workloads` | 2388-2421 | Liste workloads |
| `runs` | 2596-2661 | Archive runs |
| `replay` | 2663-2783 | Replay validation |
| `scenarios` | 2784+ | Liste scénarios |

---

## Problèmes Identifiés

### 1. Duplication TIMESCALE_PARADIGMS (5 occurrences)

```python
# gradient.py:418
needs_restart = self.paradigm in ("P1", "P2", "M2", "O2")

# gradient.py:584
needs_restart = self.paradigm in ("P1", "P2", "M2", "O2")

# scenario.py:451
timescale_paradigms = {"P1", "P2", "M2", "O2"}

# scenario.py:577
uses_timescale = paradigm in ("P1", "P2", "M2", "O2")

# isolation.py:146
timescale_paradigms = {"P1", "P2", "M2", "O2"}
```

**Solution**: Ajouter dans `config.py`:
```python
TIMESCALE_PARADIGMS = frozenset({"P1", "P2", "M2"})  # Sans O2 (deprecated)
```

### 2. gradient.py trop complexe (1,318 lignes, 60+ méthodes)

**Problème**: `RAMGradientExecutor` fait TOUT:
- Calibration RAM
- Exécution gradient
- Chargement queries
- Gestion params
- Mesure baseline
- Détection OOM

**Solution**: Extraire en modules:
```
gradient/
  __init__.py
  executor.py       # RAMGradientExecutor (simplifié)
  calibrator.py     # calibrate_minimum_viable()
  query_loader.py   # _load_query_files(), _find_query_file()
  param_handler.py  # _init_param_sampler(), _get_variant_params()
```

### 3. cli.py trop long (3,126 lignes)

**Problème**: 17 commandes, dont ~5 utilisées régulièrement

**Solution**: Marquer commandes deprecated avec warning

---

## Architecture Technique

### Stockage par paradigme

| Paradigme | Graph Storage | Timeseries Storage | Container(s) |
|-----------|---------------|-------------------|--------------|
| **P1** | CTEs récursifs SQL | `ts.timeseries` (hypertable) | benchmark-timescale |
| **P2** | CTEs + JSONB operators | `ts.timeseries` (partagé) | benchmark-timescale |
| **M1** | Cypher natif | **TimeseriesChunk nodes** | benchmark-memgraph |
| **M2** | Cypher natif | `ts.timeseries` (partagé) | memgraph + timescale |

### Protocole RAM 2-phases

```
Phase 1: CALIBRATION (descente)
─────────────────────────────────
  8GB → 4GB → 2GB → 1GB → 512MB → OOM!
                              └── minimum_viable = 1GB

Phase 2: GRADIENT (montée depuis minimum)
─────────────────────────────────────────
  1GB → 2GB → 4GB → 8GB → 16GB
              └── plateau détecté (< 5% amélioration)
                  └── RAM optimale = 4GB
```

### Exécution queries hybrides (M2)

```
┌──────────────────┐     ┌──────────────────┐
│  Phase 1: Graph  │     │  Phase 2: TS     │
│  (Cypher)        │────▶│  (SQL)           │
└──────────────────┘     └──────────────────┘
        │                         │
        ▼                         ▼
MATCH (p:Point {bid: $bid})    SELECT point_id, VAR_SAMP(value)
RETURN collect(p.id)           FROM ts.timeseries
                               WHERE point_id = ANY(%(ids)s)
        │                         │
        └────────┬────────────────┘
                 ▼
         HybridRunner.execute_hybrid()
```

---

## Flux Principal

```
run.py (wizard)
    │
    ├── btb-runner benchmark --calibration-only
    │       └── cli.py:benchmark()
    │               └── scenario.py:BenchmarkOrchestrator
    │                       ├── _export_paradigm() → exporters/
    │                       ├── _load_data() → loaders/
    │                       └── gradient.py:calibrate_minimum_viable()
    │
    └── btb-runner benchmark (full)
            └── (même flux + run_gradient())
```

---

## TODO Refactoring

### Phase 1: Quick Wins

| Tâche | Fichier(s) | Priorité |
|-------|------------|----------|
| Extraire `TIMESCALE_PARADIGMS` | config.py + 5 fichiers | **HAUTE** |
| Supprimer `_get_query_text()` | gradient.py | Moyenne |
| Marquer commandes deprecated | cli.py | Moyenne |
| **Supprimer code O2** | ~1,600 lignes dans 10+ fichiers | **HAUTE** |

### Phase 2: Refactoring

| Tâche | Lignes impactées | Priorité |
|-------|------------------|----------|
| Extraire QueryLoader | ~200 | Moyenne |
| Extraire ParamHandler | ~150 | Moyenne |
| Simplifier gradient.py | cible: 600 lignes | Moyenne |

### Phase 3: Polish

| Tâche | Description |
|-------|-------------|
| Intégrer feedback.py | Meilleure UX dans run.py |
| Tests unitaires | calibration, validation |

---

## Validation

```bash
# Test import
python -c "from basetype_benchmark.runner import cli_app; print('OK')"

# Test wizard
python run.py

# Test calibration
btb-runner benchmark -s data/generated/medium-1w -p P1 --calibration-only

# Vérifier cgroups fonctionne
sudo -E python -c "from basetype_benchmark.runner.monitoring import cgroups; print('OK')"
```

---

## Pour Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour:
- Règles de développement
- Patterns à suivre
- Constantes à utiliser
- Checklist avant commit

---

*Document de cartographie architecture - BaseType Benchmark v3*
