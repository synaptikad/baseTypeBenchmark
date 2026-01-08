# Addendum - Option A (Timescale partagé) avec isolation par schémas + extension requêtes en écriture

Ce document complète les documents du dossier `refactor/`.

Objectifs:
- Rendre l'Option A (timeseries partagée) compatible avec P1 et P2 malgré des schémas structurels différents.
- Définir une extension contrôlée du benchmark pour inclure des requêtes en écriture (usage), sans confondre avec le chargement initial (setup).

Contraintes méthodologiques:
- On ne mesure pas le chargement initial (setup). Les métriques concernent l'usage (queries lecture/écriture) sous contrainte de RAM.
- Les statuts `NATIVE/DEGRADED/VERY_DEGRADED/IMPOSSIBLE` restent la source de vérité pour ce qui doit ou non être exécuté par moteur.
- Pas d'invention de sémantique: les IDs, relations, colonnes attendues doivent rester alignés sur `schema/data_model.yaml`, `queries/catalog.yaml` et les fichiers `queries/*`.


## 1) Option A corrigée - Isolation par schémas (P1/P2) avec TS partagée

### 1.1 Problème observé

- P1 et P2 ont des schémas structurels différents.
- Exemple typique: `edges.properties` (JSONB) n'existe pas en P1 mais est nécessaire en P2 pour les requêtes JSONB.
- Garder la même base "structure" entre P1 et P2 en ne faisant que `TRUNCATE` conduit à un échec de création/chargement ou à des erreurs de requêtes.

Conclusion:
- L'Option A ne peut pas signifier "P1 et P2 partagent les mêmes tables structurelles".
- L'Option A doit signifier "P1 et P2 partagent la même table timeseries", mais isolent la structure par schéma (namespace).

### 1.2 Design recommandé

Dans un seul conteneur Timescale/PostgreSQL:
- Un schéma `ts` pour les tables timeseries partagées (hypertable).
- Un schéma `p1` pour les tables structurelles P1.
- Un schéma `p2` pour les tables structurelles P2.

Exemple:
- `ts.timeseries` (commune)
- `p1.nodes`, `p1.edges`, `p1.points`, etc.
- `p2.nodes`, `p2.edges` (avec JSONB), `p2.points`, etc.

Les requêtes P1 et P2 s'exécutent dans la même instance Postgres, mais avec un `search_path` différent:
- P1: `SET search_path TO p1, ts, public;`
- P2: `SET search_path TO p2, ts, public;`

Remarque:
- Alternativement, qualifier explicitement les tables (`p1.edges`, `p2.edges`, `ts.timeseries`). Le `search_path` est plus simple mais doit être appliqué systématiquement à chaque connexion (ou transaction).

Impact performance:
- Négligeable. C'est une résolution de noms (namespace) et non une couche applicative. Les plans, indexes et opérateurs restent identiques.

### 1.3 SQL de base (à appliquer dans le loader Postgres)

Créer les schémas:
```sql
CREATE SCHEMA IF NOT EXISTS ts;
CREATE SCHEMA IF NOT EXISTS p1;
CREATE SCHEMA IF NOT EXISTS p2;
```

Créer la table timeseries dans `ts`:
```sql
CREATE TABLE IF NOT EXISTS ts.timeseries (
  ts          TIMESTAMPTZ NOT NULL,
  point_id    TEXT        NOT NULL,
  value       DOUBLE PRECISION,
  quality     INTEGER,
  PRIMARY KEY (ts, point_id)
);
```

Transformer en hypertable (Timescale):
```sql
SELECT create_hypertable('ts.timeseries', 'ts', if_not_exists => TRUE);
```

Index recommandé (usage):
```sql
CREATE INDEX IF NOT EXISTS idx_timeseries_point_ts
  ON ts.timeseries (point_id, ts DESC);
```

Note:
- Ne pas créer `timeseries` dans `public` si vous choisissez `ts`. Il faut ensuite aligner les loaders/queries pour viser `ts.timeseries` (via `search_path` ou qualification).

### 1.4 Modifications attendues dans le code (V3)

Les chemins ci-dessous sont à adapter si votre arborescence exacte diffère, mais les responsabilités doivent rester les mêmes.

#### A) Loader Postgres: création et gestion des schémas

Fichier: `src/basetype_benchmark/runner/loaders/postgres.py`

Actions:
1) Ajouter une notion de `schema_name` dépendante du paradigme:
   - P1 -> `p1`
   - P2 -> `p2`
   - Pour TS: `ts`

2) `ensure_schema()` doit:
   - créer les schémas (`ts`, `p1`, `p2`)
   - créer `ts.timeseries` et hypertable si absent
   - créer les tables structurelles dans `p1` ou `p2` selon `self.paradigm`

