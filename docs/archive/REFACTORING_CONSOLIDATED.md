# Refactoring Consolidé - BaseType Benchmark

> Document unique fusionnant AUDIT, REFACTORING_SPEC, et STACK
> Aligné sur l'objectif papier: "Un graphe in-memory est-il justifié pour les SI bâtimentaires?"

Date de mise à jour: 2025-12-22

---

## 1. Objectif et Contexte

### 1.1 Question de recherche (papier.md)

> Un graphe in-memory est-il justifié pour les SI bâtimentaires ?

**Contribution unique**: Premier benchmark bâtimentaire avec analyse paramétrique coût-mémoire (RAM comme variable expérimentale)

### 1.2 Livrables scientifiques attendus

| Livrable | Description | Section papier |
|----------|-------------|----------------|
| Matrices RAM × Moteur | Latences p95 par profil (small/medium/large) | §4.5 |
| RAM_min par config | Plus petite RAM sans OOM ni dégradation > 20% | §4.5 |
| Courbes latence = f(RAM) | Visualisation du point d'inflexion | §4.5 |
| Ratio efficience | Performance / Go alloué | §4.5 |

### 1.3 Stack technique

```
┌─────────────────────────────────────────────────────────────┐
│ ORCHESTRATION                                               │
│ run.py (4000+ lignes) - smoke_benchmark.py                 │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ DATASET                                                     │
│ generator_v2.py → exporter_v2.py → dataset_manager.py      │
│ Format pivot: Parquet (reproductibilité)                   │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ DOCKER CONTAINERS                                           │
│ btb_timescaledb │ btb_memgraph │ btb_oxigraph              │
│ (P1/P2/M2/O2)   │ (M1/M2)      │ (O1/O2)                   │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ MONITORING                                                  │
│ cgroup v2: memory.current, memory.peak, cpu.stat           │
│ Fallback: docker stats (parsing fragile)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Corrections Effectuées

### 2.1 Daily Chunks - BOS Pattern ✅

**Problème**: Ancien modèle = chunks fixes (50 valeurs) → 520k chunks → M1 loading 3h+

**Solution**: 1 chunk par (point, jour) → ~44k chunks → ~5 min

| Fichier | Modification |
|---------|--------------|
| `exporter_v2.py` | `DailyChunk`, `generate_daily_chunks()` |
| `run.py` | `_load_memgraph_chunks_csv()` → `ArchiveDay` + `HAS_TIMESERIES` |
| `queries/m1/*.cypher` | `TSChunk` → `ArchiveDay` |
| `queries/m2/graph/*.cypher` | Idem |

**Justification papier**: Q13 = stress-test dechunking (DOW filter)

### 2.2 P2 Schema Fix ✅

**Problème**: Colonne `building_id` manquante dans schema JSONB

**Solution**:
```sql
-- Ajouté dans run.py
CREATE TABLE nodes (
    ...
    building_id TEXT,  -- AJOUTÉ
    ...
);
CREATE INDEX idx_nodes_building ON nodes(building_id);
```

### 2.3 Lazy Export/Prune Workflow ✅

**Problème**: Export complet large-1y > 100GB, dépasse capacité disque

**Solution**:
```
1. generate_parquet_only() → Parquet pivot conservé
2. Pour chaque scénario:
   a. export_scenario_only() → export lazy
   b. run benchmark
   c. prune_scenario() → libère disque
3. timeseries.csv partagée entre P1/P2/M2/O2
```

| Fichier | Méthode ajoutée |
|---------|-----------------|
| `dataset_manager.py` | `generate_parquet_only()` |
| `dataset_manager.py` | `export_scenario_only()` |
| `dataset_manager.py` | `prune_scenario()` |
| `smoke_benchmark.py` | Workflow intégré |

### 2.4 Auto-reorder Scenarios ✅

**Problème**: Si M1/O1 avant P2/M2/O2, timeseries.csv prunée trop tôt

**Solution**:
```python
OPTIMAL_ORDER = ["P1", "P2", "M2", "O2", "M1", "O1"]
scenarios = sorted(scenarios, key=lambda s: OPTIMAL_ORDER.index(s))
```

### 2.5 UX Progress Bars ✅

**Problème**: Exports longs sans feedback

**Solution**:
```python
def _progress_bar(current, total, prefix="", start_time=None):
    # [=====>......] 1,234/5,000 (24.7%) ETA: 2.3m
```

### 2.6 Monitoring cgroup v2 ✅

**Problème**: Parsing `docker stats` fragile

**Solution**: Lecture directe cgroup v2
- `memory.current` → RAM actuelle
- `memory.peak` → RAM max (reset avec sudo -n)
- `cpu.stat` → usage_usec

### 2.7 Corrections antérieures ✅

| Bug | Fix | Commit |
|-----|-----|--------|
| StatusSimulator écrase `states` | Renommer en `state_values` | 8726340 |
| AlarmSimulator abstrait | Ajouter `step()` trivial | f37d076 |
| Postgres creds mismatch | Lire `docker/.env` | 42a4fae |
| TimescaleDB timeout | Retry budget 60→120s | 18d4d5c |

---

## 3. Travaux Futurs (Priorités)

### P1: Docker SDK (robustesse monitoring)

**Problème actuel**: Fallback `docker stats` encore utilisé si cgroup indisponible

**Solution cible**:
```python
import docker
client = docker.from_env()
stats = client.containers.get(name).stats(stream=False)
mem_bytes = stats['memory_stats']['usage']  # Pas de parsing string
```

**Fichiers à modifier**:
- `run.py` → `get_container_stats()`
- `src/basetype_benchmark/benchmark/resource_monitor.py`

**Impact papier**: Robustesse, pas bloquant

### P2: Fédération Scalable (temp tables)

**Problème actuel**: `WHERE point_id = ANY(ARRAY[id1, id2, ...])` génère SQL gigantesque

**Solution cible**:
```python
class FederationHandler:
    BATCH_THRESHOLD = 10000

    def execute_federated_query(self, point_ids, ts_query):
        if len(point_ids) < self.BATCH_THRESHOLD:
            return self._execute_with_array(point_ids, ts_query)
        else:
            return self._execute_with_temp_table(point_ids, ts_query)

    def _execute_with_temp_table(self, point_ids, ts_query):
        cursor.execute("CREATE TEMP TABLE _fed_ids (point_id TEXT)")
        cursor.copy_from(buffer, "_fed_ids")
        # JOIN au lieu de IN(...)
```

**Impact papier**: Requis pour large-1y

### P3: Découpage run.py (maintenabilité)

**État actuel**: 4000+ lignes, ~85 fonctions, responsabilités mélangées

**Architecture cible**:
```
src/basetype_benchmark/
├── runners/
│   ├── base.py           # BenchmarkRunner (abstract)
│   ├── postgres.py       # PostgresRunner (P1/P2)
│   ├── memgraph.py       # MemgraphRunner (M1/M2)
│   └── oxigraph.py       # OxigraphRunner (O1/O2)
├── infrastructure/
│   ├── docker_manager.py # docker-py API
│   └── cgroup_monitor.py # Métriques cgroup v2
├── queries/
│   ├── loader.py         # load_query, substitute_params
│   └── federation.py     # FederationHandler
└── workflows/
    ├── dataset.py        # workflow_dataset
    └── benchmark.py      # workflow_benchmark
```

**Impact papier**: Maintenabilité long terme, pas bloquant pour publication

---

## 4. État du Smoke Test

### 4.1 Scénarios

| Scénario | État | Notes |
|----------|------|-------|
| P1 | ✅ OK | p50 = 1.3ms (Q1) |
| P2 | ✅ Corrigé | building_id ajouté |
| M1 | 🔄 Prêt | Regenerate requis |
| M2 | ⏳ Pending | Après P1/P2 |
| O1 | ⏳ Pending | Après M1 |
| O2 | ⏳ Pending | Après P1/P2 |

### 4.2 Métriques Daily Chunks

| Métrique | Ancien | Nouveau |
|----------|--------|---------|
| Chunks M1 | ~520k | ~44k |
| Réduction | - | ~12x |
| Pattern | TSChunk (50 fixe) | ArchiveDay (1/jour) |

---

## 5. Roadmap

### Phase 1: Baseline reproductible (ACTUEL)

```bash
# Sur B3
git pull
rm -rf src/basetype_benchmark/dataset/exports/small-2d_seed42/
python3 scripts/smoke_benchmark.py --profile small-2d \
  --scenarios P1 P2 M2 O2 M1 O1 --ram-levels 8 \
  --n-warmup 1 --n-runs 1 --queries Q1
```

**Critère**: 6 scénarios × Q1 = 6 JSON valides

### Phase 2: Campagne small-2d complète

```bash
python3 scripts/smoke_benchmark.py --profile small-2d \
  --scenarios P1 P2 M1 M2 O1 O2 \
  --ram-levels 8 16 32 \
  --n-warmup 3 --n-runs 10 \
  --queries Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9 Q10 Q11 Q12 Q13
```

**Livrable**: Première matrice RAM × Moteur

### Phase 3: Extension medium-1m

**Prerequis**: Fédération temp tables (P2)

### Phase 4: Large-1y

**Prerequis**:
- ✅ Lazy export/prune
- ⏳ Fédération temp tables
- Serveur 128+ Go RAM

---

## 6. Checklist Publication

### Données

- [ ] Matrices RAM × Moteur (small, medium, large)
- [ ] Courbes latence = f(RAM)
- [ ] RAM_min par configuration
- [ ] Ratio efficience

### Reproductibilité

- [x] Seed=42 fixe
- [x] Docker Compose versionné
- [x] Fingerprint intégrité
- [ ] Scripts publics documentés
- [ ] README exécution

### Code

- [x] Daily chunks (BOS pattern)
- [x] cgroup v2 monitoring
- [x] Lazy export/prune
- [ ] Fédération temp tables (P2)
- [ ] Docker SDK (P1)
- [ ] Découpage run.py (P3)

---

## 7. Commits Récents

```
d1368c7 Auto-reorder scenarios for optimal disk usage
dd23ee3 Lazy export workflow + UX progress + neutrality cleanup
c3d167f Add OVH B3 runbook (diagnostics + Postgres debug)
42a4fae Fix Postgres connection config (read docker/.env)
18d4d5c Increase TimescaleDB connection retry budget
f37d076 Fix AlarmSimulator abstract step implementation
8726340 Fix StatusSimulator state storage
```

---

## 8. Fichiers Obsolètes (à supprimer)

Les documents suivants sont désormais fusionnés dans ce fichier:

| Fichier | Contenu migré vers |
|---------|-------------------|
| `AUDIT_REFACTORING_SPEC.md` | §2 (Corrections), §3 (Priorités) |
| `REFACTORING_SPEC.md` | §3.P3 (Architecture cible) |
| `REFactoring_AUDIT_vs_SPEC_and_STACK.md` | §1.3 (Stack), §3 (Priorités) |
| `SYNTHESIS_SPECS_PAPER.md` | §1 (Objectif papier), §6 (Checklist) |
| `PROGRESS_TRACKER.md` | §2 (Corrections), §4 (État smoke) |

**Action**: Supprimer ces 5 fichiers après validation de ce document.
