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

## Scenarios compares

| ID | Nom | Structure | Series temporelles | Containers |
|----|-----|-----------|-------------------|------------|
| P1 | PostgreSQL Relationnel | Tables SQL | Hypertables (TimescaleDB) | timescaledb |
| P2 | PostgreSQL JSONB | Documents JSONB | Hypertables (TimescaleDB) | timescaledb |
| M1 | Memgraph Standalone | Property Graph (Cypher) | Chunks en memoire | memgraph |
| M2 | Memgraph + TimescaleDB | Property Graph (Cypher) | Hypertables (externe) | memgraph + timescaledb |
| O1 | Oxigraph Standalone | Triplets RDF (SPARQL) | Chunks RDF | oxigraph |
| O2 | Oxigraph + TimescaleDB | Triplets RDF (SPARQL) | Hypertables (externe) | oxigraph + timescaledb |

---

## Installation

### Prerequis

- Docker et Docker Compose
- Python 3.10+
- Instance cloud recommandee : 256 Go RAM, 32 vCPU (ex: AWS m8g.16xlarge)

### Installation rapide

```bash
# Cloner le repository
git clone https://github.com/synaptikad/baseTypeBenchmark.git
cd baseTypeBenchmark

# Creer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dependances
pip install -e .
pip install -r requirements.txt

# Lancer le menu interactif
python run.py
```

### Scripts de deploiement cloud

Des scripts de setup sont disponibles pour differents providers :

```bash
# AWS EC2 (m8g.16xlarge Graviton4)
curl -sSL https://raw.githubusercontent.com/.../deploy/aws_setup.sh | sudo bash

# Hetzner CCX63
bash deploy/hetzner_setup.sh

# OVH B3-256
bash deploy/ovh_setup.sh
```

---

## Utilisation

### Menu principal interactif

```bash
python run.py
```

Affiche le menu :

```
============================================================
  BASETYPE BENCHMARK
============================================================
Available datasets: small-1w, medium-1m
On disk: 2 datasets, 1250.5 MB

  1. Purge Datasets
  2. Generate Dataset
  3. Run Benchmark
  4. Publish Results
  0. Exit

Select [2]:
```

### Generation de dataset

Option **2. Generate Dataset** :

1. Choisir la source : Generation locale ou HuggingFace Hub
2. Selectionner le profil "master" (ex: `large-1y`)
3. Le generateur cree tous les formats (CSV, JSON, N-Triples)

Les sous-profils (ex: `small-1w` depuis `large-1y`) sont extraits automatiquement pendant le benchmark.

### Execution du benchmark

Option **3. Run Benchmark** :

```
============================================================
  BENCHMARK EXECUTION
============================================================
Master dataset: large-1y
Available scales: small, medium, large
Available durations: 1w, 1m, 6m, 1y
Total configurations: 12

  F. FULL CAMPAIGN - All configurations automatically
     12 profiles x 6 scenarios x 7 RAM levels = 504 runs
  S. SELECT - Choose profiles, scenarios, RAM levels
  Q. QUICK TEST - Single profile, all scenarios, single RAM
  R. RESUME - Continue interrupted campaign (2 found)

  0. Back
```

| Mode | Description |
|------|-------------|
| **F (Full)** | Execute toutes les combinaisons automatiquement |
| **S (Select)** | Choix fin des profils, scenarios et niveaux RAM |
| **Q (Quick)** | Test rapide : 1 profil, 6 scenarios, 1 niveau RAM |
| **R (Resume)** | Reprend une campagne interrompue |

### Mode SELECT (selection fine)

Permet de choisir :

1. **Scales** : small, medium, large (ou tous)
2. **Durations** : 1w, 1m, 6m, 1y (ou toutes)
3. **Scenarios** : P1, P2, M1, M2, O1, O2 (ou tous)
4. **Niveaux RAM** : 4, 8, 16, 32, 64, 128, 256 GB (ou tous)

### Mode RESUME (reprise)

Detecte automatiquement les campagnes interrompues et permet de les reprendre :

- Affiche la progression (ex: "15/36 complete")
- Ne re-execute que les combinaisons manquantes
- Conserve les resultats deja obtenus

---

## Profils de donnees

### Echelles (scales)

| Scale | Batiments | Espaces | Equipements | Points |
|-------|-----------|---------|-------------|--------|
| small | 1 | ~120 | ~1 800 | ~70 000 |
| medium | 3 | ~430 | ~6 500 | ~245 000 |
| large | 12 | ~2 600 | ~39 000 | ~1 500 000 |

### Durees (durations)

| Duration | Jours | Cas d'usage |
|----------|-------|-------------|
| 1w | 7 | Tests rapides |
| 1m | 30 | Analyse mensuelle |
| 6m | 180 | Patterns saisonniers |
| 1y | 365 | Reporting annuel |

