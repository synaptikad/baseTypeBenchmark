# Points de Parking Sensor (Ultrasonic)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Distance Measurement | sensor-point | cm | 30-400 cm | 1s | Distance mesurée à l'objet |
| Ultrasonic Echo Time | sensor-point | µs | 150-23000 µs | 1s | Temps écho ultrasonore |
| Detection Confidence | sensor-point | % | 0-100% | 1s | Confiance détection |
| Occupancy Duration | sensor-point | min | 0-1440 min | 5min | Durée occupation actuelle |
| Power Consumption | sensor-elec-power-point | W | 0-5 W | 5min | Consommation électrique |
| Operating Hours | sensor-point | h | 0-100000 h | 1h | Heures fonctionnement total |
| Temperature | sensor-temp-point | °C | -40 à +85°C | 5min | Température capteur |
| Detection Count | sensor-point | count | 0-999999 | 1h | Nombre détections total |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Sensor Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation capteur |
| Detection Threshold | cmd-sp-point | cm | 50-300 cm | Analog | Seuil distance détection |
| Measurement Rate | cmd-sp-point | Hz | 0.1-10 Hz | Analog | Fréquence mesures |
| Calibration Trigger | cmd-point | - | CALIBRATE | Binaire | Lancement calibration |
| Reset Statistics | cmd-point | - | RESET | Binaire | Remise à zéro compteurs |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Sensor Status | status-point | Enum | OK/FAULT/OFFLINE | État général capteur |
| Occupancy Status | status-point | Enum | FREE/OCCUPIED/UNKNOWN | État occupation place |
| Transducer Status | status-point | Enum | OK/FAULT | État transducteur ultrason |
| Communication Status | status-point | Enum | CONNECTED/DISCONNECTED | État connexion réseau |
| Calibration Status | status-point | Enum | OK/REQUIRED/IN_PROGRESS | État calibration |
| Last State Change Time | status-point | Timestamp | ISO8601 | Horodatage dernier changement |
| Fault Code | status-point | String | Alphanumeric | Code erreur détecté |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Sensor Status | MSV0 | 40001 |
| Occupancy Status | BI0 | 10001 |
| Distance Measurement | AI0 | 40002 |
| Detection Confidence | AI1 | 40003 |
| Temperature | AI2 | 40004 |
| Occupancy Duration | AI3 | 40005 |
| Sensor Enable | BO0 | 00001 |
| Detection Threshold | AO0 | 40101 |

## Sources
- [Ultrasonic Sensor Technology](https://www.ultrasonicsensors.com/)
- [LoRaWAN for Parking Sensors](https://lora-alliance.org/)
- [Parking Guidance System Documentation](https://www.parking-guidance.com/)
