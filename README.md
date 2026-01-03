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

- Protocole RAM-Gradient: test systematique de 512 Mo a 256 Go par moteur
- Metriques d'efficience: performance / Go alloue
- Formule de dimensionnement: `RAM_recommandee = RAM_min x 1.5`

### Pourquoi ce benchmark ?

La transformation numerique des batiments conduit a des architectures orientees graphe, souvent in-memory. Mais le graphe batimentaire est-il suffisamment complexe pour justifier ce choix ?

**Complexite structurelle bornee**

Les ontologies batimentaires (Brick, Haystack, RealEstateCore, Google DBO) definissent ~10 types de relations: containment (isPartOf), flux (feeds), spatial (serves), controle (controls), metering (isMeteredBy). Meme en modelisant un SI complet incluant usagers, mainteneurs, tickets, reservations et contrats (~25 types de relations), le graphe reste simple:

| Metrique           | Batiment | Reseau social | Biologie (PPI) | PLM Aerospatial |
|--------------------|----------|---------------|----------------|-----------------|
| Degre moyen        | ~1       | 100+          | 50+            | 20+             |
| Types de relations | ~25      | 50+           | 200+           | 100+            |
| Profondeur max     | 6-8      | unbounded     | unbounded      | 30+             |

Cette simplicite (pattern arborescent + references) suggere que les traversees sont realisables avec SQL recursif, sans necessiter un moteur graphe in-memory specialise.

**Cout des architectures in-memory**

- **Economique**: Prix DRAM +170% YoY (T3 2025, TrendForce)
- **Energetique**: 256 Go RAM = 25-40 W permanent = 220-350 kWh/an
- **Ecologique**: Empreinte carbone DRAM vs stockage SSD

L'hypothese in-memory merite verification empirique avec mesures de latence, RAM et CPU.

---

## Scenarios compares

| ID | Nom | Structure | Series temporelles | Containers |
|----|-----|-----------|-------------------|------------|
| P1 | PostgreSQL Relationnel | Tables SQL | Hypertables (TimescaleDB) | timescaledb |
| P2 | PostgreSQL JSONB | Documents JSONB | Hypertables (TimescaleDB) | timescaledb |
| M1 | Memgraph Standalone | Property Graph (Cypher) | Chunks en memoire | memgraph |
| M2 | Memgraph + TimescaleDB | Property Graph (Cypher) | Hypertables (externe) | memgraph + timescaledb |
| O2 | Oxigraph + TimescaleDB | Triplets RDF (SPARQL) | Hypertables (externe) | oxigraph + timescaledb |

> **Note**: O1 (Oxigraph standalone) n'est pas teste car RDF n'a pas de type liste natif pour stocker des series temporelles. Les alternatives (triplet par valeur, `rdf:List`, litteraux JSON) sont soit explosives en volume, soit inexploitables par SPARQL.

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
python -m pip install -r requirements.txt
python -m pip install -e .

# Lancer le menu interactif
python run.py

# (Alternative sans activer le venv)
# .venv/bin/python run.py
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

Le runner affiche un menu interactif avec feedback detaille sur les operations longues:

```
══════════════════════════════════════════════════════════════════════
  BASETYPE BENCHMARK
══════════════════════════════════════════════════════════════════════

  Datasets disponibles: 2 (14.2 GB)
    • large-1w_seed42 (1,234,567 noeuds)
    • small-2d_seed42 (45,678 noeuds)

  Actions:

  1. Generer un dataset
  2. Lancer le benchmark
  3. Voir les resultats
  4. Supprimer des datasets

  0. Quitter
```

### Generation de dataset

Option **1. Generer un dataset** :

Le runner recommande automatiquement le profil `large-1w` :

```
┌────────────────────────────────────────────────────────────────┐
│  Profil recommande pour ce benchmark:                          │
│                                                                │
│    large-1w (1 semaine, ~1.2M points)                         │
│                                                                │
│  Ce profil offre un bon equilibre entre:                       │
│    • Taille suffisante pour stresser les moteurs               │
│    • Temps de generation raisonnable (~5-10 min)               │
│    • Taille disque moderee (~14 GB)                           │
└────────────────────────────────────────────────────────────────┘
```

### Execution du benchmark

Option **2. Lancer le benchmark** :

```
══════════════════════════════════════════════════════════════════════
  EXECUTION DU BENCHMARK
══════════════════════════════════════════════════════════════════════

── Selection du dataset ──

  Datasets disponibles:

  1. large-1w_seed42 (14.2 GB)
     1,234,567 noeuds, 2,345,678 aretes

Choisir le dataset [1-1, defaut=1]: 1
[10:45:32] ✓  Dataset selectionne: large-1w_seed42
```

