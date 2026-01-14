# Q4 - Floor Temperature Inventory

## Question
> **FR:** Pour un étage donné, quels sont tous les points de mesure de température avec leur équipement parent ?
>
> **EN:** For a given floor, what are all the temperature measurement points with their parent equipment?

## Cas d'usage / Use case
Vérification couverture capteurs pour confort thermique.
Sensor coverage check for thermal comfort.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| FLOOR_ID | string | ID d'un étage existant | `floor_b1_02` |

## Relations
`CONTAINS`, `SERVES`, `HAS_POINT`

## Filtres
- `quantity = "temperature"`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
