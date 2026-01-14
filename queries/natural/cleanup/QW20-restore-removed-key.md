# QW20 - Restore Removed Key

## Question
> **FR:** Comment restaurer une clé de métadonnées supprimée ?
>
> **EN:** How to restore a removed metadata key?

## Nettoie / Cleans up
**[QW8](../write/QW8-remove-metadata-key.md)** - Remove Metadata Key

## Cas d'usage / Use case
Restauration données, annulation suppression accidentelle.
Data restoration, accidental deletion cancellation.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| QW8_NODE_ID | string | ID du nœud | `eq_submeter_8` |
| QW8_KEY_TO_REMOVE | string | Clé à restaurer | `legacy_protocol_id` |
| QW8_ORIGINAL_VALUE | string | Valeur originale | `MODBUS_001` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ❌ |
