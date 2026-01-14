# Q11 - IT Infrastructure Impact

## Question
> **FR:** Quels serveurs, switches et baies de stockage dépendent d'une alimentation spécifique (UPS, circuit) ?
>
> **EN:** What servers, switches, and storage arrays depend on a specific power supply (UPS, circuit)?

## Cas d'usage / Use case
Planification maintenance, analyse risque datacenter.
Maintenance planning, datacenter risk analysis.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| UPS_ID | string | ID d'un UPS ou circuit électrique | `equip_ups_dc_1` |

## Relations
`FEEDS` (downstream, max 5 hops)

## Filtres
- `equipment_type IN ["RackServer", "NetworkSwitch", "StorageArray"]`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
