# Q24 - Maintenance History

## Question
> **FR:** Quel est l'historique de maintenance complet d'un équipement avec agrégations (nombre d'événements, coût total, pièces remplacées) ?
>
> **EN:** What is the complete maintenance history of equipment with aggregations (event count, total cost, parts replaced)?

## Valide / Validates
**[QW4](../write/QW4-maintenance-event-append.md)** - Maintenance Event Append

## Cas d'usage / Use case
Reporting maintenance, analyse coûts, planning.
Maintenance reporting, cost analysis, planning.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| EQUIPMENT_ID | string | ID de l'équipement | `eq_ahu_6` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
