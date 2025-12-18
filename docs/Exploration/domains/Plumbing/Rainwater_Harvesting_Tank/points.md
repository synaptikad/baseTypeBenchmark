# Points de Rainwater Harvesting Tank (Cuve récupération eau pluie)

## Synthèse
- **Total points mesure** : 9
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Tank Level | sensor-level-point | % | 0-100% | 1min | Niveau cuve |
| Volume Available | sensor-volume-point | L | 0-50000 | 1min | Volume disponible |
| Inlet Flow | sensor-flow-point | L/min | 0-200 | 10s | Débit entrée (pluie) |
| Outlet Flow | sensor-flow-point | L/min | 0-100 | 10s | Débit utilisation |
| Water Temperature | sensor-temp-point | °C | 5-30°C | 5min | Température eau |
| Turbidity | sensor-point | NTU | 0-100 | 15min | Turbidité |
| pH | sensor-point | pH | 5-9 | 1h | pH eau |
| Volume Collected Daily | sensor-volume-point | L | 0-10000 | 1h | Volume collecté aujourd'hui |
| Volume Used Daily | sensor-volume-point | L | 0-5000 | 1h | Volume utilisé aujourd'hui |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Distribution Pump | cmd-point | - | START/STOP/AUTO | Enum | Pompe distribution |
| Mains Backup Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Secours eau ville |
| First Flush Valve | cmd-point | - | OPEN/CLOSE/AUTO | Enum | Vanne premier flot |
| Low Level Setpoint | cmd-sp-point | % | 10-30% | Analog | Seuil niveau bas |
| Filter Flush | cmd-point | - | TRIGGER | Binaire | Rinçage filtre |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | OK/LOW/BACKUP/FAULT | État général |
| Pump Status | status-point | Enum | RUNNING/STOPPED/FAULT | État pompe |
| Filter Status | status-point | Enum | OK/CLOGGED/FAULT | État filtre |
| Mains Backup Active | status-point | Boolean | FALSE/TRUE | Secours eau ville actif |
| Low Level Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau bas |
| Overflow Alarm | status-point | Boolean | FALSE/TRUE | Alarme débordement |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Tank Level | AI0 | 30001 |
| Volume Available | AI1 | 30002-30003 |
| System Status | MSV0 | 40001 |
| Distribution Pump | MSV1 | 40101 |
| Mains Backup Enable | BO0 | 00001 |
| Low Level Alarm | BI0 | 10001 |
| Pump Status | MSV2 | 40010 |

## Sources
- [EN 16941 Rainwater Harvesting](https://www.en-standard.eu/)
- [BS 8515 Rainwater Harvesting Systems](https://www.bsigroup.com/)
