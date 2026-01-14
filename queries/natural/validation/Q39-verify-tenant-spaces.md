# Q39 - Verify Tenant Spaces

## Question
> **FR:** Les espaces ont-ils été correctement assignés au nouveau locataire après l'emménagement ?
>
> **EN:** Were spaces correctly assigned to the new tenant after move-in?

## Valide / Validates
**[QW9](../write/QW9-tenant-move-in.md)** - Tenant Move-In

## Cas d'usage / Use case
Validation emménagement, gestion locataires, facturation.
Move-in validation, tenant management, billing.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| TENANT_ID | string | ID du nouveau locataire | `tenant_newco` |
| SPACE_IDS | array | Liste d'IDs d'espaces attendus | `["space_101", "space_102"]` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
