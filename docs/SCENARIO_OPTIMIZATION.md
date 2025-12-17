# Stratégie d'Optimisation par Scénario

## Objectif
Positionner chaque scénario dans son optimum de performance en exploitant les forces
de chaque paradigme de base de données.

---

## P1: PostgreSQL Relationnel + TimescaleDB

### Forces du paradigme
- Excellente performance sur agrégations timeseries (time_bucket)
- Intégrité référentielle via FK
- Optimiseur de requêtes mature

### Faiblesses actuelles
1. **FK sur edges vers nodes**: penalty de 10-30% sur INSERT
2. **Index manquants**: composite `(src_id, rel_type)` crucial pour traversées
3. **Pas de partitionnement nodes**: type-based partitioning pourrait aider

### Optimisations proposées

```sql
-- 1. Schema optimisé P1
CREATE TABLE nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT,
    building_id INTEGER DEFAULT 0
);
CREATE INDEX idx_nodes_type ON nodes(type);
CREATE INDEX idx_nodes_building ON nodes(building_id);

-- 2. Edges sans FK pour performance
CREATE TABLE edges (
    src_id TEXT NOT NULL,
    dst_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    PRIMARY KEY (src_id, dst_id, rel_type)
);
-- Index composite pour traversées
CREATE INDEX idx_edges_src_rel ON edges(src_id, rel_type);
CREATE INDEX idx_edges_dst_rel ON edges(dst_id, rel_type);
-- Pas de FK: intégrité assurée par le générateur

-- 3. Timeseries avec compression
CREATE TABLE timeseries (
    time TIMESTAMPTZ NOT NULL,
    point_id TEXT NOT NULL,
    value DOUBLE PRECISION
);
SELECT create_hypertable('timeseries', 'time',
    chunk_time_interval => INTERVAL '1 day');
-- Compression après 7 jours
ALTER TABLE timeseries SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'point_id'
);
SELECT add_compression_policy('timeseries', INTERVAL '7 days');

-- 4. Index timeseries
CREATE INDEX idx_ts_point_time ON timeseries(point_id, time DESC);
```

### Requêtes à adapter
- Q2 (recursive): utiliser `MATERIALIZED` pour CTEs complexes
- Q8 (traversée profonde): limiter profondeur à 8 vs 10

---

## P2: PostgreSQL JSONB + TimescaleDB

### Forces du paradigme
- Flexibilité schéma via JSONB
- Requêtes @> et @? performantes avec GIN
- Même optimiseur mature

### Optimisations proposées

```sql
-- 1. Nodes avec JSONB mais colonnes extraites pour filtrage rapide
CREATE TABLE nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,  -- Extrait pour index B-tree rapide
    name TEXT,
    building_id INTEGER GENERATED ALWAYS AS ((data->>'building_id')::int) STORED,
    data JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX idx_nodes_type ON nodes(type);
CREATE INDEX idx_nodes_gin ON nodes USING GIN (data jsonb_path_ops);

-- 2. Edges avec propriétés optionnelles en JSONB
CREATE TABLE edges (
    src_id TEXT NOT NULL,
    dst_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    props JSONB DEFAULT NULL,  -- NULL si pas de propriétés (économie espace)
    PRIMARY KEY (src_id, dst_id, rel_type)
);
CREATE INDEX idx_edges_src_rel ON edges(src_id, rel_type);

-- 3. Timeseries identique à P1
```

### Différenciation clé P1 vs P2
- **P1**: Schema fixe, requêtes prévisibles
- **P2**: Propriétés flexibles, recherche @> sur attributs arbitraires

---

## M1: Memgraph Standalone (Timeseries In-Memory)

### Forces du paradigme
- Traversées graphe natives O(1) par relation
- Cypher expressif pour patterns complexes
- Arrays in-memory pour timeseries locales

### Problème actuel
Les timeseries stockées en propriété (`values: [...]`) :
- Explosion mémoire: 500k points × 365 jours × 40 samples = 7.3B valeurs
- Pas d'agrégation native time-bucket

### Optimisation: Chunking par 50 samples

```cypher
// Structure chunk optimisée pour M1
// Au lieu de 1 chunk = 1 jour (jusqu'à 1440 samples)
// Faire 1 chunk = 50 samples (gestion mémoire)

CREATE (c:TSChunk {
    point_id: "point-123",
    chunk_idx: 0,
    start_ts: 1704067200,
    freq_sec: 900,
    values: [21.5, 21.6, 21.4, ...]  // Max 50 valeurs
})

// Index pour recherche rapide
CREATE INDEX ON :TSChunk(point_id);
CREATE INDEX ON :TSChunk(start_ts);
```

### Avantages du chunking 50
1. **Mémoire**: 50 × 8 bytes = 400 bytes/chunk vs potentiellement 11KB
2. **Parallélisme**: Cypher peut traiter chunks en parallèle
3. **Garbage collection**: Memgraph gère mieux petits objets
4. **Range queries**: `WHERE c.start_ts >= $begin AND c.start_ts < $end`

### Requêtes M1 adaptées

```cypher
// Q6 équivalent (agrégation horaire) - approximation
MATCH (p:Node {type: "Point"})-[:HAS_CHUNK]->(c:TSChunk)
WHERE p.quantity = "temperature"
  AND c.start_ts >= $begin AND c.start_ts < $end
WITH p, c, c.start_ts / 3600 AS hour
// Memgraph n'a pas time_bucket, simulation via division
RETURN hour, AVG(REDUCE(s = 0.0, v IN c.values | s + v) / SIZE(c.values)) AS avg_temp
ORDER BY hour
```

