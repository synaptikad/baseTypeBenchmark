# Guide de Contribution - BaseType Benchmark

> **Pour Claude Opus 4.5 et développeurs humains**
> Ce document contient les règles et patterns à suivre pour contribuer au projet.

## Contexte Projet

Ce projet est un benchmark comparant **4 paradigmes** de bases de données pour un middleware smart building (BOS):

| Paradigme | Description | Storage |
|-----------|-------------|---------|
| **P1** | PostgreSQL relationnel pur | CTEs récursifs + TimescaleDB |
| **P2** | PostgreSQL avec JSONB | CTEs + JSONB operators + TimescaleDB |
| **M1** | Memgraph standalone | Cypher natif, tout en RAM |
| **M2** | Memgraph + TimescaleDB | Cypher + TimescaleDB hybride |

> **Note**: O2 (Oxigraph + TimescaleDB) a été retiré du benchmark actif. Voir [O2_ARCHIVE.md](docs/O2_ARCHIVE.md) si besoin de le réactiver.

Le benchmark mesure les performances sous contrainte RAM (512MB → 128GB).

---

## Règles de Développement

### Principes Fondamentaux

1. **NO OVER-ENGINEERING** - Solutions simples et directes
2. **DRY** - Pas de duplication, extraire les constantes
3. **YAGNI** - Supprimer le code non utilisé
4. **Type hints** - Toujours typer les fonctions
5. **Dataclasses** - Pour les structures de données

### Conventions de Langue

| Contexte | Langue |
|----------|--------|
| Messages utilisateur (wizard, CLI) | Français |
| Code, variables, fonctions | Anglais |
| Commentaires techniques | Anglais |
| Documentation utilisateur | Français |

---

## Fichiers Clés

| Fichier | Rôle | Quand le modifier |
|---------|------|-------------------|
| `run.py` | Wizard interactif | UX utilisateur |
| `runner/ram/gradient.py` | Calibration + Gradient RAM | Logique benchmark |
| `runner/ram/isolation.py` | Docker containers | Gestion mémoire |
| `runner/benchmark/scenario.py` | Orchestration | Flux benchmark |
| `runner/cli.py` | CLI btb-runner | Nouvelles commandes |
| `runner/config.py` | Constantes partagées | Ajouter constantes |
| `dataset/generator.py` | Génération données | Nouveaux types |
| `dataset/calibration.py` | Cache calibration | Format cache |

---

## Constantes Importantes

```python
# Dans runner/config.py - UTILISER CES CONSTANTES

# Paradigmes utilisant PostgreSQL/TimescaleDB (nécessitent restart pour changer RAM)
TIMESCALE_PARADIGMS = frozenset({"P1", "P2", "M2"})

# Paradigmes utilisant Memgraph
MEMGRAPH_PARADIGMS = frozenset({"M1", "M2"})

# Tous les paradigmes actifs (sans O2)
PARADIGMS = ["P1", "P2", "M1", "M2"]
```

**IMPORTANT**: Ne JAMAIS hardcoder `("P1", "P2", "M2")` ou similaire. Toujours utiliser les constantes de `config.py`.

---

## Patterns à Suivre

### Gestion RAM avec restart conditionnel

```python
from runner.config import TIMESCALE_PARADIGMS

def change_memory(self, limit_mb: int):
    needs_restart = self.paradigm in TIMESCALE_PARADIGMS
    if needs_restart:
        self._restart_with_memory_limit(limit_mb)
    else:
        self.isolation.set_memory_limit(self.paradigm, limit_mb)
```

### Messages wizard (Rich)

```python
# run.py - utiliser Rich pour le feedback
console.print("[bold]Titre principal[/bold]")
console.print("[dim]Description secondaire...[/dim]")
console.print("[green]✓ Succès[/green]")
console.print("[red]✗ Erreur[/red]")
console.print("[yellow]⚠ Warning[/yellow]")
```

