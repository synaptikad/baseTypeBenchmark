# Critères d'évaluation

Cette grille fournit un cadre d'interprétation des résultats du benchmark. Elle est destinée aux architectes, CTO et maîtres d'ouvrage qui doivent traduire les mesures en décisions.

## Critères techniques

### 1. Adéquation au profil de données

Le paradigme choisi doit correspondre à la nature réelle des données :

- Séries temporelles massives (ratio structure/temporel de 1:1000 à 1:3000)
- Structure faiblement dynamique (schéma stable)
- Relations majoritairement bornées (profondeur < 10)

### 2. Performance utile

Les métriques du benchmark à considérer :

- **Latence p50** : temps de réponse typique
- **Latence p95** : temps de réponse en conditions défavorables
- **Stabilité** : variance entre les runs

Une latence de l'ordre de la seconde reste généralement acceptable pour les tableaux de bord, alertes et boucles de réglage. La recherche de la milliseconde n'est pas un critère central dans un contexte bâtimentaire.

### 3. Scalabilité

- **Verticale** : comment le moteur exploite l'ajout de RAM/CPU
- **Horizontale** : complexité opérationnelle du clustering
- **Volumétrique** : sensibilité à la croissance des données

## Critères d'efficience

### 4. Coût mémoire

Métriques du benchmark :

- **RAM steady-state** : consommation en régime nominal
- **RAM peak** : consommation maximale (ingestion, recalculs)

Questions à se poser :

- Le moteur peut-il externaliser les données froides ?
- Le ratio RAM/données est-il proportionné au service rendu ?

### 5. Coût énergétique

Estimation à partir des métriques :

- RAM steady-state × 0.15 W/Go ≈ consommation permanente
- Extrapolation annuelle : consommation × 8760 h

### 6. Coût d'exploitation

Facteurs qualitatifs :

- Complexité de déploiement (Docker, dépendances)
- Outillage disponible (monitoring, backup, migration)
- Maturité des pratiques DevOps

## Critères stratégiques

### 7. Réversibilité

Questions clés :

- Le modèle de données est-il explicite et documenté ?
- Les formats sont-ils standards ou propriétaires ?
- Une migration est-elle possible sans réécriture complète ?

### 8. Compétences

- Disponibilité sur le marché : SQL >> Cypher > SPARQL
- Courbe d'apprentissage
- Pérennité des langages et standards

### 9. Séparation des responsabilités

Le benchmark évalue cette séparation via Q8 :

- Le moteur structure peut-il déléguer le temporel ?
- Les requêtes hybrides sont-elles supportées ?
- L'architecture est-elle modulaire ?

## Smell tests (anti-patterns)

Ces signaux doivent déclencher une analyse approfondie :

### Confusion structure/temporel

> Utiliser un moteur graphe in-memory pour stocker des séries temporelles — même sur une fenêtre courte — sans avoir mesuré le surcoût par rapport à une base time-series spécialisée.

**Indicateur** : RAM steady-state disproportionnée par rapport au volume structurel.

### Traversées non bornées

> Concevoir un modèle nécessitant des traversées de profondeur arbitraire alors que les chaînes réelles sont bornées.

**Indicateur** : requêtes avec `*` ou profondeur non spécifiée.

### Optimisation prématurée

> Choisir un paradigme pour sa performance sur des algorithmes avancés (PageRank, communautés) non utilisés en pratique.

**Indicateur** : aucune requête du benchmark n'utilise ces algorithmes.

### Confusion expressivité/efficience

> Adopter un langage pour son expressivité sans vérifier que les requêtes réelles l'exploitent.

**Indicateur** : les requêtes Q1-Q8 se réduisent à des jointures et agrégations classiques.

### Fausse réversibilité

> Confondre export JSON avec réversibilité du modèle.

**Indicateur** : absence de schéma explicite, dépendance au runtime pour interpréter les données.

## Grille de synthèse

| Critère | Métrique benchmark | Seuil d'alerte |
|---------|-------------------|----------------|
| Performance | p95 | > 5s pour requêtes courantes |
| Mémoire | RAM steady-state | > 10× taille données structurelles |
| Ingestion | Temps total | > 10 min pour profil small |
| Disque | Occupation | > 5× taille données brutes |

Ces seuils sont indicatifs et doivent être ajustés selon le contexte opérationnel.
