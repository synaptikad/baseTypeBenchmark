# Générateur de dataset bâtimentaire synthétique

Ce module produit un jeu de données reproductible représentant un bâtiment tertiaire conséquent. Il vise à comparer des moteurs relationnels (PostgreSQL avec TimescaleDB), des property graphs en mémoire (Memgraph) et des moteurs RDF/SPARQL (Oxigraph) sans biais technologique. Les données sont synthétiques et ne reposent sur aucune source propriétaire.

## Modèle conceptuel

Le graphe est fondé sur une hiérarchie explicite et un ensemble fermé de relations:

- Types de nœuds: Site, Building, Floor, Space, Equipment, Point, Meter, Tenant.
- Relations orientées: CONTAINS (site→building, building→floor, floor→space), LOCATED_IN (equipment→space), HAS_PART (equipment→equipment), HAS_POINT (equipment→point), MEASURES (point→quantité logique), CONTROLS (point→equipment), FEEDS (meter→equipment ou meter→meter), SERVES (equipment→space), OCCUPIES (tenant→space).

Les mesures portent uniquement sur des quantités logiques simples (température, CO2, puissance, débit, statut, commande). Aucune ontologie experte n’est imposée afin de conserver un coût structurel comparable entre paradigmes.

## Inspirations et neutralité

Le modèle s’inspire des structures courantes des standards Haystack, Brick et de certaines notions du RealEstateCore. Ces inspirations guident les noms et la granularité mais ne constituent pas des implémentations strictes, ce qui évite d’optimiser le dataset pour un moteur donné. Les exports reprennent exactement les mêmes informations logiques pour les trois cibles afin de préserver la neutralité.

## Profils de volumétrie

Deux profils contrôlent la taille du dataset via la variable d’environnement `SCALE_MODE`:

- `small`: ~10 étages, ~800 espaces, ~3 000 équipements, ~15 000 points, ~200 compteurs.
- `large`: ~20 étages, ~2 000 espaces, ~8 000 équipements, ~50 000 points, ~500 compteurs.

Les alias historiques `laptop` (small) et `server` (large) restent acceptés pour faciliter les scripts existants.

Les profondeurs sont bornées pour rester représentatives d’un bâtiment conséquent: chaînes FEEDS ≤ 8, chaînes fonctionnelles (HAS_PART/SERVES) ≤ 6, traversée globale ≤ 10.

## Utilisation

La génération est déterministe: la graine peut être fournie via la variable `SEED` (valeur par défaut `42`). Un lancement typique se fait avec:

```
python -m dataset_gen.run  # ou SEED=123 SCALE_MODE=large python -m dataset_gen.run
```

Les exports sont produits dans `dataset_gen/out/` au format CSV pour PostgreSQL/TimescaleDB, JSON pour Memgraph et JSON-LD pour RDF/SPARQL.

## Limites assumées

- Les identifiants sont synthétiques et incrémentaux, sans correspondance avec des équipements réels.
- Les quantités mesurées sont limitées à quelques catégories usuelles pour privilégier la structure sur la sémantique métier.
- La répartition spatiale et fonctionnelle est réaliste mais simplifiée: un seul site et un bâtiment principal, avec des distributions non uniformes mais contrôlées.
- Le dataset est statique (pas de séries temporelles), ce qui permet de tester la structure et la volumétrie avant d’ajouter des mesures temporelles dans un benchmark ultérieur.
