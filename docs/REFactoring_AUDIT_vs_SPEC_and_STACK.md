# Refactoring: AUDIT vs SPEC + Stack Exploration

Date: 2025-12-21

## Contexte

Deux documents de refactor coexistent :

- `docs/REFACTORING_SPEC.md` (vision large / architecture cible)
- `docs/AUDIT_REFACTORING_SPEC.md` (post-audit / quick wins + priorités)

Ce document sert de **synthèse opérationnelle** :

1. comparer les deux specs (convergences + divergences)
2. documenter la **stack réelle** (code + docker + données + métriques)
3. lister les **recommandations** et un ordre d’exécution pragmatique

---

## 1) Comparaison des specs

### 1.1 Convergences (accord)

Les deux docs convergent sur 3 points structurants :

- **Monitoring** : le parsing CLI de `docker stats` est fragile → migration vers des mesures plus robustes.
- **Monolithe `run.py`** : trop de responsabilités dans un fichier unique → extraction (runners / infra / queries / workflows).
- **Hybride M2/O2** : injection d’IDs massifs dans SQL (`ANY(ARRAY[...])`) ne scale pas → tables temporaires + `JOIN`.

### 1.2 Divergences (accent / stratégie)

- `REFACTORING_SPEC.md` propose une **refonte modulaire complète** (nouveaux packages `cli/`, `runners/`, `infrastructure/`, `queries/`, `workflows/`, `config/`).
- `AUDIT_REFACTORING_SPEC.md` insiste sur des **quick wins** :
  - Docker SDK (fiabilité immédiate)
  - pattern Strategy / Runner pour sortir du monolithe
  - fédération scalable via temp tables
  - vérification des structures de données (ex: `TSChunk`/timestamps explicites)

### 1.3 Synthèse: comment les lire ensemble

- `AUDIT_REFACTORING_SPEC.md` = **ordre de bataille** (ce qui doit être fait en premier pour fiabiliser l’expérimental).
- `REFACTORING_SPEC.md` = **destination** (où l’on veut aller pour rendre le code maintenable).

---

## 2) Stack exploration (réalité du repo)

### 2.1 Noyau d’orchestration

- `run.py` : orchestrateur principal (workflow interactif + exécution benchmarks).
  - Démarre/stoppe les conteneurs via `docker compose`.
  - Déclenche ingestion / exécution requêtes / collecte métriques.
  - Contient encore beaucoup de logique “infra + runners + queries”.

### 2.2 Services Docker (Compose)

- `docker/docker-compose.yml` définit 3 services :
  - `timescaledb` → container `btb_timescaledb` (PostgreSQL + Timescale)
  - `memgraph` → container `btb_memgraph`
  - `oxigraph` → container `btb_oxigraph`

Points importants :

- `docker/docker-compose.yml` référence un `env_file: .env`.
  - Sur serveur, on copie typiquement `config/benchmark.env` vers `docker/.env`.
- `MEMORY_LIMIT` est injecté au runtime (`mem_limit`, `memswap_limit`).

### 2.3 Scénarios benchmark

Scénarios (tel que décrit dans README / docs) :

- P1 / P2 : TimescaleDB (relational vs JSONB)
- M1 : Memgraph avec timeseries “chunks” en base graphe
- M2 : Memgraph (structure) + TimescaleDB (timeseries)
- O1 : Oxigraph avec timeseries “chunks” RDF
- O2 : Oxigraph (structure) + TimescaleDB (timeseries)

### 2.4 Requêtes / workloads

- `queries/` contient les requêtes pour chaque paradigme:
  - `queries/p1_p2/*.sql`
  - `queries/m1/*.cypher`
  - `queries/o1/*.sparql`
  - plus des sous-dossiers `m2/` / `o2/` (graph + ts)

### 2.5 Données / génération / exports

- Génération v2: `src/basetype_benchmark/dataset/generator_v2.py`
- Exports v2: `src/basetype_benchmark/dataset/exporter_v2.py`
- Orchestration dataset: `src/basetype_benchmark/dataset/dataset_manager.py`

Les exports se retrouvent typiquement dans :

- `src/basetype_benchmark/dataset/exports/<profile>_seed<seed>/...`

### 2.6 Métriques & instrumentation

