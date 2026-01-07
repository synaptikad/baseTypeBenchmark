# HOTFIX - Bugs Critiques Runner V3

**Date**: 2026-01-07
**Urgence**: BLOQUANT
**Symptome**: Tous les paradigmes retournent "All OOM" meme avec 128GB RAM et baseline 230MB

## Diagnostic

Le benchmark s'arrete a Q1 sans afficher de resultat et passe directement au niveau RAM suivant:
```
Q1 (1/23)     RAM 65536MB (2/5)
      Warmup (3 runs)...
```

Resultat final incorrect:
```
RAM Viable (smallest without OOM):
  P1: All OOM
  P2: All OOM
  M1: All OOM
  M2: All OOM
  O2: All OOM

RAM Baseline:
  P1: 230 MB   <-- Baseline OK, donc pas de vrai OOM!
```

---

## Bug #1 (BLOQUANT) - RunStatus.OK n'existe pas

### Localisation
`src/basetype_benchmark/runner/ram/gradient.py` ligne 492

### Code fautif
```python
# Ligne 492
if last_status == RunStatus.OK:  # FAUX!
```

### Cause
L'enum `RunStatus` dans `base.py` definit:
```python
class RunStatus(str, Enum):
    SUCCESS = "success"   # <-- C'est SUCCESS, pas OK!
    TIMEOUT = "timeout"
    ERROR = "error"
    OOM = "oom"
```

### Impact
`AttributeError: 'RunStatus' object has no attribute 'OK'` qui crashe silencieusement dans le bloc verbose et remonte comme "error".

### Fix
```python
# gradient.py ligne 492
# AVANT
if last_status == RunStatus.OK:

# APRES
if last_status == RunStatus.SUCCESS:
```

---

## Bug #2 (BLOQUANT) - MultiContainerSampler.stop() retourne dict

### Localisation
`src/basetype_benchmark/runner/ram/gradient.py` lignes 348-368

### Code fautif
```python
# Lignes 348-353
if len(container_ids) == 1:
    container_id = list(container_ids.values())[0]
    sampler = MetricsSampler(container_id)
else:
    sampler = MultiContainerSampler(container_ids)

# Ligne 368
sampling_result = sampler.stop()

# Ligne 373
if sampling_result.oom_detected:  # CRASH pour MultiContainerSampler!
```

### Cause
`MultiContainerSampler.stop()` retourne `dict[str, SamplingResult]`, pas `SamplingResult`:
```python
# sampler.py ligne 282
def stop(self) -> dict[str, SamplingResult]:  # Retourne DICT!
    results = {}
    for name, sampler in self.samplers.items():
        results[name] = sampler.stop()
    return results
```

### Impact
Pour M2 et O2 (paradigmes hybrides avec plusieurs containers), `sampling_result.oom_detected` leve `AttributeError` car un dict n'a pas d'attribut `oom_detected`.

### Fix
```python
# gradient.py lignes 366-368
# AVANT
sampler.start()
query_stats = self._run_queries(queries, sampler)
sampling_result = sampler.stop()

# APRES
sampler.start()
query_stats = self._run_queries(queries, sampler)

# Utiliser la bonne methode selon le type de sampler
if isinstance(sampler, MultiContainerSampler):
    sampling_result = sampler.get_combined_result()
else:
    sampling_result = sampler.stop()
```

**Alternative** (modifier MultiContainerSampler):
```python
# sampler.py - Ajouter alias pour coherence
def stop(self) -> SamplingResult:
    """Stop all samplers and return combined result."""
    return self.get_combined_result()
```

---

## Bug #3 (Mineur) - Message "All OOM" trompeur

### Localisation
`src/basetype_benchmark/runner/benchmark/scenario.py` ligne 465

### Code fautif
```python
if ram is not None:
    console.print(f"  {paradigm}: {ram:,} MB ({ram/1024:.0f} GB)")
else:
    console.print(f"  {paradigm}: [red]All OOM[/red]")  # Trompeur!
```

### Cause
`ram_viable_mb` retourne `None` si aucun level n'a `status == "success"`. Cela inclut les cas "error", pas seulement "oom".

### Impact
L'utilisateur voit "All OOM" alors que le vrai probleme est une erreur de code.

