# QW14 - Remove Calibration Tag

## Question
> **FR:** Comment supprimer un tag de calibration d'un équipement ?
>
> **EN:** How to remove a calibration tag from equipment?

## Nettoie / Cleans up
**[QW2](../write/QW2-metadata-update.md)** - Metadata Update

## Cas d'usage / Use case
Rollback configuration, correction d'erreur de tagging, nettoyage données.
Configuration rollback, tagging error correction, data cleanup.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| QW2_NODE_ID | string | ID de l'équipement | `eq_submeter_8` |
| QW2_TAG_KEY | string | Clé du tag à supprimer | `calibration_status` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ❌ |
