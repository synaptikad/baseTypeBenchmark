# Q23 - Failure Impact Analysis

## Question
> **FR:** Si cet équipement tombe en panne, quels espaces et équipements sont impactés dans un rayon de N hops ?
>
> **EN:** If this equipment fails, what spaces and equipment are impacted within N hops?

## Cas d'usage / Use case
Analyse d'impact de panne, planification maintenance, résilience infrastructure.
Failure impact analysis, maintenance planning, infrastructure resilience.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| EQUIPMENT_ID | string | ID équipement source de la panne | `eq_mainmeter_1` |
| MAX_HOPS | integer | Nombre maximum de hops | `3` |

## Relations
`FEEDS`, `SERVES`, `POWERS`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ⚠️ |