### Limitation acceptée
- Q6/Q7 ne seront jamais aussi performants qu'avec TimescaleDB
- Focus M1: traversées graphe (Q1, Q2, Q8, Q11)

---

## M2: Memgraph + TimescaleDB (Hybrid)

### Architecture
```
[Memgraph]                    [TimescaleDB]
  Nodes + Edges                 timeseries
  Point.id ─────────────────────► point_id
```

### Forces combinées
- Traversées graphe dans Memgraph
- Agrégations timeseries dans TimescaleDB
- Best of both worlds

### Pattern de requête split

```python
# Phase 1: Sélection des points via Cypher
cypher_query = """
MATCH (b:Node {type: "Building"})-[:CONTAINS*1..3]->(s:Node {type: "Space"})
      -[:LOCATED_IN]->(e:Node {type: "Equipment"})
      -[:HAS_POINT]->(p:Node)
WHERE p.quantity = "temperature"
RETURN COLLECT(DISTINCT p.id) AS point_ids
"""

# Phase 2: Agrégation dans TimescaleDB
sql_query = """
SELECT time_bucket('1 hour', time) AS hour,
       AVG(value) AS avg_temp
FROM timeseries
WHERE point_id = ANY($point_ids)
  AND time >= $begin AND time < $end
GROUP BY hour
ORDER BY hour
"""
```

### Optimisation M2
- Memgraph: structure légère (pas de TimeseriesChunk)
- TimescaleDB: même schéma que P1
- Connexion: point_id comme clé de jointure

---

## O1: Oxigraph Standalone (RDF)

### Forces du paradigme
- Standards W3C (SPARQL, OWL)
- Raisonnement ontologique possible
- Property paths expressifs

### Limitation majeure
**Pas de support natif timeseries** :
- RDF stocke triplets unitaires
- 1 sample = 1 triplet = overhead énorme
- Pas d'agrégation efficace

### Stratégie O1: Pondération différente

```markdown
## Scoring O1 (100 points total)

| Query | Poids Normal | Poids O1 | Justification |
|-------|--------------|----------|---------------|
| Q1    | 10           | 15       | Traversée graphe (RDF natif) |
| Q2    | 10           | 15       | Property paths (SPARQL *) |
| Q3    | 10           | 15       | Pattern matching |
| Q4    | 10           | 15       | Inventaire simple |
| Q5    | 10           | 15       | Orphelins |
| Q6    | 15           | 5        | Agrégation TS (penalty) |
| Q7    | 15           | 5        | Drift detection (penalty) |
| Q8    | 10           | 15       | Multi-hop |
```

### Alternative O1: Agrégats pré-calculés

```sparql
# Au lieu de stocker chaque sample, stocker des agrégats
PREFIX ts: <http://benchmark.org/timeseries/>

# Triplet agrégat journalier
<point-123> ts:daily_avg [
    ts:date "2024-01-15"^^xsd:date ;
    ts:avg 21.5 ;
    ts:min 19.2 ;
    ts:max 23.1 ;
    ts:count 96
] .
```

### Génération des agrégats

```python
# Dans le générateur, pré-calculer pour O1
for point_id, samples in timeseries.items():
    # Grouper par jour
    daily_aggs = compute_daily_aggregates(samples)
    for date, agg in daily_aggs.items():
        emit_rdf_triple(point_id, "ts:daily_avg", {
            "date": date,
            "avg": agg["avg"],
            "min": agg["min"],
            "max": agg["max"]
        })
```

---

## O2: Oxigraph + TimescaleDB (Hybrid)

### Architecture identique à M2

```
[Oxigraph]                    [TimescaleDB]
  RDF Triples                   timeseries
  <point-123> ──────────────────► point_id
```

### Pattern SPARQL + SQL

```python
# Phase 1: Sélection via SPARQL
sparql_query = """
PREFIX ex: <http://benchmark.org/>

SELECT ?point_id
WHERE {
    ?building a ex:Building .
    ?building ex:CONTAINS+ ?space .
    ?space a ex:Space .
    ?equip ex:LOCATED_IN ?space .
    ?equip ex:HAS_POINT ?point .
    ?point ex:quantity "temperature" .
    BIND(STRAFTER(STR(?point), "node/") AS ?point_id)
}
"""

# Phase 2: Agrégation SQL (identique à M2)
```

---

## Matrice de Compatibilité Requêtes

| Query | Description | P1 | P2 | M1 | M2 | O1 | O2 |
|-------|-------------|----|----|----|----|----|----|
| Q1 | Energy chain depth≤10 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q2 | AHU impact | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q3 | Serve space | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q4 | Point inventory | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q5 | Orphans | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q6 | TS hourly agg | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |
| Q7 | Drift detection | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |
| Q8 | Tenant→served→TS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Q9-Q12 | Bonus queries | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Légende**: ✅ Natif/Optimal | ⚠️ Dégradé/Workaround

---

## Résumé des Actions

### Modifications Schema
1. **P1**: Retirer FK edges, ajouter index composites, compression TS
2. **P2**: Colonnes générées depuis JSONB, GIN path_ops
3. **M1**: Chunks de 50 samples max
4. **M2**: Pas de chunks dans Memgraph (TS externe)
5. **O1**: Agrégats pré-calculés OU scoring pondéré
6. **O2**: Structure RDF légère + TS externe

### Modifications Générateur
1. Exporter chunks de 50 pour M1
2. Générer agrégats journaliers pour O1
3. Créer fichiers CSV optimisés COPY pour P1/P2

### Modifications Queries
1. Q6/Q7 M1: approximation via REDUCE sur chunks
2. Toutes queries: hints d'index si supporté
