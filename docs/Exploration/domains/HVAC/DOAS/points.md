# Points de DOAS (Dedicated Outdoor Air System)

## Synthèse
- **Total points mesure** : 18
- **Total points commande** : 10
- **Total points état** : 8

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| outdoor_temp | outside air temp sensor | °C | -20-45 | 1min | Température air extérieur |
| outdoor_humidity | outside air humidity sensor | %RH | 10-100 | 1min | Humidité air extérieur |
| outdoor_dewpoint | outside air dewpoint temp sensor | °C | -30-30 | 1min | Point de rosée air extérieur |
| discharge_temp | discharge air temp sensor | °C | 10-25 | 1min | Température air soufflé |
| discharge_humidity | discharge air humidity sensor | %RH | 30-70 | 1min | Humidité air soufflé |
| discharge_dewpoint | discharge air dewpoint temp sensor | °C | 8-16 | 1min | Point de rosée air soufflé |
| return_temp | return air temp sensor | °C | 18-28 | 1min | Température air reprise (si ERV) |
| return_humidity | return air humidity sensor | %RH | 30-70 | 1min | Humidité air reprise (si ERV) |
| supply_flow | supply air flow sensor | m³/h | 0-50000 | 1min | Débit air neuf soufflé |
| exhaust_flow | exhaust air flow sensor | m³/h | 0-50000 | 1min | Débit air extrait (si ERV) |
| supply_fan_speed | supply fan speed sensor | % | 0-100 | 1min | Vitesse ventilateur soufflage |
| cooling_coil_temp | cooling coil leaving temp sensor | °C | 8-16 | 1min | Température après batterie froide |
| heating_coil_temp | heating coil leaving temp sensor | °C | 14-25 | 1min | Température après réchauffage |
| erv_efficiency | erv sensible efficiency sensor | % | 40-85 | 5min | Efficacité récupération énergie |
| filter_dp | filter differential pressure sensor | Pa | 50-500 | 5min | Pression différentielle filtres |
| chw_valve_position | chilled water valve position sensor | % | 0-100 | 1min | Position vanne eau glacée |
| hw_valve_position | hot water valve position sensor | % | 0-100 | 1min | Position vanne eau chaude |
| supply_static_pressure | discharge duct pressure sensor | Pa | 0-1000 | 1min | Pression statique gaine |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| supply_fan_enable_cmd | supply fan enable cmd | - | 0/1 | Actionneur | Commande marche ventilateur |
| supply_fan_speed_cmd | supply fan speed cmd | % | 0-100 | Actionneur | Commande vitesse ventilateur |
| chw_valve_cmd | chilled water valve cmd | % | 0-100 | Actionneur | Commande vanne eau glacée |
| hw_valve_cmd | hot water valve cmd | % | 0-100 | Actionneur | Commande vanne eau chaude |
| erv_enable_cmd | erv enable cmd | - | 0/1 | Actionneur | Activation récupération énergie |
| discharge_dewpoint_sp | discharge dewpoint sp | °C | 8-14 | Consigne | Consigne point de rosée soufflage |
| discharge_temp_sp | discharge air temp sp | °C | 12-20 | Consigne | Consigne température soufflage |
| supply_flow_sp | supply air flow sp | m³/h | 1000-50000 | Consigne | Consigne débit air neuf |
| supply_pressure_sp | discharge duct pressure sp | Pa | 200-800 | Consigne | Consigne pression gaine |
| dehumidification_cmd | dehumidification cmd | % | 0-100 | Actionneur | Commande déshumidification |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| supply_fan_run | supply fan run status | Boolean | true/false | Ventilateur soufflage en marche |
| cooling_active | cooling run status | Boolean | true/false | Refroidissement/déshumidification actif |
| heating_active | heating run status | Boolean | true/false | Réchauffage actif |
| erv_active | erv run status | Boolean | true/false | Récupération énergie active |
| filter_dirty_alarm | filter dirty alarm | Boolean | true/false | Alarme filtre encrassé |
| freeze_protect_active | freeze protect alarm | Boolean | true/false | Protection antigel active |
| supply_fan_fault | supply fan fault alarm | Boolean | true/false | Défaut ventilateur |
| unit_mode | unit mode status | Enum | off/vent/dehumid/heat | Mode de fonctionnement |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| outdoor_temp | AI:1 | 40001 (HR) |
| outdoor_humidity | AI:2 | 40002 (HR) |
| outdoor_dewpoint | AV:1 | 40101 (HR) |
| discharge_temp | AI:3 | 40003 (HR) |
| discharge_humidity | AI:4 | 40004 (HR) |
| discharge_dewpoint | AV:2 | 40102 (HR) |
| return_temp | AI:5 | 40005 (HR) |
| return_humidity | AI:6 | 40006 (HR) |
| supply_flow | AI:7 | 40007 (HR) |
| exhaust_flow | AI:8 | 40008 (HR) |
| supply_fan_speed | AI:9 | 40009 (HR) |
| cooling_coil_temp | AI:10 | 40010 (HR) |
| heating_coil_temp | AI:11 | 40011 (HR) |
| erv_efficiency | AV:3 | 40103 (HR) |
| filter_dp | AI:12 | 40012 (HR) |
| chw_valve_position | AI:13 | 40013 (HR) |
| hw_valve_position | AI:14 | 40014 (HR) |
| supply_static_pressure | AI:15 | 40015 (HR) |
| supply_fan_enable_cmd | BO:1 | 00001 (Coil) |
| supply_fan_speed_cmd | AO:1 | 40201 (HR) |
| chw_valve_cmd | AO:2 | 40202 (HR) |
| hw_valve_cmd | AO:3 | 40203 (HR) |
| erv_enable_cmd | BO:2 | 00002 (Coil) |
| discharge_dewpoint_sp | AV:4 | 40104 (HR) |
| discharge_temp_sp | AV:5 | 40105 (HR) |
| supply_flow_sp | AV:6 | 40106 (HR) |
| supply_pressure_sp | AV:7 | 40107 (HR) |
| dehumidification_cmd | AO:4 | 40204 (HR) |
| supply_fan_run | BI:1 | 10001 (DI) |
| cooling_active | BI:2 | 10002 (DI) |
| heating_active | BI:3 | 10003 (DI) |
| erv_active | BI:4 | 10004 (DI) |
| filter_dirty_alarm | BI:5 | 10005 (DI) |
| freeze_protect_active | BI:6 | 10006 (DI) |
| supply_fan_fault | BI:7 | 10007 (DI) |
| unit_mode | MSV:1 | 40301 (HR) |

## Consignes Typiques DOAS

| Application | Point de Rosée Cible | Température Soufflage |
|-------------|---------------------|----------------------|
| Bureaux standard | 12-14°C | 16-18°C |
| Avec chilled beams | 10-12°C | 14-16°C |
| Climat humide | 8-10°C | 12-14°C |
| Climat sec | 14-16°C | 18-20°C |

## Sources
- ASHRAE DOAS Design Guide
- Greenheck DOAS BACnet Integration Guide
- Project Haystack - DOAS Equipment Tags
- Brick Schema - DOAS Class
