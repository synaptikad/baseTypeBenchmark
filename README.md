## 1. Contexte et motivation

La transformation numérique des bâtiments impose une consolidation progressive des données issues de la gestion technique, de l'énergie et de l'occupation. La généralisation des jumeaux numériques et des graphes de connaissances conduit à des architectures orientées graphe, souvent maintenues intégralement en mémoire pour maximiser la réactivité. Cette approche accroît cependant les coûts d'infrastructure lorsque le volume de points et d'événements croît.

### Contexte économique 2024-2025

Le marché de la mémoire vive connaît une tension structurelle sans précédent :

- Les prix contractuels DRAM ont augmenté de plus de 170 % en glissement annuel au T3 2025 (TrendForce).
- Les modules DDR5 64 Go RDIMM, standard dans les datacenters, pourraient coûter deux fois plus cher fin 2026 qu'au début 2025 (Counterpoint Research).
- Samsung, SK Hynix et Micron ont réorienté leur production vers la mémoire haute bande passante (HBM) pour les accélérateurs IA, créant une pénurie sur les gammes conventionnelles.
- Les nouvelles capacités de production n'entreront en service qu'entre 2027 et 2028.

Cette pression économique rend d'autant plus critique l'évaluation du rapport coût/bénéfice des architectures in-memory.

### Contexte énergétique

La mémoire vive consomme de l'énergie en permanence, indépendamment de la charge :

- Un module DIMM DDR4/DDR5 consomme typiquement 3 à 5 W en continu (rafraîchissement des cellules).
- Un serveur équipé de 256 Go de RAM consomme 25 à 40 W uniquement pour maintenir sa mémoire active, soit 220 à 350 kWh par an.
- Les datacenters représentaient 4,4 % de la consommation électrique américaine en 2023, avec une projection entre 6,7 % et 12 % d'ici 2028 (Berkeley Lab, décembre 2024).

À titre de comparaison, un SSD NVMe consomme principalement lors des opérations d'I/O et reste quasi passif au repos. Les moteurs de bases de données spécialisés exploitent cette asymétrie.

### Motivation du benchmark

Les avancées récentes des bases relationnelles et des moteurs de séries temporelles invitent à réévaluer la pertinence d'une stratégie tout-graphe tout-en-mémoire pour les systèmes d'information du bâtiment. Ce benchmark vise à fournir des mesures empiriques pour éclairer ce choix architectural.
