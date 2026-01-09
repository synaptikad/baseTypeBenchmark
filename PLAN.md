# Plan V3 - Correctifs Batch 1 ✅ COMPLET

## Corrections appliquées

| # | Fix | Fichier | Status |
|---|-----|---------|--------|
| 1 | O2 Healthcheck | `docker/docker-compose.yml` | ✅ |
| 2 | P1 Q20/Q21 CTE cast `::text[]` | `queries/p1/Q20.sql`, `Q21.sql` | ✅ |
| 3 | P2 Q15/Q18 ajout REFERENCE_DATE | `queries/catalog.yaml` | ✅ |
| 4 | P2 Q22 `properties` → `data` | `queries/p2/Q22.sql` | ✅ |
| 5 | M1 Q7 calcul variance manuel | `queries/m1/Q7.cypher` | ✅ |
| 6 | M1 Q20 `shortestPath()` → `*BFS` | `queries/m1/Q20.cypher` | ✅ |
| 7 | M1 Q21 `allShortestPaths()` → `*ALLSHORTEST` | `queries/m1/Q21.cypher` | ✅ |
| 8 | Paramètres dynamiques | `param_sampler.py` + `gradient.py` | ✅ |

---

## Alignement Dataset → Export → Query

### Structure par paradigme

| Paradigme | Structure | Propriétés |
|-----------|-----------|------------|
| P1 | Tables relationnelles | Colonnes directes |
| P2 | JSONB | `data` contient tout |
| M1/M2 | Graphe aplati | `metadata_*`, `protocol_*`, `calibration_*` |
| O2 | RDF triples | URIs et littéraux |

### Mapping M1/M2 (flatten_jsonb)

- `node.properties.*` → racine (`floor_id`, `equipment_type`, etc.)
- `node.metadata.*` → `metadata_*`
- `node.protocol.*` → `protocol_*`
- `node.calibration.*` → `calibration_*`
- `node.capabilities` → liste native
- `node.tags` → liste native

---

## Syntaxe Memgraph vs Neo4j

| Fonction | Neo4j | Memgraph |
|----------|-------|----------|
| Shortest path | `shortestPath((a)-[*..N]->(b))` | `(a)-[*BFS ..N]->(b)` |
| All shortest | `allShortestPaths(...)` | `(a)-[*ALLSHORTEST ..N]->(b)` |
| K shortest | `SHORTEST K` | `*KSHORTEST \| K` |
| Std dev | `stDev(values)` | Calcul manuel |
| EXISTS | `EXISTS { MATCH }` | ✅ Supporté |
| duration() | `duration({days: N})` | ✅ Supporté (ISO 8601) |

---

## Paramètres dynamiques

### Nouveau: `param_sampler.py`

```python
class ParamSampler:
    """Échantillonne IDs valides depuis la DB chargée."""

    def sample(self) -> SampledParams:
        # Extrait: building_id, floor_id, space_id,
        #          equipment_id, meter_id, ups_id,
        #          tenant_id, point_id, etc.
```

### Stratégie

1. Au démarrage du gradient, `_init_param_sampler()` extrait des IDs
2. `_get_default_params()` utilise ces IDs dynamiques
3. Fallback vers `golden_answers.yaml` si sampling échoue

---

## Fichiers modifiés

```
docker/docker-compose.yml
queries/p1/Q20.sql
queries/p1/Q21.sql
queries/p2/Q22.sql
queries/m1/Q7.cypher
queries/m1/Q20.cypher
queries/m1/Q21.cypher
queries/catalog.yaml
src/basetype_benchmark/runner/core/param_sampler.py (nouveau)
src/basetype_benchmark/runner/ram/gradient.py
```

---

## Prochaines étapes

1. **Tester** avec `python run.py` sur small-1m
2. **Valider** O2 se connecte
3. **Vérifier** moins de 0 rows avec params dynamiques
4. **Identifier** erreurs M1/M2 restantes
