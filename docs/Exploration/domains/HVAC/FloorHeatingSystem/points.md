# Points de Plancher Chauffant (Floor Heating System)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 4

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_temp | zone air temp sensor | °C | 18-26 | 1min | Température ambiante zone |
| floor_temp | floor surface temp sensor | °C | 20-35 | 1min | Température surface du sol |
| water_supply_temp | supply water temp sensor | °C | 25-50 | 1min | Température eau départ collecteur |
| water_return_temp | return water temp sensor | °C | 20-45 | 1min | Température eau retour collecteur |
| zone_water_supply_temp | zone supply water temp sensor | °C | 25-45 | 1min | Température eau départ zone |
| zone_water_return_temp | zone return water temp sensor | °C | 20-40 | 1min | Température eau retour zone |
| outdoor_temp | outside air temp sensor | °C | -20-40 | 5min | Température extérieure (loi d'eau) |
| water_flow | zone water flow sensor | l/h | 0-500 | 5min | Débit eau zone |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_sp | zone air temp sp | °C | 18-24 | Consigne | Consigne température zone |
| zone_valve_cmd | zone valve cmd | % | 0-100 | Actionneur | Commande vanne de zone |
| supply_temp_sp | supply water temp sp | °C | 25-50 | Consigne | Consigne température départ |
| floor_temp_limit_sp | floor temp high limit sp | °C | 26-29 | Consigne | Limite température sol |
| heating_curve_offset | heating curve offset sp | K | -5-5 | Consigne | Décalage loi d'eau |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| heating_active | heating run status | Boolean | true/false | Chauffage zone actif |
| valve_open | zone valve open status | Boolean | true/false | Vanne zone ouverte |
| floor_temp_limit_alarm | floor temp high alarm | Boolean | true/false | Alarme température sol élevée |
| pump_run | pump run status | Boolean | true/false | Pompe circulation en marche |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_temp | AI:1 | 40001 (HR) | 1/1/1 |
| floor_temp | AI:2 | 40002 (HR) | 1/1/2 |
| water_supply_temp | AI:3 | 40003 (HR) | 1/1/3 |
| water_return_temp | AI:4 | 40004 (HR) | 1/1/4 |
| zone_water_supply_temp | AI:5 | 40005 (HR) | 1/1/5 |
| zone_water_return_temp | AI:6 | 40006 (HR) | 1/1/6 |
| outdoor_temp | AI:7 | 40007 (HR) | 1/1/7 |
| water_flow | AI:8 | 40008 (HR) | 1/1/8 |
| zone_temp_sp | AV:1 | 40101 (HR) | 1/2/1 |
| zone_valve_cmd | AO:1 | 40201 (HR) | 1/2/2 |
| supply_temp_sp | AV:2 | 40102 (HR) | 1/2/3 |
| floor_temp_limit_sp | AV:3 | 40103 (HR) | 1/2/4 |
| heating_curve_offset | AV:4 | 40104 (HR) | 1/2/5 |
| heating_active | BI:1 | 10001 (DI) | 1/3/1 |
| valve_open | BI:2 | 10002 (DI) | 1/3/2 |
| floor_temp_limit_alarm | BI:3 | 10003 (DI) | 1/3/3 |
| pump_run | BI:4 | 10004 (DI) | 1/3/4 |

## Loi d'Eau Typique

| T_extérieure | T_départ eau | Application |
|--------------|--------------|-------------|
| -10°C | 45°C | Froid intense |
| 0°C | 38°C | Froid |
| 10°C | 30°C | Mi-saison |
| 15°C | 25°C | Doux |
| > 18°C | Arrêt | Pas de chauffage |

## Limites de Température Sol (EN 1264)

| Zone | T_surface max | Application |
|------|---------------|-------------|
| Zones occupées | 29°C | Bureaux, séjour |
| Zones périphériques | 35°C | Bandes vitrées |
| Salles de bains | 33°C | Confort pieds nus |

## Sources
- EN 1264 - Water based surface embedded heating and cooling systems
- ASHRAE Handbook - Radiant Heating and Cooling
- Project Haystack - Radiant Floor Tags
- Uponor / Rehau - Floor Heating Design Guides
