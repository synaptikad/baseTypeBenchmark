# QW24 - Revert Tenant Merge

## Question
> **FR:** Comment annuler une fusion de locataires ?
>
> **EN:** How to revert a tenant merge?

## Nettoie / Cleans up
**[QW12](../write/QW12-tenant-merge.md)** - Tenant Merge

## Cas d'usage / Use case
Annulation fusion, scission entreprise, correction erreur.
Merge cancellation, company split, error correction.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| SOURCE_TENANT_ID | string | Tenant source (absorbé) | `tenant_2` |
| TARGET_TENANT_ID | string | Tenant target (absorbant) | `tenant_1` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ❌ |
