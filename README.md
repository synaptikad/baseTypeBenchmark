# Benchmark BaseType V3

Benchmark académique comparant 5 paradigmes de stockage pour les systèmes d'information bâtimentaires.

**Question de recherche** : Un graphe in-memory est-il justifié pour les SI bâtimentaires ?

**Hypothèse** : Les graphes bâtimentaires sont structurellement simples (degré ~1, profondeur 6-8), donc SQL récursif suffit.

---

## Paradigmes comparés

| ID | Paradigme | Graph | Timeseries | Statut JSONB |
|----|-----------|-------|------------|--------------|
| P1 | PostgreSQL Relational | CTEs récursifs | TimescaleDB | IMPOSSIBLE |
| P2 | PostgreSQL JSONB | CTEs + JSONB | TimescaleDB | NATIVE |
| M1 | Memgraph Standalone | Cypher natif | Chunks in-memory | DEGRADED |
| M2 | Memgraph + TimescaleDB | Cypher natif | TimescaleDB externe | DEGRADED |
| O2 | Oxigraph + TimescaleDB | SPARQL | TimescaleDB externe | DEGRADED |

---

## 23 Queries de benchmark

| Catégorie | Queries | Description |
|-----------|---------|-------------|
| Graph-only | Q1-Q5 | Traversées structurelles (FEEDS, SERVES, CONTAINS) |
| Timeseries | Q6 | Agrégation horaire |
| Hybrid | Q7-Q13 | Sélection graph + agrégation timeseries |
| JSONB-specific | Q14-Q19 | protocol{}, metadata{}, capabilities[], tags[] |
| Graph-native | Q20-Q23 | shortestPath, allShortestPaths, siblings, propagation |

---

## Installation

```bash
# Cloner le repo
git clone <repo-url>
cd benchmarkV3

# Installer les dépendances Python
pip install pyyaml pyarrow
```

---

## Usage rapide

### 1. Générer un dataset

```bash
# Profil small (1 bâtiment, ~1300 nodes)
python -m src.basetype_benchmark.dataset.generator --profile small

# Profil medium avec seed spécifique
python -m src.basetype_benchmark.dataset.generator --profile medium --seed 42
```

### 2. Exporter vers les paradigmes

```bash
# Tous les exports
python -m src.basetype_benchmark.exporters.p1_extractor
python -m src.basetype_benchmark.exporters.p2_extractor
python -m src.basetype_benchmark.exporters.m1m2_extractor
python -m src.basetype_benchmark.exporters.o2_extractor
```

### 3. Charger dans les moteurs

```bash
# PostgreSQL (P1/P2)
psql -d benchmark -f data/export/p1/schema_p1.sql
psql -d benchmark -f data/export/p1/load_p1.sql

# Memgraph (M1/M2)
cat data/export/m1m2/load_memgraph.cypher | mgconsole

# Oxigraph (O2)
./data/export/o2/load_oxigraph.sh
```

---

## Structure du projet

```
benchmarkV3/
├── config/
│   ├── equipment/          # 32 types d'équipements (AHU, VAV, IPCamera, ...)
│   └── profiles/           # Profils volumétrie (small, medium, large)
├── data/
│   ├── export/             # Exports par paradigme
│   └── generated/          # Datasets générés
├── queries/
│   ├── catalog.yaml        # Définition des 23 queries
│   ├── golden_answers.yaml # Réponses attendues
│   ├── p1/*.sql           # Implémentations P1
│   ├── p2/*.sql           # Implémentations P2
│   ├── m1/*.cypher        # Implémentations M1
│   ├── m2/                # Implémentations M2 (graph + ts)
│   └── o2/                # Implémentations O2 (graph + ts)
├── src/basetype_benchmark/
│   ├── schema/            # Schéma canonique
│   ├── dataset/           # Générateur + golden
│   ├── exporters/         # Transformateurs par paradigme
│   └── validation/        # Validateurs cross-paradigm
└── docs/
    └── IMPLEMENTATION_STATUS.md
```

---

## Modèle de données

### 10 Types de nœuds
Site → Building → Floor → Space → Equipment → Point
+ Tenant, Contract, Ticket, Zone

### ~20 Types de relations
- **Spatiales** : CONTAINS, LOCATED_IN, ADJACENT_TO
- **Fonctionnelles** : HAS_POINT, SERVES, CONTROLS, MONITORS
- **Énergétiques** : FEEDS, METERS_TENANT, METERS_ZONE
- **IT** : HOSTS, NETWORK_LINK
- **Contractuelles** : COVERED_BY, OCCUPIES, LEASED_TO

### Propriétés JSONB (P2 = NATIVE)
```yaml
Equipment:
  capabilities: ["cooling", "heating", "humidity_control"]
  metadata: {manufacturer, warranty_end, serial_number}
  tags: ["brick:AHU", "haystack:ahu"]
  protocol: {type: "BACnet", device_id: 1234}

Point:
  protocol: {type: "BACnet", object_type: "analogInput"}
  calibration: {next_date: "2024-06-01"}
  range: {min: 0, max: 100, unit: "°C"}
```

---

## Protocoles supportés

| Domaine | Protocoles |
|---------|------------|
| HVAC | BACnet, Modbus, LON, KNX |
| Electrical | Modbus TCP/RTU, BACnet, IEC 61850 |
| Security | ONVIF, OSDP, Wiegand |
| IT | SNMP, IPMI, Redfish |
| Lighting | DALI, KNX |

---

## Documentation

- [IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) - État d'avancement détaillé
- [SPEC_BENCHMARK_V3.md](docs_private/SPEC_BENCHMARK_V3.md) - Spécification complète
- [catalog.yaml](queries/catalog.yaml) - Définition des 23 queries

---

## Licence

Projet académique - Usage recherche uniquement.