### Combinaisons (profils)

12 profils disponibles : `small-1w`, `small-1m`, `small-6m`, `small-1y`, `medium-1w`, etc.

---

## Niveaux RAM testes

Le benchmark teste chaque scenario avec differentes allocations memoire :

```
RAM_LEVELS = [4, 8, 16, 32, 64, 128, 256]  # GB
```

Pour chaque combinaison (profil, scenario, RAM) :

1. Demarre le container avec `--memory={RAM}g`
2. Charge les donnees
3. Execute les 13 requetes (Q1-Q13)
4. Enregistre latences, RAM utilisee, OOM eventuel

---

## Requetes benchmark (Q1-Q13)

| # | Nom | Nature | Description |
|---|-----|--------|-------------|
| Q1 | Chaine energetique | Traversee FEEDS | Parcours arbre compteurs |
| Q2 | Impact fonctionnel | Traversee HAS_PART + SERVES | Espaces impactes par panne |
| Q3 | Services spatiaux | Lookup SERVES | Equipements servant un espace |
| Q4 | Inventaire temperature | Multi-hop | Points temp par etage |
| Q5 | Equipements orphelins | Scan global | Equipements sans relation |
| Q6 | Agregation horaire | Time-series | Moyennes horaires |
| Q7 | Derive top 20 | Time-series | Points les plus instables |
| Q8 | Energie tenant | Hybride | Consommation par locataire |
| Q9 | Empreinte carbone | Hybride | CO2 par tenant |
| Q10 | Analyse securite | Traversee | Points d'acces par zone |
| Q11 | Impact IT | Traversee | Equipements dependant d'un rack |
| Q12 | Analytics complet | Multi-domaine | Vue consolidee |
| Q13 | Confort vendredis | Stress-test | DOW filter + dechunking |

---

## Structure du projet

```
BaseTypeBenchmark/
├── run.py                      # Point d'entree principal (menu interactif)
├── config/
│   ├── profiles/               # small.yaml, medium.yaml, large.yaml
│   ├── space_types.yaml        # Types d'espaces et domaines
│   └── equipment_distribution.yaml
├── docker/
│   ├── docker-compose.yml      # TimescaleDB, Memgraph, Oxigraph
│   └── .env
├── queries/
│   ├── sql/                    # Q1-Q13 pour PostgreSQL
│   ├── cypher/                 # Q1-Q13 pour Memgraph
│   └── sparql/                 # Q1-Q13 pour Oxigraph
├── src/basetype_benchmark/
│   ├── dataset/                # Generation et export
│   │   ├── generator_v2.py     # Generateur synthetique
│   │   ├── exporter_v2.py      # Export multi-format
│   │   └── huggingface.py      # Integration HuggingFace
│   ├── benchmark/              # Monitoring et metriques
│   │   ├── resource_monitor.py # CPU, RAM, I/O, energie
│   │   └── checkpoint.py       # Reprise apres interruption
│   └── loaders/                # Chargement par moteur
│       ├── postgres/
│       ├── memgraph/
│       └── oxigraph/
├── deploy/                     # Scripts cloud (AWS, Hetzner, OVH)
└── docs_private/               # Article academique
```

---

## Resultats

Les resultats sont sauvegardes dans `benchmark_results/` :

```
benchmark_results/
├── full_20250119_143022/
│   ├── small-1w_P1.json
│   ├── small-1w_P2.json
│   ├── ...
│   └── summary.json
```

Chaque fichier JSON contient :
- Latences par requete (p50, p95, min, max)
- RAM utilisee (steady-state, peak)
- CPU moyen
- Statut OOM

---

## Metriques collectees

| Categorie | Metrique | Description |
|-----------|----------|-------------|
| Performance | p50, p95 | Latences en ms |
| Memoire | RAM steady-state | Usage median |
| Memoire | RAM peak | Maximum observe |
| CPU | CPU moyen | % utilisation |
| I/O | IOPS read/write | Operations par seconde |
| Energie | RAPL (Linux) | Consommation CPU/DRAM |

---

## Limites methodologiques

- Tuning volontairement limite (configurations par defaut)
- Environnement Docker (overhead constant mais comparable)
- Seed unique (42) pour reproductibilite
- Pas de benchmark de concurrence (single-thread)

---

## References

1. Project Haystack. https://project-haystack.org/
2. Brick Schema. https://brickschema.org/
3. RealEstateCore. https://realestatecore.io/
4. TrendForce. DRAM Contract Prices. 2025.
5. Berkeley Lab. United States Data Center Energy Usage Report. December 2024.

---

## Licence

Ce travail est distribue sous licence [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
