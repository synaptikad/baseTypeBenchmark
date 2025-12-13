# Méthodologie

## Principes fondamentaux

Le benchmark suit le principe **same data, same questions, same metrics** : le jeu de données est identique pour les trois moteurs, les requêtes posent les mêmes questions métier, et les métriques sont communes.

## Protocole expérimental

Chaque campagne comprend :

1. Vérification de la disponibilité des services via leur healthcheck Docker
2. Ingestion des données (mesurée séparément)
3. Warmup systématique (N répétitions) pour évacuer les effets de cache froid
4. Exécution des requêtes (N répétitions) avec chronométrage individuel
5. Collecte des métriques système pendant l'exécution
6. Export des résultats structurés

## Métriques collectées

### Performance

| Métrique | Description |
|----------|-------------|
| Latence p50 | Médiane des temps de réponse |
| Latence p95 | 95e percentile des temps de réponse |
| Temps d'ingestion | Durée totale du chargement des données |

### Ressources

| Métrique | Description |
|----------|-------------|
| RAM steady-state | Consommation mémoire en régime nominal |
| RAM peak | Consommation mémoire maximale (ingestion, recalculs) |
| CPU moyen | Utilisation CPU pendant l'exécution |
| Disque | Occupation du volume Docker |

## Séparation structure / temporel

Le principe retenu distingue clairement :

- **Structure** : entités, relations, navigation contextuelle
- **Temporel** : mesures, agrégations, séries longues

Cette séparation permet de comparer chaque paradigme sur son domaine d'optimisation principal et d'éviter les biais liés au volume massif des séries temporelles. Elle reflète également les pratiques industrielles observées où une base time-series coexiste avec un graphe ou un relationnel pour la structure.

### Justification

Les accès structurels (navigation des relations) et les accès temporels (agrégation, lissage, comparaison) relèvent de profils d'optimisation fondamentalement différents :

- Les traversées de graphe bénéficient de la localité des données en mémoire
- Les agrégations temporelles bénéficient de la compression, du stockage colonne et des index temporels

Évaluer les deux dans un même moteur généraliste masque ces différences fondamentales.

### Requête Q8 comme cas hybride

La requête Q8 illustre une architecture hybride : sélection des points via le graphe (tenant → espaces → équipements → points de puissance), puis agrégation des consommations dans TimescaleDB. Cette séparation exploite chaque paradigme sur son domaine d'optimisation.

## Reproductibilité

- Dépôt public contenant scripts et définitions d'infrastructure
- Orchestration via Docker Compose pour aligner les environnements
- Génération déterministe du dataset (seed configurable)
- Résultats exportables en CSV et JSON
- Versions des outils et paramètres loggés pour chaque campagne

## Limites assumées

- Le tuning est volontairement limité et documenté (pas d'optimisation opportuniste)
- L'effet cache est atténué par le warmup mais pas totalement éliminé
- Les représentations alternatives (autres modélisations possibles) ne sont pas évaluées
- L'environnement d'exécution (Docker) introduit un overhead constant mais comparable
