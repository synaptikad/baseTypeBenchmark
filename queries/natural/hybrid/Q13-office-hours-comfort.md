# Q13 - Office Hours Comfort

## Question
> **FR:** Quel est le confort (température, CO2) dans les bureaux pendant les heures de travail (8h-18h, lun-ven) ?
>
> **EN:** What is the comfort level (temperature, CO2) in offices during work hours (8am-6pm, Mon-Fri)?

## Cas d'usage / Use case
Conformité bien-être au travail, optimisation CVC.
Workplace wellness compliance, HVAC optimization.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| BUILDING_ID | string | ID d'un bâtiment | `building_hq_1` |
| DATE_START | timestamp | Début de période | `2024-01-01T00:00:00Z` |
| DATE_END | timestamp | Fin de période | `2024-01-31T23:59:59Z` |

## Relations
`CONTAINS`, `SERVES`, `HAS_POINT`

## Filtres
- `space_type LIKE "office%"`
- `quantity IN ["temperature", "co2"]`
- Heures: 8h-18h, Lundi-Vendredi

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
