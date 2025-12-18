# Points de Thermostat (Thermostat)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 7
- **Total points état** : 5

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_temp | zone air temp sensor | °C | 15-35 | 1min | Température ambiante mesurée |
| zone_humidity | zone air humidity sensor | %RH | 20-80 | 5min | Humidité relative (si équipé) |
| zone_co2 | zone air co2 sensor | ppm | 400-2000 | 5min | Concentration CO2 (si équipé) |
| outdoor_temp | outside air temp sensor | °C | -20-45 | 5min | Température extérieure (affichage) |
| floor_temp | floor surface temp sensor | °C | 18-35 | 5min | Température sol (plancher chauffant) |
| supply_temp | supply air temp sensor | °C | 10-45 | 1min | Température soufflage (si sonde déportée) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_sp | zone air temp sp | °C | 15-30 | Consigne | Consigne température occupée |
| zone_temp_heating_sp | zone air temp heating sp | °C | 15-24 | Consigne | Consigne chauffage |
| zone_temp_cooling_sp | zone air temp cooling sp | °C | 22-30 | Consigne | Consigne climatisation |
| zone_temp_standby_sp | zone air temp standby sp | °C | 12-28 | Consigne | Consigne mode économique |
| hvac_mode_cmd | hvac mode cmd | - | 0-4 | Actionneur | Mode HVAC (Off/Heat/Cool/Auto/Fan) |
| fan_speed_cmd | fan speed cmd | - | 0-3 | Actionneur | Vitesse ventilateur (Off/Low/Med/High) |
| occ_override_cmd | occ override cmd | - | 0/1 | Actionneur | Forçage mode occupé |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| occ_status | occ status | Boolean | true/false | Zone occupée (capteur ou programme) |
| heating_active | heating run status | Boolean | true/false | Demande chauffage active |
| cooling_active | cooling run status | Boolean | true/false | Demande climatisation active |
| fan_run | fan run status | Boolean | true/false | Ventilateur en marche |
| window_open | window open status | Boolean | true/false | Fenêtre ouverte (contact) |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_temp | AI:1 | 40001 (HR) | 1/1/1 |
| zone_humidity | AI:2 | 40002 (HR) | 1/1/2 |
| zone_co2 | AI:3 | 40003 (HR) | 1/1/3 |
| zone_temp_sp | AV:1 | 40101 (HR) | 1/2/1 |
| zone_temp_heating_sp | AV:2 | 40102 (HR) | 1/2/2 |
| zone_temp_cooling_sp | AV:3 | 40103 (HR) | 1/2/3 |
| zone_temp_standby_sp | AV:4 | 40104 (HR) | 1/2/4 |
| hvac_mode_cmd | MSV:1 | 40201 (HR) | 1/3/1 |
| fan_speed_cmd | MSV:2 | 40202 (HR) | 1/3/2 |
| occ_override_cmd | BO:1 | 00001 (Coil) | 1/3/3 |
| occ_status | BI:1 | 10001 (DI) | 1/4/1 |
| heating_active | BI:2 | 10002 (DI) | 1/4/2 |
| cooling_active | BI:3 | 10003 (DI) | 1/4/3 |
| fan_run | BI:4 | 10004 (DI) | 1/4/4 |
| window_open | BI:5 | 10005 (DI) | 1/4/5 |

## Modes HVAC (MSV:1)

| Valeur | Mode | Description |
|--------|------|-------------|
| 0 | Off | Système arrêté |
| 1 | Heat | Chauffage uniquement |
| 2 | Cool | Climatisation uniquement |
| 3 | Auto | Changeover automatique |
| 4 | Fan Only | Ventilation seule |

## Vitesses Ventilateur (MSV:2)

| Valeur | Vitesse | Description |
|--------|---------|-------------|
| 0 | Off | Ventilateur arrêté |
| 1 | Low | Petite vitesse |
| 2 | Medium | Vitesse moyenne |
| 3 | High | Grande vitesse |
| 4 | Auto | Vitesse automatique |

## Gestion de la Bande Morte

| Paramètre | Valeur typique | Description |
|-----------|----------------|-------------|
| Deadband | 1-2°C | Écart entre consignes chaud/froid |
| Heating offset | -1°C | Décalage consigne chauffage |
| Cooling offset | +1°C | Décalage consigne climatisation |

Exemple : Consigne 22°C → Chauffe si < 21°C, Refroidit si > 23°C

## Modes d'Occupation

| Mode | Consigne typique | Application |
|------|------------------|-------------|
| Occupied | 21-23°C | Présence active |
| Standby | 18-25°C | Absence courte |
| Unoccupied | 15-28°C | Nuit/weekend |
| Frost protection | 7°C | Protection gel |

## Sources
- ASHRAE Standard 55 - Thermal Comfort
- EN 15500 - Building Automation Controls
- Project Haystack - Thermostat Tags
- Brick Schema - Thermostat Class
- Honeywell / Siemens / Schneider - Thermostat Integration Guides
