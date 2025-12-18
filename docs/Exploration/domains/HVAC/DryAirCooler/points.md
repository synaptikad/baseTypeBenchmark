# Points d'Aéroréfrigérant (Dry Air Cooler)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 5

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| water_entering_temp | entering water temp sensor | °C | 25-45 | 1min | Température eau entrée (chaude) |
| water_leaving_temp | leaving water temp sensor | °C | 20-40 | 1min | Température eau sortie (refroidie) |
| ambient_temp | outside air temp sensor | °C | -20-45 | 1min | Température air extérieur |
| fan_speed | fan speed sensor | % | 0-100 | 1min | Vitesse ventilateurs |
| water_flow | water flow sensor | m³/h | 0-200 | 1min | Débit d'eau |
| water_dp | differential pressure sensor | kPa | 10-100 | 5min | Perte de charge eau |
| approach_temp | approach temp sensor | K | 5-20 | 5min | Approche (T_eau_sortie - T_air) |
| heat_rejection | heat rejection sensor | kW | 0-2000 | 5min | Puissance rejetée (calculée) |
| motor_current | fan motor current sensor | A | 0-100 | 5min | Courant moteurs ventilateurs |
| adiabatic_water_flow | adiabatic water flow sensor | l/h | 0-500 | 5min | Débit eau pulvérisation (si adiabatique) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| fan_speed_cmd | fan speed cmd | % | 0-100 | Actionneur | Commande vitesse ventilateurs |
| fan_enable_cmd | fan enable cmd | - | 0/1 | Actionneur | Commande marche ventilateurs |
| water_temp_sp | leaving water temp sp | °C | 15-35 | Consigne | Consigne température eau sortie |
| adiabatic_enable_cmd | adiabatic enable cmd | - | 0/1 | Actionneur | Activation mode adiabatique |
| bypass_valve_cmd | bypass valve cmd | % | 0-100 | Actionneur | Commande vanne bypass |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| fan_run | fan run status | Boolean | true/false | Ventilateurs en marche |
| adiabatic_active | adiabatic run status | Boolean | true/false | Mode adiabatique actif |
| fan_fault | fan fault alarm | Boolean | true/false | Défaut ventilateur |
| low_flow_alarm | low flow alarm | Boolean | true/false | Alarme débit eau faible |
| freeze_protect_active | freeze protect alarm | Boolean | true/false | Protection antigel active |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| water_entering_temp | AI:1 | 40001 (HR) |
| water_leaving_temp | AI:2 | 40002 (HR) |
| ambient_temp | AI:3 | 40003 (HR) |
| fan_speed | AI:4 | 40004 (HR) |
| water_flow | AI:5 | 40005 (HR) |
| water_dp | AI:6 | 40006 (HR) |
| approach_temp | AV:1 | 40101 (HR) |
| heat_rejection | AV:2 | 40102 (HR) |
| motor_current | AI:7 | 40007 (HR) |
| adiabatic_water_flow | AI:8 | 40008 (HR) |
| fan_speed_cmd | AO:1 | 40201 (HR) |
| fan_enable_cmd | BO:1 | 00001 (Coil) |
| water_temp_sp | AV:3 | 40103 (HR) |
| adiabatic_enable_cmd | BO:2 | 00002 (Coil) |
| bypass_valve_cmd | AO:2 | 40202 (HR) |
| fan_run | BI:1 | 10001 (DI) |
| adiabatic_active | BI:2 | 10002 (DI) |
| fan_fault | BI:3 | 10003 (DI) |
| low_flow_alarm | BI:4 | 10004 (DI) |
| freeze_protect_active | BI:5 | 10005 (DI) |

## Performance Typique

| Condition | Approche | Mode |
|-----------|----------|------|
| T_air < 15°C | 5-8 K | Sec |
| 15°C < T_air < 25°C | 8-12 K | Sec |
| T_air > 25°C | 12-15 K | Sec ou Adiabatique |
| T_air > 30°C | 6-10 K | Adiabatique |

## Sources
- ASHRAE Handbook - HVAC Systems and Equipment
- Güntner / Alfa Laval - Dry Cooler Selection Guide
- Project Haystack - Dry Cooler Tags
- Brick Schema - Dry_Cooler Class
