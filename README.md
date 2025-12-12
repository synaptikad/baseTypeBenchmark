# Base Type Benchmark

## Objectif du projet
Ce dépôt prépare un banc de test reproductible pour comparer trois paradigmes de gestion de données autour d'un même jeu de données bâtimentaire : PostgreSQL + TimescaleDB, un graphe de propriétés (Neo4j) et un triple store RDF/JSON-LD (Apache Jena Fuseki). L'ambition est de mesurer de façon méthodique l'impact du modèle de données et des moteurs pour des cas d'usage mêlant graphes bornés et séries temporelles.

## Hypothèse testée
Pour des traversées bornées (≤ 10 sauts) combinées à une composante importante de séries temporelles, PostgreSQL/TimescaleDB devrait offrir un meilleur compromis coût total de possession et empreinte mémoire tout en restant compétitif en performance face aux moteurs graphe ou RDF.

## Principes généraux
- Mêmes données, mêmes questions, mêmes métriques entre les moteurs
- Données générées avec un seed explicite et des modes de volumétrie comparables (laptop vs server)
- Scripts reproductibles, sans configuration manuelle cachée
- Résultats versionnés et documentés

## Quickstart (bientôt)
1. Copier le fichier `.env.example` vers `.env` et ajuster les secrets.
2. Lancer les services avec `make up` puis vérifier l'état avec `make ps`.
3. Générer les données (`make gen`), charger (`make load`) puis lancer le benchmark (`make bench`).
4. Récupérer les résultats dans `results/` et `out/` (à créer lors de l'exécution).

Les étapes 3 et 4 sont des placeholders et seront implémentées dans les prochaines itérations.

## Licence et contributions
Le projet est sous licence MIT (voir LICENSE). Les contributions sont bienvenues dès que la méthodologie et les scripts seront stabilisés. Merci d'ouvrir des issues pour proposer des améliorations ou signaler des problèmes.
