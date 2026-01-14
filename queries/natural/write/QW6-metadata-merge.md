# QW6 - Metadata Merge

## Question
> **FR:** Comment fusionner un patch JSON dans les métadonnées existantes d'un équipement (préserve les champs non mentionnés) ?
>
> **EN:** How to merge a JSON patch into existing equipment metadata (preserves unmentioned fields)?

## Validé par / Validated by
**[Q25](../validation/Q25-equipment-audit-trail.md)** - Equipment Audit Trail (firmware info)

## Cas d'usage / Use case
Mise à jour firmware, campagne bulk update.
Firmware update, bulk update campaign.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| EQUIPMENT_ID | string | ID de l'équipement | `eq_ahu_7` |
| METADATA_PATCH | json | Patch à fusionner | `{"firmware_version": "3.2.1", "last_update": "2024-06-20"}` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