3) `clear_database(keep_timeseries=True)` doit:
   - ne jamais `TRUNCATE ts.timeseries` si `keep_timeseries=True`
   - supprimer/vider uniquement le schéma structurel correspondant:
     Option la plus simple et robuste:
     - `DROP SCHEMA p1 CASCADE; CREATE SCHEMA p1;` (pour P1)
     - `DROP SCHEMA p2 CASCADE; CREATE SCHEMA p2;` (pour P2)
     Puis `ensure_schema()` recrée les tables.
   - Alternative: `TRUNCATE` table par table dans le schéma. Le `DROP SCHEMA ... CASCADE` est plus fiable quand les schémas divergent.

4) Protéger contre la duplication TS:
   - Si vous rechargez TS par erreur, vous aurez des doublons.
   - Mettre un garde-fou:
     - PK sur (ts, point_id) si la génération garantit l'unicité, ou
     - utiliser `COPY` dans une table staging puis dédoublonnage.
   - Le plus simple: faire du "load TS une fois" et imposer un flag `skip_timeseries_load=True` après le premier load.

Acceptance:
- Exécuter P1 puis P2 dans le même conteneur Timescale sans erreur de schéma.
- `ts.timeseries` reste identique entre P1 et P2 (même nombre de lignes, pas de wipe).
- P2 peut charger et utiliser `edges.properties` sans dépendre du schéma P1.

#### B) Runner Postgres: `search_path` par paradigme

Fichier typique: `src/basetype_benchmark/runner/runners/postgres.py`

Action:
- À l'ouverture de connexion (ou avant chaque exécution), appliquer:
  - P1: `SET search_path TO p1, ts, public;`
  - P2: `SET search_path TO p2, ts, public;`
- Cela permet de garder les requêtes SQL P1/P2 identiques (sans préfixer les tables), tout en pointant vers les bonnes tables.

Acceptance:
- Une requête P1 ne "voit" jamais les tables P2.
- Une requête P2 ne "voit" jamais les tables P1.

#### C) Orchestration Docker: ne jamais détruire les volumes TS pendant le run Option A

Problème courant:
- `docker compose down -v` supprime les volumes et donc la TS. Option A devient impossible.

Action:
- Pour Option A, remplacer:
  - `down -v` par `stop` ou `down` sans `-v` pour Timescale.
- Pour Memgraph/Oxigraph, vous pouvez garder `down -v` si vous acceptez de perdre leur état à chaque paradigme, mais attention aux effets caches et au temps.

Acceptance:
- La TS reste sur disque pendant tout le benchmark Option A.
- Le benchmark peut exécuter P1 puis P2 puis M2 puis O2 sans recharger TS.

### 1.5 Note méthodologique (anti-biais)

Le "schéma" est un namespace Postgres:
- Il n'ajoute pas de logique applicative.
- Il n'altère pas les plans d'exécution.
- Le seul biais possible vient des caches (shared_buffers/page cache), pas des schémas.

Recommandation protocole:
- Entre paradigmes, faire:
  - reset RAM (docker update)
  - drop_caches host
  - warmup standard
- Si vous voulez une séparation stricte tout en gardant la TS: redémarrer Timescale sans supprimer le volume (pas de `-v`).


## 2) Extension benchmark - Intégration de requêtes en écriture (usage)

Cette section définit comment ajouter des requêtes d'écriture dans le benchmark pour représenter un contexte middleware smart building/city, sans confondre avec la phase de chargement initial.

### 2.1 Principes

- Les écritures ajoutées sont des workloads d'usage, donc mesurées comme les lectures:
  - latence, débit, RAM peak, CPU, statut.
- La phase de setup (load initial) reste hors métriques.
- Les écritures doivent être reproductibles entre runs:
  - soit elles sont idempotentes
  - soit elles sont isolées par `run_id`/`tenant_id` pour éviter les effets cumulés.

### 2.2 Modèle d'intégration dans le catalog

