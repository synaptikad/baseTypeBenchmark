# Points de Sprinkler Flow Switch (Pressostat de débit sprinkler)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 2
- **Total points état** : 4

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Flow Rate | sensor-flow-point | L/min | 0-500 | 1s | Débit mesuré |
| Flow Duration | sensor-point | s | 0-3600 | 1s | Durée écoulement |
| Activation Count | sensor-point | count | 0-999 | Sur événement | Compteur activations |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Flow Threshold | cmd-sp-point | L/min | 10-100 | Analog | Seuil détection débit |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Switch Status | status-point | Enum | NORMAL/FLOW/FAULT | État général |
| Flow Detected | status-point | Boolean | FALSE/TRUE | Débit détecté |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Tentative sabotage |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA/CEI Protocol |
|-------|---------------|-----------------|------------------|
| Flow Rate | AI0 | 30001 | - |
| Switch Status | MSV0 | 40001 | Status 0x00 |
| Flow Detected | BI0 | 10001 | Event WF |
| Tamper Status | BI1 | 10002 | Event TA |
| Flow Threshold | AO0 | 40101 | - |

## Sources
- [EN 12259-5 Flow Switches](https://www.en-standard.eu/)
- [NFPA 13 Sprinkler Systems](https://www.nfpa.org/)
- [FM 1035 Waterflow Indicators](https://www.fmglobal.com/)
