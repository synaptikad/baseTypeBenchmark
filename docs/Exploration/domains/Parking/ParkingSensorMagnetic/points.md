# Points de Parking Sensor (Magnetic)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 4
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Magnetic Field X | sensor-point | µT | -100 à +100 µT | Sur événement | Champ magnétique axe X |
| Magnetic Field Y | sensor-point | µT | -100 à +100 µT | Sur événement | Champ magnétique axe Y |
| Magnetic Field Z | sensor-point | µT | -100 à +100 µT | Sur événement | Champ magnétique axe Z |
| Occupancy Duration | sensor-point | min | 0-1440 min | 5min | Durée occupation actuelle |
| Battery Voltage | sensor-elec-volt-point | V | 2.5-3.8 V | 1h | Tension batterie |
| Signal Strength | sensor-point | dBm | -120 à -40 dBm | 10min | Force signal radio |
| Temperature | sensor-temp-point | °C | -40 à +85°C | 1h | Température capteur |
| Detection Count | sensor-point | count | 0-999999 | 1h | Nombre détections total |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Calibration Trigger | cmd-point | - | CALIBRATE | Binaire | Lancement calibration champ |
| Transmit Interval | cmd-sp-point | min | 1-60 min | Analog | Intervalle transmission |
| Detection Sensitivity | cmd-sp-point | - | 1-10 | Analog | Sensibilité détection |
| Reset Sensor | cmd-point | - | RESET | Binaire | Réinitialisation capteur |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Sensor Status | status-point | Enum | OK/FAULT/LOW_BATTERY/OFFLINE | État général capteur |
| Occupancy Status | status-point | Enum | FREE/OCCUPIED | État occupation place |
| Battery Status | status-point | Enum | OK/LOW/CRITICAL | État batterie |
| Calibration Status | status-point | Enum | OK/REQUIRED/IN_PROGRESS | État calibration |
| Communication Status | status-point | Enum | CONNECTED/DISCONNECTED | État connexion gateway |
| Last Transmission Time | status-point | Timestamp | ISO8601 | Horodatage dernière transmission |
| Fault Code | status-point | String | Alphanumeric | Code erreur détecté |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | LoRaWAN |
|-------|---------------|-----------------|---------|
| Sensor Status | MSV0 | 40001 | Uplink Port 1 |
| Occupancy Status | BI0 | 10001 | Uplink Port 1, Byte 0 |
| Magnetic Field Z | AI0 | 40002 | Uplink Port 2 |
| Battery Voltage | AI1 | 40003 | Uplink Port 1, Byte 2-3 |
| Temperature | AI2 | 40004 | Uplink Port 1, Byte 4-5 |
| Occupancy Duration | AI3 | 40005 | - |
| Detection Count | AI4 | 40006-40007 | - |
| Battery Status | MSV1 | 40011 | Uplink Port 1, Byte 1 |

## Sources
- [LoRaWAN Specification](https://lora-alliance.org/resource_hub/lorawan-specification-v1-1/)
- [NB-IoT 3GPP Standards](https://www.3gpp.org/)
- [Smart Parking Sensor Documentation](https://www.smart-parking.com/)
