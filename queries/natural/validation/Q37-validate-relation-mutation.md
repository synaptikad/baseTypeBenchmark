# Q37 - Validate Relation Mutation

## Question
> **FR:** La relation entre deux nœuds a-t-elle été correctement modifiée (ajoutée/supprimée) ?
>
> **EN:** Was the relation between two nodes correctly modified (added/removed)?

## Valide / Validates
**[QW3](../write/QW3-relation-mutation.md)** - Relation Mutation

## Cas d'usage / Use case
Validation mutation graphe, test intégration, audit relations.
Graph mutation validation, integration testing, relation audit.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| SOURCE_ID | string | ID du nœud source | `eq_ahu_1` |
| TARGET_ID | string | ID du nœud cible | `space_office_101` |
| RELATION_TYPE | string | Type de relation | `SERVES` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
