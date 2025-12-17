# Gestion des Datasets

Ce répertoire contient les outils pour générer, gérer et distribuer les datasets du benchmark.

## Architecture

```
dataset_gen/
├── config.py          # Configuration des profils de génération
├── generator.py       # Générateur de datasets synthétiques
├── model.py           # Modèle de données
├── export_*.py        # Exporteurs (PostgreSQL, Graph, RDF)
├── dataset_manager.py # Gestionnaire de cache et export
├── release_manager.py # Gestionnaire de releases GitHub
├── workflow.py        # Workflow optimisé pour Codespace
├── orchestrator.py    # Orchestrateur automatique des benchmarks
├── pregenerate.py     # Pré-génération des datasets
└── run.py            # Interface simple
```

## 🎯 Vision Générale

### Phase 1: Génération des Datasets
- **Génération séquentielle** avec stockage GitHub
- **36 profils** : 3 échelles × 4 durées × 3 formats
- **Stockage optimisé** : pas de stockage local permanent

### Phase 2: Orchestration Automatique
- **Séquence automatique** : upload → container → benchmark → nettoyage
- **3 modèles** : PostgreSQL, Memgraph, Oxigraph
- **Métriques** : performance, mémoire, temps d'exécution
- **Rapport final** consolidé

## 🚀 Workflow Complet

### 1. Préparation des Datasets
```bash
cd /workspaces/baseTypeBenchmark/dataset_gen

# Sélection intelligente selon stockage disponible
python workflow.py smart-select 10

# Génération séquentielle avec nettoyage automatique
python workflow.py sequential small-1w small-1m medium-1w
```

### 2. Suite de Benchmarks Automatisée
```bash
# Exécute TOUS les tests automatiquement
python orchestrator.py full-suite

# OU test individuel pour debug
python orchestrator.py single small-1w postgres
```

### 3. Analyse des Résultats
```bash
# Résultats détaillés
cat results/benchmark_results.json

# Rapport consolidé
cat results/benchmark_report.md
```

## 📊 Couverture des Tests

### Modèles Testés
- **🐘 PostgreSQL** : TimescaleDB pour séries temporelles
- **🕸️ Memgraph** : Property Graph en mémoire
- **🗂️ Oxigraph** : RDF/SPARQL

### Profils de Charge
| Échelle | Points | Durée | Exemple |
|---------|--------|-------|---------|
| **SMALL** | 50k | 1w/1m/6m/1y | Bâtiment moyen |
| **MEDIUM** | 100k | 1w/1m/6m/1y | Grand bâtiment |
| **LARGE** | 500k | 1w/1m/6m/1y | Campus/ensemble |

**Total : 36 combinaisons × 3 modèles = 108 tests**

## ⚙️ Orchestration Technique

### Séquence par Test
1. **📥 Téléchargement** : Dataset depuis GitHub Release
2. **🐳 Container** : Démarrage du service approprié
3. **📤 Chargement** : Import des données
4. **⚡ Benchmark** : Exécution des 8 queries
5. **📊 Métriques** : Collecte performance/mémoire
6. **🧹 Nettoyage** : Arrêt container + suppression données

### Métriques Collectées
- **Temps d'exécution** par query
- **Utilisation mémoire** peak
- **Temps de chargement** des données
- **Taux de succès** des opérations

## 💾 Gestion du Volume pour Codespace

### Problème Résolu
- **Total théorique** : ~1 TB (tous datasets)
- **Limite Codespace** : 128 GB max
- **Solution** : Téléchargement à la demande

### Charge Réelle par Test
| Profil | Archive | Format Max | RAM Peak |
|--------|---------|------------|----------|
| small-1w | 0.5 GB | 1 GB | **1 GB** |
| medium-1m | 4 GB | 8 GB | **8 GB** |
| large-1y | 50 GB | 500 GB | **50 GB** |

**✅ Tests faisables même sur 16 GB RAM !**

## 🔧 Configuration

### Variables d'Environnement
```bash
# Token GitHub pour les datasets
export GITHUB_TOKEN=your_token

# Timeout des services (secondes)
export SERVICE_TIMEOUT=60

# Nettoyage automatique
export CLEANUP_AFTER_TEST=true
```

### Docker Compose
Les services sont définis dans `docker-compose.yml` à la racine :
- `postgres` : PostgreSQL + TimescaleDB
- `memgraph` : Property Graph
- `oxigraph` : RDF/SPARQL

## 📈 Résultats et Rapports

### Structure des Résultats
```
results/
├── benchmark_results.json    # Résultats détaillés JSON
└── benchmark_report.md       # Rapport consolidé Markdown
```

### Métriques par Modèle
- **PostgreSQL** : Temps queries SQL, index performance
- **Memgraph** : Temps traversées graphe, mémoire cache
- **Oxigraph** : Temps SPARQL, optimisation RDF

### Comparaisons
- **Performance relative** entre modèles
- **Scalabilité** selon la taille des données
- **Efficacité mémoire** par paradigme

## 🚦 États et Commandes

### Préparation
```bash
# Vérifier stockage
python workflow.py storage

# Lister profils disponibles
python orchestrator.py list

# Test connexion GitHub
python workflow.py session small-1w
```

### Exécution
```bash
# Suite complète (108 tests)
python orchestrator.py full-suite

# Test rapide (debug)
python orchestrator.py single small-1w postgres

# Arrêt manuel
docker-compose down
```

### Monitoring
```bash
# Suivre les résultats
tail -f results/benchmark_results.json

# Vérifier containers
docker ps

# Logs services
docker-compose logs postgres
```

## 🔍 Debugging

### Tests Individuels
```bash
# Tester seulement le chargement
python workflow.py session small-1w

# Tester un container seul
docker-compose up -d postgres
docker-compose logs postgres

# Test de chargement manuel
python orchestrator.py single small-1w postgres
```

### Problèmes Courants
1. **Timeout service** : Augmenter `SERVICE_TIMEOUT`
2. **Mémoire insuffisante** : Commencer par `small-1w`
3. **Rate limiting GitHub** : Pauses entre téléchargements
4. **Espace disque** : Nettoyage automatique activé

## 🎯 Prochaines Étapes

1. **Phase 1** ✅ : Architecture dataset + workflow optimisé
2. **Phase 2** 🔄 : Implémentation orchestrateur (en cours)
3. **Phase 3** 📋 : Tests pilotes sur small-1w
4. **Phase 4** 📊 : Suite complète + analyse résultats
5. **Phase 5** 📈 : Optimisations et comparaisons détaillées

---

**🎉 Prêt pour la révolution des benchmarks !**
