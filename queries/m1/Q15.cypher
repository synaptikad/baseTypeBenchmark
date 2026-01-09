// Q15: Warranty Expiry
// Status: DEGRADED pour M1/M2
// Note: Suppose que metadata_warranty_end est exporté
// Paramètres: $days_ahead, $reference_date (date string YYYY-MM-DD)

MATCH (eq:Equipment)
WHERE eq.metadata_warranty_end IS NOT NULL
WITH eq,
     date(eq.metadata_warranty_end) AS warranty_date,
     date($reference_date) AS ref_date
WHERE warranty_date <= ref_date + duration({day: $days_ahead})
  AND warranty_date >= ref_date
RETURN
    eq.id AS equipment_id,
    eq.name,
    eq.equipment_type,
    warranty_date AS warranty_end,
    (warranty_date - ref_date).day AS days_remaining
ORDER BY days_remaining, equipment_id;
