# Analyse d'Alignement: Expected Answers vs Queries

## Contexte

Le benchmark génère :
1. **Dataset** (nodes, edges, timeseries) → exporté vers chaque moteur
2. **queries_params.yaml** → paramètres extraits du dataset
3. **expected_answers.json** → **GROUND TRUTH** calculé directement sur les données générées

Les queries sont exécutées par chaque paradigme, puis les résultats raw sont normalisés et comparés aux expected answers.

---

## Résumé Exécutif

| Query | Qui doit changer ? | Raison métier |
|-------|-------------------|---------------|
| Q3 | **QUERY** | "Serves" ≠ "Located in" sémantiquement |
| Q4 | **EXPECTED** | `quantity` est plus sémantique que `"temp" in name` |
| Q6 | **NORMALIZER** | Format timestamp technique, pas sémantique |
| Q8/Q9 | **INVESTIGATION** | Données manquantes ? |
| Q10 | **INVESTIGATION** | Traversée hiérarchique différente ? |
| Q13 | **EXPECTED** | `space_type` est plus sémantique que `"office" in name` |
| Q16 | **EXPORTER/QUERY M1/M2** | Structure tags Neo4j |
| Q19 | **INVESTIGATION** | Format JSON P2/M2 |
| Q20/Q21 | **DEGRADED OK** | Limitation SQL intrinsèque |
| Q23 | **REFORMULER ou SUPPRIMER** | Query "graph-native" sans cas métier clair |

---

## Analyse Détaillée

### Q3: Equipment Serving Space
**Status**: MISMATCH (4 rows vs 1 expected)

**Question métier** : "Quels équipements **desservent** cet espace ?"

**Expected Answer Logic** (`expected_answers.py`):
```python
for edge in self.edges_by_target.get(space_id, []):
    if edge.rel_type == "SERVES":  # UNIQUEMENT SERVES
```

**Query SQL** (`queries/p1/Q3.sql`):
```sql
WHERE ed.rel_type IN ('SERVES', 'LOCATED_IN', 'MONITORS', 'CONTAINS', 'SECURES', 'GRANTS_ACCESS')
```

**Analyse métier** :
- Un équipement qui **dessert** = fournit un service (CVC, éclairage)
- Un capteur **situé dans** un bureau ne le **dessert** pas, il le **monitore**
- `LOCATED_IN` ≠ `SERVES`

**Verdict**: **QUERY DOIT CHANGER**
- Correction : `WHERE ed.rel_type = 'SERVES'`

---

### Q4: Temperature Points on Floor
**Status**: MISMATCH (9 rows vs 14 expected)

**Question métier** : "Quels sont les points de température sur cet étage ?"

**Expected Answer Logic** (`expected_answers.py`):
```python
if point and "temp" in point.name.lower():
```

**Query SQL** (`queries/p1/Q4.sql`):
```sql
WHERE p.quantity = 'temperature'
```

**Analyse métier** :
- En smart building, on veut les points qui **mesurent** la température
- Un point `temp_setpoint_override_status` n'est pas une mesure de température
- La grandeur physique (`quantity`) est plus fiable que le nom

**Verdict**: **EXPECTED DOIT CHANGER**
- Correction : utiliser `quantity == 'temperature'` au lieu de `"temp" in name`

---

### Q6: Hourly Aggregation
**Status**: MISMATCH (168 missing groups)

**Expected Answer** (`Q6.json`):
```json
"2024-01-15T00:00:00": { "avg_value": 17.9917, ... }
```

**Query SQL** (`queries/p1/Q6.sql`):
```sql
time_bucket('1 hour', time) AS hour_bucket
```
PostgreSQL retourne: `2024-01-15 00:00:00+00`

**Analyse** : Les deux sont corrects, format différent (ISO vs PostgreSQL).

**Verdict**: **NORMALIZER DOIT CHANGER**
- Convertir les timestamps en format ISO uniforme

---

### Q8/Q9: Tenant Energy
**Status**: MISMATCH (meter_count=0 vs 1 expected)

**Query SQL** (`queries/p1/Q8.sql`):
```sql
JOIN edges e_mt ON e_mt.target_id = t.id AND e_mt.rel_type = 'METERS_TENANT'
JOIN equipment eq ON eq.id = e_mt.source_id
```

