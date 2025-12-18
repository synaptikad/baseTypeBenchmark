# Points d'Aérotherme (Unit Heater)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_temp | zone air temp sensor | °C | 5-30 | 1min | Température de la zone |
| discharge_temp | discharge air temp sensor | °C | 20-60 | 1min | Température air soufflé |
| water_entering_temp | entering hot water temp sensor | °C | 40-80 | 1min | Température eau chaude entrée (si hydraulique) |
| water_leaving_temp | leaving hot water temp sensor | °C | 30-70 | 1min | Température eau chaude sortie (si hydraulique) |
| fan_current | fan motor current sensor | A | 0-20 | 5min | Courant moteur ventilateur |
| gas_pressure | gas pressure sensor | mbar | 0-50 | 1min | Pression gaz (si gaz) |
| flue_temp | flue gas temp sensor | °C | 100-300 | 1min | Température fumées (si gaz) |
| run_hours | run hours sensor | h | 0-99999 | 15min | Heures de fonctionnement |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_sp | zone air temp sp | °C | 10-25 | Consigne | Consigne température zone |
| enable_cmd | enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |
| hw_valve_cmd | hot water valve cmd | % | 0-100 | Actionneur | Commande vanne eau chaude (si hydraulique) |
| heating_stage_cmd | heating stage cmd | - | 0-3 | Actionneur | Étage de chauffage (si multi-étage) |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| fan_run | fan run status | Boolean | true/false | Ventilateur en marche |
| heating_active | heating run status | Boolean | true/false | Chauffage actif |
| burner_active | burner run status | Boolean | true/false | Brûleur actif (si gaz) |
| fan_fault | fan fault alarm | Boolean | true/false | Défaut ventilateur |
| flame_failure | flame failure alarm | Boolean | true/false | Défaut flamme (si gaz) |
| high_limit_trip | high limit alarm | Boolean | true/false | Déclenchement thermostat limite haute |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_temp | AI:1 | 40001 (HR) | 1/1/1 |
| discharge_temp | AI:2 | 40002 (HR) | 1/1/2 |
| water_entering_temp | AI:3 | 40003 (HR) | 1/1/3 |
| water_leaving_temp | AI:4 | 40004 (HR) | 1/1/4 |
| fan_current | AI:5 | 40005 (HR) | 1/1/5 |
| gas_pressure | AI:6 | 40006 (HR) | 1/1/6 |
| flue_temp | AI:7 | 40007 (HR) | 1/1/7 |
| run_hours | AI:8 | 40008 (HR) | 1/1/8 |
| zone_temp_sp | AV:1 | 40101 (HR) | 1/2/1 |
| enable_cmd | BO:1 | 00001 (Coil) | 1/2/2 |
| hw_valve_cmd | AO:1 | 40201 (HR) | 1/2/3 |
| heating_stage_cmd | AO:2 | 40202 (HR) | 1/2/4 |
| fan_run | BI:1 | 10001 (DI) | 1/3/1 |
| heating_active | BI:2 | 10002 (DI) | 1/3/2 |
| burner_active | BI:3 | 10003 (DI) | 1/3/3 |
| fan_fault | BI:4 | 10004 (DI) | 1/3/4 |
| flame_failure | BI:5 | 10005 (DI) | 1/3/5 |
| high_limit_trip | BI:6 | 10006 (DI) | 1/3/6 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Points Spécifiques par Type

| Type Aérotherme | Points Additionnels |
|-----------------|---------------------|
| Eau chaude | water_entering_temp, water_leaving_temp, hw_valve_cmd |
| Vapeur | steam_pressure, steam_valve_cmd |
| Électrique | heating_current, element_status |
| Gaz | gas_pressure, flue_temp, burner_active, flame_failure |

## Seuils de Sécurité

| Protection | Seuil | Action |
|------------|-------|--------|
| Température limite haute | 80-90°C | Arrêt immédiat |
| Défaut flamme (gaz) | Détection | Fermeture gaz + alarme |
| Température fumées (gaz) | > 250°C | Alarme surchauffe |
| Surcharge moteur | > 1.2x nominal | Arrêt ventilateur |

## Sources
- ASHRAE Handbook - Space Heating Equipment
- Project Haystack - Unit Heater Tags
- Brick Schema - Unit_Heater Class
- Manufacturer BACnet Integration Guides (Reznor, Modine, Trane)
