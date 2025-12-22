# BaseType Benchmark

Benchmark comparatif des paradigmes de stockage pour les systemes d'information batimentaires.

**Auteur:** Antoine Debienne ([ORCID 0009-0002-6674-2691](https://orcid.org/0009-0002-6674-2691))

**Licence:** CC-BY-4.0

---

## Question de recherche

> **Un graphe in-memory est-il justifie pour les systemes d'information batimentaires ?**

Ce benchmark fournit des **mesures empiriques reproductibles** pour eclairer ce choix architectural. Contrairement aux benchmarks existants (LDBC, gMark), il introduit la **RAM comme variable experimentale** et cible specifiquement le domaine batimentaire.

### Contribution principale

**Premier benchmark batimentaire avec analyse parametrique cout-memoire:**

- Protocole RAM-Gradient: test systematique de 8 a 128 Go par moteur
- Metriques d'efficience: performance / Go alloue
- Formule de dimensionnement: `RAM_recommandee = RAM_min x 1.5`

### Pourquoi ce benchmark ?

La transformation numerique des batiments conduit a des architectures orientees graphe, souvent en memoire. Mais:

- **Cout economique**: Prix DRAM +170% YoY (T3 2025, TrendForce)
- **Cout energetique**: 256 Go RAM = 25-40 W permanent = 220-350 kWh/an
- **Ratio structure/temporel**: Les donnees batimentaires sont 1:1000 a 1:3000 (structure vs timeseries)

Les traversees graphe dans un SI batimentaire sont **bornees** (profondeur < 10). L'hypothese in-memory merite verification empirique.

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
- Instance cloud recommandee : 256 Go RAM, 32 vCPU (ex: OVH B3-256)

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

### Script de deploiement cloud

```bash
# OVH B3-256 (256 Go RAM, 32 vCPU, 400 Go NVMe)
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
├── run.py                      # Menu interactif principal
├── scripts/
│   └── smoke_benchmark.py      # Execution non-interactive (CI/cloud)
├── config/
│   ├── profiles/               # small.yaml, medium.yaml, large.yaml
│   └── space_types.yaml        # Types d'espaces et domaines
├── docker/
│   ├── docker-compose.yml      # TimescaleDB, Memgraph, Oxigraph
│   └── .env                    # Credentials (copier depuis config/benchmark.env)
├── queries/
│   ├── p1_p2/                  # SQL PostgreSQL (Q1-Q13)
│   ├── m1/                     # Cypher standalone avec chunks
│   ├── m2/graph/ + m2/ts/      # Cypher + SQL federation
│   ├── o1/                     # SPARQL standalone avec chunks
│   └── o2/graph/ + o2/ts/      # SPARQL + SQL federation
├── src/basetype_benchmark/
│   ├── dataset/
│   │   ├── generator_v2.py     # Generateur synthetique (seed=42)
│   │   ├── exporter_v2.py      # Export Parquet → CSV/N-Triples
│   │   └── dataset_manager.py  # Workflow lazy export/prune
│   ├── benchmark/
│   │   └── resource_monitor.py # cgroup v2, RAM peak, CPU
│   └── loaders/                # Chargement par moteur
│       ├── postgres/load.py
│       ├── memgraph/load.py
│       └── oxigraph/load.py
├── docs/
│   ├── REFACTORING_CONSOLIDATED.md  # Architecture et roadmap
│   └── B3_RUNBOOK.md                # Deploiement OVH
├── deploy/                     # Scripts cloud
└── benchmark_results/          # Resultats JSON
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

## Reproduire l'experience

### Execution complete

```bash
# Lancer le menu interactif
python run.py

# → Option 2: Generate Dataset (choisir profil, ex: small-1m)
# → Option 3: Run Benchmark → F (Full Campaign)
```

Le benchmark execute automatiquement:
- Generation du dataset (ou telechargement HuggingFace)
- Test de chaque scenario (P1, P2, M1, M2, O1, O2)
- Variation RAM (8, 16, 32, 64, 128 Go)
- 13 requetes avec warmup et mesures repetees

### Resultats attendus

Apres execution, le dossier `benchmark_results/` contient:
- Latences par requete (p50, p95)
- RAM utilisee (steady-state, peak)
- Statut OOM par configuration
- Matrices RAM × Moteur pour analyse comparative

---

## Etendre le benchmark

### Ajouter un nouveau moteur

Ce benchmark est concu pour etre etendu. Pour ajouter un moteur (Neo4j, NebulaGraph, Stardog, etc.):

1. **Fork** ce repository
2. **Ajouter le container** dans `docker/docker-compose.yml`
3. **Creer le loader** dans `src/basetype_benchmark/loaders/votre_moteur/`
4. **Adapter les requetes** dans `queries/votre_scenario/`
5. **Declarer le scenario** dans `run.py` (dict `SCENARIOS`)

### Structure des requetes

```
queries/
├── p1_p2/           # SQL PostgreSQL (P1 et P2 partagent)
├── m1/              # Cypher Memgraph standalone (avec chunks)
├── m2/
│   ├── graph/       # Cypher pour la partie graphe
│   └── ts/          # SQL pour la partie TimescaleDB
├── o1/              # SPARQL Oxigraph standalone (avec chunks)
└── o2/
    ├── graph/       # SPARQL pour la partie graphe
    └── ts/          # SQL pour la partie TimescaleDB
```

### Tester votre propre moteur BOS

Editeurs de jumeaux numeriques, solutions BOS (Spinal, ProptechOS, etc.):

1. Exporter le dataset Parquet vers votre format
2. Implementer les 13 requetes dans votre langage
3. Mesurer avec le protocole RAM-Gradient
4. Comparer aux baselines P1/P2/M1/M2/O1/O2

Le format Parquet (`exports/<profile>/parquet/`) sert de **reference neutre** pour garantir l'equivalence des donnees.

---

## Documentation technique

| Document | Description |
|----------|-------------|
| [REFACTORING_CONSOLIDATED.md](docs/REFACTORING_CONSOLIDATED.md) | Architecture, corrections, roadmap |
| [B3_RUNBOOK.md](docs/B3_RUNBOOK.md) | Runbook deploiement OVH B3 |
| [methodology.md](docs/methodology.md) | Methodologie benchmark |

---

## Licence

Ce travail est distribue sous licence [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

---

## Citation

Si vous utilisez ce benchmark dans vos travaux:

```bibtex
@misc{debienne2025basetype,
  author = {Debienne, Antoine},
  title = {BaseType Benchmark: Comparative Analysis of Storage Paradigms for Building Information Systems},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/synaptikad/baseTypeBenchmark}
}
```
