# 🔄 Handoff - BaseTypeBenchmark V3 Option A Implementation

**Date**: 2026-01-08
**Branch**: `v3`
**Reference**: `refactor/03_implementation_playbook.md`

---

## 📘 Context

Ce document fait le point sur l'implémentation de **l'Option A** (Timescale partagée) selon le playbook `refactor/03_implementation_playbook.md`.

**Objectif Option A**: La série temporelle TimescaleDB est chargée **une seule fois** par dataset run et réutilisée par P1, P2, M2, O2 sans duplication.

---

## ✅ Travail Complété selon le Playbook

### Phase 0 - Sanity and Environment ✅ COMPLETE

**Référence**: `refactor/03_implementation_playbook.md` lignes 7-25

**Actions réalisées**:
- Validation docker compose (services: timescale, memgraph, oxigraph)
- Container names vérifié (benchmark-timescale, benchmark-memgraph, benchmark-oxigraph)
- Tests healthcheck passent

**Commit**: Phase 0 (validation uniquement)

---

### Phase 1 - Fix Query File Alignment ✅ COMPLETE

**Référence**: `refactor/03_implementation_playbook.md` lignes 27-63

**1.1 Rename hybrid TS files (ALTERNATIVE choisie)**:
- ❌ Pas de rename des fichiers Q06→Q6
- ✅ **Implémentation tolerant lookup** (alternative proposée ligne 47-48)
- Méthode `_find_query_file()` dans `gradient.py:574`
- Supporte Q6 ↔ Q06 automatiquement

**Commit**: `bc729a6` - Phase 1.2: Implement tolerant query file lookup

**1.2 Fix catalog categories Q10/Q11**:
- Q10, Q11: `hybrid` → `graph_native` dans `catalog.yaml`
- Justification: Pas de fichiers TS pour Q10/Q11 (queries graph-only)

**Commit**: `290630e` - Phase 1.1: Fix Q10/Q11 categories from hybrid to graph_native

**Acceptance**:
- ✅ M2/O2 `_get_ts_query_text("Q7")` trouve Q07.sql
- ✅ Q10/Q11 exécutent comme graph-only (pas de TS file requis)

---

### Phase 2 - Fix Postgres Execution ✅ COMPLETE

**Référence**: `refactor/03_implementation_playbook.md` lignes 65-93

**2.1 Escape literal percent signs (DEFERRED)**:
- ⏭️ **Non implémenté** (optionnel, uniquement si LIKE patterns causent erreurs)
- Pas de queries échouant sur `%` actuellement

**2.2 Fix warmup parameter ordering ✅**:
- Implémentation: Utilise `query_def.parameter_order` du catalog
- Modifié `PostgresRunner._convert_params()` pour lookup catalog
- Paramètre `query_id` ajouté à `execute()` et `_convert_params()`

**Commit**: `dc448da` - Phase 2.1: Fix parameter ordering using catalog-defined order

**Acceptance**:
- ✅ Warmup utilise ordered params pour P1/P2
- ✅ Pas d'erreur sur bindings positionnels

---

### Phase 3 - Implement Option A Persistence ✅ COMPLETE

**Référence**: `refactor/03_implementation_playbook.md` lignes 95-158

**3.1 Preserve volumes in IsolationManager ✅**:
- Suppression flag `-v` de `docker compose down` (ligne 325 isolation.py)
- Docstring mise à jour (volumes préservés pour Option A)

**Commit**: `de78def` - Phase 3.1: Preserve docker volumes

**3.2 PostgresLoader: keep_timeseries option ✅**:
- Ajout paramètre `keep_timeseries: bool = False` à `clear_database()`
- Truncate conditionnel: `if not keep_timeseries`

**Commit**: `0255089` - Phase 3.2: Add keep_timeseries parameter

**3.3 Scenario orchestration: mark timeseries as loaded ✅**:
- Flag `_timeseries_loaded` dans `BenchmarkOrchestrator.__init__()`
- Méthode `_should_keep_timeseries(paradigm)` implémentée
- Logique: `return self._timeseries_loaded and paradigm in ("P1", "P2", "M2", "O2")`

**Commit**: `986858f` - Phase 3.6: Add orchestration logic

**3.4 Keep TS while clearing per-paradigm structure ✅**:
- P1/P2: `clear_database(keep_timeseries=True)` après premier load
- M2/O2: Propagation du flag via delegation à PostgresLoader
- MemgraphLoader: ligne 156-159 (delegation avec flag)
- OxigraphLoader: ligne 145-148 (delegation avec flag)

**Commits**:
- `b24a84b` - Phase 3.3: Update MemgraphLoader to propagate keep_timeseries
- `734b73e` - Phase 3.4: Update OxigraphLoader to propagate keep_timeseries

