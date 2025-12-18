# Points de EV Charger Level 2

## Synthèse
- **Total points mesure** : 9
- **Total points commande** : 6
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Active Power | sensor-elec-power-point | kW | 0-22 kW | 1s | Puissance de charge active |
| Output Voltage | sensor-elec-volt-point | V | 220-400 V | 5s | Tension de sortie AC |
| Output Current | sensor-elec-current-point | A | 0-32 A | 1s | Courant de sortie AC |
| Energy Delivered | sensor-elec-energy-point | kWh | 0-999999 kWh | 10s | Énergie totale délivrée session |
| Power Factor | sensor-elec-pf-point | - | 0-1 | 10s | Facteur de puissance |
| Charge Session Duration | sensor-point | min | 0-720 min | 1min | Durée de la session en cours |
| Charger Temperature | sensor-temp-point | °C | -25 à +50°C | 1min | Température interne chargeur |
| Frequency | sensor-elec-freq-point | Hz | 49-51 Hz | 10s | Fréquence réseau |
| RFID Read Count | sensor-point | count | 0-999999 | Sur événement | Nombre total authentifications |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Charge Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation charge |
| Max Current Limit | cmd-sp-point | A | 6-32 A | Analog | Limitation courant maximum |
| Charge Mode | cmd-point | - | SMART/NORMAL | Enum | Mode de charge |
| Connector Lock | cmd-point | - | LOCK/UNLOCK | Binaire | Verrouillage connecteur |
| Load Management Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Gestion de charge dynamique |
| Remote Stop | cmd-point | - | STOP | Binaire | Arrêt à distance de la charge |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Charger Status | status-point | Enum | AVAILABLE/CHARGING/ERROR/OFFLINE | État général chargeur |
| Connector Status | status-point | Enum | AVAILABLE/OCCUPIED/FAULTED/UNAVAILABLE | État connecteur |
| Session Status | status-point | Enum | IDLE/CHARGING/COMPLETE/FAULT | État session de charge |
| RFID Auth Status | status-point | Enum | SUCCESS/FAILED/PENDING | État dernière authentification |
| Fault Code | status-point | String | Alphanumeric | Code erreur actuelle |
| OCPP Connection | status-point | Enum | CONNECTED/DISCONNECTED | État connexion OCPP backend |
| Cable Connected | status-point | Boolean | TRUE/FALSE | Câble connecté au véhicule |
| Ground Fault | status-point | Boolean | TRUE/FALSE | Défaut terre détecté |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OCPP |
|-------|---------------|-----------------|------|
| Active Power | AI0 | 40001-40002 (Float) | MeterValues.Power.Active.Import |
| Output Voltage | AI1 | 40003 | MeterValues.Voltage |
| Output Current | AI2 | 40004 | MeterValues.Current.Import |
| Energy Delivered | AI3 | 40005-40006 (Float) | MeterValues.Energy.Active.Import.Register |
| Charger Temperature | AI4 | 40007 | MeterValues.Temperature |
| Charge Enable | BO0 | 00001 | RemoteStartTransaction |
| Max Current Limit | AO0 | 40101 | SetChargingProfile |
| Charger Status | MSV0 | 40201 | StatusNotification |

## Sources
- [OCPP 1.6 Specification](https://www.openchargealliance.org/)
- [IEC 61851-1 Standard](https://webstore.iec.ch/)
- [ISO 15118 Vehicle-to-Grid](https://www.iso.org/)
