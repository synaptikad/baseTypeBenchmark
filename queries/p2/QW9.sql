-- QW9: Tenant Move-In
-- Créer relation OCCUPIES et optionnellement METERS_TENANT
-- Paramètres: %(tenant_id)s, %(space_id)s, %(meter_id)s (optionnel)

INSERT INTO edges (source_id, target_id, rel_type)
VALUES (%(tenant_id)s, %(space_id)s, 'OCCUPIES')
ON CONFLICT DO NOTHING;

-- Note: La partie METERS_TENANT doit être gérée par une seconde requête
-- ou par le runner si meter_id est fourni
