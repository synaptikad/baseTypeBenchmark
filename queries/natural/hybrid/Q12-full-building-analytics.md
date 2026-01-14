# Q12 - Full Building Analytics

## Question
> **FR:** Quelles sont les métriques globales d'un bâtiment (énergie totale, température moyenne, occupation) sur une période ?
>
> **EN:** What are the global metrics of a building (total energy, average temperature, occupancy) over a period?

## Cas d'usage / Use case
Dashboard direction, reporting mensuel.
Executive dashboard, monthly reporting.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| BUILDING_ID | string | ID d'un bâtiment | `building_hq_1` |
| DATE_START | timestamp | Début de période | `2024-01-01T00:00:00Z` |
| DATE_END | timestamp | Fin de période | `2024-01-31T23:59:59Z` |

## Relations
`CONTAINS`, `HAS_POINT`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
