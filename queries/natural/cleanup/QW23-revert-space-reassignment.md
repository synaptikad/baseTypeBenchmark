# QW23 - Revert Space Reassignment

## Question
> **FR:** Comment annuler une réaffectation d'espace ?
>
> **EN:** How to revert a space reassignment?

## Nettoie / Cleans up
**[QW11](../write/QW11-space-reassignment.md)** - Space Reassignment

## Cas d'usage / Use case
Annulation réaffectation, correction erreur, litige bail.
Reassignment cancellation, error correction, lease dispute.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| QW_SPACE_ID | string | ID de l'espace | `space_1_7_6` |
| OLD_TENANT_ID | string | Ancien locataire | `tenant_1` |
| NEW_TENANT_ID | string | Nouveau locataire | `tenant_2` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ⚠️ |
