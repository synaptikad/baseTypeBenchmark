# Méthodologie

Le benchmark suivra le principe « same data, same queries » : le jeu de données sera identique pour les trois moteurs, et les requêtes poseront les mêmes questions métier.

Chaque campagne comprendra un warmup, puis plusieurs répétitions contrôlées pour mesurer p50 et p95. Les temps d'ingestion seront mesurés séparément des temps de requête.

Deux profils de volumétrie (small et large) permettent d'observer les effets d'échelle en ne faisant varier que la taille du dataset et la charge associée. Les exécutions de référence s'appuient sur une infrastructure contrôlée (VPS) afin de limiter les biais matériels.

La consommation mémoire conteneur (RSS) et l'espace disque des volumes seront relevés. Les versions exactes des images Docker utilisées seront notées dans les résultats pour assurer la traçabilité.

### Séries temporelles et séparation des responsabilités
Le principe retenu distingue clairement la structure (entités, relations, navigation) de l'historique temporel (mesures, agrégations, séries longues). D'un point de vue scientifique, cette séparation permet de comparer chaque paradigme sur son domaine d'optimisation principal et d'éviter les biais liés au volume massif des séries temporelles. Elle reflète également les pratiques industrielles observées où une base time-series coexiste avec un graphe ou un relationnel pour la structure. La décision vise la comparabilité expérimentale et ne constitue pas une disqualification d'un paradigme donné.
