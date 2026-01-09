// Q26: Capability Evolution
// Équivalent M1 - Distribution capabilities par type
// Paramètres: $domain

MATCH (eq:Equipment)
WHERE eq.domain = $domain
WITH eq.equipment_type AS equipment_type,
     collect(eq) AS equipments,
     count(eq) AS equipment_count
UNWIND equipments AS eq
UNWIND coalesce(eq.capabilities, []) AS cap
WITH equipment_type, equipment_count, cap, count(*) AS cap_count
ORDER BY equipment_type, cap_count DESC
WITH equipment_type,
     equipment_count,
     collect({capability: cap, count: cap_count}) AS cap_distribution,
     head(collect(cap)) AS most_common
RETURN equipment_type,
       equipment_count,
       cap_distribution AS capabilities_distribution,
       most_common AS most_common_capability,
       toFloat(reduce(total = 0, c IN cap_distribution | total + c.count)) / equipment_count AS avg_capabilities
ORDER BY equipment_count DESC;
