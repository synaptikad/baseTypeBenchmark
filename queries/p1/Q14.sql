-- Q14: Protocol Query (BACnet)
-- Status: IMPOSSIBLE pour P1
-- Raison: P1 n'a pas de colonne 'protocol' JSONB pour stocker device_id BACnet.
-- Le schema relationnel ne capture pas les métadonnées protocolaires.

SELECT 'IMPOSSIBLE: P1 ne supporte pas les requêtes sur protocol JSONB' AS error;