Ajouter une nouvelle catégorie (si vous souhaitez l'expliciter):
- `write_workload` (ou `mutation`)

Définir dans `queries/catalog.yaml`:
- `id`: QW1, QW2, ... (ou réutiliser Q24+ si vous voulez conserver un espace unique)
- `category`: `write_workload`
- `intention`: exemple "Append sensor readings", "Update point tags"
- `parameters`: identiques au système existant (pas de nouvelle mécanique)
- `paradigm_status` par moteur:
  - P1/P2: généralement `NATIVE`
  - M2/O2: dépend si l'écriture concerne la TS (Timescale) ou la structure (graph/rdf)
  - M1: si TS chunkée, écrire est possible mais peut être `DEGRADED` si la mutation est coûteuse

Important:
- Les statuts `IMPOSSIBLE` doivent être respectés: on n'exécute pas, on enregistre.

### 2.3 Définir 3 familles d'écritures (recommandé)

Pour rester aligné smart building/city et comparable entre moteurs, utiliser 3 familles:

#### Famille W1 - Append timeseries (usage ingestion)
But:
- Simuler l'ingestion continue de mesures (append-only).

Implémentation:
- Cible `ts.timeseries` pour P1/P2/M2/O2.
- Pour M1 (chunks), créer une variante spécifique ou marquer `DEGRADED/IMPOSSIBLE`.

Exemple SQL (Postgres/Timescale):
```sql
INSERT INTO ts.timeseries (ts, point_id, value, quality)
SELECT * FROM UNNEST(
  %(ts_arr)s::timestamptz[],
  %(point_id_arr)s::text[],
  %(value_arr)s::float8[],
  %(quality_arr)s::int[]
);
```

Mesures:
- latence par batch (ms)
- throughput (rows/sec) calculé à partir du nombre de lignes du batch et de la latence

Idempotence:
- Utiliser un intervalle temporel dédié par `run_id` (ex: ts dans une fenêtre future) pour éviter conflit avec données existantes.
- Ou ajouter un champ `run_id` dans une table de benchmark dédiée si vous ne voulez pas toucher la TS principale.

#### Famille W2 - Update metadata (tags/properties)
But:
- Simuler des mises à jour de tags, calibration, classification.

P2 (JSONB) doit être favorisé:
- mise à jour dans `p2.nodes.properties` ou `p2.points.properties`

Exemple P2:
```sql
UPDATE p2.points
SET properties = jsonb_set(properties, '{tag,co2}', to_jsonb(%(new_value)s::text), true)
WHERE point_id = %(point_id)s;
```

P1:
- update sur une colonne normalisée ou table tags join.

Statuts:
- P2: `NATIVE`
- P1: `DEGRADED` possible si la modélisation tags nécessite join.

#### Famille W3 - Update relations (structure)
But:
- Simuler changement de relation FEEDS/SERVES (rare mais réel: reconfiguration, maintenance).

P1:
- insertion/suppression dans `p1.edges`
P2:
- idem, avec properties JSONB en plus si besoin

M2:
- Cypher create/delete relation
O2:
- SPARQL UPDATE (si supporté), sinon `IMPOSSIBLE` (à déclarer explicitement)

### 2.4 Intégration dans l'exécution (runner)

Le runner doit supporter des queries d'écriture de la même manière que les lectures:
- exécution
- mesure temps
- mesure ressources (cgroups memory.peak)
- statut

Différence:
- Les écritures modifient l'état. Donc:
  - soit on exécute sur des tables dédiées au benchmark et on nettoie entre paliers,
  - soit on rend la charge idempotente via `run_id` et on ne nettoie pas.

Recommandation simple:
- Tables dédiées `bench_write_*` (dans `ts` ou dans un schéma `bench`), avec FK optionnelles.
- Nettoyage rapide entre runs (TRUNCATE), mais attention à ne pas inclure le nettoyage dans les métriques.

### 2.5 Reporting

Ajouter dans le JSON results:
- `query_mode`: `read` ou `write`
- Pour write: `rows_written` et `throughput_rows_per_sec` (calculé)
- Conserver `memory_peak` et `cpu_avg`

Acceptance:
- Les requêtes W1-W3 s'exécutent pour P1/P2 sur un dataset small-2d.
- Au moins W1 (append TS) est exécutable pour M2/O2 (Timescale), et correctement marquée pour M1 si chunk.
- Les résultats sont reproduisibles (pas de dérive explosive entre runs).

### 2.6 Où placer les fichiers de requêtes

Créer un dossier dédié:
- `queries/write/` avec:
  - `QW1_timeseries_append.sql`
  - `QW2_update_point_tags_p2.sql`
  - etc.

Ou garder le même dossier `queries/sql/` mais avec un préfixe `QW`.

Important:
- Conserver l'unicité des IDs dans `catalog.yaml`.
- Conserver la même mécanique de résolution de fichiers (pas d'exception ad-hoc).


## 3) Checklist courte pour l'agent

### Option A (schémas)
- [ ] Implémenter `SCHEMA ts/p1/p2`
- [ ] Créer `ts.timeseries` hypertable et index
- [ ] `search_path` par paradigme en runner
- [ ] `clear_database(keep_timeseries=True)` -> drop/recreate schéma structurel seulement
- [ ] Docker: jamais `down -v` sur Timescale en Option A
- [ ] Vérifier P1 -> P2 sans erreur et sans wipe TS

### Écritures (extension)
- [ ] Ajouter 1 query W1 (append TS) dans catalog + fichier SQL
- [ ] Exécuter W1 en usage-only (mesures)
- [ ] Ajouter W2 (update tags) avec focus P2 JSONB
- [ ] Définir statuts par moteur (IMPOSSIBLE explicite si nécessaire)

Fin.
