# Points de Heat Exchanger (Échangeur thermique)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Primary Inlet Temperature | sensor-temp-point | °C | 40-90°C | 5s | Température entrée primaire |
| Primary Outlet Temperature | sensor-temp-point | °C | 30-70°C | 5s | Température sortie primaire |
| Secondary Inlet Temperature | sensor-temp-point | °C | 10-50°C | 5s | Température entrée secondaire |
| Secondary Outlet Temperature | sensor-temp-point | °C | 30-80°C | 5s | Température sortie secondaire |
| Primary Flow Rate | sensor-flow-point | L/min | 0-500 | 10s | Débit primaire |
| Secondary Flow Rate | sensor-flow-point | L/min | 0-500 | 10s | Débit secondaire |
| Pressure Drop Primary | sensor-pressure-point | kPa | 0-100 | 1min | Perte charge primaire |
| Pressure Drop Secondary | sensor-pressure-point | kPa | 0-100 | 1min | Perte charge secondaire |
| Heat Transfer Rate | sensor-point | kW | 0-1000 | 1min | Puissance échangée |
| Efficiency | sensor-point | % | 0-100% | 5min | Rendement échangeur |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Secondary Setpoint | cmd-sp-point | °C | 30-70°C | Analog | Consigne température secondaire |
| Primary Valve Position | cmd-sp-point | % | 0-100% | Analog | Position vanne primaire |
| Bypass Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation bypass |
| Flush Sequence | cmd-point | - | TRIGGER | Binaire | Séquence rinçage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Exchanger Status | status-point | Enum | OK/FOULED/FAULT | État général |
| Fouling Level | status-point | Enum | CLEAN/MODERATE/HEAVY | Niveau encrassement |
| Primary Flow Status | status-point | Enum | OK/LOW/NO_FLOW | État débit primaire |
| Secondary Flow Status | status-point | Enum | OK/LOW/NO_FLOW | État débit secondaire |
| Freeze Protection | status-point | Boolean | FALSE/TRUE | Protection antigel active |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Primary Inlet Temperature | AI0 | 30001 |
| Primary Outlet Temperature | AI1 | 30002 |
| Secondary Inlet Temperature | AI2 | 30003 |
| Secondary Outlet Temperature | AI3 | 30004 |
| Heat Transfer Rate | AI4 | 30005-30006 |
| Secondary Setpoint | AO0 | 40101 |
| Exchanger Status | MSV0 | 40001 |

## Sources
- [TEMA Standards](https://www.tema.org/)
- [EN 305 Heat Exchangers](https://www.en-standard.eu/)
- [AHRI Standard 400](https://www.ahrinet.org/)
