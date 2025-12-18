# Points de Water Tank (Réservoir incendie)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Water Level | sensor-level-point | % | 0-100% | 1min | Niveau eau |
| Water Level Absolute | sensor-level-point | m | 0-20 | 1min | Niveau absolu |
| Water Volume | sensor-volume-point | m³ | 0-1000 | 5min | Volume eau |
| Water Temperature | sensor-temp-point | °C | 0-40°C | 5min | Température eau |
| Inlet Flow Rate | sensor-flow-point | L/min | 0-500 | 30s | Débit remplissage |
| Outlet Pressure | sensor-pressure-point | bar | 0-10 | 30s | Pression sortie |
| Fill Time | sensor-point | h | 0-48 | Sur événement | Temps remplissage |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Fill Valve | cmd-point | - | OPEN/CLOSE | Binaire | Vanne remplissage |
| High Level Setpoint | cmd-sp-point | % | 80-100% | Analog | Seuil niveau haut |
| Low Level Setpoint | cmd-sp-point | % | 20-50% | Analog | Seuil niveau bas |
| Drain Valve | cmd-point | - | OPEN/CLOSE | Binaire | Vanne vidange |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Tank Status | status-point | Enum | OK/LOW/CRITICAL/FAULT | État général |
| High Level Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau haut |
| Low Level Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau bas |
| Fill Valve Status | status-point | Enum | OPEN/CLOSED/FAULT | État vanne remplissage |
| Freeze Protection | status-point | Boolean | FALSE/TRUE | Protection gel active |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Water Level | AI0 | 30001 |
| Water Volume | AI1 | 30002-30003 |
| Water Temperature | AI2 | 30004 |
| Outlet Pressure | AI3 | 30005 |
| Tank Status | MSV0 | 40001 |
| High Level Alarm | BI0 | 10001 |
| Low Level Alarm | BI1 | 10002 |
| Fill Valve | BO0 | 00001 |
| High Level Setpoint | AO0 | 40101 |

## Sources
- [EN 12845 Water Supplies](https://www.en-standard.eu/)
- [NFPA 22 Water Tanks](https://www.nfpa.org/)
- [FM Global Data Sheet 3-2](https://www.fmglobal.com/)
