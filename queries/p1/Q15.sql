-- Q15: Warranty Expiry
-- Status: IMPOSSIBLE pour P1
-- Raison: P1 n'a pas de colonne 'metadata' JSONB avec warranty_end.
-- Nécessiterait une colonne dédiée warranty_end sur la table equipment.

SELECT 'IMPOSSIBLE: P1 ne supporte pas les requêtes sur metadata JSONB' AS error;
