# Q31 - Rolling Aggregation

## Question
> **FR:** Quelles sont les agrégations glissantes (moyenne mobile, percentiles, écart-type) sur les timeseries d'un bâtiment ?
>
> **EN:** What are the rolling aggregations (moving average, percentiles, standard deviation) on a building's timeseries?

## Cas d'usage / Use case
Analyse tendances, lissage données, reporting avancé.
Trend analysis, data smoothing, advanced reporting.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| BUILDING_ID | string | ID du bâtiment | `building_hq_1` |
| DATE_START | timestamp | Début de période | `2024-01-01T00:00:00Z` |
| DATE_END | timestamp | Fin de période | `2024-01-31T23:59:59Z` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ⚠️ | ✅ | ✅ |
