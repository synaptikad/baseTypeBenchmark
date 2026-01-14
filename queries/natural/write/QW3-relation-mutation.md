# QW3 - Relation Mutation

## Question
> **FR:** Comment ajouter ou supprimer une relation entre deux nœuds du graphe ?
>
> **EN:** How to add or remove a relation between two graph nodes?

## Validé par / Validated by
**[Q37](../validation/Q37-validate-relation-mutation.md)** - Validate Relation Mutation

## Cas d'usage / Use case
Réorganisation topologie, correction erreurs import.
Topology reorganization, import error correction.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| SOURCE_ID | string | ID du nœud source | `eq_ahu_1` |
| TARGET_ID | string | ID du nœud cible | `space_office_101` |
| RELATION_TYPE | string | Type de relation | `SERVES` |
| OPERATION | string | add ou remove | `add` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
