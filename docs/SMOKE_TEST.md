# Smoke test (instance réduite)

Objectif : valider rapidement que la chaîne end-to-end (dataset V2 → containers → ingestion → exécution Q → métriques) fonctionne sur une petite instance Linux avant de lancer une campagne complète.

## 1) Pré-requis

- Linux (cgroup v2 recommandé)
- Docker + Docker Compose
- Accès réseau sortant si vous utilisez HuggingFace (optionnel)

## 2) Diagnostic environnement (métriques)

Lance un diagnostic non-invasif et écrit un JSON de sortie.

```bash
python scripts/diagnose_env.py \
  --containers btb_timescaledb btb_memgraph btb_oxigraph \
  --out benchmark_results/diagnostics.json
```

Points à vérifier dans la sortie :
- `cgroup v2: true`
- Pour chaque container : `cgroup_path` résolu
- `memory.peak reset_ok=true` si votre kernel autorise le reset (sinon prévoir fallback)

## 3) Smoke benchmark non-interactif

Par défaut :
- profil `small-2d`
- scénarios `P1 P2 M1 M2 O1 O2`
- RAM `8 16`
- requêtes `Q1 Q6 Q8` (inclut l’hybride)
- protocole réduit : `--n-warmup 1 --n-runs 3`

```bash
python scripts/smoke_benchmark.py \
  --profile small-2d \
  --ram-levels 8 16 \
  --n-warmup 1 \
  --n-runs 3
```

Dataset :
- `--dataset-source auto` (défaut) : utilise le dataset existant sinon tente HuggingFace sinon génère localement.
- `--dataset-source hf` : force HuggingFace.
- `--dataset-source generate` : force génération locale.

Résultats :
- écrits dans `benchmark_results/<timestamp>_smoke_.../`
- un fichier par couple `(scenario, ram)` + un `smoke_results.json` agrégé.
