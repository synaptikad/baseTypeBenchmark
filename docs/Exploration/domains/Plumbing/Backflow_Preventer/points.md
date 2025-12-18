# Points de Backflow Preventer (Clapet anti-retour)

## Synthèse
- **Total points mesure** : 4
- **Total points commande** : 2
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Inlet Pressure | sensor-pressure-point | bar | 0-10 | 30s | Pression entrée |
| Outlet Pressure | sensor-pressure-point | bar | 0-10 | 30s | Pression sortie |
| Differential Pressure | sensor-pressure-point | bar | 0-2 | 30s | Pression différentielle |
| Test Date | sensor-point | date | - | Sur événement | Date dernier test |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Test Reminder Period | cmd-sp-point | months | 1-12 | Analog | Période rappel test |
| Maintenance Reset | cmd-point | - | RESET | Binaire | RAZ maintenance |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Device Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Relief Valve Status | status-point | Enum | CLOSED/OPEN/FAULT | État soupape décharge |
| Test Required | status-point | Boolean | FALSE/TRUE | Test requis |
| Backflow Detected | status-point | Boolean | FALSE/TRUE | Retour détecté |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Inlet Pressure | AI0 | 30001 |
| Outlet Pressure | AI1 | 30002 |
| Differential Pressure | AI2 | 30003 |
| Device Status | MSV0 | 40001 |
| Test Required | BI0 | 10001 |
| Backflow Detected | BI1 | 10002 |

## Sources
- [EN 1717 Protection against pollution](https://www.en-standard.eu/)
- [ASSE 1015 Backflow Preventers](https://www.asse-plumbing.org/)
