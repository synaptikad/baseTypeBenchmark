# QW1 - Timeseries Append

## Question
> **FR:** Comment insérer de nouvelles mesures IoT dans la table timeseries (ingestion continue) ?
>
> **EN:** How to insert new IoT measurements into the timeseries table (continuous ingestion)?

## Validé par / Validated by
**[Q35](../validation/Q35-validate-timeseries-append.md)** - Validate Timeseries Append

## Cas d'usage / Use case
Ingestion capteurs, gateway IoT, middleware temps réel.
Sensor ingestion, IoT gateway, real-time middleware.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| POINT_IDS | array | Liste d'IDs de points | `["point_temp_101"]` |
| TIMESTAMP | timestamp | Horodatage de la mesure | `2024-01-15T10:30:00Z` |
| VALUE | float | Valeur mesurée | `21.5` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
