# Progress Tracker - Benchmark Refactoring

Date de mise à jour: 2025-12-21

## Référence des specs

| Document | Rôle |
|----------|------|
| `REFACTORING_SPEC.md` | Architecture cible (destination) |
| `AUDIT_REFACTORING_SPEC.md` | Quick wins et priorités (ordre de bataille) |
| `REFactoring_AUDIT_vs_SPEC_and_STACK.md` | Synthèse comparée + stack réelle |
| **Ce document** | Suivi des corrections effectuées |

---

## Corrections effectuées (session 2025-12-21)

### 1. Modèle Daily Chunks (BOS standard)

**Problème identifié:**
- L'ancien modèle utilisait des chunks de taille fixe (50 valeurs par chunk)
- Cela générait ~520k chunks pour small-2d → chargement M1 > 3h
- Non conforme aux patterns industriels BOS

**Solution appliquée:**
- Adoption du pattern "daily archive" (standard BOS)
- 1 chunk par (point, jour) au lieu de 1 chunk par 50 valeurs
- Réduction ~29x du nombre de chunks (520k → ~18k)

**Fichiers modifiés:**

| Fichier | Modification |
|---------|--------------|
| `src/basetype_benchmark/dataset/exporter_v2.py` | Ajout `DailyChunk`, `generate_daily_chunks()`, `generate_daily_aggregates()` |
| `src/basetype_benchmark/dataset/generator_v2.py` | Nettoyé (fonctions déplacées vers exporter) |
| `run.py` | `_load_memgraph_chunks_csv()` utilise `ArchiveDay` + `HAS_TIMESERIES` |
| `queries/m1/Q6_timeseries_hourly_agg.cypher` | `TSChunk` → `ArchiveDay`, `HAS_CHUNK` → `HAS_TIMESERIES` |
| `queries/m1/Q7_drift_top20.cypher` | Idem |
| `queries/m1/Q13_friday_office_comfort.cypher` | Idem |
| `queries/m2/graph/Q6_timeseries_hourly_agg.cypher` | Idem |
| `queries/m2/graph/Q7_drift_top20.cypher` | Idem |
| `queries/m2/graph/Q13_friday_office_comfort.cypher` | Idem |

**Design préservé:**
```
Générateur → Parquet (format neutre, référence académique)
     ↓
Exporteurs → M1/O1: daily chunks (BOS pattern)
           → P1/P2: SQL direct
```

### 2. Fix P2 Schema - building_id manquant

**Problème identifié:**
- Les requêtes P1/P2 partagent les mêmes fichiers SQL
- Le schéma P2 (JSONB) n'avait pas la colonne `building_id`
- Erreur: `column n.building_id does not exist`

**Solution appliquée:**

| Fichier | Modification |
|---------|--------------|
| `run.py` | Schéma P2: ajout `building_id TEXT` |
| `run.py` | Index P2: ajout `idx_nodes_building` |
| `run.py` | INSERT P2: inclut `building_id` |

### 3. Corrections précédentes (sessions antérieures)

| Correction | Fichier | Commit |
|------------|---------|--------|
| StatusSimulator `states` dict | `generator_v2.py` | 8726340 |
| AlarmSimulator abstract step | `generator_v2.py` | f37d076 |
| Postgres connection config | `loaders/postgres/load.py` | 42a4fae |
| TimescaleDB retry budget | `loaders/postgres/load.py` | 18d4d5c |
| B3 Runbook | `docs/B3_RUNBOOK.md` | c3d167f |

---

## État actuel du smoke test

### Scénarios testés

| Scénario | État | Notes |
|----------|------|-------|
| P1 | ✅ OK | p50 = 1.3ms (Q1) |
| P2 | ✅ Corrigé | building_id ajouté |
| M1 | 🔄 En cours | Chargement daily chunks (~44k) |
| O1 | ⏳ Pending | Après M1 |

### Métriques chargement M1

| Métrique | Ancien modèle | Nouveau modèle |
|----------|---------------|----------------|
| Chunks | ~520k | ~44k |
| Vitesse | ~39/s | ~142/s |
| Temps estimé | 3h+ | ~5 min |

---

## Prochaines étapes

### Court terme (smoke test)

- [ ] Terminer chargement M1
- [ ] Valider Q1 sur M1
- [ ] Tester O1
- [ ] Tester M2/O2 (fédération hybride)

### Moyen terme (refactoring selon specs)

| Priorité | Action | Spec source |
|----------|--------|-------------|
| P0 | Baseline stable + reproductibilité | AUDIT §4.1 |
| P1 | Monitoring fiable (cgroup v2 / Docker SDK) | AUDIT §2.1 |
| P2 | Fédération scalable (temp tables) | AUDIT §4 |
| P3 | Découpage run.py (runners/) | REFACTORING §3.1 |

### Améliorations suggérées

1. **Résumé structure dataset** - Afficher après export:
   ```
   === Dataset Structure ===
   Nodes: 52,073 (Building: 10, Floor: 50, Space: 500, Equipment: 5000, Point: 22000)
   Edges: 55,545 (CONTAINS: 12000, HAS_POINT: 22000, LOCATED_IN: 5000, FEEDS: 500)
   Timeseries:
     - Points: 22,000
     - Daily archives (M1/O1): 44,000 (2 days)
     - Samples: ~2.5M
   ```

2. **Validation structure chunks** - Vérifier cohérence après export:
   ```bash
   wc -l exports/small-2d_seed42/m1/chunks.csv
   # Attendu: points × jours + 1 (header)
   ```

---

## Commits récents

```
6c0f022 Adopt daily chunks model (BOS pattern) + fix P2 schema
c3d167f Add OVH B3 runbook (diagnostics + Postgres debug)
42a4fae Fix Postgres connection config (read docker/.env)
18d4d5c Increase TimescaleDB connection retry budget
f37d076 Fix AlarmSimulator abstract step implementation
8726340 Fix StatusSimulator state storage
```
