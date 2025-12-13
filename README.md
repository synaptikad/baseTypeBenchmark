# Base Type Benchmark

## 1. Contexte et motivation
La transformation numérique des bâtiments impose une consolidation progressive des données issues de la gestion technique, de l'énergie et de l'occupation. La généralisation des jumeaux numériques et des graphes de connaissances conduit à des architectures orientées graphe, souvent maintenues intégralement en mémoire pour maximiser la réactivité. Cette approche accroît cependant les coûts d'infrastructure lorsque le volume de points et d'événements croît. Les avancées récentes des bases relationnelles et des moteurs de séries temporelles invitent à réévaluer la pertinence d'une stratégie tout graphe tout en mémoire pour les systèmes d'information du bâtiment.

## 2. Question de recherche
Dans un bâtiment conséquent, où les chaînes fonctionnelles et énergétiques sont de profondeur limitée (typiquement inférieure à 10 relations), et où la majorité des données sont des séries temporelles, un paradigme graphe in-memory apporte-t-il un avantage mesurable par rapport à une base relationnelle moderne bien conçue ?

## 3. Hypothèses
- H0 (hypothèse nulle) : à volumétrie et requêtes équivalentes, le recours à un graphe en mémoire n'apporte pas de gain significatif de performance ou de consommation de ressources face à une base relationnelle optimisée avec extension time-series.
- H1 (hypothèse alternative) : à volumétrie et requêtes équivalentes, un graphe en mémoire présente un avantage mesurable en latence ou en consommation de ressources par rapport à une base relationnelle optimisée avec extension time-series.

## 4. Périmètre de l'étude
- Échelle : bâtiment tertiaire conséquent, avec plusieurs milliers d'espaces et équipements.
- Typologies de données : espaces, équipements, points, relations fonctionnelles, énergétiques et chaînes de commande, séries temporelles issues des capteurs et compteurs.
- Inspirations sémantiques : Haystack v4, Brick Schema, RealEstateCore pour la structuration des entités et des relations.
- Exclusions : graphes sociaux, traversées non bornées, algorithmes de graphe avancés ou de recommandation, cas nécessitant des parcours de profondeur arbitraire.

## 5. Technologies comparées
- PostgreSQL combiné à TimescaleDB, représentatif d'un socle relationnel moderne avec support natif des séries temporelles et une maturité opérationnelle élevée.
- Memgraph, moteur de graphe de propriétés en mémoire mettant en avant la performance temps réel et l'intégration Cypher, représentant les architectures graphe modernes.
- Oxigraph, implémentation RDF/SPARQL récente et performante, adaptée aux modèles sémantiques et à la compatibilité avec les standards du web de données.

## 6. Méthodologie
- Same data, same questions, same metrics : un jeu de données unique sert aux trois moteurs, avec des requêtes fonctionnelles identiques et des métriques communes.
- Dataset synthétique mais réaliste : génération paramétrable reflétant un bâtiment tertiaire, incluant des séquences de séries temporelles cohérentes.
- Génération déterministe : utilisation d'un seed pour garantir la reproductibilité et la comparaison des runs.
- Séparation ingestion et requêtes : phases distinctes pour charger les données puis exécuter les requêtes de benchmark.
- Mesures : latence p50 et p95 des requêtes, consommation RAM, occupation disque, temps d'ingestion complet.

## Hypothèses d’optimisation et bornes de comparaison
Les moteurs évalués (PostgreSQL, TimescaleDB, Memgraph, Oxigraph) sont des solutions reconnues et matures. Les modèles de données mobilisés restent compacts et réalistes afin d'éviter toute pénalisation artificielle. L'étude cherche à établir des bornes basses réalistes de coût pour chaque paradigme et examine le rapport coût / bénéfice dans un contexte smart building, sans conclure sur une faisabilité théorique absolue.

### Menaces à la validité
- Effet cache.
- Tuning volontairement limité et documenté.
- Représentations alternatives non évaluées.
- Environnement d'exécution.

## 7. Reproductibilité
- Dépôt public contenant scripts et définitions d'infrastructure.
- Orchestration via Docker Compose pour aligner les environnements.
- Profils de volumétrie small et large pour ajuster le dataset et observer les effets d'échelle.
- Exécution de référence sur une infrastructure contrôlée (VPS) pour isoler la variable volumétrie.
- Les profils décrivent uniquement la taille du dataset et la charge appliquée, indépendamment du matériel local.
- Résultats exportables en CSV et JSON pour partage et analyses externes.
- Versions des outils et paramètres loggés pour chaque campagne d'exécution.

