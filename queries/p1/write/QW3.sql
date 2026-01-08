-- QW3: Relation Mutation
-- Inserts a new edge/relation between two nodes
-- Parameters: %(source_id)s, %(target_id)s, %(rel_type)s

INSERT INTO p1.edges (source_id, target_id, rel_type)
VALUES (%(source_id)s, %(target_id)s, %(rel_type)s)
ON CONFLICT DO NOTHING;
