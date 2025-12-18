# Points de Compresseur d'Air (Air Compressor)

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 4
- **Total points état** : 8

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| discharge_pressure | discharge air pressure sensor | bar | 0-15 | 30sec | Pression air comprimé sortie |
| inlet_pressure | inlet air pressure sensor | bar | 0.9-1.1 | 1min | Pression air entrée (atmosphérique) |
| system_pressure | system air pressure sensor | bar | 5-13 | 30sec | Pression réseau air comprimé |
| discharge_temp | discharge air temp sensor | °C | 40-120 | 1min | Température air comprimé sortie |
| oil_temp | oil temp sensor | °C | 40-100 | 1min | Température huile (si lubrifié) |
| oil_pressure | oil pressure sensor | bar | 1-5 | 1min | Pression huile |
| motor_current | motor elec current sensor | A | 0-500 | 1min | Courant moteur |
| motor_power | motor elec power sensor | kW | 0-500 | 5min | Puissance électrique consommée |
| air_flow | air flow sensor | m³/min | 0-50 | 1min | Débit air comprimé (FAD) |
| dewpoint | dewpoint temp sensor | °C | -40-20 | 5min | Point de rosée (si sécheur) |
| run_hours | run hours sensor | h | 0-99999 | 15min | Heures de fonctionnement |
| load_hours | load hours sensor | h | 0-99999 | 15min | Heures en charge |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| enable_cmd | enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |
| pressure_sp | pressure sp | bar | 5-13 | Consigne | Consigne pression réseau |
| load_cmd | load cmd | - | 0/1 | Actionneur | Commande mise en charge |
| capacity_cmd | capacity cmd | % | 0-100 | Actionneur | Commande capacité (VSD) |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| compressor_run | compressor run status | Boolean | true/false | Compresseur en marche |
| compressor_loaded | compressor loaded status | Boolean | true/false | Compresseur en charge |
| motor_fault | motor fault alarm | Boolean | true/false | Défaut moteur |
| high_temp_alarm | high temp alarm | Boolean | true/false | Alarme haute température |
| high_pressure_alarm | high pressure alarm | Boolean | true/false | Alarme haute pression |
| low_oil_alarm | low oil alarm | Boolean | true/false | Alarme niveau/pression huile |
| filter_dirty_alarm | filter dirty alarm | Boolean | true/false | Alarme filtre encrassé |
| maintenance_alarm | maintenance alarm | Boolean | true/false | Alarme maintenance requise |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | Profibus |
|-------|---------------|-----------------|----------|
| discharge_pressure | AI:1 | 40001 (HR) | DB1.DBD0 |
| inlet_pressure | AI:2 | 40002 (HR) | DB1.DBD4 |
| system_pressure | AI:3 | 40003 (HR) | DB1.DBD8 |
| discharge_temp | AI:4 | 40004 (HR) | DB1.DBD12 |
| oil_temp | AI:5 | 40005 (HR) | DB1.DBD16 |
| oil_pressure | AI:6 | 40006 (HR) | DB1.DBD20 |
| motor_current | AI:7 | 40007 (HR) | DB1.DBD24 |
| motor_power | AI:8 | 40008 (HR) | DB1.DBD28 |
| air_flow | AI:9 | 40009 (HR) | DB1.DBD32 |
| dewpoint | AI:10 | 40010 (HR) | DB1.DBD36 |
| run_hours | AI:11 | 40011 (HR) | DB1.DBD40 |
| load_hours | AI:12 | 40012 (HR) | DB1.DBD44 |
| enable_cmd | BO:1 | 00001 (Coil) | DB2.DBX0.0 |
| pressure_sp | AV:1 | 40101 (HR) | DB2.DBD4 |
| load_cmd | BO:2 | 00002 (Coil) | DB2.DBX0.1 |
| capacity_cmd | AO:1 | 40201 (HR) | DB2.DBD8 |
| compressor_run | BI:1 | 10001 (DI) | DB3.DBX0.0 |
| compressor_loaded | BI:2 | 10002 (DI) | DB3.DBX0.1 |
| motor_fault | BI:3 | 10003 (DI) | DB3.DBX0.2 |
| high_temp_alarm | BI:4 | 10004 (DI) | DB3.DBX0.3 |
| high_pressure_alarm | BI:5 | 10005 (DI) | DB3.DBX0.4 |
| low_oil_alarm | BI:6 | 10006 (DI) | DB3.DBX0.5 |
| filter_dirty_alarm | BI:7 | 10007 (DI) | DB3.DBX0.6 |
| maintenance_alarm | BI:8 | 10008 (DI) | DB3.DBX0.7 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- Profibus : DB = Data Block

## Seuils d'Alarme Typiques

| Paramètre | Avertissement | Alarme | Action |
|-----------|---------------|--------|--------|
| Température sortie | > 100°C | > 110°C | Arrêt |
| Pression sortie | > 12 bar | > 13 bar | Décharge |
| Température huile | > 90°C | > 100°C | Arrêt |
| Point de rosée | > 5°C | > 10°C | Alarme qualité |

## Sources
- Atlas Copco - Elektronikon Controller Documentation
- Kaeser - Sigma Air Manager
- CompAir - BACnet/Modbus Integration Guide
- ISO 8573 - Compressed Air Quality Standards
