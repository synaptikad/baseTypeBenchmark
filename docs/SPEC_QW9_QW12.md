# Spécification QW9-QW12 + Q35-Q37

> Spec pour implémentation des Write Queries graph-native et leurs Queries de vérification

**Objectif** : Équilibrer le benchmark en ajoutant des writes où M1/M2 sont NATIVE (actuellement 3 NATIVE sur 8, cible 7 sur 12).

**Justification académique** : Les queries QW9-QW12 représentent des cas d'usage de gestion locative actuellement traités par des systèmes externes (ERP, GMAO). Leur inclusion vise à équilibrer le benchmark en testant des patterns de mutation relationnelle où les moteurs graph sont natifs, sans prétendre que ces cas sont aujourd'hui implémentés dans les middlewares smart building.

---

## 1. Vue d'Ensemble

### 1.1 Nouvelles Queries

| ID | Nom | Type | Relations | M1/M2 | P1/P2 |
|----|-----|------|-----------|-------|-------|
| QW9 | Tenant Move-In | Write | OCCUPIES, METERS_TENANT | NATIVE | NATIVE |
| QW10 | Tenant Move-Out | Write | OCCUPIES | NATIVE | NATIVE |
| QW11 | Space Reassignment | Write | OCCUPIES | NATIVE | NATIVE |
| QW12 | Tenant Merge | Write | OCCUPIES, METERS_TENANT | NATIVE | NATIVE |
| Q35 | Verify Tenant Spaces | Read (vérif) | OCCUPIES | NATIVE | NATIVE |
| Q36 | Verify Tenant Meters | Read (vérif) | METERS_TENANT | NATIVE | NATIVE |
| Q37 | Verify Tenant Consolidation | Read (vérif) | OCCUPIES, METERS_TENANT | NATIVE | NATIVE |

### 1.2 Mapping Write → Query de Vérification

| Write | Query Vérification | Ce qu'on vérifie |
|-------|-------------------|------------------|
| QW9 (Move-In) | Q35 + Q36 | Espace ajouté + Compteur associé |
| QW10 (Move-Out) | Q35 | Espace retiré |
| QW11 (Reassignment) | Q35 (x2) | Ancien tenant perd l'espace, nouveau l'a |
| QW12 (Merge) | Q37 | Toutes relations transférées au target |

---

## 2. Spécifications Détaillées des Writes

### 2.1 QW9 - Tenant Move-In

**Intention** : Un nouveau locataire s'installe dans un espace. Créer la relation OCCUPIES et optionnellement METERS_TENANT vers un sous-compteur.

**Use case** : Signature de bail, emménagement.

**Paramètres** :

| Param | Type | Description | Exemple |
|-------|------|-------------|---------|
| TENANT_ID | string | ID du locataire | `tenant_3` |
| SPACE_ID | string | ID de l'espace à occuper | `space_floor1_b2_5` |
| METER_ID | string (optionnel) | ID du sous-compteur à associer | `eq_submeter_tenant_3` |

**Pré-conditions** :
- Le tenant existe
- L'espace existe
- L'espace n'est PAS déjà occupé par ce tenant (éviter doublon)
- Le meter existe (si fourni)

**Post-conditions** :
- Relation `(tenant)-[:OCCUPIES]->(space)` créée
- Relation `(meter)-[:METERS_TENANT]->(tenant)` créée (si METER_ID fourni)

**Implémentation par paradigme** :

```sql
-- P1/P2
INSERT INTO edges (source_id, target_id, rel_type)
VALUES (%(tenant_id)s, %(space_id)s, 'OCCUPIES')
ON CONFLICT DO NOTHING;

-- Si METER_ID fourni :
INSERT INTO edges (source_id, target_id, rel_type)
VALUES (%(meter_id)s, %(tenant_id)s, 'METERS_TENANT')
ON CONFLICT DO NOTHING;
```

