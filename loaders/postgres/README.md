# Loader PostgreSQL/TimescaleDB

Ce dossier propose deux profils comparables pour PostgreSQL/TimescaleDB afin de mesurer l'impact d'un stockage optionnel des propriétés en JSONB sans changer le modèle relationnel principal.

## Profils disponibles
- **pg_rel** : schéma relationnel strict. Tables `nodes` et `edges` ne contiennent que les colonnes relationnelles. Les contraintes et index sont minimaux mais suffisants pour les requêtes Q1..Q8.
- **pg_jsonb** : schéma relationnel identique avec une colonne `props JSONB` sur `nodes` et `edges`. Les propriétés supplémentaires restent neutres (`kind`, `tags`, `confidence`, `source`) et ne remplacent jamais `type`, `name` ou `rel_type`.

Le fichier `timeseries.sql` est commun aux deux profils et crée l'hypertable utilisée pour Q6 et Q8.

## Règles de comparabilité
- Les exports `nodes.csv` et `edges.csv` produits par `dataset_gen` ne sont pas modifiés. Les quantités logiques (`MEASURES`) sont ajoutées côté loader comme nœuds de type `Quantity` pour préserver les clés étrangères.
- Les requêtes conceptuelles Q1..Q8 sont identiques entre profils, à l'exception d'un filtre JSONB ciblé dans Q4 pour mesurer l'impact d'un prédicat de tags.
- L'indexation reste minimale. Profil JSONB : un seul index GIN sur `nodes.props` pour le filtre de tags; pas d'index sur `edges.props` car ces propriétés ne sont pas interrogées.

## Propriétés injectées (profil JSONB)
- `nodes.props.kind` reprend la colonne `type` pour faciliter les filtres JSONB.
- `nodes.props.tags` contient une liste courte dépendant du type (ex. `haystack:site`, `brick:Equipment`, `haystack:tenant`). Pour les points, des tags `quantity:<quantité>` sont ajoutés à partir des arêtes `MEASURES`.
- `edges.props` contient uniquement `confidence=1.0` et `source="synthetic"` pour documenter l'origine des données sans influencer les parcours.

## Scripts SQL
- `schema_rel.sql` / `schema_jsonb.sql` : création des tables et contraintes.
- `indexes_rel.sql` / `indexes_jsonb.sql` : index structurels, plus l'index GIN pour `pg_jsonb`.
- `load_nodes_rel.sql`, `load_edges_rel.sql` : chargement direct depuis les CSV avec ajout des nœuds de quantité.
- `load_nodes_jsonb.sql`, `load_edges_jsonb.sql` : chargement équivalent avec enrichissement JSONB reproductible.
- `queries_rel.sql`, `queries_jsonb.sql` : requêtes Q1..Q8. Seule Q4 applique un prédicat JSONB sur les tags pour filtrer les points de température.
- `timeseries.sql` : création de l'hypertable commune.

## Utilisation
Les scripts utilisent des variables psql pour ne pas figer les chemins. Exemple minimal :

```bash
PGPROFILE=rel   # ou jsonb
psql $PG_CONN -v nodes_csv=/chemin/nodes.csv -f loaders/postgres/schema_${PGPROFILE}.sql
psql $PG_CONN -v nodes_csv=/chemin/nodes.csv -f loaders/postgres/load_nodes_${PGPROFILE}.sql
psql $PG_CONN -v edges_csv=/chemin/edges.csv -f loaders/postgres/load_edges_${PGPROFILE}.sql
psql $PG_CONN -f loaders/postgres/timeseries.sql
psql $PG_CONN -f loaders/postgres/indexes_${PGPROFILE}.sql
psql $PG_CONN -f loaders/postgres/queries_${PGPROFILE}.sql  # pour mesurer les plans/exécutions
```

`$PG_CONN` correspond aux paramètres de connexion psql classiques (`-h`, `-U`, `-d`).