### Nouvelle query

1. Ajouter le fichier SQL/Cypher dans `queries/{paradigm}/`
2. Ajouter les paramètres dans `dataset/generator.py` → `_generate_query_params()`
3. Ajouter la réponse attendue dans `dataset/expected_answers.py` → `_gen_qX()`
4. Tester avec `btb-runner run-query QX -p P1`

### Nouveau type d'entité

1. Ajouter dans `dataset/generator.py`:
   - Génération dans `_generate_XXX()`
   - Export dans nodes/edges
2. Ajouter dans chaque exporter (`exporters/*.py`):
   - Mapping vers format cible
3. Mettre à jour les queries concernées

---

## Commandes Utiles

### Développement

```bash
# Test import rapide
python -c "from basetype_benchmark.runner import cli_app; print('OK')"

# Lancer wizard
python run.py

# Test calibration seule
btb-runner benchmark -s data/generated/medium-1w -p P1 --calibration-only --calibration-max 2048 --calibration-min 512

# Debug une query
btb-runner run-query Q7 -p P1 -s data/generated/medium-1w

# Dry-run (affiche matrice queries)
btb-runner dry-run -s data/generated/medium-1w
```

### Vérification

```bash
# Compter lignes de code
wc -l src/basetype_benchmark/runner/**/*.py | tail -1

# Vérifier imports
python -c "from basetype_benchmark.runner import cli"

# Lancer tests
pytest tests/ -v
```

---

## Checklist Avant Commit

```
[ ] Code compile sans erreur
[ ] python -c "from basetype_benchmark.runner import cli" → OK
[ ] Wizard démarre: python run.py
[ ] Pas de duplication de constantes (TIMESCALE_PARADIGMS, etc.)
[ ] Type hints sur les nouvelles fonctions
[ ] Messages utilisateur en français
[ ] Pas de régression sur benchmark existant
```

---

## Architecture Mémoire (cgroups)

**ATTENTION**: Le fichier `runner/monitoring/cgroups.py` est **ESSENTIEL**.

- Lit `memory.peak` via cgroups v2
- Nécessite `sudo -E` pour préserver le venv
- Ne JAMAIS supprimer ce fichier

```bash
# Exécution avec droits cgroups
sudo -E python run.py
```

---

## Tâches de Refactoring en Cours

Voir [CARTO.md](CARTO.md) pour la liste complète des tâches. Résumé:

### Phase 1: Quick Wins
- [x] GARDER feedback.py (pour intégration future UX)
- [x] GARDER cgroups.py (ESSENTIEL pour memory.peak)
- [ ] Extraire `TIMESCALE_PARADIGMS` → config.py (5 occurrences)
- [ ] Supprimer `_get_query_text()` déprécié dans gradient.py
- [ ] Marquer commandes CLI deprecated

### Phase 2: Refactoring gradient.py
- [ ] Extraire QueryLoader classe (~200 lignes)
- [ ] Extraire ParamHandler classe (~150 lignes)
- [ ] Simplifier RAMGradientExecutor

### Phase 3: Nettoyage CLI
- [ ] Marquer commandes dépréciées (gradient, load, generate, export)
- [ ] Documenter commandes core

---

## Notes sur O2 (Oxigraph)

Le paradigme O2 (Oxigraph + TimescaleDB, RDF/SPARQL) a été **retiré du benchmark actif** car:
- Exploratoire uniquement
- Performances non compétitives pour le cas d'usage BOS
- Complexité SPARQL vs SQL/Cypher

Le code reste présent pour référence mais n'est plus maintenu activement:
- `exporters/o2_extractor.py`
- `runners/oxigraph.py`
- `loaders/oxigraph.py`
- `queries/O2/`

Pour réactiver O2, ajouter `"O2"` dans `PARADIGMS` et `TIMESCALE_PARADIGMS` dans `config.py`.

---

*Document de contribution pour BaseType Benchmark v3*