```cypher
// M1/M2
MATCH (t:Tenant {id: $tenant_id})
MATCH (s:Space {id: $space_id})
MERGE (t)-[:OCCUPIES]->(s)
WITH t
MATCH (m:Equipment {id: $meter_id})
WHERE $meter_id IS NOT NULL
MERGE (m)-[:METERS_TENANT]->(t)
RETURN t.id AS tenant_id, count(*) AS relations_created
```

**Result schema** :
```yaml
columns:
  - {name: tenant_id, type: string}
  - {name: relations_created, type: integer}
```

---

### 2.2 QW10 - Tenant Move-Out

**Intention** : Un locataire quitte un espace. Supprimer la relation OCCUPIES.

**Use case** : Fin de bail, déménagement.

**Paramètres** :

| Param | Type | Description | Exemple |
|-------|------|-------------|---------|
| TENANT_ID | string | ID du locataire | `tenant_3` |
| SPACE_ID | string | ID de l'espace libéré | `space_floor1_b2_5` |

**Pré-conditions** :
- La relation `(tenant)-[:OCCUPIES]->(space)` existe

**Post-conditions** :
- Relation `(tenant)-[:OCCUPIES]->(space)` supprimée
- Note : METERS_TENANT n'est PAS supprimé (le compteur reste associé pour historique facturation)

**Implémentation par paradigme** :

```sql
-- P1/P2
DELETE FROM edges
WHERE source_id = %(tenant_id)s
  AND target_id = %(space_id)s
  AND rel_type = 'OCCUPIES';
```

```cypher
// M1/M2
MATCH (t:Tenant {id: $tenant_id})-[r:OCCUPIES]->(s:Space {id: $space_id})
DELETE r
RETURN t.id AS tenant_id, s.id AS space_id, 1 AS relations_deleted
```

**Result schema** :
```yaml
columns:
  - {name: tenant_id, type: string}
  - {name: space_id, type: string}
  - {name: relations_deleted, type: integer}
```

---

### 2.3 QW11 - Space Reassignment

**Intention** : Réaffecter un espace d'un locataire A vers un locataire B. Opération atomique.

**Use case** : Changement d'affectation, restructuration des baux.

**Paramètres** :

| Param | Type | Description | Exemple |
|-------|------|-------------|---------|
| SPACE_ID | string | ID de l'espace à réaffecter | `space_floor1_b2_5` |
| OLD_TENANT_ID | string | ID du locataire actuel | `tenant_2` |
| NEW_TENANT_ID | string | ID du nouveau locataire | `tenant_3` |

**Pré-conditions** :
- La relation `(old_tenant)-[:OCCUPIES]->(space)` existe
- Le new_tenant existe
- old_tenant ≠ new_tenant

**Post-conditions** :
- Relation `(old_tenant)-[:OCCUPIES]->(space)` supprimée
- Relation `(new_tenant)-[:OCCUPIES]->(space)` créée

**Implémentation par paradigme** :

```sql
-- P1/P2 (transaction)
BEGIN;
DELETE FROM edges
WHERE source_id = %(old_tenant_id)s
  AND target_id = %(space_id)s
  AND rel_type = 'OCCUPIES';

INSERT INTO edges (source_id, target_id, rel_type)
VALUES (%(new_tenant_id)s, %(space_id)s, 'OCCUPIES');
COMMIT;
```

```cypher
// M1/M2
MATCH (old:Tenant {id: $old_tenant_id})-[r:OCCUPIES]->(s:Space {id: $space_id})
DELETE r
WITH s
MATCH (new:Tenant {id: $new_tenant_id})
MERGE (new)-[:OCCUPIES]->(s)
RETURN s.id AS space_id, $old_tenant_id AS old_tenant, $new_tenant_id AS new_tenant
```

**Result schema** :
```yaml
columns:
  - {name: space_id, type: string}
  - {name: old_tenant_id, type: string}
  - {name: new_tenant_id, type: string}
  - {name: reassigned, type: boolean}
```

---

### 2.4 QW12 - Tenant Merge

**Intention** : Fusionner deux locataires. Transférer toutes les relations OCCUPIES et METERS_TENANT du source vers le target.

**Use case** : Rachat d'entreprise, consolidation entités juridiques.

