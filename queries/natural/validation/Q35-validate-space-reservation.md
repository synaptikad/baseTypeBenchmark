# Q35 - Validate Space Reservation

## Question
> **FR:** Qui occupe cette salle sur cette période ?
>
> **EN:** Who is occupying this room during this period?

## Valide / Validates
**[QW1](../write/QW1-space-reservation.md)** - Space Reservation

## Cas d'usage / Use case
Vérification disponibilité, audit occupation, planning.
Availability check, occupancy audit, scheduling.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| QW1_SPACE_ID | string | ID de la salle | `space_1_2_5` |
| QW1_START_DATE | date | Date début période | `2024-01-20` |
| QW1_END_DATE | date | Date fin période | `2024-01-27` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ❌ |