- Objectif méthodologique: collecter latences (p50/p95) + RAM/CPU + (si possible) I/O.
- Le repo utilise désormais 2 sources possibles :
  - cgroup v2 (Linux) : `memory.current`, `memory.peak`, `cpu.stat`, etc.
  - fallback “docker stats” (moins robuste) quand cgroup indisponible.

**Point critique validé sur OVH B3** :
- cgroup v2 est actif.
- `memory.peak` est resettable mais nécessite souvent des droits root.
- Le code a été adapté pour un fallback `sudo -n` (sans prompt), ce qui permet de rester en user pour le benchmark.

---

## 3) Constats issus de l’exécution B3 (baseline tooling)

### 3.1 Validations obtenues

- Docker fonctionne (daemon OK, user dans groupe docker).
- cgroup v2 OK.
- reset `memory.peak` OK via fallback `sudo -n`.
- génération locale `small-2d_seed42` OK (export ~10GB) lorsque HuggingFace ne contient pas les datasets.

### 3.2 Problèmes rencontrés (et correctifs appliqués)

1) Simulation dataset
- Bug: `StatusSimulator` écrasait le dict `PointSimulator.states` → crash lors de la génération.
- Fix: conserver `states` comme dict et renommer la liste de valeurs en `state_values`.

2) Simulation dataset
- Bug: `AlarmSimulator` était abstrait (pas de `step()`), Python refusait de l’instancier.
- Fix: ajout d’un `step()` trivial (la logique event-driven reste dans `simulate()`).

3) Connexion TimescaleDB
- Symptomatique: “not ready” puis, après patch, erreur non-transiente sur `host=localhost user=benchmark db=benchmark`.
- Cause probable: mismatch entre creds Compose (`docker/.env`) et ceux utilisés côté Python.
- Fix partiel: le loader Postgres lit désormais `docker/.env` si `POSTGRES_*` ne sont pas exportés.

### 3.3 Ce qu’il reste à trancher côté PostgreSQL

Si la connexion échoue encore, il faut déterminer :

- `docker/.env` est-il présent et contient-il les bonnes valeurs ?
- le conteneur a-t-il réellement reçu ces envs ? (`docker inspect`)
- un volume persistant a-t-il initialisé un cluster avec d’autres identifiants ? (nécessite éventuellement `docker compose down -v` pour un test)

Voir `docs/B3_RUNBOOK.md` pour la procédure pas-à-pas.

---

## 4) Recommandations de refactor (ordre pragmatique)

### 4.1 Priorité 0: baseline & reproductibilité

- Stabiliser l’environnement: scripts de diagnostic + smoke test.
- Logger versions (Docker, kernel, images) + paramètres (RAM level, warmup/runs).

### 4.2 Priorité 1: Monitoring fiable

- Cgroup v2 comme source principale (memory.current/peak, cpu.stat).
- Fallback Docker SDK plutôt que parsing CLI quand cgroup indisponible.
- Éviter les manipulations root interactives : `sudo -n` ou fallback calculé (max(memory.current)).

### 4.3 Priorité 2: Hybride scalable

- Remplacer `ANY(ARRAY[...])` par :
  - temp table `temp_ids`
  - insert batch/copy
  - `JOIN` côté SQL

### 4.4 Priorité 3: Découpage de `run.py`

- Extraire “runners” (Strategy) : PostgresRunner / MemgraphRunner / OxigraphRunner.
- Extraire “queries” : loader + substitution + variantes + fédération.
- Extraire “infrastructure” : docker start/stop/wait health + cgroup monitor.

---

## 5) Livrables recommandés (docs)

- `docs/B3_RUNBOOK.md` : runbook d’exécution OVH B3 (diagnostics + debug Postgres)
- (ce document) `docs/REFactoring_AUDIT_vs_SPEC_and_STACK.md` : comparaison specs + stack map

---

## 6) Next steps (concrets)

1. Résoudre définitivement la connexion Postgres (env/volumes) sur B3.
2. Relancer smoke P1 (Q1) → puis P2 → puis M1 → puis O1.
3. Étendre smoke à M2/O2 (valider fédération hybride).
4. Une fois le baseline stable: lancer campagne RAM gradient et figer un “baseline revision”.
