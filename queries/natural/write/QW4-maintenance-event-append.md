# QW4 - Maintenance Event Append

## Question
> **FR:** Comment ajouter un événement de maintenance à l'historique JSONB d'un équipement ?
>
> **EN:** How to append a maintenance event to an equipment's JSONB history?

## Validé par / Validated by
**[Q24](../validation/Q24-maintenance-history.md)** - Maintenance History

## Cas d'usage / Use case
Suivi maintenance, GMAO, historique interventions.
Maintenance tracking, CMMS, intervention history.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| EQUIPMENT_ID | string | ID de l'équipement | `eq_ahu_6` |
| EVENT | json | Objet événement maintenance | `{"date": "2024-06-15", "type": "preventive", "technician": "John", "cost": 150}` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ✅ | ✅ | ⚠️ |