Le benchmark affiche une barre de progression et les metriques en temps reel:

```
── [1/6] Scenario P1: PostgreSQL Relationnel ──

[10:46:02] ▸  Demarrage containers: timescaledb (limite 8GB RAM)...
[10:46:15] ✓  Containers operationnels (13.2s)
[10:46:15] ▸  Chargement des donnees (P1)...
[10:47:45] ✓  Donnees chargees en 1m 30s
[10:47:45] ℹ   RAM timescaledb: 2,456 MB

  P1 [████████████████████████░░░░░░] 10/13 (77%) Q10...
    ✓ Q1: 827 rows, 12.3ms
    ✓ Q2: 156 rows, 8.7ms
    ...
```

Les scenarios disponibles sont:

| ID | Nom | Description |
|----|-----|-------------|
| P1 | PostgreSQL Relationnel | Tables SQL normalisees + TimescaleDB |
| P2 | PostgreSQL JSONB | Documents JSONB + TimescaleDB |
| M1 | Memgraph Standalone | Property Graph in-memory (Cypher) |
| M2 | Memgraph + TimescaleDB | Graphe hybride + TimescaleDB |
| O2 | Oxigraph + TimescaleDB | RDF hybride + TimescaleDB |

---

## Profils de donnees

### Echelles (scales)

| Scale | Batiments | Espaces | Equipements | Points | Ratio |
|-------|-----------|---------|-------------|--------|-------|
| small | 1 | ~90 | ~1 050 | ~12 000 | 1.2 pts/m² |
| medium | 3 | ~430 | ~4 600 | ~53 000 | 1.3 pts/m² |
| large | 5 | ~875 | ~9 600 | ~110 000 | 1.3 pts/m² |
| xlarge | 9 | ~3 100 | ~33 000 | ~365 000 | 1.2 pts/m² |

> Les ratios pts/m² sont calibres sur des batiments tertiaires reels (~1.2-1.3 pts/m²).

### Durees (durations)

| Duration | Jours | Cas d'usage |
|----------|-------|-------------|
| 2d | 2 | Tests rapides (smoke test) |
| 1w | 7 | **Benchmark standard (recommande)** |
| 1m | 30 | Analyse mensuelle |
| 6m | 180 | Etudes longitudinales |
| 1y | 365 | Historique annuel |

### Profil recommande

Pour valider les hypotheses de ce benchmark, le profil **`large-1w`** est suffisant:

- **~110k points de mesure** : stress suffisant pour differencier les moteurs
- **~5-10 GB de donnees** : teste les contraintes memoire
- **Generation en ~5 min** : iteration rapide

> Le profil `xlarge` (~365k points) est disponible pour des stress-tests comparables a la Tour Duo Paris.

### Combinaisons (profils)

Profils disponibles : `small-2d`, `small-1w`, `medium-1w`, `large-1w`, `xlarge-1w`, etc.

---

## Niveaux RAM testes

Le benchmark teste chaque scenario avec differentes allocations memoire :

```
RAM_LEVELS = [4, 8, 16, 32, 64, 128, 256]  # GB
```

### Protocole RAM-Gradient

Le runner propose trois modes de selection :

| Mode | Description | Cas d'usage |
|------|-------------|-------------|
| **SINGLE** | Un seul niveau RAM | Test rapide |
| **GRADIENT** | Selection manuelle de plusieurs niveaux | Protocole personnalise |
| **AUTO** | Niveaux adaptes a la taille du dataset | Recommande |

Le mode **AUTO** ajuste automatiquement :
- Dataset < 1 GB : 4, 8, 16 GB
- Dataset 1-5 GB : 8, 16, 32 GB
- Dataset > 5 GB : 16, 32, 64, 128 GB

### Detection de plateau

Le benchmark detecte automatiquement les **plateaux de performance** :

- Compare la latence moyenne entre deux niveaux RAM consecutifs
- Si l'amelioration est < 10%, les niveaux suivants sont ignores
- Evite l'escalade inutile et accelere le benchmark

```
[17:45:30] ℹ  Plateau detecte: 150ms → 145ms (+3.3%)
[17:45:30] ℹ  Plateau detecte → skip P1@64GB
```

### Metriques cgroups Linux

Les mesures RAM utilisent les **cgroups v2** Linux pour une precision maximale :

```
/sys/fs/cgroup/system.slice/docker-{id}.scope/
├── memory.current    # RAM actuelle
├── memory.peak       # Pic RAM depuis reset
└── cpu.stat          # Temps CPU (user/system)
```

