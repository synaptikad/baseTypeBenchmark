# Plan : Fix RAM Benchmark - 2 Protocoles

## Problème identifié

Les résultats RAM du benchmark sont aberrants :
- **P1** : RAM viable 8GB (alors que testé manuellement à 512MB = OK)
- **P2** : RAM viable 8GB (idem)
- **M1** : RAM viable 4GB (alors que M1 stocke TOUT en mémoire)

### Cause racine

Le code `gradient.py:401-408` **skip les niveaux RAM** basé sur `memory.peak` :

```python
if limit_mb < result.baseline_peak_mb * 0.8:
    # Skip niveau - marqué comme "OOM" sans même essayer
```

**Problème** : `memory.peak` pour PostgreSQL = RAM disponible utilisée comme cache (8GB), pas RAM nécessaire.

### Preuves expérimentales

1. **P1 à 512MB** : Query TS lourde (agrégation 26M rows) → **OK**
2. **M1 chargé à 1.3GB** puis réduit à 512MB → **CRASH (exit 137 = OOM)**

C'est le comportement attendu : P1/P2 utilisent le disque, M1 garde tout en RAM.

---

## Solution : 2 Protocoles séparés

### Protocole 1 : Étalonnage RAM Minimum Viable (DESCENDANT)

**But** : Trouver la RAM minimum pour que le paradigme fonctionne.

```
1. Start container à RAM max (128GB / sans limite)
2. Load données UNE FOIS
3. Pour chaque niveau RAM (DESCENDANT: 64GB → 32GB → 16GB → 8GB → 4GB → 2GB → 1GB → 512MB):
    a. docker update --memory <limit>
    b. Test 1 query simple (Q1)
    c. Si OK → continuer descente
    d. Si CRASH/OOM → STOP, restart container

Résultat: RAM_minimum_viable = dernier niveau qui a marché
```

**Résultats attendus** :
- P1 : ~512MB (PostgreSQL disk-based)
- P2 : ~512MB (PostgreSQL disk-based)
- M1 : ~1.5-2GB pour small dataset (tout en RAM)
- M2 : ~512MB pour TS, ~1GB pour graph

### Protocole 2 : Gradient Performance (ASCENDANT depuis minimum)

**But** : Mesurer la courbe performance vs RAM.

```
Prérequis: RAM_minimum_viable connu (protocole 1)

1. Start container à RAM max (128GB)
2. Load données UNE FOIS
3. Pour chaque niveau RAM (ASCENDANT: RAM_minimum_viable → plateau):
    a. docker update --memory <limit>
    b. Run TOUTES les queries (n runs)
    c. Mesurer latences (p50, p95, avg)
    d. Si amélioration < 5% vs niveau précédent → plateau détecté, STOP

Résultat: Courbe latence vs RAM + RAM_plateau
```

---

## Changements de code

### 1. Supprimer le skip baseline (`gradient.py`)

```python
# SUPPRIMER ces lignes (401-408):
if limit_mb < result.baseline_peak_mb * 0.8:
    result.levels.append(GradientLevel(
        limit_mb=limit_mb,
        status="oom",
        error_message="Skipped: limit below baseline",
    ))
    continue
```

### 2. Nouvelle fonction `calibrate_minimum_viable()`

```python
def calibrate_minimum_viable(
    self,
    levels_mb: list[int],  # Descendant: [65536, 32768, 16384, 8192, 4096, 2048, 1024, 512]
    test_query: str = "Q1",
) -> int:
    """Find minimum viable RAM by descending until OOM.

    Returns:
        RAM level in MB that last worked
    """
    last_working = levels_mb[0]  # Start with max

    for limit_mb in levels_mb:
        try:
            self.isolation.set_memory_limit(self.paradigm, limit_mb)
            # Run simple test query
            result = self._run_single_query(test_query)
            if result.success:
                last_working = limit_mb
            else:
                break  # Query failed, stop
        except Exception:
            # Container crashed (OOM)
            self._restart_and_reload()
            break

    return last_working
```