**Paramètres** :

| Param | Type | Description | Exemple |
|-------|------|-------------|---------|
| SOURCE_TENANT_ID | string | ID du locataire à absorber | `tenant_2` |
| TARGET_TENANT_ID | string | ID du locataire qui absorbe | `tenant_1` |

**Pré-conditions** :
- Les deux tenants existent
- source ≠ target

**Post-conditions** :
- Toutes les relations `(source)-[:OCCUPIES]->(space)` deviennent `(target)-[:OCCUPIES]->(space)`
- Toutes les relations `(meter)-[:METERS_TENANT]->(source)` deviennent `(meter)-[:METERS_TENANT]->(target)`
- Le node source reste (pas de suppression de node) mais n'a plus de relations

**Implémentation par paradigme** :

```sql
-- P1/P2 (transaction)
BEGIN;
-- Transférer OCCUPIES
UPDATE edges
SET source_id = %(target_tenant_id)s
WHERE source_id = %(source_tenant_id)s
  AND rel_type = 'OCCUPIES';

-- Transférer METERS_TENANT
UPDATE edges
SET target_id = %(target_tenant_id)s
WHERE target_id = %(source_tenant_id)s
  AND rel_type = 'METERS_TENANT';
COMMIT;
```

```cypher
// M1/M2
// Étape 1: Transférer OCCUPIES
MATCH (src:Tenant {id: $source_tenant_id})-[r:OCCUPIES]->(s:Space)
MATCH (tgt:Tenant {id: $target_tenant_id})
MERGE (tgt)-[:OCCUPIES]->(s)
DELETE r
WITH count(*) AS spaces_transferred

// Étape 2: Transférer METERS_TENANT
MATCH (m:Equipment)-[r:METERS_TENANT]->(src:Tenant {id: $source_tenant_id})
MATCH (tgt:Tenant {id: $target_tenant_id})
MERGE (m)-[:METERS_TENANT]->(tgt)
DELETE r
RETURN spaces_transferred, count(*) AS meters_transferred
```

**Result schema** :
```yaml
columns:
  - {name: source_tenant_id, type: string}
  - {name: target_tenant_id, type: string}
  - {name: spaces_transferred, type: integer}
  - {name: meters_transferred, type: integer}
```

---

## 3. Spécifications Détaillées des Queries de Vérification

### 3.1 Q35 - Verify Tenant Spaces

**Intention** : Lister tous les espaces occupés par un locataire donné.

**Paramètres** :

| Param | Type | Description | Exemple |
|-------|------|-------------|---------|
| TENANT_ID | string | ID du locataire | `tenant_3` |

**Implémentation par paradigme** :

```sql
-- P1/P2
SELECT
    e.target_id AS space_id,
    n.name AS space_name,
    n.node_type AS space_type
FROM edges e
JOIN nodes n ON n.id = e.target_id
WHERE e.source_id = $1
  AND e.rel_type = 'OCCUPIES'
ORDER BY space_id;
```

```cypher
// M1/M2
MATCH (t:Tenant {id: $tenant_id})-[:OCCUPIES]->(s:Space)
RETURN s.id AS space_id, s.name AS space_name, labels(s)[0] AS space_type
ORDER BY space_id
```

**Result schema** :
```yaml
columns:
  - {name: space_id, type: string}
  - {name: space_name, type: string}
  - {name: space_type, type: string}
order_by: [space_id]
```

**Expected Answer** :
- `answer_type`: "set"
- `semantic_content`: Set des space_id occupés

---

### 3.2 Q36 - Verify Tenant Meters

**Intention** : Lister tous les compteurs associés à un locataire (via METERS_TENANT).

**Paramètres** :

| Param | Type | Description | Exemple |
|-------|------|-------------|---------|
| TENANT_ID | string | ID du locataire | `tenant_3` |

**Implémentation par paradigme** :

```sql
-- P1/P2
SELECT
    e.source_id AS meter_id,
    n.name AS meter_name,
    n.node_type AS meter_type
FROM edges e
JOIN nodes n ON n.id = e.source_id
WHERE e.target_id = $1
  AND e.rel_type = 'METERS_TENANT'
ORDER BY meter_id;
```

