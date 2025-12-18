# Points de Rafraîchisseur Évaporatif (Evaporative Cooler)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 6

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| outdoor_temp | outside air temp sensor | °C | 20-45 | 1min | Température air extérieur entrée |
| outdoor_humidity | outside air humidity sensor | %RH | 10-60 | 1min | Humidité air extérieur |
| outdoor_wetbulb | outside air wetbulb temp sensor | °C | 10-30 | 1min | Température bulbe humide extérieur |
| discharge_temp | discharge air temp sensor | °C | 15-35 | 1min | Température air soufflé |
| discharge_humidity | discharge air humidity sensor | %RH | 40-90 | 1min | Humidité air soufflé |
| zone_temp | zone air temp sensor | °C | 20-35 | 1min | Température de la zone |
| supply_flow | supply air flow sensor | m³/h | 0-50000 | 1min | Débit air soufflé |
| water_consumption | water flow sensor | l/h | 0-500 | 5min | Consommation d'eau |
| water_tank_level | water level sensor | % | 0-100 | 5min | Niveau réservoir eau |
| power_consumption | elec power sensor | kW | 0-20 | 5min | Puissance électrique consommée |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| fan_speed_cmd | fan speed cmd | % | 0-100 | Actionneur | Commande vitesse ventilateur |
| pump_enable_cmd | pump enable cmd | - | 0/1 | Actionneur | Commande pompe circulation eau |
| enable_cmd | enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |
| zone_temp_sp | zone air temp sp | °C | 22-30 | Consigne | Consigne température zone |
| humidity_limit_sp | humidity high limit sp | %RH | 60-80 | Consigne | Limite haute humidité soufflage |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| fan_run | fan run status | Boolean | true/false | Ventilateur en marche |
| pump_run | pump run status | Boolean | true/false | Pompe eau en marche |
| low_water_alarm | low water alarm | Boolean | true/false | Alarme niveau eau bas |
| fan_fault | fan fault alarm | Boolean | true/false | Défaut ventilateur |
| pump_fault | pump fault alarm | Boolean | true/false | Défaut pompe |
| media_dirty_alarm | media dirty alarm | Boolean | true/false | Alarme média encrassé |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| outdoor_temp | AI:1 | 40001 (HR) |
| outdoor_humidity | AI:2 | 40002 (HR) |
| outdoor_wetbulb | AV:1 | 40101 (HR) |
| discharge_temp | AI:3 | 40003 (HR) |
| discharge_humidity | AI:4 | 40004 (HR) |
| zone_temp | AI:5 | 40005 (HR) |
| supply_flow | AI:6 | 40006 (HR) |
| water_consumption | AI:7 | 40007 (HR) |
| water_tank_level | AI:8 | 40008 (HR) |
| power_consumption | AI:9 | 40009 (HR) |
| fan_speed_cmd | AO:1 | 40201 (HR) |
| pump_enable_cmd | BO:1 | 00001 (Coil) |
| enable_cmd | BO:2 | 00002 (Coil) |
| zone_temp_sp | AV:2 | 40102 (HR) |
| humidity_limit_sp | AV:3 | 40103 (HR) |
| fan_run | BI:1 | 10001 (DI) |
| pump_run | BI:2 | 10002 (DI) |
| low_water_alarm | BI:3 | 10003 (DI) |
| fan_fault | BI:4 | 10004 (DI) |
| pump_fault | BI:5 | 10005 (DI) |
| media_dirty_alarm | BI:6 | 10006 (DI) |

## Efficacité selon Conditions

| T_bulbe_sec | T_bulbe_humide | Delta T possible | Efficacité |
|-------------|----------------|------------------|------------|
| 35°C | 20°C | ~12°C | Excellente |
| 35°C | 25°C | ~8°C | Bonne |
| 35°C | 30°C | ~4°C | Faible |

## Calcul Température Sortie (Direct)

```
T_sortie = T_entrée - (Efficacité × (T_bulbe_sec - T_bulbe_humide))
```

Avec efficacité typique de 80% :
- Entrée 35°C / 20% HR (bulbe humide 18°C) → Sortie ~21°C

## Sources
- ASHRAE Handbook - Evaporative Air-Cooling Equipment
- Project Haystack - Evaporative Cooler Tags
- Brick Schema - Evaporative_Cooler Class
- Munters / Seeley - Evaporative Cooling Application Guide
