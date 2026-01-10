# Spécification: Scénarios de Charge (Workload Scenarios)

## Contexte

Le benchmark BaseType V3 dispose actuellement de deux modes:

1. **Simple Benchmark** (existant): Exécute chaque query 1x par paradigme par niveau RAM, avec reset entre chaque query. Mesure les métriques isolées par query (p50, p95, avg_ms).

2. **Load Scenarios** (À IMPLÉMENTER): Enchaîne des séquences de queries pour simuler des profils d'usage middleware réels (read-heavy, write-heavy, mixed).

Ce document spécifie le système de Load Scenarios à implémenter.

---

## Objectif

Permettre de tester les paradigmes sous charge réaliste en simulant:
- Un dashboard qui refresh toutes les 5 secondes (lectures répétées)
- Un gateway IoT qui ingère 1000 points/seconde (écritures massives)
- Un middleware qui mélange lectures analytiques et écritures temps réel

---

## Architecture Proposée

### 1. Modèle de Données

**Fichier**: `src/basetype_benchmark/runner/workload/models.py`

```python
from dataclasses import dataclass, field
from typing import Literal
from enum import Enum

class WorkloadProfile(Enum):
    READ_HEAVY = "read_heavy"      # 90% reads, 10% writes
    WRITE_HEAVY = "write_heavy"    # 20% reads, 80% writes
    MIXED = "mixed"                # 50% reads, 50% writes
    ANALYTICS = "analytics"        # 100% reads, complex queries
    INGESTION = "ingestion"        # 100% writes, timeseries append

@dataclass
class QueryStep:
    """Single step in a workload sequence."""
    query_id: str                           # Q1, Q6, QW1, etc.
    repeat: int = 1                         # Number of times to execute
    think_time_ms: int = 0                  # Pause after execution
    batch_size: int | None = None           # For write queries (QW1)
    concurrent: bool = False                # Run in parallel with next step

@dataclass
class WorkloadScenario:
    """Complete workload scenario definition."""
    name: str
    description: str
    profile: WorkloadProfile
    paradigms: list[str]                    # Which paradigms to test
    sequence: list[QueryStep]               # Query sequence
    duration_seconds: int | None = None     # Max duration (None = run sequence once)
    loop: bool = False                      # Repeat sequence until duration

    # Metrics to collect
    collect_throughput: bool = True         # QPS (queries per second)
    collect_latency_distribution: bool = True
    collect_error_rate: bool = True

@dataclass
class WorkloadResult:
    """Results from workload execution."""
    scenario_name: str
    paradigm: str

    # Throughput
    total_queries: int
    total_duration_seconds: float
    qps: float                              # Queries per second

    # Latency distribution
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    latency_max_ms: float

    # Errors
    total_errors: int
    error_rate: float

    # Per-query breakdown
    query_stats: dict[str, QueryStats]      # query_id -> stats
```

### 2. Format YAML des Scénarios

**Emplacement**: `config/workloads/`

```yaml
# config/workloads/dashboard_refresh.yaml
name: "Dashboard Refresh"
description: "Simulates a dashboard refreshing every 5 seconds"
profile: read_heavy

paradigms:
  - P1
  - M1
  - M2

sequence:
  # Initial data load
  - query: Q12    # Full Building Analytics
    repeat: 1

  # Repeated refresh cycle
  - query: Q6     # Hourly Aggregation
    repeat: 10
    think_time_ms: 5000

  - query: Q7     # Drift Top-20
    repeat: 5
    think_time_ms: 5000

  - query: Q13    # Office Hours Comfort
    repeat: 5
    think_time_ms: 5000

duration_seconds: 300   # 5 minutes
loop: true

metrics:
  throughput: true
  latency_distribution: true
  error_rate: true
```

```yaml
# config/workloads/iot_ingestion.yaml
name: "IoT Gateway Ingestion"
description: "Simulates IoT gateway ingesting sensor data"
profile: write_heavy

paradigms:
  - P1
  - P2
  - M1
  - M2

sequence:
  - query: QW1    # Timeseries Append
    repeat: 1000
    batch_size: 100
    think_time_ms: 10

  # Occasional metadata update
  - query: QW2    # Metadata Update
    repeat: 10
    think_time_ms: 100

duration_seconds: 60
loop: true
```

```yaml
# config/workloads/mixed_middleware.yaml
name: "Mixed Middleware"
description: "Realistic middleware with reads and writes"
profile: mixed

paradigms:
  - P1
  - P2
  - M1
  - M2
  - O2

sequence:
  # Write batch
  - query: QW1
    repeat: 50
    batch_size: 10

  # Read queries
  - query: Q1     # Energy Chain
    repeat: 5

  - query: Q8     # Tenant Energy
    repeat: 3

  # More writes
  - query: QW1
    repeat: 50
    batch_size: 10

  # Analytics query
  - query: Q7
    repeat: 1

duration_seconds: 180
loop: true
```

### 3. Exécuteur de Workload

**Fichier**: `src/basetype_benchmark/runner/workload/executor.py`