**Expected Answer Logic** (`expected_answers.py`):
```python
for edge in self.edges_by_target.get(tenant_id, []):
    if edge.rel_type == "METERS_TENANT":
        meter_id = edge.source_id
```

**Analyse**: Les deux ont la MÊME logique (meter=source, tenant=target).

**Verdict**: **INVESTIGATION REQUISE**
- Vérifier si les edges `METERS_TENANT` sont générés dans le dataset
- Vérifier si l'export/load préserve ces edges
- Debug : `SELECT * FROM edges WHERE rel_type = 'METERS_TENANT' LIMIT 5;`

---

### Q10: Security Equipment per Space
**Status**: MISMATCH (2 rows attendus, résultat différent)

**Expected Answer** (`Q10.json`):
```json
"space_1_2_1:BadgeReader": 1, "space_1_2_1:IPCamera": 1
```

**Query SQL** (`queries/p1/Q10.sql`):
```sql
eq.equipment_type IN ('BadgeReader', 'IPCamera', 'DoorContact', 'PIRDetector')
```

**Analyse**: Les types correspondent. Hypothèse : différence de traversée hiérarchique.

**Verdict**: **INVESTIGATION REQUISE**
- Vérifier si les espaces sont traversés de la même façon (via Floor vs directement)
- Comparer les chemins de traversée query vs expected

---

### Q12: Building Global Metrics
**Status**: MISMATCH

**Query SQL** (`queries/p1/Q12.sql`):
```sql
WHERE p.building_id = $1
```

**Expected Answer Logic** (`expected_answers.py`):
```python
# Traverse: Building -> Floor -> Space -> Equipment -> Point
```

**Analyse**: La query utilise `building_id` dénormalisé, l'expected traverse le graphe.

**Verdict**: **INVESTIGATION REQUISE**
- Vérifier si `points.building_id` est correctement peuplé lors de l'export

---

### Q13: Office Air Quality
**Status**: MISMATCH (4/4 mais valeurs différentes)

**Question métier** : "Quelle est la qualité d'air dans les **bureaux** ?"

**Expected Answer Logic** (`expected_answers.py`):
```python
if not space or "office" not in space.name.lower():
```

**Query SQL** (`queries/p1/Q13.sql`):
```sql
WHERE s.space_type LIKE 'office%%'
```

**Analyse métier** :
- En smart building, on classe les espaces par **type** (office, meeting_room, corridor)
- Un espace nommé "back_office_storage" n'est pas un bureau
- `space_type` est plus fiable que convention de nommage

**Verdict**: **EXPECTED DOIT CHANGER**
- Correction : utiliser `space_type` au lieu de `"office" in name`

---

### Q16: Semantic Tags (M1/M2 seulement)
**Status**: MISMATCH (0/1142 pour M1/M2)

**Query Cypher** (`queries/m1/Q16.cypher`):
```cypher
MATCH (eq:Equipment)
WHERE eq.tags IS NOT NULL
UNWIND eq.tags AS tag
WHERE toString(tag) STARTS WITH $tag_pattern
```

**Analyse**: En Neo4j, les tags sont peut-être stockés différemment (JSON string vs array natif).

**Verdict**: **EXPORTER ou QUERY M1/M2 DOIT CHANGER**
- Vérifier la structure de `eq.tags` dans Neo4j après export
- Adapter l'exporter OU la query pour parser correctement

---

### Q19: Digital Twin Document
**Status**: MISMATCH pour P2/M2 ("Missing required fields: ['id', 'name', 'type']")

**Query P2** (`queries/p2/Q19.sql`):
```sql
SELECT jsonb_build_object(
    'id', eq.id,
    'name', eq.name,
    'type', eq.data->>'equipment_type',
```

**Analyse**: La query retourne bien `id`, `name`, `type`. Problème de parsing ?

**Verdict**: **INVESTIGATION REQUISE**
- Vérifier le format exact du JSON retourné
- Debug le validateur/normalizer

---

### Q20: Shortest Path
**Status**: DEGRADED/MISMATCH

