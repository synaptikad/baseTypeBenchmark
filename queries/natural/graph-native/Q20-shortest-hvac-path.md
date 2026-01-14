# Q20 - Shortest HVAC Path

## Question
> **FR:** Quel est le chemin le plus court entre un équipement HVAC source et un espace cible ?
>
> **EN:** What is the shortest path between a source HVAC equipment and a target space?

## Cas d'usage / Use case
Diagnostic flux d'air, identification du trajet de distribution.
Airflow diagnostics, distribution path identification.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| EQUIPMENT_ID | string | ID équipement HVAC source | `equip_ahu_1` |
| SPACE_ID | string | ID espace cible | `space_office_201` |

## Relations
`FEEDS`, `SERVES`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ⚠️ | ⚠️ | ✅ | ✅ | ❌ |
