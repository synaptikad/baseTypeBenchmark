# Q34 - Materialized Energy Summary

## Question
> **FR:** Quel est le résumé énergétique matérialisé (pré-calculé) par étage et par jour ?
>
> **EN:** What is the materialized (pre-computed) energy summary per floor per day?

## Cas d'usage / Use case
Reporting mensuel, comparaison entre étages, optimisation.
Monthly reporting, floor comparison, optimization.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| BUILDING_ID | string | ID du bâtiment | `building_hq_1` |
| DATE_START | timestamp | Début de période | `2024-01-01T00:00:00Z` |
| DATE_END | timestamp | Fin de période | `2024-01-31T23:59:59Z` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ❌ | ⚠️ | ⚠️ |
