# Analyse de dimensionnement - Cas réels

## Profils actuels vs réalité

| Métrique | small | large | **Campus réel** | **Parc tertiaire** | **Smart district** |
|----------|-------|-------|-----------------|--------------------|--------------------|
| Bâtiments | 1 | 1 | 50 | 200 | 500 |
| Étages | 10 | 20 | 500 | 2 000 | 5 000 |
| Espaces | 800 | 2 000 | 20 000 | 80 000 | 200 000 |
| Équipements | 3 000 | 8 000 | 100 000 | 400 000 | 1 000 000 |
| Points | 15 000 | 50 000 | 500 000 | 2 000 000 | 5 000 000 |
| Compteurs | 200 | 500 | 5 000 | 20 000 | 50 000 |

## Calcul du volume de données

### Graphe de connaissances (nœuds + relations)

Pour un **parc tertiaire (200 bâtiments)** :

```
Nœuds totaux ≈ 2.5M
- Sites: 10
- Buildings: 200
- Floors: 2 000
- Spaces: 80 000
- Equipment: 400 000
- Points: 2 000 000
- Meters: 20 000
- Tenants: 5 000

Relations ≈ 5M (ratio ~2 edges/node)
- CONTAINS: 82 210
- LOCATED_IN: 400 000
- HAS_POINT: 2 000 000
- HAS_PART: 200 000 (sous-équipements)
- FEEDS: 100 000 (chaîne énergie)
- SERVES: 800 000
- OCCUPIES: 80 000
```

### Time-series (historique 5 ans)

```
Points: 2 000 000
Intervalle: 15 min = 35 040 samples/an
Historique: 5 ans

Volume brut = 2M × 35040 × 5 = 350 milliards de points

Par sample: timestamp (8 bytes) + value (8 bytes) + point_id (8 bytes) = 24 bytes
Volume brut = 350B × 24 bytes = 8.4 To (non compressé)
```

## Consommation mémoire estimée par moteur

### Scénario: Parc tertiaire (200 bâtiments, 2M points)

| Moteur | Type | Graphe seul | + Time-series 1 an | + TS 5 ans | Notes |
|--------|------|-------------|--------------------|-----------:|-------|
| **Memgraph** | In-memory graph | 8-12 Go | N/A* | N/A* | *TS via TimescaleDB |
| **Neo4j** | In-memory graph | 12-20 Go | N/A* | N/A* | Heap + page cache |
| **TimescaleDB** | Disk + cache | 2-4 Go | 8-16 Go | 16-32 Go | Compression ~10x |
| **PostgreSQL rel** | Disk + cache | 1-2 Go | 8-16 Go | 16-32 Go | Shared buffers |
| **Oxigraph** | RDF in-memory | 15-25 Go | N/A* | N/A* | Verbose RDF triples |

### Formules d'estimation

**Graphe in-memory (Memgraph/Neo4j):**
```
RAM_graph = (nodes × 200 bytes) + (edges × 150 bytes) + overhead 30%
RAM_graph = (2.5M × 200) + (5M × 150) × 1.3
RAM_graph ≈ 1.6 Go (données) → 8-12 Go (avec index, structures internes)
```

**RDF triplestore (Oxigraph):**
```
Triples = nodes × 5 (propriétés) + edges
Triples ≈ 2.5M × 5 + 5M = 17.5M triples
RAM = triples × 500 bytes (URI + littéraux verbose)
RAM ≈ 8.7 Go → 15-25 Go (avec index)
```

**TimescaleDB (time-series):**
```
Données brutes 1 an = 2M points × 35040 × 24 bytes = 1.68 To
Compression TimescaleDB ≈ 10-20x → 84-168 Go sur disque
RAM recommandée = 25% du working set actif
RAM ≈ 8-16 Go pour requêtes fluides
```

## Recommandations VPS par cas d'usage

### Profil "Enterprise" (benchmark réaliste)

| Cas | RAM min | RAM recommandée | Disque | vCPU | Coût OVH/mois |
|-----|---------|-----------------|--------|------|---------------|
| Campus (50 bât) | 16 Go | 32 Go | 200 Go NVMe | 4 | ~40€ |
| Tertiaire (200 bât) | 32 Go | 64 Go | 500 Go NVMe | 8 | ~80€ |
| Smart district | 64 Go | 128 Go | 1 To NVMe | 16 | ~160€ |