### Fix
```python
# scenario.py lignes 460-465
# AVANT
console.print("\n[cyan]RAM Viable (smallest without OOM):[/cyan]")
for paradigm, ram in summary["ram_viable"].items():
    if ram is not None:
        console.print(f"  {paradigm}: {ram:,} MB ({ram/1024:.0f} GB)")
    else:
        console.print(f"  {paradigm}: [red]All OOM[/red]")

# APRES
console.print("\n[cyan]RAM Viable (smallest without OOM):[/cyan]")
for paradigm, ram in summary["ram_viable"].items():
    if ram is not None:
        console.print(f"  {paradigm}: {ram:,} MB ({ram/1024:.0f} GB)")
    else:
        # Verifier si c'est vraiment OOM ou une erreur
        pr = results.results.get(paradigm)
        if pr and any(l.status == "error" for l in pr.levels):
            console.print(f"  {paradigm}: [red]ERROR (voir logs)[/red]")
        else:
            console.print(f"  {paradigm}: [red]All OOM[/red]")
```

---

## Ordre d'application des fixes

1. **Bug #1** - Fix `RunStatus.OK` -> `RunStatus.SUCCESS` (1 ligne)
2. **Bug #2** - Fix `MultiContainerSampler.stop()` (3-5 lignes)
3. **Bug #3** - Fix message trompeur (optionnel, 5 lignes)

---

## Verification post-fix

Apres application des fixes, relancer:
```bash
make run
# Choisir option 3 (Benchmark)
# Scenario 1 (Quick Test) pour validation rapide
```

Resultat attendu:
```
Q1 (1/23) OK avg=X.Xms rows=Y
Q2 (2/23) OK avg=X.Xms rows=Y
...
RAM Viable (smallest without OOM):
  P1: 8192 MB (8 GB)
  M1: 8192 MB (8 GB)
```

---

## Fichiers a modifier

| Fichier | Lignes | Bug |
|---------|--------|-----|
| `src/basetype_benchmark/runner/ram/gradient.py` | 492 | #1 |
| `src/basetype_benchmark/runner/ram/gradient.py` | 366-368 | #2 |
| `src/basetype_benchmark/runner/benchmark/scenario.py` | 460-465 | #3 |

---

## Diff complet

```diff
diff --git a/src/basetype_benchmark/runner/ram/gradient.py b/src/basetype_benchmark/runner/ram/gradient.py
index abc123..def456 100644
--- a/src/basetype_benchmark/runner/ram/gradient.py
+++ b/src/basetype_benchmark/runner/ram/gradient.py
@@ -363,7 +363,12 @@ class RAMGradientExecutor:
                 )
             sampler.start()
             query_stats = self._run_queries(queries, sampler)
-            sampling_result = sampler.stop()
+
+            # Fix Bug #2: MultiContainerSampler.stop() returns dict
+            if isinstance(sampler, MultiContainerSampler):
+                sampling_result = sampler.get_combined_result()
+            else:
+                sampling_result = sampler.stop()

             duration = time.perf_counter() - start_time

@@ -489,7 +494,8 @@ class RAMGradientExecutor:
             if self.verbose:
                 if query_stats.runs:
                     last_status = query_stats.runs[-1].status
-                    if last_status == RunStatus.OK:
+                    # Fix Bug #1: RunStatus.OK doesn't exist, use SUCCESS
+                    if last_status == RunStatus.SUCCESS:
                         avg_ms = query_stats.avg_ms
                         self._console.print(
                             f"[green]OK[/green] "
```

```diff
diff --git a/src/basetype_benchmark/runner/benchmark/scenario.py b/src/basetype_benchmark/runner/benchmark/scenario.py
index abc123..def456 100644
--- a/src/basetype_benchmark/runner/benchmark/scenario.py
+++ b/src/basetype_benchmark/runner/benchmark/scenario.py
@@ -462,7 +462,12 @@ class BenchmarkOrchestrator:
             if ram is not None:
                 console.print(f"  {paradigm}: {ram:,} MB ({ram/1024:.0f} GB)")
             else:
-                console.print(f"  {paradigm}: [red]All OOM[/red]")
+                # Fix Bug #3: Distinguish OOM from ERROR
+                pr = results.results.get(paradigm)
+                if pr and any(l.status == "error" for l in pr.levels):
+                    console.print(f"  {paradigm}: [red]ERROR (check logs)[/red]")
+                else:
+                    console.print(f"  {paradigm}: [red]All OOM[/red]")

         console.print("\n[cyan]RAM Baseline:[/cyan]")
```