**Expected**: Path de 2 nœuds `[eq_vav_21, space_1_2_7]`
**Query**: Retourne 1 row (seulement la destination)

**Analyse**: SQL CTE n'a pas d'équivalent natif à `shortestPath()` de Cypher. C'est une **limitation intrinsèque** du paradigme SQL.

**Verdict**: **DEGRADED est le statut correct**
- SQL ne peut pas faire de BFS optimal nativement
- Marquer comme DEGRADED dans validation_rules.yaml

---

### Q21: Electrical Paths (SPOF)
**Status**: DEGRADED/MISMATCH

**Expected**: 323 chemins
**Query**: Retourne beaucoup moins

**Analyse**: L'énumération exhaustive des chemins est une limitation SQL. Le résultat sera **partiel ou approchant**.

**Verdict**: **DEGRADED est le statut correct**
- Confirmer DEGRADED dans validation_rules.yaml

---

### Q23: N-hop Reachability
**Status**: MISMATCH (24-92 rows vs 151 expected)

**Intention originale** : Montrer l'avantage des graphes pour certaines queries (comme Q14-Q19 montrent l'avantage JSONB pour P2).

**Expected Answer Logic** (`expected_answers.py`):
```python
# Traverse TOUS les edges (pas de filtre sur rel_type)
for edge in self.edges_by_source.get(node_id, []):
```

**Query SQL** (`queries/p1/Q23.sql`):
```sql
AND e.rel_type IN ('ADJACENT_TO', 'CONTAINS', 'MONITORS', 'SERVES')
```

**Analyse métier** : "N-hop reachability" sans contexte n'a pas de sens métier clair.

**Options** :
1. **Reformuler** en cas métier : "Failure Impact Analysis" (quels espaces sont affectés si cet équipement tombe ?) avec rel_types `FEEDS`, `SERVES`, `POWERS`
2. **Supprimer** Q23 si pas de cas d'usage réel justifiable

**Verdict**: **REFORMULER ou SUPPRIMER**

---

## Plan d'Action

### Phase 1: Corrections sémantiques (Query)
| Query | Action | Fichiers |
|-------|--------|----------|
| Q3 | `IN (...)` → `= 'SERVES'` | `queries/*/Q3.*` |

### Phase 2: Corrections sémantiques (Expected)
| Query | Action | Fichiers |
|-------|--------|----------|
| Q4 | Utiliser `quantity == 'temperature'` | `expected_answers.py` |
| Q13 | Utiliser `space_type` au lieu de `name` | `expected_answers.py` |

### Phase 3: Normalizer
| Query | Action | Fichiers |
|-------|--------|----------|
| Q6 | Normaliser timestamps en ISO | `normalizer.py` |

### Phase 4: Investigation données
| Query | Action |
|-------|--------|
| Q8/Q9 | Vérifier edges `METERS_TENANT` dans dataset et export |
| Q10 | Comparer traversée hiérarchique query vs expected |
| Q12 | Vérifier `points.building_id` peuplé |
| Q19 | Debug format JSON P2/M2 |

### Phase 5: Neo4j spécifique
| Query | Action | Fichiers |
|-------|--------|----------|
| Q16 | Fix structure tags (exporter ou query) | `exporters/memgraph.py` ou `queries/m1/Q16.cypher` |

### Phase 6: Validation rules
| Query | Action | Fichiers |
|-------|--------|----------|
| Q20 | Ajouter statut DEGRADED pour P1/P2 | `validation_rules.yaml` |
| Q21 | Confirmer statut DEGRADED pour P1/P2 | `validation_rules.yaml` |

### Phase 7: Décision Q23
| Option | Action |
|--------|--------|
| A | Reformuler en "Failure Impact Analysis" avec rel_types métier |
| B | Supprimer Q23 du benchmark |

---

## Checklist

- [ ] Phase 1: Q3 query fix
- [ ] Phase 2: Q4, Q13 expected fixes
- [ ] Phase 3: Q6 normalizer
- [ ] Phase 4: Investigations (Q8/Q9, Q10, Q12, Q19)
- [ ] Phase 5: Q16 Neo4j
- [ ] Phase 6: Q20, Q21 validation rules
- [ ] Phase 7: Décision Q23