### Configuration VPS OVH recommandée

**Pour benchmark enterprise réaliste:**
- **VPS Elite** : 8 vCPU / 32 Go RAM / 320 Go NVMe (~50€/mois)
- Ou **Bare Metal S** : 16 cores / 64 Go RAM / 500 Go SSD (~100€/mois)

## Worst-case : pourquoi l'in-memory explose

### Le piège du "tout graphe in-memory"

```
Scénario: Smart building avec historique complet en graphe

Chaque sample TS devient un nœud:
- 2M points × 35040 samples/an × 5 ans = 350 milliards de nœuds
- RAM nécessaire ≈ 350B × 200 bytes = 70 Po (pétaoctets)

→ IMPOSSIBLE en in-memory
→ C'est pourquoi l'architecture hybride avec CHUNKING est obligatoire
```

---

## Stratégie Hybride avec Chunking

### Principe : Ne jamais charger tout le graphe

```
┌────────────────────────────────────────────────────────────────────┐
│                         APPLICATION                                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │              GRAPHE CHUNKÉ (topologie)                      │  │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │  │
│   │  │ Bât. A  │ │ Bât. B  │ │ Bât. C  │ │   ...   │  ON-DISK  │  │
│   │  │  chunk  │ │  chunk  │ │  chunk  │ │         │           │  │
│   │  └────┬────┘ └─────────┘ └─────────┘ └─────────┘           │  │
│   │       │                                                     │  │
│   │       ▼ LOAD ON DEMAND                                      │  │
│   │  ┌─────────────────────┐                                    │  │
│   │  │   CACHE LRU RAM     │  ← Seulement 1-3 bâtiments actifs  │  │
│   │  │   (hot chunks)      │    en mémoire à la fois            │  │
│   │  └─────────────────────┘                                    │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │              TIME-SERIES CHUNKÉ (mesures)                   │  │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │  │
│   │  │ 2024-Q1 │ │ 2024-Q2 │ │ 2024-Q3 │ │ 2024-Q4 │  CHUNKS   │  │
│   │  │ compres.│ │ compres.│ │ compres.│ │  actif  │  TEMPORELS│  │
│   │  └─────────┘ └─────────┘ └─────────┘ └────┬────┘           │  │
│   │       ↑ TIERED STORAGE                    │                 │  │
│   │  ┌─────────────────────┐      ┌───────────▼─────────────┐  │  │
│   │  │   COLD (S3/HDD)     │      │   HOT (SSD + RAM cache) │  │  │
│   │  │   Archive 90 jours+ │      │   Derniers 90 jours     │  │  │
│   │  └─────────────────────┘      └─────────────────────────┘  │  │
│   └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

### Stratégies de partitionnement du graphe

| Stratégie | Clé de partition | Cas d'usage | RAM par chunk |
|-----------|------------------|-------------|---------------|
| **Par bâtiment** | `building_id` | Multi-sites | 50-200 Mo |
| **Par système** | `system_type` (CVC, élec) | Maintenance | 100-500 Mo |
| **Par étage** | `floor_id` | Navigation UI | 10-50 Mo |
| **Par locataire** | `tenant_id` | Facturation | 20-100 Mo |

### Calcul RAM avec chunking (parc 200 bâtiments)

```
SANS CHUNKING:
- Graphe complet en RAM: 8-12 Go
- Tous les bâtiments chargés = gaspillage

AVEC CHUNKING PAR BÂTIMENT:
- 1 chunk = 1 bâtiment ≈ 50 Mo
- Cache LRU = 5 bâtiments actifs max
- RAM graphe = 5 × 50 Mo = 250 Mo  ← 40x moins !

- Reste de la RAM pour:
  - TimescaleDB shared_buffers: 4-8 Go
  - Cache TS hot data: 2-4 Go
  - OS + overhead: 2 Go
