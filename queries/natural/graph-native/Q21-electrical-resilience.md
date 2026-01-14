# Q21 - Electrical Resilience

## Question
> **FR:** Pour un équipement critique, quels sont tous les chemins d'alimentation et les points de défaillance unique (SPOF) ?
>
> **EN:** For critical equipment, what are all the power paths and single points of failure (SPOF)?

## Cas d'usage / Use case
Analyse risque datacenter, planification redondance, audit sécurité électrique.
Datacenter risk analysis, redundancy planning, electrical security audit.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| EQUIPMENT_ID | string | ID équipement critique | `equip_server_critical_1` |
| SOURCE_TYPE | string | Type de source d'alimentation | `MainMeter` ou `UPS` |

## Relations
`FEEDS` (upstream)

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ⚠️ | ⚠️ | ✅ | ✅ | ❌ |
