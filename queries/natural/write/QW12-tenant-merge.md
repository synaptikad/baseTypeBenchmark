# QW12 - Tenant Merge

## Question
> **FR:** Comment fusionner deux locataires en transférant tous les espaces et compteurs vers un locataire cible ?
>
> **EN:** How to merge two tenants by transferring all spaces and meters to a target tenant?

## Validé par / Validated by
**[Q41](../validation/Q41-verify-tenant-consolidation.md)** - Verify Tenant Consolidation

## Cas d'usage / Use case
Fusion entreprises, restructuration locataires, consolidation.
Company merger, tenant restructuring, consolidation.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| SOURCE_TENANT_ID | string | ID du locataire à absorber | `tenant_absorbed` |
| TARGET_TENANT_ID | string | ID du locataire cible | `tenant_merged` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
