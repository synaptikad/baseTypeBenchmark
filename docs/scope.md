# Périmètre du benchmark

## Échelle et volumétrie

Le dataset porte sur un bâtiment tertiaire de taille conséquente, avec une modélisation inspirée des ontologies Haystack, Brick et RealEstateCore. Les relations couvrent équipements HVAC, zones, espaces, points de mesure et liens fonctionnels.

### Profils de volumétrie

Deux profils sont fournis pour garantir la reproductibilité sur des contextes différents :

| Profil | Étages | Espaces | Équipements | Points | Compteurs |
|--------|--------|---------|-------------|--------|-----------|
| small  | 10     | 800     | 3 000       | 15 000 | 200       |
| large  | 20     | 2 000   | 8 000       | 50 000 | 500       |

Ces profils décrivent uniquement la taille du dataset et la charge ; ils n'impliquent pas un matériel particulier. Les exécutions de référence sont réalisées sur une infrastructure contrôlée (VPS) afin d'isoler la variable de volumétrie.

### Projection volumétrique des séries temporelles

Pour contextualiser l'enjeu des séries temporelles :

| Profil | Points | Fréquence | Horizon | Enregistrements |
|--------|--------|-----------|---------|-----------------|
| small  | 15 000 | 15 min    | 1 an    | ~525 millions   |
| small  | 15 000 | 15 min    | 3 ans   | ~1,6 milliard   |
| large  | 50 000 | 15 min    | 1 an    | ~1,75 milliard  |
| large  | 50 000 | 15 min    | 3 ans   | ~5,25 milliards |

Ces volumes illustrent pourquoi la séparation structure/temporel est critique : le modèle structurel (quelques dizaines de milliers d'entités) ne prédit pas le volume réel des données opérationnelles.

### Estimation de l'empreinte mémoire

À titre indicatif, pour le profil large avec 3 ans d'historique :

- Stockage brut des séries temporelles : ~150-200 Go (sans compression)
- Avec compression time-series typique (TimescaleDB) : ~15-30 Go
- Modèle structurel seul (nœuds + arêtes) : ~50-100 Mo

Le ratio structure/temporel est de l'ordre de 1:1000 à 1:3000, ce qui explique l'inadéquation d'un stockage uniforme in-memory.

## Bornes de traversée

Les profondeurs sont bornées pour rester représentatives d'un bâtiment réel :

- Chaînes FEEDS : ≤ 8 relations
- Chaînes fonctionnelles (HAS_PART/SERVES) : ≤ 6 relations
- Traversée globale : ≤ 10 relations

Ces bornes correspondent aux observations de terrain : les chaînes énergétiques et fonctionnelles d'un bâtiment tertiaire sont structurellement limitées.

## Exclusions explicites

Le benchmark ne couvre pas :

- Les graphes sociaux et réseaux à haute connectivité
- Les traversées non bornées ou de profondeur arbitraire
- Les algorithmes de graphe avancés (PageRank, détection de communautés, recommandation)
- Les cas nécessitant des parcours récursifs sans limite

Ces exclusions ne constituent pas une disqualification du paradigme graphe, mais une délimitation du périmètre pertinent pour les systèmes d'information du bâtiment.

## Comparabilité

Aucune comparaison biaisée ne sera acceptée : chaque moteur recevra une configuration équivalente autant que possible (RAM, stockage, paramètres par défaut), et les optimisations seront documentées.