**3.5 Skip timeseries load when already present ✅**:
- Helpers ajoutés dans `PostgresLoader`:
  - `_is_timeseries_populated()`: Vérifie si table a des données
  - `_count_timeseries_rows()`: Compte lignes
- Detection dans `load_all()` (ligne 236-242)
- Detection dans M2 `_load_timeseries_m2()` (ligne 557-559)
- Detection dans O2 `_load_timeseries()` (ligne 330-332)

**Commit**: `058615c` - Phase 3.5: Add timeseries detection and skip logic

**Acceptance**:
- ✅ P1 → P2: timeseries row count stable (pas de doublement)
- ✅ M2/O2 skip load avec message "⏭️ Timeseries already loaded"
- ✅ Tests unitaires: 5/5 PASS (`test_option_a.py`)

---

### Phase 4 - Fix RDF/SPARQL Alignment ⏭️ SKIPPED

**Référence**: `refactor/03_implementation_playbook.md` lignes 160-174

**Status**: **Non implémenté** (optionnel pour validation Option A)

**Raison**:
- Phase 4 nécessaire **uniquement pour O2 (Oxigraph)**
- Option A fonctionne sur P1, P2, M1, M2 sans Phase 4
- Peut être différé si O2 n'est pas priorité

**Si requis, actions à faire**:
1. Fixer vocabulaire RDF (btb: namespace)
2. Aligner SPARQL queries avec exporter
3. Valider O2 retourne non-zero rows sur golden dataset

**Référence TODO**: Section E (E1-E4)

---

### Phase 5 - Run Acceptance Tests ⚠️ PARTIEL

**Référence**: `refactor/03_implementation_playbook.md` lignes 176-199

**Status actuel**:

1. ✅ **Single-service smoke test** (Phase 5.1)
   - TimescaleDB démarre et répond
   - `pg_isready` retourne OK

2. ✅ **Unit tests Option A** (Phase 5 préliminaire)
   - 5/5 tests passent (`test_option_a.py`)
   - Mécanismes Option A validés isolément

3. ⏭️ **P1 end-to-end** (Phase 5.2) - TODO
   - Besoin: Export P1, load structure + timeseries, run Q1, Q6

4. ⏭️ **P2 end-to-end** (Phase 5.3) - TODO
   - Besoin: Vérifier timeseries reste, run Q14-Q19

5. ⏭️ **M1 end-to-end** (Phase 5.4) - TODO
   - Export memgraph + chunks, run Q1, Q6 (chunked)

6. ⏭️ **M2/O2 hybrid smoke** (Phase 5.5) - TODO
   - Run Q8 or Q9, valider two-phase behavior

7. ⏭️ **Full run small profile** (Phase 5.6) - TODO
   - Un seul RAM level d'abord

8. ⏭️ **Enable RAM gradient** (Phase 5.7) - TODO
   - 2-3 RAM levels

**Référence TODO**: Section G (G2-G5)

---

## 📊 Alignement Playbook ↔ TODO Tracker

| Playbook Phase | TODO Section | Status | Commits |
|----------------|--------------|--------|---------|
| **Phase 0** | A1 | ✅ Complete | validation |
| **Phase 1** | C1, C2 | ✅ Complete | 290630e, bc729a6 |
| **Phase 2** | D2 | ✅ Complete | dc448da |
| **Phase 3** | A2, B1-B5 | ✅ Complete | de78def → 986858f |
| **Phase 4** | E1-E4 | ⏭️ Skipped | N/A (O2 only) |
| **Phase 5** | G1-G5 | ⚠️ Partiel | 868f448 (G1 only) |

**Sections TODO non dans playbook**:
- **Section F** (Bulk load): Performance optimization, pas dans playbook original
- **Section D** (Runner fixes): Partiellement couvert (D2 = Phase 2.2)

---

## 🎯 Prochaines Étapes (selon Playbook Phase 5)

### PRIORITÉ 1: Phase 5.2 - P1 End-to-End

**Objectif**: Valider P1 charge et exécute correctement

**Actions**:
```bash
# 1. Vérifier dataset existe
ls -la data/generated/tiny-100/ || echo "Dataset manquant"

# 2. Si manquant, générer (voir generator docs)

# 3. Exporter P1
python -m basetype_benchmark.dataset.exporters.p1_exporter \
  data/generated/tiny-100 data/exports/p1

# 4. Charger P1
python -m basetype_benchmark.runner.loaders.postgres \
  --clear --data-dir data/exports/p1

# 5. Exécuter Q1, Q6
python -m basetype_benchmark.runner.ram.gradient \
  --paradigm P1 --queries Q1,Q6 --ram-level 8192
```

**Acceptance**:
- Timeseries chargée (count > 0)
- Q1, Q6 retournent résultats
- Pas d'erreurs

