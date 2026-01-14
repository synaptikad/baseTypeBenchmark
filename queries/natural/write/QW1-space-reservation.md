# QW1 - Space Reservation

## Question
> **FR:** Comment réserver une salle pour un locataire sur une période donnée ?
>
> **EN:** How to book a room for a tenant during a given period?

## Validé par / Validated by
**[Q35](../validation/Q35-validate-space-reservation.md)** - Validate Space Reservation

## Cas d'usage / Use case
Réservation de salles de réunion, gestion des espaces partagés.
Meeting room booking, shared space management.

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