Le **peak RAM est reset apres le chargement** pour mesurer uniquement l'impact des queries.

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
| Q13 | Confort heures bureau | Stress-test | Hour filter + dechunking |

---

## Structure du projet

```
BaseTypeBenchmark/
├── run.py                      # Menu interactif principal
├── metrics.py                  # Metriques cgroups Linux (RAM peak, CPU)
├── scripts/
│   └── smoke_benchmark.py      # Execution non-interactive (CI/cloud)
├── config/
│   ├── profiles/               # small.yaml, medium.yaml, large.yaml, xlarge.yaml
│   ├── equipment/              # Definitions YAML equipements (FCU, AHU, etc.)
│   ├── equipment_distribution.yaml  # Matrice equipements par espace
│   ├── space_types.yaml        # Types d'espaces et domaines
│   └── schemas/                # JSON Schema validation
├── docker/
│   ├── docker-compose.yml      # TimescaleDB, Memgraph, Oxigraph
│   └── .env                    # Credentials (copier depuis config/benchmark.env)
├── queries/
│   ├── p1_p2/                  # SQL PostgreSQL (Q1-Q13)
│   ├── m1/                     # Cypher standalone avec chunks
│   ├── m2/graph/ + m2/ts/      # Cypher + SQL federation
│   └── o2/graph/ + o2/ts/      # SPARQL + SQL federation
├── src/basetype_benchmark/
│   ├── dataset/
│   │   ├── generator_v2.py     # Generateur synthetique (seed=42)
│   │   ├── equipment_loader.py # Chargement definitions equipements
│   │   ├── exporter_v2.py      # Export Parquet → CSV/N-Triples
│   │   └── dataset_manager.py  # Workflow lazy export/prune
│   ├── runner/engines/         # Moteurs de requetes
│   │   ├── postgres.py         # PostgreSQL/TimescaleDB
│   │   ├── memgraph.py         # Memgraph (Cypher)
│   │   └── oxigraph.py         # Oxigraph (SPARQL)
│   └── loaders/                # Chargement donnees par moteur
├── docs/
│   ├── REFACTORING_CONSOLIDATED.md  # Architecture et roadmap
│   ├── B3_RUNBOOK.md                # Deploiement OVH
│   └── Exploration/                 # Documentation equipements (221 types)
└── deploy/                     # Scripts cloud OVH
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
- RAM utilisee (steady-state, peak par query)
- Metriques par container (pour M2/O2)
- Reponses pour validation inter-moteurs
- Statut OOM

### Format des resultats

```json
{
  "scenario": "M2",
  "ram_gb": 8,
  "load_time_s": 3.5,
  "mem_after_load_mb": {
    "memgraph": {"memory_mb": 429, "memory_peak_mb": 430},
    "timescaledb": {"memory_mb": 164, "memory_peak_mb": 169}
  },
  "queries": {
    "Q1": {
      "row_count": 198,
      "latency_ms": 14.2,
      "memory_mb": 593,
      "memory_peak_mb": 600,
      "memory_by_container": {
        "memgraph": {"memory_mb": 429, "peak_mb": 430},
        "timescaledb": {"memory_mb": 164, "peak_mb": 170}
      }
    }
  },
  "responses": {
    "Q1": {"row_count": 198, "hash": 123456789, "sample": [...]}
  }
}
```

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
4. Google Digital Buildings Ontology. https://google.github.io/digitalbuildings/
5. TrendForce. DRAM Contract Prices. 2025.
6. Berkeley Lab. United States Data Center Energy Usage Report. December 2024.

---

## Reproduire l'experience

### Workflow recommande

```bash
# 1. Lancer le menu interactif
python run.py

# 2. Option 1: Generer un dataset
#    → Choisir echelle: large
#    → Choisir duree: 1w (recommande)
#    → Seed: 42

# 3. Option 2: Lancer le benchmark
#    → Selectionner le dataset large-1w_seed42
#    → Scenarios: ALL (5 scenarios)
#    → RAM: 8 GB (recommande)
#    → Requetes: ALL (Q1-Q13)

# 4. Option 3: Voir les resultats
```

### Test rapide (smoke test)

Pour valider l'installation:

```bash
python run.py
# → Option 1: Generer dataset small-2d
# → Option 2: Benchmark avec scenarios P1, M1, O1
```

Duree estimee: ~5 minutes.

### Resultats attendus

Apres execution, le dossier `benchmark_results/` contient:
- Latences par requete et par scenario
- RAM utilisee apres chargement
- Resume comparatif JSON

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
