# Q35 - Validate Timeseries Append

## Question
> **FR:** Les nouvelles mesures IoT ont-elles été correctement insérées dans la table timeseries ?
>
> **EN:** Were the new IoT measurements correctly inserted into the timeseries table?

## Valide / Validates
**[QW1](../write/QW1-timeseries-append.md)** - Timeseries Append

## Cas d'usage / Use case
Validation ingestion, test intégration, monitoring pipeline.
Ingestion validation, integration testing, pipeline monitoring.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| POINT_IDS | array | Liste d'IDs de points | `["point_temp_101", "point_energy_1"]` |
| DATE_START | timestamp | Début de période | `2024-01-01T00:00:00Z` |
| DATE_END | timestamp | Fin de période | `2024-01-01T01:00:00Z` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
