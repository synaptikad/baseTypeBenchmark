# Q6 - Hourly Aggregation

## Question
> **FR:** Pour un point de mesure donné, quels sont les agrégats horaires (moyenne, min, max) sur une période ?
>
> **EN:** For a given measurement point, what are the hourly aggregates (avg, min, max) over a period?

## Cas d'usage / Use case
Courbe de charge, analyse consommation.
Load curve, consumption analysis.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| POINT_ID | string | ID d'un point de mesure | `point_temp_101` |
| DATE_START | timestamp | Début de période | `2024-01-01T00:00:00Z` |
| DATE_END | timestamp | Fin de période | `2024-01-31T23:59:59Z` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
