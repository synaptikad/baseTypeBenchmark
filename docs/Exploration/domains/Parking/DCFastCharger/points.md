# Points de DC Fast Charger

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 6
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Active Power | sensor-elec-power-point | kW | 0-350 kW | 1s | Puissance de charge active |
| Output Voltage | sensor-elec-volt-point | V | 200-920 V | 1s | Tension de sortie DC |
| Output Current | sensor-elec-current-point | A | 0-500 A | 1s | Courant de sortie DC |
| Energy Delivered | sensor-elec-energy-point | kWh | 0-999999 kWh | 10s | Énergie totale délivrée session |
| Power Factor | sensor-elec-pf-point | - | 0-1 | 5s | Facteur de puissance |
| Charge Session Duration | sensor-point | min | 0-120 min | 1min | Durée de la session en cours |
| Battery SoC | sensor-point | % | 0-100% | 10s | État de charge batterie véhicule |
| Charger Temperature | sensor-temp-point | °C | -30 à +50°C | 30s | Température interne chargeur |
| Cooling System Flow | sensor-point | L/min | 0-20 L/min | 1min | Débit système refroidissement |
| Cable Temperature | sensor-temp-point | °C | -30 à +80°C | 10s | Température câble de charge |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Charge Start | cmd-point | - | START/STOP | Binaire | Démarrage/arrêt charge |
| Max Power Limit | cmd-sp-point | kW | 0-350 kW | Analog | Limitation puissance max |
| Charge Mode | cmd-point | - | FAST/NORMAL/ECO | Enum | Mode de charge |
| Connector Unlock | cmd-point | - | UNLOCK | Binaire | Déverrouillage connecteur |
| Load Shedding Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation délestage de charge |
| Smart Charging Profile | cmd-point | - | PROFILE_ID | Analog | Profil de charge intelligent |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Charger Status | status-point | Enum | AVAILABLE/CHARGING/ERROR/OFFLINE | État général chargeur |
| Connector Status | status-point | Enum | AVAILABLE/OCCUPIED/FAULTED | État connecteur |
| Session Status | status-point | Enum | IDLE/STARTING/CHARGING/STOPPING/COMPLETE | État session de charge |
| Communication Protocol | status-point | Enum | DIN/ISO15118/CCS | Protocole communication actif |
| Fault Code | status-point | String | Alphanumeric | Code erreur actuelle |
| OCPP Connection | status-point | Enum | CONNECTED/DISCONNECTED | État connexion OCPP backend |
| Cable Locked | status-point | Boolean | TRUE/FALSE | État verrouillage câble |
| Emergency Stop Active | status-point | Boolean | TRUE/FALSE | Arrêt d'urgence activé |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OCPP |
|-------|---------------|-----------------|------|
| Active Power | AI0 | 40001-40002 (Float) | MeterValues.Power.Active.Import |
| Output Voltage | AI1 | 40003-40004 (Float) | MeterValues.Voltage |
| Output Current | AI2 | 40005-40006 (Float) | MeterValues.Current.Import |
| Energy Delivered | AI3 | 40007-40008 (Float) | MeterValues.Energy.Active.Import.Register |
| Charger Temperature | AI4 | 40009 | MeterValues.Temperature |
| Charge Start | BO0 | 00001 | RemoteStartTransaction |
| Max Power Limit | AO0 | 40101-40102 (Float) | SetChargingProfile |
| Charger Status | MSV0 | 40201 | StatusNotification |

## Sources
- [OCPP 2.0.1 Specification](https://www.openchargealliance.org/)
- [ISO 15118-2 Standard](https://www.iso.org/)
- [IEC 61851-23](https://webstore.iec.ch/)