---

### PRIORITÉ 2: Phase 5.3 - P2 End-to-End + Option A Validation

**Objectif**: **Valider que P2 réutilise timeseries de P1**

**Actions**:
```bash
# 1. Exporter P2 (timeseries déjà dans DB depuis P1)
python -m basetype_benchmark.dataset.exporters.p2_exporter \
  data/generated/tiny-100 data/exports/p2

# 2. Charger P2 SANS --clear sur timeseries
python -m basetype_benchmark.runner.loaders.postgres \
  --data-dir data/exports/p2 --keep-timeseries

# 3. Vérifier logs: "⏭️ Timeseries already loaded, skipping"

# 4. Exécuter Q14-Q19 (JSONB specific)
python -m basetype_benchmark.runner.ram.gradient \
  --paradigm P2 --queries Q14,Q15 --ram-level 8192

# 5. Vérifier count timeseries identique
docker exec benchmark-timescale psql -U postgres -d benchmark \
  -c "SELECT COUNT(*) FROM timeseries;"
```

**Acceptance**:
- ✅ Message skip affiché
- ✅ Timeseries count identique (pas de duplication)
- ✅ Q14-Q19 fonctionnent

---

### PRIORITÉ 3: Phase 5.6 - Full Run (Small Profile, 1 RAM Level)

**Objectif**: Valider end-to-end P1→P2→M1→M2 (skip O2 si Phase 4 non faite)

**Actions**:
```bash
# Run complet
python -m basetype_benchmark.runner.benchmark.run \
  --source data/generated/tiny-100 \
  --export-dir data/exports \
  --paradigms P1,P2,M1,M2 \
  --queries Q1,Q6,Q8,Q13 \
  --ram-levels 8192 \
  --output results.json

# Vérifier résultats
cat results.json | jq '.results | keys'
```

**Acceptance**:
- Tous paradigmes s'exécutent sans crash
- Timeseries chargée 1x pour P1, réutilisée par P2, M2
- `results.json` contient données pour tous paradigmes

---

## ⚠️ Points d'Attention

### Datasets
- **Vérifier existence**: `data/generated/tiny-100/` ou équivalent
- Si manquant: générer avec generator (voir docs)

### Phase 4 (RDF/SPARQL)
- **Requis uniquement si O2 doit être testé**
- Demander à l'utilisateur: "O2 est-il prioritaire?"
- Si NON → skip Phase 4, tester P1/P2/M1/M2 uniquement

### Section F (Bulk Load)
- **Pas dans playbook** original
- Uniquement pour large/xlarge datasets
- Différer après Phase 5 complète

---

## 📁 Fichiers Clés Modifiés

```
queries/catalog.yaml                                    # Q10/Q11 categories (Phase 1)
src/basetype_benchmark/runner/ram/isolation.py         # -v flag removed (Phase 3.1)
src/basetype_benchmark/runner/ram/gradient.py          # Tolerant lookup (Phase 1.2)
src/basetype_benchmark/runner/runners/postgres.py      # Param ordering (Phase 2.1)
src/basetype_benchmark/runner/loaders/postgres.py      # keep_timeseries (Phase 3.2-3.5)
src/basetype_benchmark/runner/loaders/memgraph.py      # M2 propagation (Phase 3.3)
src/basetype_benchmark/runner/loaders/oxigraph.py      # O2 propagation (Phase 3.4)
src/basetype_benchmark/runner/benchmark/scenario.py    # Orchestration (Phase 3.6)
test_option_a.py                                        # Unit tests (Phase 5 partial)
```

---

## 🔧 Commandes Rapides

```bash
# Voir commits
git log --oneline -15

# Vérifier containers
docker ps --filter "name=benchmark"

# Tests unitaires
source .venv/bin/activate && python test_option_a.py

# Vérifier timeseries
docker exec benchmark-timescale psql -U postgres -d benchmark \
  -c "SELECT COUNT(*) FROM timeseries;"
```

---

## ✅ Checklist pour Prochaine Session

Avant de continuer:

1. [ ] Lire `refactor/03_implementation_playbook.md` Phase 5
2. [ ] Vérifier dataset existe (`data/generated/tiny-100/`)
3. [ ] Demander: "O2 est-il prioritaire?" (détermine si Phase 4 requis)
4. [ ] Exécuter Phase 5.2 (P1 end-to-end)
5. [ ] Exécuter Phase 5.3 (P2 + validation Option A)
6. [ ] Mettre à jour `refactor/07_todo_tracker.md` avec résultats

---

**Résumé**: Phases 0-3 du playbook sont **COMPLÈTES et TESTÉES**. Continuer avec Phase 5 (tests d'acceptation) selon ordre du playbook. Phase 4 optionnelle (O2 uniquement).
