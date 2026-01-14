# QW9 - Tenant Move-In

## Question
> **FR:** Comment assigner des espaces et compteurs à un nouveau locataire (emménagement) ?
>
> **EN:** How to assign spaces and meters to a new tenant (move-in)?

## Validé par / Validated by
**[Q39](../validation/Q39-verify-tenant-spaces.md)** - Verify Tenant Spaces

## Cas d'usage / Use case
Gestion locataires, emménagement, activation facturation.
Tenant management, move-in, billing activation.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| TENANT_ID | string | ID du nouveau locataire | `tenant_newco` |
| SPACE_IDS | array | Espaces à assigner | `["space_101", "space_102"]` |
| METER_IDS | array | Compteurs à assigner | `["meter_sub_1"]` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
