# Loader Oxigraph

Ce dossier décrit le chargement du graphe RDF/JSON-LD dans Oxigraph et les requêtes SPARQL associées au benchmark.

## Démarrage du service

Oxigraph est exposé sur le port 7878 via docker-compose. Un démarrage minimal se fait avec:

```
docker compose up -d oxigraph
```

Le conteneur `btb_oxigraph` conserve ses données dans le volume `oxigraph_data`. Le point d'entrée HTTP `/sparql` accepte les requêtes SPARQL 1.1, et `/store` implémente le protocole Graph Store pour les importations RDF.

## Import JSON-LD

Le chargement recommandé passe par le fichier `dataset_gen/out/graph.jsonld` généré par le module `dataset_gen`. Les identifiants et types sont matérialisés par des IRIs stables, sans enrichissement sémantique supplémentaire.

```
python loaders/oxigraph/load.py \
  --endpoint http://localhost:7878 \
  --jsonld-file dataset_gen/out/graph.jsonld
```

Caractéristiques du loader:
- Nettoyage optionnel du graphe par défaut avant chargement (`--skip-clear` pour le désactiver).
- Chargement direct du JSON-LD via Graph Store, sans inférence ni ontologie additionnelle.
- Mesure du temps d'ingestion et vérification du nombre total de triplets via une requête SPARQL `COUNT`.

## Séries temporelles

Les requêtes Q6 (agrégation horaire) et Q7 (détection de dérive) sont notées « Not applicable » dans le dossier `queries/sparql/` et doivent être exécutées dans TimescaleDB. Oxigraph est réservé aux parcours structurels bornés (≤ 10 relations) et ne stocke pas de séries temporelles.

## Rôle structurel du RDF

L'export JSON-LD fournit une vue RDF du même graphe que les autres moteurs du benchmark. Il permet de mesurer le coût structurel du modèle (triplets générés, profondeur des parcours) et l'expressivité de SPARQL sur des chaînes bornées, sans mobiliser d'ontologie experte ni d'inférence.
