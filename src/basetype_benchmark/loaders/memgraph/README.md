# Loader Memgraph

Ce dossier contient les scripts nécessaires pour charger le dataset synthétique dans Memgraph, exécuter les requêtes Cypher Q1 à Q8 et documenter les limites méthodologiques liées aux séries temporelles.

## Démarrage du service

Memgraph est exposé en Bolt sur le port 7688 (relié au port interne 7687) via docker-compose. Un démarrage minimal se fait avec:

```
make mg-up
```

Le conteneur `btb_memgraph` conserve les données dans un volume nommé `memgraph_data`.

## Chargement des données

Le chargement recommandé passe par le script Python `load.py`, qui s'appuie sur le driver Neo4j (compatible Memgraph) et lit les exports JSON ligne par ligne produits par `dataset_gen`.

```
python loaders/memgraph/load.py \
  --uri bolt://localhost:7688 \
  --nodes-file dataset_gen/out/nodes.json \
  --edges-file dataset_gen/out/edges.json \
  --batch-size 1000
```

Caractéristiques du loader:
- Contraintes créées: unicité sur `Node.id`, index sur `Node.type`.
- Traduction des relations `MEASURES` en propriété `quantity` sur les points (pas de nœuds supplémentaires).
- Relations typées créées avec une propriété minimale `source: "synthetic"`.

Une alternative pure Cypher existe dans `load.cypher` pour les cas où les CSV sont montés dans `/import`, mais le passage par Python reste la voie déterministe principale.

## Requêtes Cypher

Les requêtes Q1 à Q8 sont fournies dans `queries.cypher` ainsi que dans `queries/cypher/`. Les paramètres attendus sont rappelés en commentaire dans chaque fichier. Les traversées sont bornées à 10 pour rester comparables aux autres moteurs.

## Séries temporelles (Q6 et Q7)

Memgraph n'est pas un moteur de séries temporelles. Les requêtes Q6 (agrégation horaire) et Q7 (détection de dérive) sont marquées "Not applicable" pour éviter toute simulation biaisée par des nœuds de mesure artificiels. Les comparaisons temporelles doivent être réalisées dans TimescaleDB.

## Approche hybride pour Q8

La requête Q8 renvoie uniquement les identifiants des points de puissance associés aux espaces occupés par un locataire donné. L'agrégation énergétique reste à effectuer dans TimescaleDB en réutilisant ces identifiants, afin de conserver une séparation claire entre graphe structurel et stockage de séries temporelles.
