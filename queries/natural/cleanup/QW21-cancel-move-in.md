# QW21 - Cancel Tenant Move-In

## Question
> **FR:** Comment annuler un emménagement de locataire ?
>
> **EN:** How to cancel a tenant move-in?

## Nettoie / Cleans up
**[QW9](../write/QW9-tenant-move-in.md)** - Tenant Move-In

## Cas d'usage / Use case
Annulation bail signé, erreur de saisie, changement de locataire.
Signed lease cancellation, data entry error, tenant change.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| TENANT_ID | string | ID du locataire | `tenant_2` |
| QW_SPACE_ID | string | ID de l'espace | `space_1_7_6` |
| SUBMETER_ID | string (opt) | ID du compteur | `eq_submeter_5` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ⚠️ |
