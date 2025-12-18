# Points de License Plate Reader (Lecteur plaque immatriculation)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Read Count | sensor-point | count | 0-999999 | Sur événement | Compteur lectures |
| Recognition Rate | sensor-point | % | 0-100% | 1h | Taux reconnaissance |
| Average Confidence | sensor-point | % | 0-100% | Sur événement | Confiance moyenne |
| Processing Time | sensor-point | ms | 0-1000 | Sur événement | Temps traitement |
| Daily Reads | sensor-point | count | 0-10000 | 1h | Lectures journalières |
| IR Illumination | sensor-point | % | 0-100% | 1s | Niveau IR |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Recognition Enable | cmd-point | - | ON/OFF | Binaire | Activation reconnaissance |
| IR Mode | cmd-sp-point | - | AUTO/ON/OFF | Enum | Mode infrarouge |
| Confidence Threshold | cmd-sp-point | % | 50-99% | Analog | Seuil confiance |
| Whitelist Enable | cmd-point | - | ON/OFF | Binaire | Activation liste blanche |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Reader Status | status-point | Enum | OK/FAULT | État général |
| Recognition Status | status-point | Enum | IDLE/PROCESSING/ERROR | État reconnaissance |
| Last Read Result | status-point | Enum | MATCH/NO_MATCH/UNKNOWN | Dernier résultat |
| Camera Status | status-point | Enum | OK/FAULT | État caméra |
| IR Status | status-point | Enum | OFF/ON | État infrarouge |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | ONVIF |
|-------|---------------|-----------------|-------|
| Read Count | AI0 | 30001 | - |
| Recognition Rate | AI1 | 30002 | - |
| Reader Status | MSV0 | 40001 | GetDeviceStatus |
| Last Read Result | MSV1 | 40002 | Analytics Event |
| Recognition Enable | BO0 | 00001 | - |
| Confidence Threshold | AO0 | 40101 | - |

## Sources
- [ONVIF Analytics](https://www.onvif.org/)
- [EN 62676 Video Surveillance](https://www.en-standard.eu/)
