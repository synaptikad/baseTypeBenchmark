# Points de Ventiloconvecteur (Unit Ventilator)

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 8
- **Total points état** : 6

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_temp | zone air temp sensor | °C | 18-28 | 1min | Température de la zone |
| discharge_temp | discharge air temp sensor | °C | 12-35 | 1min | Température air soufflé |
| outdoor_temp | outside air temp sensor | °C | -20-45 | 1min | Température air extérieur (local ou BMS) |
| mixed_temp | mixed air temp sensor | °C | 10-30 | 1min | Température air mélangé |
| supply_flow | supply air flow sensor | m³/h | 0-3000 | 1min | Débit air total soufflé |
| oa_flow | outside air flow sensor | m³/h | 0-1500 | 1min | Débit air neuf |
| chw_entering_temp | entering chilled water temp sensor | °C | 5-15 | 1min | Température eau glacée entrée |
| hw_entering_temp | entering hot water temp sensor | °C | 35-60 | 1min | Température eau chaude entrée |
| fan_speed | fan speed sensor | % | 0-100 | 1min | Vitesse ventilateur |
| filter_dp | filter differential pressure sensor | Pa | 50-300 | 5min | Pression différentielle filtre |
| zone_co2 | zone co2 sensor | ppm | 400-2000 | 5min | Concentration CO2 (optionnel) |
| zone_humidity | zone air humidity sensor | %RH | 30-70 | 5min | Humidité zone (optionnel) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_cooling_sp | zone air temp cooling sp | °C | 22-28 | Consigne | Consigne température refroidissement |
| zone_temp_heating_sp | zone air temp heating sp | °C | 18-22 | Consigne | Consigne température chauffage |
| fan_speed_cmd | fan speed cmd | % | 0-100 | Actionneur | Commande vitesse ventilateur |
| oa_damper_cmd | outside air damper cmd | % | 0-100 | Actionneur | Position registre air neuf |
| chw_valve_cmd | chilled water valve cmd | % | 0-100 | Actionneur | Position vanne eau glacée |
| hw_valve_cmd | hot water valve cmd | % | 0-100 | Actionneur | Position vanne eau chaude |
| oa_min_sp | outside air min sp | % | 15-30 | Consigne | Minimum air neuf |
| enable_cmd | enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| fan_run | fan run status | Boolean | true/false | Ventilateur en marche |
| heating_active | heating run status | Boolean | true/false | Chauffage actif |
| cooling_active | cooling run status | Boolean | true/false | Refroidissement actif |
| economizer_active | economizer run status | Boolean | true/false | Mode économiseur actif |
| filter_dirty_alarm | filter dirty alarm | Boolean | true/false | Alarme filtre encrassé |
| unit_fault | unit fault alarm | Boolean | true/false | Défaut général unité |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_temp | AI:1 | 40001 (HR) | 1/1/1 |
| discharge_temp | AI:2 | 40002 (HR) | 1/1/2 |
| outdoor_temp | AI:3 | 40003 (HR) | 1/1/3 |
| mixed_temp | AI:4 | 40004 (HR) | 1/1/4 |
| supply_flow | AI:5 | 40005 (HR) | 1/1/5 |
| oa_flow | AI:6 | 40006 (HR) | 1/1/6 |
| chw_entering_temp | AI:7 | 40007 (HR) | 1/1/7 |
| hw_entering_temp | AI:8 | 40008 (HR) | 1/1/8 |
| fan_speed | AI:9 | 40009 (HR) | 1/1/9 |
| filter_dp | AI:10 | 40010 (HR) | 1/1/10 |
| zone_co2 | AI:11 | 40011 (HR) | 1/1/11 |
| zone_humidity | AI:12 | 40012 (HR) | 1/1/12 |
| zone_temp_cooling_sp | AV:1 | 40101 (HR) | 1/2/1 |
| zone_temp_heating_sp | AV:2 | 40102 (HR) | 1/2/2 |
| fan_speed_cmd | AO:1 | 40201 (HR) | 1/2/3 |
| oa_damper_cmd | AO:2 | 40202 (HR) | 1/2/4 |
| chw_valve_cmd | AO:3 | 40203 (HR) | 1/2/5 |
| hw_valve_cmd | AO:4 | 40204 (HR) | 1/2/6 |
| oa_min_sp | AV:3 | 40103 (HR) | 1/2/7 |
| enable_cmd | BO:1 | 00001 (Coil) | 1/2/8 |
| fan_run | BI:1 | 10001 (DI) | 1/3/1 |
| heating_active | BI:2 | 10002 (DI) | 1/3/2 |
| cooling_active | BI:3 | 10003 (DI) | 1/3/3 |
| economizer_active | BI:4 | 10004 (DI) | 1/3/4 |
| filter_dirty_alarm | BI:5 | 10005 (DI) | 1/3/5 |
| unit_fault | BI:6 | 10006 (DI) | 1/3/6 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Modes de Ventilation ASHRAE

| Mode | Air Neuf | Recirculation | Application |
|------|----------|---------------|-------------|
| Minimum OA | 15-30% | 70-85% | Conditions normales |
| 100% Air Neuf | 100% | 0% | Free-cooling ou flush |
| Recirculation | 0% | 100% | Préchauffage (interdit ASHRAE 62.1) |

## Séquence Typique (Salle de Classe)

| État | Ventilateur | Air Neuf | Chauffage | Refroidissement |
|------|-------------|----------|-----------|-----------------|
| Inoccupé | Off | Fermé | Off | Off |
| Pré-occupation | On (low) | Minimum | Si T < SP | Off |
| Occupé | On (auto) | DCV ou min | Modulé | Modulé |
| Free-cooling | On (high) | 100% | Off | Off |

## Sources
- ASHRAE Standard 62.1 - Classroom Ventilation Requirements
- Project Haystack - Unit Ventilator Tags
- Brick Schema - Unit_Ventilator Class
- Trane / Carrier Unit Ventilator Application Guides
