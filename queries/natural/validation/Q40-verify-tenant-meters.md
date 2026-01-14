# Q40 - Verify Tenant Meters

## Question
> **FR:** Les compteurs ont-ils été correctement dissociés du locataire après le déménagement ?
>
> **EN:** Were meters correctly disassociated from the tenant after move-out?

## Valide / Validates
**[QW10](../write/QW10-tenant-move-out.md)** - Tenant Move-Out

## Cas d'usage / Use case
Validation déménagement, clôture contrat, facturation finale.
Move-out validation, contract closure, final billing.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| TENANT_ID | string | ID de l'ancien locataire | `tenant_oldco` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