```cypher
// M1/M2
MATCH (m:Equipment)-[:METERS_TENANT]->(t:Tenant {id: $tenant_id})
RETURN m.id AS meter_id, m.name AS meter_name, labels(m)[0] AS meter_type
ORDER BY meter_id
```

**Result schema** :
```yaml
columns:
  - {name: meter_id, type: string}
  - {name: meter_name, type: string}
  - {name: meter_type, type: string}
order_by: [meter_id]
```

**Expected Answer** :
- `answer_type`: "set"
- `semantic_content`: Set des meter_id associés

---

### 3.3 Q37 - Verify Tenant Consolidation

**Intention** : Après un merge, vérifier le nombre total de relations du tenant target.

**Paramètres** :

| Param | Type | Description | Exemple |
|-------|------|-------------|---------|
| TENANT_ID | string | ID du tenant (target après merge) | `tenant_1` |

**Implémentation par paradigme** :

```sql
-- P1/P2
SELECT
    $1 AS tenant_id,
    COUNT(*) FILTER (WHERE e.rel_type = 'OCCUPIES' AND e.source_id = $1) AS occupied_spaces,
    COUNT(*) FILTER (WHERE e.rel_type = 'METERS_TENANT' AND e.target_id = $1) AS associated_meters
FROM edges e
WHERE (e.source_id = $1 AND e.rel_type = 'OCCUPIES')
   OR (e.target_id = $1 AND e.rel_type = 'METERS_TENANT');
```

```cypher
// M1/M2
MATCH (t:Tenant {id: $tenant_id})
OPTIONAL MATCH (t)-[o:OCCUPIES]->(:Space)
OPTIONAL MATCH (:Equipment)-[m:METERS_TENANT]->(t)
RETURN t.id AS tenant_id,
       count(DISTINCT o) AS occupied_spaces,
       count(DISTINCT m) AS associated_meters
```

**Result schema** :
```yaml
columns:
  - {name: tenant_id, type: string}
  - {name: occupied_spaces, type: integer}
  - {name: associated_meters, type: integer}
```

**Expected Answer** :
- `answer_type`: "aggregate"
- `semantic_content`: Dict avec counts

---

## 4. Modifications Fichiers

### 4.1 queries/catalog.yaml

Ajouter dans la section `categories` :
```yaml
categories:
  # ... existantes ...
  tenant_write:
    description: "Mutations tenant/space (graph-native)"
    queries: [QW9, QW10, QW11, QW12]
  tenant_validation:
    description: "Vérification post-write tenant"
    queries: [Q35, Q36, Q37]
```

Ajouter les 7 nouvelles queries dans la section `queries` (voir specs ci-dessus).

### 4.2 src/basetype_benchmark/runner/core/param_sampler.py

Ajouter à `SampledParams` :
```python
@dataclass
class SampledParams:
    # ... existants ...

    # QW9-QW12 / Q35-Q37 specific
    tenant_id_alt: Optional[str] = None  # Pour QW11/QW12 (second tenant)
```

Ajouter à `get_params_for_query()` :
```python
"QW9": {
    "TENANT_ID": sampled.tenant_id,
    "SPACE_ID": sampled.space_id,
    "METER_ID": sampled.meter_id,
},
"QW10": {
    "TENANT_ID": sampled.tenant_id,
    "SPACE_ID": sampled.space_id,
},
"QW11": {
    "SPACE_ID": sampled.space_id,
    "OLD_TENANT_ID": sampled.tenant_id,
    "NEW_TENANT_ID": sampled.tenant_id_alt,
},
"QW12": {
    "SOURCE_TENANT_ID": sampled.tenant_id,
    "TARGET_TENANT_ID": sampled.tenant_id_alt,
},
"Q35": {"TENANT_ID": sampled.tenant_id},
"Q36": {"TENANT_ID": sampled.tenant_id},
"Q37": {"TENANT_ID": sampled.tenant_id},
```

