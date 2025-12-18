# Points de Water Softener (Adoucisseur)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Inlet Hardness | sensor-point | °f | 0-100 | 1h | Dureté eau entrée |
| Outlet Hardness | sensor-point | °f | 0-10 | 1h | Dureté eau sortie |
| Salt Level | sensor-point | % | 0-100% | 1h | Niveau sel bac |
| Flow Rate | sensor-flow-point | L/min | 0-100 | 10s | Débit instantané |
| Volume Treated | sensor-volume-point | m³ | 0-999999 | 1h | Volume traité cumulé |
| Regeneration Count | sensor-point | count | 0-99999 | Sur événement | Régénérations cumulées |
| Capacity Remaining | sensor-point | % | 0-100% | 1h | Capacité résiduelle |
| Water Temperature | sensor-temp-point | °C | 5-40°C | 1min | Température eau |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Regeneration Start | cmd-point | - | TRIGGER | Binaire | Démarrage régénération |
| Regeneration Schedule | cmd-point | - | TIME/VOLUME/AUTO | Enum | Mode régénération |
| Bypass Valve | cmd-point | - | SERVICE/BYPASS | Enum | Vanne bypass |
| Hardness Setpoint | cmd-sp-point | °f | 0-10 | Analog | Consigne dureté sortie |
| Salt Alert Level | cmd-sp-point | % | 10-30% | Analog | Seuil alerte sel |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Softener Status | status-point | Enum | SERVICE/REGENERATING/BYPASS/FAULT | État général |
| Regeneration Status | status-point | Enum | IDLE/BACKWASH/BRINE/RINSE/FILL | Phase régénération |
| Salt Level Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau sel bas |
| Hardness Alarm | status-point | Boolean | FALSE/TRUE | Alarme dureté sortie |
| Valve Status | status-point | Enum | OK/FAULT | État vanne |
| Capacity Status | status-point | Enum | OK/LOW/EXHAUSTED | État capacité |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Outlet Hardness | AI0 | 30001 |
| Salt Level | AI1 | 30002 |
| Softener Status | MSV0 | 40001 |
| Regeneration Start | BO0 | 00001 |
| Bypass Valve | MSV1 | 40101 |
| Salt Level Alarm | BI0 | 10001 |
| Capacity Remaining | AI2 | 30003 |

## Sources
- [EN 14743 Water Softeners](https://www.en-standard.eu/)
- [NSF/ANSI 44 Water Softeners](https://www.nsf.org/)
