# QW13 - Cancel Space Reservation

## Question
> **FR:** Comment annuler une réservation de salle ?
>
> **EN:** How to cancel a room reservation?

## Nettoie / Cleans up
**[QW1](../write/QW1-space-reservation.md)** - Space Reservation

## Cas d'usage / Use case
Annulation de réunion, libération de salle, changement de planning.
Meeting cancellation, room release, schedule change.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| QW1_TENANT_ID | string | ID du locataire | `tenant_1` |
| QW1_SPACE_ID | string | ID de la salle | `space_1_2_5` |
| QW1_START_DATE | date | Date début réservation | `2024-01-20` |
| QW1_END_DATE | date | Date fin réservation | `2024-01-27` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ❌ |
