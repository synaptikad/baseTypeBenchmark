# QW15 - Remove Created Relation

## Question
> **FR:** Comment supprimer une relation créée entre deux équipements ?
>
> **EN:** How to remove a relation created between two equipment?

## Nettoie / Cleans up
**[QW3](../write/QW3-relation-mutation.md)** - Relation Mutation

## Cas d'usage / Use case
Correction topologie réseau, annulation connexion erronée.
Network topology correction, wrong connection cancellation.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| QW3_SOURCE_ID | string | ID source | `eq_mainmeter_4` |
| QW3_TARGET_ID | string | ID cible | `eq_submeter_8` |
| QW3_REL_TYPE | string | Type de relation | `FEEDS` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ⚠️ |
