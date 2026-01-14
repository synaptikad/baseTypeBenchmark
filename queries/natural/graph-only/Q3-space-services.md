# Q3 - Space Services

## Question
> **FR:** Pour un espace donné, quels sont tous les équipements qui le desservent, le contiennent ou le surveillent ?
>
> **EN:** For a given space, what are all the equipment that serve, contain, or monitor it?

## Cas d'usage / Use case
Inventaire équipements d'une salle de réunion.
Equipment inventory for a meeting room.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| SPACE_ID | string | ID d'un espace existant | `space_meeting_101` |

## Relations
`SERVES`, `CONTAINS`, `LOCATED_IN`, `MONITORS` (incoming)

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