### 3. Détection OOM et restart

```python
def _detect_oom_and_restart(self) -> bool:
    """Check if container crashed and restart if needed.

    Returns:
        True if container was restarted
    """
    if not self.isolation.is_paradigm_running(self.paradigm):
        # Container crashed (likely OOM)
        self.isolation.start_paradigm(self.paradigm)
        return True
    return False
```

### 4. Adapter `run.py` / CLI

```
Benchmark workflow:
1. [Étalonnage] Calibrate minimum viable RAM per paradigm
2. [Gradient] Run performance gradient from minimum to plateau
3. [Report] Generate results with both metrics
```

---

## Stockage de l'étalonnage

L'étalonnage est **lié au dataset**, pas au run. On le sauvegarde dans le dossier du dataset généré.

### Fichier : `data/generated/<dataset>/ram_calibration.json`

```json
{
  "dataset": "medium-1w",
  "calibrated_at": "2026-01-14T17:30:00Z",
  "paradigms": {
    "P1": {
      "ram_minimum_viable_mb": 512,
      "levels_tested": [65536, 32768, 16384, 8192, 4096, 2048, 1024, 512],
      "crash_level_mb": null
    },
    "P2": {
      "ram_minimum_viable_mb": 512,
      "levels_tested": [65536, 32768, 16384, 8192, 4096, 2048, 1024, 512],
      "crash_level_mb": null
    },
    "M1": {
      "ram_minimum_viable_mb": 2048,
      "levels_tested": [65536, 32768, 16384, 8192, 4096, 2048, 1024],
      "crash_level_mb": 1024
    },
    "M2": {
      "ram_minimum_viable_mb": 1024,
      "levels_tested": [65536, 32768, 16384, 8192, 4096, 2048, 1024, 512],
      "crash_level_mb": 512
    }
  }
}
```

### Workflow avec cache étalonnage

```
Avant benchmark:
1. Chercher data/generated/<dataset>/ram_calibration.json
2. Si existe ET paradigmes demandés sont dedans:
   → Utiliser les valeurs cachées (skip étalonnage)
3. Sinon:
   → Exécuter étalonnage
   → Sauvegarder dans ram_calibration.json

Option CLI: --force-calibration pour refaire même si cache existe
```

### Structure dossier dataset

```
data/generated/medium-1w/
├── nodes.parquet
├── edges.parquet
├── timeseries.parquet
├── queries_params.yaml
├── expected_answers/
│   ├── Q1.json
│   └── ...
└── ram_calibration.json    ← NOUVEAU
```

---

## Structure des résultats (run)

```json
{
  "paradigm": "M1",
  "calibration": {
    "ram_minimum_viable_mb": 2048,
    "source": "cached",
    "cache_file": "data/generated/medium-1w/ram_calibration.json"
  },
  "gradient": {
    "ram_plateau_mb": 8192,
    "levels": [
      {"limit_mb": 2048, "avg_latency_ms": 1500, "status": "ok"},
      {"limit_mb": 4096, "avg_latency_ms": 800, "status": "ok"},
      {"limit_mb": 8192, "avg_latency_ms": 650, "status": "plateau"}
    ]
  }
}
```

---

## Ordre d'implémentation

1. **[x]** Investigation et diagnostic (ce document)
2. **[x]** Supprimer skip baseline dans `gradient.py`
3. **[x]** Ajouter `calibrate_minimum_viable()` dans `gradient.py`
4. **[x]** Ajouter détection OOM + restart
5. **[x]** Ajouter lecture/écriture `ram_calibration.json` dans dataset
6. **[x]** Adapter CLI pour 2 phases (calibration + gradient)
7. **[x]** Ajouter option `--force-calibration`
7b. **[x]** Simplifier: min/max au lieu de profils (SMALL/MEDIUM/LARGE/XLARGE)
8. **[ ]** Tester sur small dataset
9. **[ ]** Valider résultats cohérents
