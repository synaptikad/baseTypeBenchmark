# Q17 - Capability Filter

## Question
> **FR:** Quels équipements HVAC possèdent une capacité spécifique (humidity_control, variable_speed, etc.) ?
>
> **EN:** What HVAC equipment has a specific capability (humidity_control, variable_speed, etc.)?

## Cas d'usage / Use case
Audit technique, planification upgrade.
Technical audit, upgrade planning.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| CAPABILITY | string | Capacité recherchée | `humidity_control` |

## JSONB Path
`data->'capabilities'`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ✅ | ✅ | ⚠️ |
