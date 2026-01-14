# Q2 - Functional Impact

## Question
> **FR:** Depuis un équipement en panne, quels sont les équipements parents affectés via les relations FEEDS, SERVES, CONTAINS (traversée inverse) ?
>
> **EN:** From a failed equipment, what parent equipment is affected via FEEDS, SERVES, CONTAINS relations (reverse traversal)?

## Cas d'usage / Use case
Diagnostic de panne, analyse de dépendances.
Failure diagnosis, dependency analysis.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| EQUIPMENT_ID | string | ID d'un équipement existant | `equip_ahu_1` |

## Relations
`FEEDS`, `SERVES`, `CONTAINS` (upstream, max 10 hops)

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
