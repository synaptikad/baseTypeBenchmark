# Points de Tape Library

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Total Capacity | sensor-point | TB | 0-10000 | 1h | Capacité totale librarie |
| Used Capacity | sensor-point | % | 0-100% | 1h | Utilisation capacité |
| Data Transfer Rate | sensor-point | MBps | 0-1500 | 30s | Débit transfert actuel |
| Drive Usage Hours | sensor-point | h | 0-100000 | 1h | Heures utilisation lecteur |
| Media Passes | sensor-point | count | 0-1000000 | 1h | Passes média (par slot) |
| Robot Moves | sensor-point | count | 0-10000000 | 1h | Mouvements robot cumulés |
| Power Consumption | sensor-elec-power-point | W | 100-2000 W | 1min | Consommation électrique |
| Temperature | sensor-temp-point | °C | 15-35°C | 5min | Température interne |
| Humidity | sensor-humidity-point | %RH | 20-80% | 5min | Humidité interne |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Robot Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation robot |
| Drive Online | cmd-point | - | ONLINE/OFFLINE | Enum | État lecteur |
| Inventory Scan | cmd-point | - | START | Binaire | Inventaire bibliothèque |
| Media Eject | cmd-point | - | EJECT | Binaire | Éjection média (par slot) |
| Clean Drive | cmd-point | - | CLEAN | Binaire | Nettoyage lecteur |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Library Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| Robot Status | status-point | Enum | READY/BUSY/FAULT | État robot |
| Drive Status | status-point | Enum | READY/BUSY/EMPTY/FAULT | État lecteur (par drive) |
| Media Status | status-point | Enum | OK/WARN/EXPIRED/WORM | État média (par slot) |
| Door Status | status-point | Enum | CLOSED/OPEN | État porte accès |
| I/E Station Status | status-point | Enum | EMPTY/FULL/MIXED | État station import/export |
| PSU Status | status-point | Enum | OK/FAULT/REDUNDANCY_LOST | État alimentation |
| Fan Status | status-point | Enum | OK/DEGRADED/FAILED | État ventilation |
| Cleaning Required | status-point | Boolean | TRUE/FALSE | Nettoyage requis |
| Firmware Status | status-point | Enum | CURRENT/UPDATE_AVAILABLE | État firmware |

## Mappings Protocoles
| Point | SNMP OID | SCSI/SMC |
|-------|----------|----------|
| Library Status | ibm3584MIBObjectsLibraryState | Element Status |
| Robot Status | ibm3584MIBObjectsAccessorState | Move Medium |
| Drive Status | ibm3584MIBObjectsDriveState | Element Status |
| Total Capacity | ibm3584MIBObjectsTotalSlots | Read Element Status |
| Used Capacity | ibm3584MIBObjectsUsedSlots | Read Element Status |
| Temperature | ibm3584MIBObjectsTemperature | Log Sense |
| Media Status | ibm3584MIBObjectsMediaState | Element Status |
| Cleaning Required | ibm3584MIBObjectsCleaningRequired | Request Sense |

## Sources
- [IBM TS4500 MIB Reference](https://www.ibm.com/)
- [Quantum Scalar MIB](https://www.quantum.com/)
- [SCSI SMC-3 Specification](https://www.t10.org/)
