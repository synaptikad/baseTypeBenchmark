# QW8 - Remove Metadata Key

## Question
> **FR:** Comment supprimer une clé obsolète des métadonnées d'un équipement ?
>
> **EN:** How to remove an obsolete key from equipment metadata?

## Validé par / Validated by
**[Q38](../validation/Q38-validate-property-removal.md)** - Validate Property Removal

## Cas d'usage / Use case
Nettoyage données, migration schéma, conformité RGPD.
Data cleanup, schema migration, GDPR compliance.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| NODE_ID | string | ID du nœud | `eq_ahu_6` |
| KEY_TO_REMOVE | string | Clé à supprimer | `legacy_protocol_id` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ✅ | ✅ | ✅ |
