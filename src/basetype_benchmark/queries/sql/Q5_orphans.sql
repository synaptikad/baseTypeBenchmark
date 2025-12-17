-- Q5: Détection des nœuds orphelins (Orphan Nodes Detection)
-- Complexité: Anti-jointures pour détecter les nœuds sans relations entrantes/sortantes
-- Domaines: Topologie globale
-- Use case: Audit de qualité du graphe - identifier les entités non connectées

WITH
-- Nœuds avec au moins une relation sortante
nodes_with_outgoing AS (
    SELECT DISTINCT src_id AS node_id FROM edges
),
-- Nœuds avec au moins une relation entrante
nodes_with_incoming AS (
    SELECT DISTINCT dst_id AS node_id FROM edges
),
-- Nœuds complètement isolés (ni entrante ni sortante)
isolated_nodes AS (
    SELECT n.id, n.type, n.name
    FROM nodes n
    LEFT JOIN nodes_with_outgoing out ON out.node_id = n.id
    LEFT JOIN nodes_with_incoming inc ON inc.node_id = n.id
    WHERE out.node_id IS NULL AND inc.node_id IS NULL
),
-- Nœuds racines (sortantes mais pas entrantes) - normal pour certains types
root_nodes AS (
    SELECT n.id, n.type, n.name
    FROM nodes n
    JOIN nodes_with_outgoing out ON out.node_id = n.id
    LEFT JOIN nodes_with_incoming inc ON inc.node_id = n.id
    WHERE inc.node_id IS NULL
    AND n.type NOT IN ('Site', 'Building', 'Organization')  -- Ces types sont normalement racines
),
-- Nœuds feuilles (entrantes mais pas sortantes) - normal pour Points
leaf_nodes AS (
    SELECT n.id, n.type, n.name
    FROM nodes n
    LEFT JOIN nodes_with_outgoing out ON out.node_id = n.id
    JOIN nodes_with_incoming inc ON inc.node_id = n.id
    WHERE out.node_id IS NULL
    AND n.type NOT IN ('Point', 'Person', 'Vehicle')  -- Ces types sont normalement feuilles
)

-- Résumé des anomalies par type
SELECT
    'isolated' AS anomaly_type,
    type AS node_type,
    COUNT(*) AS count,
    ARRAY_AGG(name ORDER BY name) FILTER (WHERE name IS NOT NULL) AS sample_names
FROM isolated_nodes
GROUP BY type

UNION ALL

SELECT
    'unexpected_root' AS anomaly_type,
    type AS node_type,
    COUNT(*) AS count,
    ARRAY_AGG(name ORDER BY name) FILTER (WHERE name IS NOT NULL) AS sample_names
FROM root_nodes
GROUP BY type

UNION ALL

SELECT
    'unexpected_leaf' AS anomaly_type,
    type AS node_type,
    COUNT(*) AS count,
    ARRAY_AGG(name ORDER BY name) FILTER (WHERE name IS NOT NULL) AS sample_names
FROM leaf_nodes
GROUP BY type

ORDER BY anomaly_type, count DESC;
