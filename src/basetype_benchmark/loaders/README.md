# Chargeurs de données

Les scripts de ce dossier chargeront le dataset généré dans chacun des moteurs :
- PostgreSQL/TimescaleDB via psql et extensions hypertable.
- Neo4j via import batch et procédures APOC si nécessaire.
- Fuseki via SPARQL Update ou chargement de fichiers.

Les implémentations concrètes seront ajoutées après stabilisation du schéma et du format des données.
