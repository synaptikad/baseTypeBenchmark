# QW7 - Add Capability

## Question
> **FR:** Comment ajouter une capacité à un équipement si elle n'existe pas déjà (opération idempotente) ?
>
> **EN:** How to add a capability to equipment if it doesn't already exist (idempotent operation)?

## Validé par / Validated by
**[Q26](../validation/Q26-capability-evolution.md)** - Capability Evolution

## Cas d'usage / Use case
Upgrade équipement, extension fonctionnelle.
Equipment upgrade, feature extension.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| EQUIPMENT_ID | string | ID de l'équipement | `eq_ahu_6` |
| NEW_CAPABILITY | string | Capacité à ajouter | `demand_control_ventilation` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
