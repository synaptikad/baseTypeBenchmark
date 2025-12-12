# Méthodologie

Le benchmark suivra le principe « same data, same queries » : le jeu de données sera identique pour les trois moteurs, et les requêtes poseront les mêmes questions métier.

Chaque campagne comprendra un warmup, puis plusieurs répétitions contrôlées pour mesurer p50 et p95. Les temps d'ingestion seront mesurés séparément des temps de requête.

La consommation mémoire conteneur (RSS) et l'espace disque des volumes seront relevés. Les versions exactes des images Docker utilisées seront notées dans les résultats pour assurer la traçabilité.
