# Spécification de Refactoring Post-Audit

## 1. Synthèse de l'Audit
L'analyse approfondie du code (`run.py`, `metrics.py`, `resource_monitor.py`) a mis en évidence une base de code scientifiquement rigoureuse mais souffrant de problèmes de maintenabilité et de fragilité sur les composants d'infrastructure.

**Points critiques identifiés :**
1.  **Fragilité du Monitoring** : Le parsing textuel de `docker stats` est instable.
2.  **Dette Technique `run.py`** : Script monolithique (>4000 lignes) difficile à faire évoluer.
3.  **Scalabilité Hybride** : La méthode de fédération actuelle (injection d'IDs dans SQL) ne passera pas l'échelle sur les gros datasets.

## 2. Actions Prioritaires (Quick Wins)

### 2.1 Migration vers Docker SDK (Fiabilité)
**Cible** : `src/basetype_benchmark/benchmark/metrics.py` et `resource_monitor.py`
**Problème** : La regex `_parse_mem_mb` échoue sur certains formats de sortie Docker (ex: `824.5MiB` vs `824.5 MiB`).
**Solution** :
-   Ajouter `docker` aux dépendances (`requirements.txt`).
-   Remplacer les appels `subprocess` par l'API Python Docker.
-   Accéder directement aux valeurs brutes (bytes) via `container.stats(stream=False)`.

```python
# Exemple d'implémentation cible
import docker
client = docker.from_env()
stats = client.containers.get(container_id).stats(stream=False)
mem_bytes = stats['memory_stats']['usage'] # Plus de parsing de string !
```

## 3. Refactoring Architectural (Maintenabilité)

### 3.1 Découpage de `run.py` (Pattern Strategy)
**Cible** : Création du package `src/basetype_benchmark/runners/`
**Objectif** : Sortir la logique spécifique à chaque moteur du script principal.

**Structure proposée :**
```text
src/basetype_benchmark/runners/
├── __init__.py
├── base.py          # Classe abstraite BenchmarkRunner
├── memgraph.py      # Implémentation pour M1/M2
├── oxigraph.py      # Implémentation pour O1/O2
└── timescale.py     # Implémentation pour P1/P2
```

**Interface `BenchmarkRunner` :**
-   `prepare_environment()` : Démarre les conteneurs, attend le healthcheck.
-   `load_data(dataset_path)` : Gère l'ingestion spécifique au moteur.
-   `execute_query(query_id, params)` : Exécute une requête et retourne les métriques.
-   `cleanup()` : Nettoyage post-benchmark.

Le fichier `run.py` ne servira plus que d'orchestrateur (CLI, chargement de config, instanciation du bon Runner).

## 4. Optimisation de la Fédération (Scalabilité)

### 4.1 Gestion des IDs Massifs (Scénarios M2/O2)
**Problème** : L'injection de milliers d'IDs dans une clause `WHERE point_id = ANY(ARRAY[...])` génère des requêtes SQL gigantesques et inefficaces.
**Solution** : Utilisation de tables temporaires.

**Nouveau flux d'exécution `run_hybrid_query` :**
1.  **Phase Graph** : Exécution Cypher/SPARQL → Récupération de la liste `[id1, id2, ...]`.
2.  **Phase Transition** :
    -   Création table temporaire : `CREATE TEMP TABLE temp_ids (id TEXT) ON COMMIT DROP`.
    -   Insertion rapide (Batch/Copy) des IDs trouvés.
3.  **Phase Timescale** :
    -   Requête SQL modifiée pour faire un `JOIN` sur `temp_ids` au lieu du `IN (...)`.
    -   Bénéfice : Le planificateur de requête PostgreSQL peut optimiser la jointure.

## 5. Impact sur le format de données
L'audit note que le format `TSChunk` a évolué pour supporter le deadband (timestamps explicites).
-   **Action** : Vérifier que les `Runner` (notamment `MemgraphRunner` et `OxigraphRunner`) utilisent bien la nouvelle structure JSON `{"timestamps": [...], "values": [...]}` lors de la création des nœuds/triplets, et non l'ancienne logique `start + idx * freq`.

## 6. Planning Suggéré
1.  **Semaine 1** : Migration Docker SDK (Urgent pour la fiabilité des mesures).
2.  **Semaine 2** : Extraction des classes `Runner` (Nécessaire avant d'ajouter de nouvelles fonctionnalités).
3.  **Semaine 3** : Implémentation des tables temporaires pour la fédération M2/O2.
