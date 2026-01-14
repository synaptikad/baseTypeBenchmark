# Q7 - Drift Top-20

## Question
> **FR:** Quels sont les 20 points avec la plus grande variance sur une période donnée ?
>
> **EN:** What are the 20 points with the highest variance over a given period?

## Cas d'usage / Use case
Détection anomalies, maintenance prédictive.
Anomaly detection, predictive maintenance.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| BUILDING_ID | string | ID d'un bâtiment | `building_hq_1` |
| DATE_START | timestamp | Début de période | `2024-01-01T00:00:00Z` |
| DATE_END | timestamp | Fin de période | `2024-01-31T23:59:59Z` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
