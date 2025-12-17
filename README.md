# BaseType Benchmark

Benchmark comparatif des paradigmes de stockage pour les systemes d'information batimentaires.

**Auteur:** Antoine Debienne ([ORCID 0009-0002-6674-2691](https://orcid.org/0009-0002-6674-2691))

**Licence:** CC-BY-4.0

---

## Contexte et motivation

### Transformation numerique des batiments

La transformation numerique des batiments implique la consolidation progressive des donnees issues des systemes de gestion technique (GTB), du suivi energetique et de l'occupation. La generalisation des jumeaux numeriques et des graphes de connaissances conduit a des architectures orientees graphe, souvent maintenues entierement en memoire pour maximiser la reactivite. Cette approche augmente les couts d'infrastructure a mesure que le nombre de points de mesure et le volume d'evenements croissent.

### Contexte economique 2024-2025

Le marche de la memoire connait une tension structurelle :

- Prix contractuels DRAM en hausse de plus de 170% en glissement annuel au T3 2025 (TrendForce)
- Modules DDR5 64 Go RDIMM : doublement des prix prevu fin 2026 par rapport a debut 2025 (Counterpoint Research)
- Reorientation de la production vers la memoire haute bande passante (HBM) pour les accelerateurs IA
- Nouvelles capacites de production attendues en 2027-2028

### Contexte energetique

La RAM consomme de l'energie en permanence, independamment de la charge :

- Un module DIMM DDR4/DDR5 consomme typiquement 3-5 W en continu (rafraichissement cellulaire)
- Un serveur avec 256 Go de RAM consomme 25-40 W uniquement pour maintenir la memoire active, soit 220-350 kWh par an
- Les datacenters americains representaient 4,4% de la consommation electrique en 2023, avec des projections de 6,7-12% d'ici 2028 (Berkeley Lab, decembre 2024)

Par comparaison, un SSD NVMe consomme principalement pendant les operations d'E/S et reste quasi passif au repos.

### Question centrale

**Un graphe in-memory est-il justifie pour les systemes d'information batimentaires ?**

Ce benchmark fournit des mesures empiriques pour eclairer ce choix architectural, dans une perspective d'ecologie de conception et d'efficience des ressources.

---

## Positionnement

### Ontologies batimentaires de reference

Ce travail s'appuie sur les standards etablis :

- **Haystack v4** (Project Haystack) : modele semantique par tags pour les equipements techniques
- **Brick Schema** (Berkeley) : ontologie formelle pour les metadonnees batimentaires
- **RealEstateCore** (REC) : ontologie de jumeau numerique pour l'immobilier

### Limites des benchmarks existants

| Benchmark | Focus | Limitation pour le batiment |
|-----------|-------|----------------------------|
| LDBC SNB | Reseaux sociaux | Pas de donnees temporelles, topologie differente |
| gMark | Requetes synthetiques | Agnostique du domaine, pas de series temporelles |
| TPC-H/DS | Charges analytiques | Pas de traversees de graphe |

Aucun de ces benchmarks ne teste la contrainte RAM comme variable experimentale.

### Specificites du domaine batimentaire

- **Ratio structure/temporel** : 1:1000 a 1:3000 (peu de noeuds, beaucoup de mesures)
- **Traversees bornees** : les requetes depassent rarement 5-10 sauts
- **Requetes hybrides** : combinent navigation dans le graphe et agregation de series temporelles
- **Temps reel et historique** : charges operationnelles et analytiques

### Apport de ce benchmark

- **Domaine-specifique** : adapte aux patterns de donnees batimentaires
- **Reproductible** : generation deterministe, seed fixe, protocole documente
- **Equitable** : pas de tuning opportuniste, configurations par defaut
- **RAM comme variable experimentale** : premier benchmark batimentaire avec analyse parametrique cout-memoire

---

## Methodologie

### Scenarios compares

| ID | Nom | Structure | Series temporelles |
|----|-----|-----------|-------------------|
| P1 | PostgreSQL Relationnel | Tables SQL | Hypertables (TimescaleDB) |
| P2 | PostgreSQL JSONB | Documents JSONB | Hypertables (TimescaleDB) |
| M1 | Memgraph Standalone | Property Graph (Cypher) | Tableaux en memoire |
| M2 | Memgraph + TimescaleDB | Property Graph (Cypher) | Hypertables (externe) |
| O1 | Oxigraph Standalone | Triplets RDF (SPARQL) | Litteraux RDF |
| O2 | Oxigraph + TimescaleDB | Triplets RDF (SPARQL) | Hypertables (externe) |

### Dataset synthetique

**Modele de donnees** (inspire de Haystack/Brick/REC) :

```
Site -> Building -> Floor -> Space -> Equipment -> Point
                                   -> Meter (arbre FEEDS)
                                   -> Tenant (OCCUPIES)
```

**Profils de volumetrie** :

| Echelle | Points | Etages | Description |
|---------|--------|--------|-------------|
| small | 50k | 25 | Batiment tertiaire standard |
| medium | 100k | 50 | Petit campus |
| large | 500k | 100 | Campus universitaire |

**Durees des series temporelles** :

| Duree | Jours | Cas d'usage |
|-------|-------|-------------|
| 2d | 2 | Tests rapides |
| 1w | 7 | Debogage operationnel |
| 1m | 30 | Analyse mensuelle |
| 6m | 180 | Patterns saisonniers |
| 1y | 365 | Reporting annuel |

### Requetes benchmark (Q1-Q12)

| Requete | Nature | Bornes | Moteurs |
|---------|--------|--------|---------|
| Q1-Q5 | Traversees structurelles | <= 10 sauts | Tous |
| Q6-Q7 | Agregations temporelles | N/A | PostgreSQL uniquement |
| Q8-Q12 | Hybride (graphe + temporel) | <= 5 + agregation | Tous |

### Protocole RAM-Gradient

Contribution methodologique : la RAM est traitee comme variable independante.

```
Pour chaque profil (small, medium, large) :
  Pour chaque allocation RAM (2, 4, 8, 16, 32, 64, 128, 256 Go) :
    Pour chaque scenario (P1, P2, M1, M2, O1, O2) :
      1. Limiter le container : docker run --memory={RAM}g
      2. Charger les donnees (mesurer succes/OOM)
      3. Si succes : executer Q1-Q12
      4. Enregistrer : latences, OOM, RAM utilisee
```

### Metriques collectees

| Metrique | Description | Unite |
|----------|-------------|-------|
| Latence p50/p95 | Temps de reponse | ms |
| RAM steady-state | Memoire au repos | Mo |
| RAM peak | Memoire maximale | Mo |
| RAM_min | Plus petite allocation sans OOM ni degradation > 20% | Go |
| Efficience | Performance / RAM utilisee | - |

---

## Installation

### Prerequis

- Ubuntu/Debian (teste sur Ubuntu 24.04)
- Acces sudo
- Instance cloud recommandee : 256 Go RAM, 32 vCPU (ex: AWS r8g.8xlarge)
- Stockage : 500 Go minimum pour les datasets large-1y

### Installation rapide (nouvelle machine)

```bash
# Telecharger et lancer le script d'installation interactif
curl -sLO https://raw.githubusercontent.com/synaptikad/baseTypeBenchmark/main/init.sh
bash init.sh
```

Le script guide l'utilisateur a travers toutes les etapes :
1. Installation des dependances systeme (Docker, Python, Make)
2. Configuration des permissions Docker
3. Clonage du repository
4. Creation d'un environnement virtuel Python et installation des dependances
5. Proposition de lancer le workflow interactif

### Installation manuelle

```bash
# Dependances systeme
sudo apt update && sudo apt install -y make docker.io docker-compose-v2 python3-pip python3-venv python3-full git
sudo usermod -aG docker $USER
newgrp docker

# Cloner et installer
git clone https://github.com/synaptikad/baseTypeBenchmark.git
cd baseTypeBenchmark
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

### Demarrage rapide

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer le menu interactif
python run.py

# Ou commandes directes
python run.py test      # Test rapide (small-2d, scenario P1)
python run.py list      # Lister les profils disponibles
python run.py matrix    # Afficher la matrice de faisabilite RAM
```

---

## Utilisation

### Operations sur les datasets

```bash
# Lister les profils avec estimations
python -m basetype_benchmark.cli list

# Details d'un profil
python -m basetype_benchmark.cli info small-1w

# Generation interactive
python -m basetype_benchmark.cli generate

# Generation directe
python -m basetype_benchmark.cli generate --profile small-1w --seed 42

# Verification d'integrite
python -m basetype_benchmark.cli verify
```

### Operations de benchmark

```bash
# Matrice de faisabilite RAM
python -m basetype_benchmark.cli matrix

# Execution interactive
python -m basetype_benchmark.cli run

# Publication des resultats
python -m basetype_benchmark.cli publish
```

### Contraintes RAM par scenario

La commande `matrix` affiche les combinaisons scenario/profil realisables :

- **P1/P2** (PostgreSQL) : stockage disque, fonctionnel avec 2-4 Go
- **M1** (Memgraph standalone) : in-memory, necessite environ 3x la taille du dataset
- **M2** (Memgraph+TimescaleDB) : hybride, 2-5 Go
- **O1/O2** (Oxigraph) : stockage disque, 1-4 Go

M1 atteint ses limites sur `large-6m` (~394 Go requis) et `large-1y` (~800 Go requis).

### Systeme de checkpoints

Les benchmarks supportent la reprise apres interruption :

```python
from basetype_benchmark.benchmark.checkpoint import CheckpointManager

manager = CheckpointManager("benchmark_results")
latest = manager.find_latest_session()
manager.load_session(latest)

progress = manager.get_progress()
print(f"Progression : {progress['completed']}/{progress['total']}")
```

### Conteneurs Docker

```bash
# Demarrer tous les moteurs
docker-compose up -d

# Demarrer un moteur specifique
docker-compose up -d timescaledb memgraph oxigraph

# Verifier le statut
docker-compose ps
```

### Variables d'environnement

| Variable | Description | Defaut |
|----------|-------------|--------|
| BENCH_SEED | Graine aleatoire | 42 |
| BENCH_SCALE_MODE | Profil par defaut | small |
| BENCH_N_RUNS | Repetitions de mesure | 10 |
| BENCH_N_WARMUP | Iterations de warmup | 3 |
| BENCH_TIMEOUT_S | Timeout des requetes | 30 |

---

## Dataset

Le dataset synthetique est disponible sur HuggingFace Hub pour garantir la reproductibilite :

**Repository** : `synaptikad/basetype-benchmark` (lien a confirmer apres publication)

### Chargement du dataset

```python
from basetype_benchmark.dataset.huggingface import load_benchmark_data

data = load_benchmark_data(scale="medium", duration="1m")
print(f"Noeuds : {len(data['nodes'])}")
print(f"Aretes : {len(data['edges'])}")
print(f"Series temporelles : {len(data['timeseries'])}")
```

### Publication

Le token HuggingFace est demande de maniere interactive lors de la publication (jamais stocke dans les fichiers) :

```bash
python -m basetype_benchmark.cli publish
```

---

## Structure du repository

```
BaseTypeBenchmark/
├── src/basetype_benchmark/
│   ├── dataset/           # Generation de donnees
│   │   ├── config.py      # Profils de volumetrie
│   │   ├── generator.py   # Generateur synthetique
│   │   └── huggingface.py # Integration HuggingFace
│   ├── benchmark/         # Framework de benchmark
│   │   ├── runner.py      # Orchestration
│   │   ├── checkpoint.py  # Reprise apres interruption
│   │   └── ram_config.py  # Matrice de faisabilite RAM
│   ├── loaders/           # Chargeurs par moteur
│   └── queries/           # Requetes SQL/Cypher/SPARQL
├── deploy/                # Scripts de deploiement
├── docker-compose.yml
├── run.py                 # Point d'entree principal
└── pyproject.toml
```

---

## Limites methodologiques

- Tuning volontairement limite (configurations par defaut)
- Environnement Docker (overhead constant mais comparable entre moteurs)
- Representations alternatives non evaluees (DuckDB, ClickHouse, etc.)
- Seed unique (reproductibilite privilegiee sur la diversite)

---

## References

1. Project Haystack. https://project-haystack.org/
2. Brick Schema. https://brickschema.org/
3. RealEstateCore. https://realestatecore.io/
4. TrendForce. DRAM Contract Prices. 2025.
5. Berkeley Lab. United States Data Center Energy Usage Report. December 2024.
6. LDBC Council. Social Network Benchmark. https://ldbcouncil.org/

---

## Licence

Ce travail est distribue sous licence [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
