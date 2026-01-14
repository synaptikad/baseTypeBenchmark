# QW19 - Remove Added Capability

## Question
> **FR:** Comment retirer une capability d'un équipement ?
>
> **EN:** How to remove a capability from equipment?

## Nettoie / Cleans up
**[QW7](../write/QW7-add-capability.md)** - Add Capability

## Cas d'usage / Use case
Retrait fonctionnalité, correction erreur configuration.
Feature removal, configuration error correction.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| QW7_EQUIPMENT_ID | string | ID de l'équipement | `eq_ahu_9` |
| QW7_NEW_CAPABILITY | string | Capability à retirer | `demand_control_ventilation` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ❌ |