## Scénarios de volumétrie et réalisme opérationnel
Les profils small et large restent cohérents avec des usages bâtimentaires courants. Ils se déclinent selon trois paramètres explicitement définis :
- **P** : nombre de points (capteurs/mesures) instrumentant le bâtiment.
- **Δt** : pas de temps moyen entre deux mesures d'un même point.
- **Horizon temporel** : durée de conservation et d'analyse continue des séries.

Deux régimes réalistes structurent les scénarios évalués :
- **Supervision énergétique standard** : Δt de 10 à 15 minutes pour l'ensemble des points utiles au pilotage énergétique et au reporting multi-sites, avec un horizon temporel pluriannuel. Le profil small représente un échantillon réduit mais complet de ce contexte ; le profil large en applique l'ordre de grandeur d'un bâtiment tertiaire conséquent.
- **Régulation plus fine** : Δt de 1 à 5 minutes sur un sous-ensemble ciblé (boucles critiques, zones sensibles ou suivi confort) avec un horizon opérationnel de quelques semaines à quelques mois, compatible avec les fenêtres courtes d'optimisation.

Dans ces deux contextes, une latence de l'ordre de la seconde reste généralement acceptable pour les tableaux de bord, alertes et boucles de réglage. La recherche de la milliseconde n'est pas un critère central : les profils small et large privilégient un réalisme opérationnel plutôt qu'une course au temps de réponse absolu.

## 8. Positionnement et limites
Ce benchmark ne vise pas à disqualifier le paradigme graphe. Il cherche à clarifier son domaine de validité face à des alternatives relationnelles et time-series récentes. Les graphes restent pertinents pour des traversées complexes, des dépendances non bornées, l'alignement sémantique interdomaines ou des traitements nécessitant des algorithmes de graphe spécialisés.

## Gestion des séries temporelles et architectures hybrides

### Constat de terrain
Dans de nombreuses plateformes bâtimentaires, les séries temporelles représentent la majorité du volume de données. Certaines architectures choisissent de conserver une fenêtre temporelle courte en mémoire pour des usages temps réel ou quasi temps réel.

### Architecture hybride couramment rencontrée
Un graphe in-memory est alors mobilisé pour la structure, les relations, l'état courant et un historique court (jours ou semaines). Une base spécialisée externe sert à l'archivage long terme, aux analyses historiques et au reporting énergétique.

### Position méthodologique de cette étude
Ce choix hybride peut avoir une justification fonctionnelle, et le benchmark présenté ici ne nie pas cette possibilité. La question scientifique formulée est la suivante : même lorsqu'on limite la conservation en mémoire des séries temporelles à une courte période, le stockage de mesures dans un graphe in-memory généraliste apporte-t-il un avantage mesurable par rapport à une base time-series spécialisée ?

### Analyse qualitative
Les accès structurels (navigation des relations) et les accès temporels (agrégation, lissage, comparaison) relèvent de profils d'optimisation fondamentalement différents. Les représentations objet graphe induisent un overhead structurel, y compris sur des fenêtres temporelles courtes, qui peut affecter l'efficacité des traitements temporels.

### Choix expérimental du benchmark
La structure est évaluée via des moteurs graphe et relationnel, tandis que les séries temporelles sont évaluées via une base spécialisée (TimescaleDB). Ce choix vise à éviter un biais volumétrique et à comparer chaque paradigme sur ce pour quoi il est conçu.

### Limite assumée
L'étude ne couvre pas l'évaluation complète d'un graphe in-memory intégrant des séries temporelles courtes ; cette évaluation constituerait un travail complémentaire distinct.

## 9. Public cible
- Ingénieurs smart building et exploitation.
- Architectes data et responsables d'infrastructure.
- Intégrateurs GTB et SGTB.
- Chercheurs appliqués en systèmes d'information du bâtiment.

## 10. Licence et réutilisation
Le dépôt est sous licence open source (voir LICENSE). Toute personne est invitée à reproduire, critiquer et étendre le protocole en conservant les contraintes de reproductibilité et en publiant les paramètres utilisés.

## 11. Services docker-compose et ports exposés
- TimescaleDB/PostgreSQL: port 5432
- Neo4j: ports 7474 (HTTP) et 7687 (Bolt)
- Memgraph: port 7688 (Bolt exposé, 7687 interne)
- Jena Fuseki: port 3030