Ajouter dans `sample()` la sélection de `tenant_id_alt` :
```python
# Sélectionner un second tenant différent du premier
all_tenants = [...]  # Query SELECT id FROM nodes WHERE node_type = 'Tenant'
sampled.tenant_id = random.choice(all_tenants)
remaining = [t for t in all_tenants if t != sampled.tenant_id]
sampled.tenant_id_alt = random.choice(remaining) if remaining else None
```

### 4.3 src/basetype_benchmark/dataset/expected_answers.py

Ajouter les méthodes de génération :
```python
def _gen_q35(self, params: dict[str, Any]) -> ExpectedAnswer:
    """Verify Tenant Spaces - espaces occupés par un tenant."""
    tenant_id = params.get("TENANT_ID") or params.get("tenant_id")
    if not tenant_id:
        return None

    occupied_spaces = set()
    full_rows = []

    for edge in self.edges:
        if edge.source_id == tenant_id and edge.rel_type == "OCCUPIES":
            space_id = edge.target_id
            occupied_spaces.add(space_id)
            space = self.nodes_by_id.get(space_id)
            full_rows.append({
                "space_id": space_id,
                "space_name": space.name if space else "",
                "space_type": space.node_type if space else "",
            })

    full_rows.sort(key=lambda x: x["space_id"])

    return ExpectedAnswer(
        query_id="Q35",
        parameters={"tenant_id": tenant_id},
        answer_type="set",
        semantic_content=occupied_spaces,
        row_count=len(occupied_spaces),
        content_hash=self._compute_hash(sorted(occupied_spaces)),
        full_rows=full_rows,
    )

def _gen_q36(self, params: dict[str, Any]) -> ExpectedAnswer:
    """Verify Tenant Meters - compteurs associés à un tenant."""
    tenant_id = params.get("TENANT_ID") or params.get("tenant_id")
    if not tenant_id:
        return None

    associated_meters = set()
    full_rows = []

    for edge in self.edges:
        if edge.target_id == tenant_id and edge.rel_type == "METERS_TENANT":
            meter_id = edge.source_id
            associated_meters.add(meter_id)
            meter = self.nodes_by_id.get(meter_id)
            full_rows.append({
                "meter_id": meter_id,
                "meter_name": meter.name if meter else "",
                "meter_type": meter.node_type if meter else "",
            })

    full_rows.sort(key=lambda x: x["meter_id"])

    return ExpectedAnswer(
        query_id="Q36",
        parameters={"tenant_id": tenant_id},
        answer_type="set",
        semantic_content=associated_meters,
        row_count=len(associated_meters),
        content_hash=self._compute_hash(sorted(associated_meters)),
        full_rows=full_rows,
    )

def _gen_q37(self, params: dict[str, Any]) -> ExpectedAnswer:
    """Verify Tenant Consolidation - counts post-merge."""
    tenant_id = params.get("TENANT_ID") or params.get("tenant_id")
    if not tenant_id:
        return None

    occupied_count = 0
    metered_count = 0

    for edge in self.edges:
        if edge.source_id == tenant_id and edge.rel_type == "OCCUPIES":
            occupied_count += 1
        if edge.target_id == tenant_id and edge.rel_type == "METERS_TENANT":
            metered_count += 1

    semantic = {
        "occupied_spaces": occupied_count,
        "associated_meters": metered_count,
        "total_relations": occupied_count + metered_count,
    }

    return ExpectedAnswer(
        query_id="Q37",
        parameters={"tenant_id": tenant_id},
        answer_type="aggregate",
        semantic_content=semantic,
        row_count=1,
        content_hash=self._compute_hash(semantic),
        full_rows=[{
            "tenant_id": tenant_id,
            "occupied_spaces": occupied_count,
            "associated_meters": metered_count,
        }],
    )
```

Ajouter au mapping `query_methods` :
```python
self.query_methods = [
    # ... existantes ...
    ("Q35", self._gen_q35),
    ("Q36", self._gen_q36),
    ("Q37", self._gen_q37),
]
```

