# Runner de benchmark reproductible

Ce dossier contient le runner académique utilisé pour comparer trois familles d'architectures de stockage : PostgreSQL/TimescaleDB (modèles relationnel et JSONB), Memgraph et Oxigraph. Les scripts se concentrent sur la reproductibilité et la transparence des mesures, sans réglages opportunistes.

## Protocole expérimental

1. Vérifier la disponibilité des services via leur healthcheck Docker
2. Réaliser l'ingestion des données à l'aide des scripts dédiés par moteur
3. Appliquer un warmup systématique (N_WARMUP répétitions) afin d'évacuer les effets de cache froid
4. Exécuter chaque requête active N_RUNS fois en chronométrant chaque passage
5. Collecter les métriques système (RAM, CPU, taille disque des volumes) pendant l'exécution
6. Exporter les résultats structurés en JSON et CSV dans `bench/results/`
7. Afficher un résumé lisible en console

Les requêtes Q6 et Q7, spécifiques aux séries temporelles Timescale, sont marquées « N/A » pour Memgraph et Oxigraph. Q8 est hybride : sélection dans le graphe ou le triplestore puis agrégation Timescale.

## Définition des métriques

- Latence par requête individuelle, plus statistiques p50/p95/min/max
- Temps total d'ingestion et volume d'éléments ingérés
- Mémoire du conteneur (steady-state, pic) et CPU moyen (échantillonnage Docker)
- Empreinte disque du volume Docker associé

## Warmup vs mesure

Le warmup n'est jamais inclus dans les métriques. Les itérations de warmup servent uniquement à stabiliser les caches et à vérifier que les requêtes s'exécutent sans erreur avant la phase mesurée.

## Limites connues

- Les commandes d'exécution supposent la présence des conteneurs déclarés dans `docker-compose.yml`
- Les scripts d'ingestion et de requêtes peuvent nécessiter des ajustements selon l'environnement matériel ; la volumétrie est contrôlée par les profils `small` et `large` (alias historiques `laptop`/`server`).
- Si Docker n'est pas disponible, les métriques de ressources seront nulles et le runner échouera sur les étapes dépendantes des conteneurs

## Reproduire un bench complet

1. Démarrer les services requis (`docker compose up -d`)
2. Choisir un profil dans `bench/profiles/`
3. Exécuter `python -m bench.runner <profil>` depuis la racine du dépôt
4. Consulter les fichiers générés dans `bench/results/` ou le résumé console

Tous les paramètres (seed, nombre de répétitions, timeouts) sont centralisés dans `bench/config.py` et surchargables par variables d'environnement.
