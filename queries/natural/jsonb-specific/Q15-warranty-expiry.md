# Q15 - Warranty Expiry

## Question
> **FR:** Quels équipements ont une garantie qui expire dans les N prochains jours ?
>
> **EN:** What equipment has a warranty expiring in the next N days?

## Cas d'usage / Use case
Planification renouvellement contrats, budget maintenance.
Contract renewal planning, maintenance budgeting.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| DAYS_AHEAD | integer | Nombre de jours avant expiration | `90` |
| REFERENCE_DATE | date | Date de référence | `2025-01-01` |

## JSONB Path
`data->'metadata'->>'warranty_end'`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
