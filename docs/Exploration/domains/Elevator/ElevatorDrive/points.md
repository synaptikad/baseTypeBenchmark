# Points de Elevator Drive (VFD)

## Synthèse
- **Total points mesure** : 14
- **Total points commande** : 6
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Output Frequency | sensor-elec-freq-point | Hz | 0-100 Hz | 100ms | Fréquence sortie |
| Output Voltage | sensor-elec-volt-point | V | 0-690 V | 100ms | Tension sortie |
| Output Current | sensor-elec-current-point | A | 0-1000 A | 100ms | Courant sortie |
| Output Power | sensor-elec-power-point | kW | 0-500 kW | 100ms | Puissance sortie |
| Motor Speed | sensor-point | RPM | 0-3000 | 100ms | Vitesse moteur |
| Motor Torque | sensor-point | % | 0-200% | 100ms | Couple moteur |
| DC Bus Voltage | sensor-elec-volt-point | V | 0-1000 V | 1s | Tension bus DC |
| Heatsink Temperature | sensor-temp-point | °C | 20-80°C | 10s | Température dissipateur |
| Motor Temperature | sensor-temp-point | °C | 30-150°C | 10s | Température moteur |
| Energy Consumed | sensor-elec-energy-point | kWh | 0-999999 | 1min | Énergie consommée |
| Energy Regenerated | sensor-elec-energy-point | kWh | 0-999999 | 1min | Énergie régénérée |
| Power Factor | sensor-elec-pf-point | - | 0-1 | 1s | Facteur de puissance |
| Running Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |
| Start Count | sensor-point | count | 0-9999999 | Sur événement | Nombre démarrages |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Run Command | cmd-point | - | RUN/STOP | Binaire | Commande marche |
| Speed Reference | cmd-sp-point | Hz | 0-100 Hz | Analog | Consigne fréquence |
| Direction | cmd-point | - | FORWARD/REVERSE | Binaire | Sens rotation |
| Torque Limit | cmd-sp-point | % | 0-200% | Analog | Limite couple |
| Reset Fault | cmd-point | - | RESET | Binaire | Acquittement défaut |
| Emergency Stop | cmd-point | - | STOP | Binaire | Arrêt d'urgence |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Drive Status | status-point | Enum | READY/RUNNING/FAULT/WARNING | État général |
| Run Status | status-point | Enum | STOPPED/ACCELERATING/AT_SPEED/DECELERATING | État marche |
| Fault Code | status-point | String | Alphanumeric | Code défaut actif |
| Warning Code | status-point | String | Alphanumeric | Code avertissement |
| Regeneration Status | status-point | Enum | IDLE/ACTIVE/BRAKE_ACTIVE | État régénération |
| Thermal Status | status-point | Enum | OK/WARNING/TRIP | État thermique |
| DC Bus Status | status-point | Enum | OK/UNDERVOLTAGE/OVERVOLTAGE | État bus DC |
| Motor Status | status-point | Enum | OK/OVERLOAD/STALL | État moteur |
| Communication Status | status-point | Enum | OK/FAULT | État communication |
| Safe Torque Off | status-point | Boolean | FALSE/TRUE | STO actif |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | Profibus/Profinet |
|-------|---------------|-----------------|-------------------|
| Output Frequency | AI0 | 40001 | PZD1 |
| Output Current | AI1 | 40002 | PZD2 |
| Output Power | AI2 | 40003-40004 | PZD3 |
| Motor Speed | AI3 | 40005 | PZD4 |
| Drive Status | MSV0 | 40010 | STW1 |
| Fault Code | CSV0 | 40011 | - |
| Run Command | BO0 | 00001 | CTW1.0 |
| Speed Reference | AO0 | 40101 | HSW |

## Sources
- [IEC 61800-5-2 Functional Safety](https://webstore.iec.ch/)
- [EN 81-20/50 Elevator Drives](https://www.en-standard.eu/)
- [Profidrive Application Guide](https://www.profibus.com/)