```python
class WorkloadExecutor:
    """Execute workload scenarios and collect metrics."""

    def __init__(
        self,
        paradigm: str,
        configs: dict,
        isolation: IsolationManager,
    ):
        self.paradigm = paradigm
        self.configs = configs
        self.isolation = isolation

    def run_scenario(
        self,
        scenario: WorkloadScenario,
        on_progress: Callable | None = None,
    ) -> WorkloadResult:
        """Execute a complete workload scenario."""

    def _execute_step(
        self,
        step: QueryStep,
        executor: QueryExecutor,
    ) -> list[StepResult]:
        """Execute a single step (possibly repeated)."""

    def _collect_metrics(
        self,
        results: list[StepResult],
    ) -> WorkloadResult:
        """Aggregate step results into final metrics."""
```

### 4. Commandes CLI

**Fichier**: `src/basetype_benchmark/runner/cli.py`

```bash
# Lister les workloads disponibles
btb-runner workloads

# Exécuter un workload
btb-runner workload run dashboard_refresh \
  --paradigms P1,M1,M2 \
  --source data/generated/small-1w \
  --output results/workload_dashboard.json

# Exécuter avec durée personnalisée
btb-runner workload run iot_ingestion \
  --duration 120 \
  --output results/workload_iot.json

# Comparer les résultats
btb-runner workload compare results/workload_*.json
```

### 5. Intégration run.py

Ajouter dans le menu Benchmark:
```
[cyan]5[/cyan]. Workload test   [dim]Stress testing with query sequences[/dim]
```

Sous-menu:
```
Workload Testing
================

[cyan]1[/cyan]. Dashboard Refresh   [dim]Read-heavy, ~5min[/dim]
[cyan]2[/cyan]. IoT Ingestion       [dim]Write-heavy, ~1min[/dim]
[cyan]3[/cyan]. Mixed Middleware    [dim]50/50 R/W, ~3min[/dim]
[cyan]4[/cyan]. Custom workload

[cyan]b[/cyan]. Back
```

---

## Différences avec Simple Benchmark

| Aspect | Simple Benchmark | Workload Scenarios |
|--------|------------------|-------------------|
| But | Métriques isolées par query | Throughput sous charge |
| Reset | Entre chaque query | Jamais (état persistant) |
| RAM Gradient | Oui | Non (RAM fixe) |
| Queries | 1x chaque | Séquences répétées |
| Métrique principale | p50/p95 par query | QPS global |
| Use case | Comparaison paradigmes | Simulation production |

---

## Fichiers à Créer

| Fichier | Description |
|---------|-------------|
| `src/basetype_benchmark/runner/workload/__init__.py` | Package init |
| `src/basetype_benchmark/runner/workload/models.py` | Dataclasses WorkloadScenario, QueryStep, etc. |
| `src/basetype_benchmark/runner/workload/executor.py` | WorkloadExecutor class |
| `src/basetype_benchmark/runner/workload/loader.py` | YAML loader pour scénarios |
| `config/workloads/dashboard_refresh.yaml` | Profil read-heavy |
| `config/workloads/iot_ingestion.yaml` | Profil write-heavy |
| `config/workloads/mixed_middleware.yaml` | Profil mixed |

---

## Queries Disponibles

### Lectures (Q1-Q26)
- **Graph pure**: Q1-Q5 (traversées)
- **Timeseries pure**: Q6 (agrégations)
- **Hybrid**: Q7-Q13 (graph + TS)
- **JSONB**: Q14-Q19, Q24-Q26

### Écritures (QW1-QW8)
- **QW1**: Timeseries Append (batch insert TS)
- **QW2**: Metadata Update (update tags)
- **QW3**: Relation Mutation (add/remove edges)
- **QW4-QW8**: JSONB writes (P2 specific)

Voir `queries/catalog.yaml` pour la liste complète.

---

## Critères de Succès

1. [ ] YAML loader parse les scénarios correctement
2. [ ] Executor exécute les séquences dans l'ordre
3. [ ] Métriques QPS calculées correctement
4. [ ] Distribution latence (p50/p95/p99) collectée
5. [ ] Gestion des erreurs sans crash
6. [ ] CLI `btb-runner workload` fonctionnel
7. [ ] Intégration run.py avec UX cohérente
8. [ ] 3 profils prédéfinis fonctionnels

---

## Notes d'Implémentation

1. **Pas de RAM gradient**: Les workloads tournent à RAM fixe (paramètre global)
2. **État persistant**: Ne pas reset la DB entre les queries
3. **Think time**: Simuler le temps de réflexion utilisateur avec `time.sleep()`
4. **Batch writes**: QW1 accepte des arrays, utiliser `batch_size` pour contrôler
5. **Durée**: Si `duration_seconds` est défini et `loop: true`, répéter la séquence jusqu'à timeout

---

## Référence: Code Existant

- **Query execution**: `src/basetype_benchmark/runner/core/query_runner.py`
- **Scenario loading**: `src/basetype_benchmark/runner/scenarios.py`
- **RAM gradient**: `src/basetype_benchmark/runner/ram/gradient.py`
- **Results model**: `src/basetype_benchmark/runner/benchmark/results.py`
- **CLI**: `src/basetype_benchmark/runner/cli.py`
- **run.py**: `/home/ubuntu/baseTypeBenchmark/run.py`
