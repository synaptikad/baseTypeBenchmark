# QW2 - Metadata Update

## Question
> **FR:** Comment mettre à jour les tags de métadonnées d'un équipement ?
>
> **EN:** How to update metadata tags of an equipment?

## Validé par / Validated by
**[Q36](../validation/Q36-validate-metadata-update.md)** - Validate Metadata Update

## Cas d'usage / Use case
Mise à jour tags Brick/Haystack, enrichissement données.
Brick/Haystack tag update, data enrichment.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| EQUIPMENT_ID | string | ID de l'équipement | `eq_ahu_6` |
| NEW_TAGS | array | Nouveaux tags à ajouter | `["brick:AHU", "haystack:ahu"]` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ⚠️ | ✅ | ✅ | ✅ | ✅ |
