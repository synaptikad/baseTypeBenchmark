# Q18 - Calibration Chain

## Question
> **FR:** Dans la chaîne énergétique d'un compteur, quels points ont une calibration échue ?
>
> **EN:** In a meter's energy chain, which points have an overdue calibration?

## Cas d'usage / Use case
Planification métrologie, conformité.
Metrology planning, compliance.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| METER_ID | string | ID d'un compteur principal | `meter_main_1` |
| REFERENCE_DATE | date | Date de référence | `2025-01-01` |

## Relations
`FEEDS`, `HAS_POINT` (max 10 hops)

## JSONB Path
`data->'calibration'->>'next_date'`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ⚠️ | ✅ | ⚠️ | ⚠️ | ⚠️ |
