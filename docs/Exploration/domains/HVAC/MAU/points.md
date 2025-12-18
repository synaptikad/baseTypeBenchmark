# Points d'Unité d'Air Neuf (MAU - Makeup Air Unit)

## Synthèse
- **Total points mesure** : 16
- **Total points commande** : 10
- **Total points état** : 8

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| outdoor_temp | outside air temp sensor | °C | -20-45 | 1min | Température air extérieur |
| outdoor_humidity | outside air humidity sensor | %RH | 10-100 | 1min | Humidité air extérieur |
| discharge_temp | discharge air temp sensor | °C | 12-30 | 1min | Température air soufflé |
| discharge_humidity | discharge air humidity sensor | %RH | 30-70 | 1min | Humidité air soufflé |
| supply_flow | supply air flow sensor | m³/h | 0-50000 | 1min | Débit air neuf soufflé |
| supply_fan_speed | supply fan speed sensor | % | 0-100 | 1min | Vitesse ventilateur soufflage |
| supply_static_pressure | discharge duct pressure sensor | Pa | 0-1000 | 1min | Pression statique gaine soufflage |
| heating_coil_temp | heating coil leaving temp sensor | °C | 15-40 | 1min | Température après batterie chaude |
| cooling_coil_temp | cooling coil leaving temp sensor | °C | 10-25 | 1min | Température après batterie froide |
| filter_dp | filter differential pressure sensor | Pa | 50-500 | 5min | Pression différentielle filtres |
| erv_efficiency | energy recovery efficiency sensor | % | 40-85 | 5min | Efficacité récupération énergie (si ERV) |
| chw_valve_position | chilled water valve position sensor | % | 0-100 | 1min | Position vanne eau glacée |
| hw_valve_position | hot water valve position sensor | % | 0-100 | 1min | Position vanne eau chaude |
| damper_position | outside air damper position sensor | % | 0-100 | 1min | Position registre air neuf |
| building_pressure | building pressure sensor | Pa | -10-30 | 1min | Pression différentielle bâtiment |
| power_consumption | elec power sensor | kW | 0-100 | 5min | Puissance électrique consommée |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| supply_fan_enable_cmd | supply fan enable cmd | - | 0/1 | Actionneur | Commande marche ventilateur |
| supply_fan_speed_cmd | supply fan speed cmd | % | 0-100 | Actionneur | Commande vitesse ventilateur |
| discharge_temp_sp | discharge air temp sp | °C | 12-25 | Consigne | Consigne température soufflage |
| chw_valve_cmd | chilled water valve cmd | % | 0-100 | Actionneur | Commande vanne eau glacée |
| hw_valve_cmd | hot water valve cmd | % | 0-100 | Actionneur | Commande vanne eau chaude |
| damper_cmd | outside air damper cmd | % | 0-100 | Actionneur | Commande registre air neuf |
| supply_flow_sp | supply air flow sp | m³/h | 2000-50000 | Consigne | Consigne débit air neuf |
| supply_pressure_sp | discharge duct pressure sp | Pa | 200-800 | Consigne | Consigne pression gaine |
| building_pressure_sp | building pressure sp | Pa | 5-25 | Consigne | Consigne pression bâtiment |
| humidification_cmd | humidification cmd | % | 0-100 | Actionneur | Commande humidification (si équipé) |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| supply_fan_run | supply fan run status | Boolean | true/false | Ventilateur soufflage en marche |
| heating_active | heating run status | Boolean | true/false | Chauffage actif |
| cooling_active | cooling run status | Boolean | true/false | Refroidissement actif |
| erv_active | erv run status | Boolean | true/false | Récupération énergie active |
| filter_dirty_alarm | filter dirty alarm | Boolean | true/false | Alarme filtre encrassé |
| freeze_protect_active | freeze protect alarm | Boolean | true/false | Protection antigel active |
| supply_fan_fault | supply fan fault alarm | Boolean | true/false | Défaut ventilateur |
| unit_mode | unit mode status | Enum | off/heat/cool/auto | Mode de fonctionnement |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| outdoor_temp | AI:1 | 40001 (HR) | 1/1/1 |
| outdoor_humidity | AI:2 | 40002 (HR) | 1/1/2 |
| discharge_temp | AI:3 | 40003 (HR) | 1/1/3 |
| discharge_humidity | AI:4 | 40004 (HR) | 1/1/4 |
| supply_flow | AI:5 | 40005 (HR) | 1/1/5 |
| supply_fan_speed | AI:6 | 40006 (HR) | 1/1/6 |
| supply_static_pressure | AI:7 | 40007 (HR) | 1/1/7 |
| heating_coil_temp | AI:8 | 40008 (HR) | 1/1/8 |
| cooling_coil_temp | AI:9 | 40009 (HR) | 1/1/9 |
| filter_dp | AI:10 | 40010 (HR) | 1/1/10 |
| erv_efficiency | AV:1 | 40101 (HR) | 1/1/11 |
| chw_valve_position | AI:11 | 40011 (HR) | 1/1/12 |
| hw_valve_position | AI:12 | 40012 (HR) | 1/1/13 |
| damper_position | AI:13 | 40013 (HR) | 1/1/14 |
| building_pressure | AI:14 | 40014 (HR) | 1/1/15 |
| power_consumption | AI:15 | 40015 (HR) | 1/1/16 |
| supply_fan_enable_cmd | BO:1 | 00001 (Coil) | 1/2/1 |
| supply_fan_speed_cmd | AO:1 | 40201 (HR) | 1/2/2 |
| discharge_temp_sp | AV:2 | 40102 (HR) | 1/2/3 |
| chw_valve_cmd | AO:2 | 40202 (HR) | 1/2/4 |
| hw_valve_cmd | AO:3 | 40203 (HR) | 1/2/5 |
| damper_cmd | AO:4 | 40204 (HR) | 1/2/6 |
| supply_flow_sp | AV:3 | 40103 (HR) | 1/2/7 |
| supply_pressure_sp | AV:4 | 40104 (HR) | 1/2/8 |
| building_pressure_sp | AV:5 | 40105 (HR) | 1/2/9 |
| humidification_cmd | AO:5 | 40205 (HR) | 1/2/10 |
| supply_fan_run | BI:1 | 10001 (DI) | 1/3/1 |
| heating_active | BI:2 | 10002 (DI) | 1/3/2 |
| cooling_active | BI:3 | 10003 (DI) | 1/3/3 |
| erv_active | BI:4 | 10004 (DI) | 1/3/4 |
| filter_dirty_alarm | BI:5 | 10005 (DI) | 1/3/5 |
| freeze_protect_active | BI:6 | 10006 (DI) | 1/3/6 |
| supply_fan_fault | BI:7 | 10007 (DI) | 1/3/7 |
| unit_mode | MSV:1 | 40301 (HR) | 1/3/8 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Équilibrage avec Extraction

| Stratégie | Description | Points Clés |
|-----------|-------------|-------------|
| Pression bâtiment | Maintien d'une surpression | building_pressure_sp |
| Équilibre débits | MAU = Σ Extraction | supply_flow_sp = exhaust_flow_total |
| Compensation hottes | Débit MAU varie avec extraction cuisine | Liaison avec hottes |

## Sources
- ASHRAE Standard 62.1 - Ventilation for Acceptable Indoor Air Quality
- Greenheck MAU BACnet Documentation
- Project Haystack - MAU Equipment Tags
- Brick Schema - Makeup_Air_Unit Class
