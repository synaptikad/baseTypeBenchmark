# Q38 - Validate Property Removal

## Question
> **FR:** La clé de métadonnées a-t-elle été correctement supprimée de l'équipement ?
>
> **EN:** Was the metadata key correctly removed from the equipment?

## Valide / Validates
**[QW8](../write/QW8-remove-metadata-key.md)** - Remove Metadata Key

## Cas d'usage / Use case
Validation suppression, nettoyage données, conformité RGPD.
Removal validation, data cleanup, GDPR compliance.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| NODE_ID | string | ID du nœud | `eq_ahu_6` |
| KEY_TO_CHECK | string | Clé à vérifier absente | `legacy_protocol_id` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ✅ | ✅ | ✅ |
