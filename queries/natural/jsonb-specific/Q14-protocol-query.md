# Q14 - Protocol Query

## Question
> **FR:** Quels sont tous les points communiquant avec un device BACnet spécifique ?
>
> **EN:** What are all the points communicating with a specific BACnet device?

## Cas d'usage / Use case
Diagnostic réseau BACnet, remplacement contrôleur, migration.
BACnet network diagnostics, controller replacement, migration.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| DEVICE_ID | integer | ID du device BACnet | `1234` |

## JSONB Path
`data->'protocol'->>'device_id'`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
