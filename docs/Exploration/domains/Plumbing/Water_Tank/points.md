# Points de Water Tank (Réservoir d'eau)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 4
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Water Level | sensor-level-point | % | 0-100% | 30s | Niveau d'eau |
| Water Level Absolute | sensor-level-point | m | 0-10 | 30s | Niveau absolu |
| Water Temperature | sensor-temp-point | °C | 5-30°C | 1min | Température eau |
| Inlet Flow Rate | sensor-flow-point | L/min | 0-500 | 10s | Débit entrée |
| Outlet Flow Rate | sensor-flow-point | L/min | 0-500 | 10s | Débit sortie |
| Tank Pressure | sensor-pressure-point | bar | 0-10 | 1min | Pression réservoir |
| Volume Available | sensor-point | L | 0-100000 | 1min | Volume disponible |
| Chlorine Level | sensor-point | mg/L | 0-5 | 15min | Niveau chlore résiduel |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Fill Valve Control | cmd-point | - | OPEN/CLOSE/AUTO | Enum | Vanne remplissage |
| Drain Valve Control | cmd-point | - | OPEN/CLOSE | Binaire | Vanne vidange |
| Low Level Setpoint | cmd-sp-point | % | 10-30% | Analog | Seuil niveau bas |
| High Level Setpoint | cmd-sp-point | % | 80-95% | Analog | Seuil niveau haut |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Tank Status | status-point | Enum | OK/LOW/HIGH/FAULT | État général |
| Fill Valve Status | status-point | Enum | OPEN/CLOSED/FAULT | État vanne remplissage |
| Drain Valve Status | status-point | Enum | OPEN/CLOSED | État vanne vidange |
| Low Level Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau bas |
| High Level Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau haut |
| Overflow Alarm | status-point | Boolean | FALSE/TRUE | Alarme débordement |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Water Level | AI0 | 30001 |
| Water Temperature | AI1 | 30002 |
| Tank Status | MSV0 | 40001 |
| Fill Valve Control | MSV1 | 40101 |
| Low Level Alarm | BI0 | 10001 |
| High Level Alarm | BI1 | 10002 |
| Low Level Setpoint | AO0 | 40201 |
| Volume Available | AI2 | 30003-30004 |

## Sources
- [EN 13828 Water Tanks](https://www.en-standard.eu/)
- [Water Quality Regulations](https://www.who.int/)
- [BACnet Water Systems](https://www.bacnet.org/)