### 4.4 Fichiers Queries SQL/Cypher

Créer les fichiers suivants :

```
queries/
├── p1/
│   ├── QW9.sql
│   ├── QW10.sql
│   ├── QW11.sql
│   ├── QW12.sql
│   ├── Q35.sql
│   ├── Q36.sql
│   └── Q37.sql
├── p2/
│   ├── QW9.sql   (identique P1)
│   ├── QW10.sql  (identique P1)
│   ├── QW11.sql  (identique P1)
│   ├── QW12.sql  (identique P1)
│   ├── Q35.sql   (identique P1)
│   ├── Q36.sql   (identique P1)
│   └── Q37.sql   (identique P1)
├── m1/
│   ├── QW9.cypher
│   ├── QW10.cypher
│   ├── QW11.cypher
│   ├── QW12.cypher
│   ├── Q35.cypher
│   ├── Q36.cypher
│   └── Q37.cypher
└── m2/
    └── graph/
        ├── QW9.cypher  (identique M1)
        ├── QW10.cypher (identique M1)
        ├── QW11.cypher (identique M1)
        ├── QW12.cypher (identique M1)
        ├── Q35.cypher  (identique M1)
        ├── Q36.cypher  (identique M1)
        └── Q37.cypher  (identique M1)
```

### 4.5 data/write_payloads.yaml

Ajouter les payloads pour QW9-QW12 :
```yaml
QW9:
  description: "Tenant Move-In"
  payloads:
    - tenant_id: "tenant_3"
      space_id: "space_floor1_b2_5"
      meter_id: "eq_submeter_tenant_3"

QW10:
  description: "Tenant Move-Out"
  payloads:
    - tenant_id: "tenant_3"
      space_id: "space_floor1_b2_5"

QW11:
  description: "Space Reassignment"
  payloads:
    - space_id: "space_floor1_b2_5"
      old_tenant_id: "tenant_2"
      new_tenant_id: "tenant_3"

QW12:
  description: "Tenant Merge"
  payloads:
    - source_tenant_id: "tenant_2"
      target_tenant_id: "tenant_1"
```

---

## 5. Validation

### 5.1 Tests Unitaires

Pour chaque QW, vérifier :
1. Exécution sans erreur
2. Q de vérification retourne le résultat attendu après QW
3. Idempotence (QW9 avec MERGE/ON CONFLICT)

### 5.2 Séquence de Test

```
1. Q35(tenant_3) → [] (pas d'espaces)
2. QW9(tenant_3, space_X, meter_Y) → OK
3. Q35(tenant_3) → [space_X]
4. Q36(tenant_3) → [meter_Y]
5. QW10(tenant_3, space_X) → OK
6. Q35(tenant_3) → []
7. Q36(tenant_3) → [meter_Y] (compteur reste)
```

### 5.3 Équilibre Final

| Paradigme | Avant | Après | NATIVE % |
|-----------|-------|-------|----------|
| P2 | 8/8 | 12/12 | 100% |
| M1 | 3/8 | 7/12 | 58% |
| M2 | 3/8 | 7/12 | 58% |
| P1 | 2/8 | 6/12 | 50% |

---

## 6. Notes Importantes

1. **Pas de suppression de node** : QW12 ne supprime pas le tenant source, il transfère juste les relations. Le node reste pour historique.

2. **METERS_TENANT persiste** : QW10 ne supprime pas METERS_TENANT pour garder l'historique de facturation.

3. **Transactions** : QW11 et QW12 en SQL doivent être dans une transaction pour atomicité.

4. **Paramètres dynamiques** : Les IDs dans write_payloads.yaml sont des exemples. Le param_sampler doit générer des IDs valides depuis le dataset.

5. **O2 (Oxigraph)** : Non spécifié car O2 utilise SPARQL qui n'a pas d'opérations de mutation standard (pas de DELETE/INSERT DATA unifié). Marquer DEGRADED ou IMPOSSIBLE selon l'implémentation.

---

*Spec version: 1.0*
*Date: 2026-01-12*
*Auteur: Claude + User*
