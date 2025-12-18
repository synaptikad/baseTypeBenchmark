# Points de Fire Hose Reel (Dévidoir incendie)

## Synthèse
- **Total points mesure** : 4
- **Total points commande** : 2
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Water Pressure | sensor-pressure-point | bar | 0-10 | 10s | Pression eau |
| Hose Length Deployed | sensor-point | m | 0-30 | 1s | Longueur déroulée |
| Flow Rate | sensor-flow-point | L/min | 0-100 | 1s | Débit eau |
| Usage Count | sensor-point | count | 0-999 | Sur événement | Compteur utilisations |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Valve Enable | cmd-point | - | ON/OFF | Binaire | Activation vanne |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Reel Status | status-point | Enum | STOWED/DEPLOYED/IN_USE/FAULT | État général |
| Cabinet Door Status | status-point | Enum | CLOSED/OPEN | État porte armoire |
| Water Available | status-point | Boolean | FALSE/TRUE | Eau disponible |
| Low Pressure Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse pression |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Water Pressure | AI0 | 30001 |
| Flow Rate | AI1 | 30002 |
| Reel Status | MSV0 | 40001 |
| Cabinet Door Status | BI0 | 10001 |
| Low Pressure Alarm | BI1 | 10002 |

## Sources
- [EN 671-1 Fire Hose Reels](https://www.en-standard.eu/)
- [NFPA 14 Standpipe and Hose Systems](https://www.nfpa.org/)
