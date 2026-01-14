# Q41 - Verify Tenant Consolidation

## Question
> **FR:** La fusion de deux locataires a-t-elle correctement transféré tous les espaces et compteurs vers le locataire cible ?
>
> **EN:** Did the merger of two tenants correctly transfer all spaces and meters to the target tenant?

## Valide / Validates
**[QW12](../write/QW12-tenant-merge.md)** - Tenant Merge

## Cas d'usage / Use case
Validation fusion, restructuration locataires, audit.
Merger validation, tenant restructuring, audit.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| TARGET_TENANT_ID | string | ID du locataire cible | `tenant_merged` |
| SOURCE_TENANT_ID | string | ID du locataire absorbé | `tenant_absorbed` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
