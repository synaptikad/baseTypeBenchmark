# Q10 - Security Access Analysis

## Question
> **FR:** Pour un bâtiment, quels sont les équipements de sécurité (badges, caméras, détecteurs) par espace avec leur couverture ?
>
> **EN:** For a building, what are the security equipment (badges, cameras, detectors) per space with their coverage?

## Cas d'usage / Use case
Audit sécurité, plan d'évacuation.
Security audit, evacuation plan.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| BUILDING_ID | string | ID d'un bâtiment | `building_hq_1` |

## Relations
`MONITORS`, `LOCATED_IN`, `CONTAINS`

## Filtres
- `equipment_type IN ["BadgeReader", "IPCamera", "DoorContact", "PIRDetector"]`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