```

### Implémentation PostgreSQL (table partitionnée)

```sql
-- Table des nœuds partitionnée par bâtiment
CREATE TABLE nodes (
    id UUID PRIMARY KEY,
    building_id UUID NOT NULL,
    type TEXT NOT NULL,
    name TEXT,
    properties JSONB
) PARTITION BY HASH (building_id);

-- Créer 32 partitions (pour 200 bâtiments, ~6 bât/partition)
CREATE TABLE nodes_p0 PARTITION OF nodes FOR VALUES WITH (MODULUS 32, REMAINDER 0);
CREATE TABLE nodes_p1 PARTITION OF nodes FOR VALUES WITH (MODULUS 32, REMAINDER 1);
-- ... jusqu'à p31

-- Index par partition (automatiquement local)
CREATE INDEX ON nodes (building_id, type);

-- Requête = scan d'une seule partition
EXPLAIN ANALYZE
SELECT * FROM nodes WHERE building_id = 'xxx' AND type = 'Equipment';
-- → Scanne seulement nodes_p[hash(xxx) % 32]
```

### Implémentation TimescaleDB (hypertables + tiered storage)

```sql
-- Hypertable avec chunks de 1 semaine
CREATE TABLE measurements (
    time        TIMESTAMPTZ NOT NULL,
    point_id    UUID NOT NULL,
    value       DOUBLE PRECISION
);

SELECT create_hypertable('measurements', 'time',
    chunk_time_interval => INTERVAL '7 days');

-- Compression automatique après 7 jours
ALTER TABLE measurements SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'point_id'
);

SELECT add_compression_policy('measurements', INTERVAL '7 days');

-- Tiered storage: archiver les chunks > 90 jours vers S3
SELECT add_tiering_policy('measurements', INTERVAL '90 days');
```

### Impact sur le dimensionnement

| Scénario | Sans chunking | Avec chunking | Économie |
|----------|---------------|---------------|----------|
| Parc 50 bât | 16 Go RAM | **4 Go RAM** | 75% |
| Parc 200 bât | 64 Go RAM | **8 Go RAM** | 87% |
| Smart district | 128 Go RAM | **16 Go RAM** | 87% |

### Nouvelle recommandation VPS avec chunking

| Cas | RAM (chunké) | Disque | Coût OVH |
|-----|--------------|--------|----------|
| Campus 50 bât | **8 Go** | 100 Go NVMe | ~12€/mois |
| Tertiaire 200 bât | **16 Go** | 250 Go NVMe | ~25€/mois |
| Smart district | **32 Go** | 500 Go NVMe | ~50€/mois |

---

### Architecture hybride recommandée (avec chunking)

```
┌─────────────────────────────────────────────────────────┐
│                    Application                          │
├─────────────────────────────────────────────────────────┤
│  Graphe (topologie, relations)  │  Time-series (mesures)│
│  ─────────────────────────────  │  ────────────────────│
│  PostgreSQL + JSONB             │  TimescaleDB          │
│  Partitionné par building_id    │  Hypertables chunked  │
│                                 │                       │
│  RAM: 2-4 Go (cache chunks)     │  RAM: 4-8 Go          │
│  Disk: 20-100 Go                │  Disk: 100-500 Go     │
│                                 │  + S3 tiered (archive)│
└─────────────────────────────────────────────────────────┘

Total RAM: 8-16 Go pour un parc de 200 bâtiments !
```

## Nouveau profil proposé : "enterprise"

```python
"enterprise": ScaleProfile(
    floors=500,           # 50 bâtiments × 10 étages
    spaces=20_000,        # 400 espaces/bâtiment
    equipments=100_000,   # 2000 équipements/bâtiment
    points=500_000,       # 5 points/équipement moyen
    meters=5_000,         # 100 compteurs/bâtiment
)
```

Avec time-series sur 1 an (optionnel):
```python
timeseries_samples=17_520_000_000  # 500k points × 35040 samples
```

## Conclusion

| Question | Réponse |
|----------|---------|
| RAM pour "small" | 4 Go suffisent |
| RAM pour "enterprise" | 32-64 Go minimum |
| RAM pour worst-case (tout in-memory) | Impossible (pétaoctets) |
| **Architecture viable** | Hybride graphe + time-series DB |
| **Coût mensuel réaliste** | 50-100€/mois VPS OVH |
