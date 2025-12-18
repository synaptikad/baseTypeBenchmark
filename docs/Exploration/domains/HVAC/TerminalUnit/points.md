# Points d'Unité Terminale (Terminal Unit)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 5

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_temp | zone air temp sensor | °C | 18-28 | 1min | Température de la zone |
| discharge_temp | discharge air temp sensor | °C | 12-35 | 1min | Température air soufflé |
| supply_flow | supply air flow sensor | m³/h | 0-5000 | 1min | Débit d'air soufflé |
| supply_dp | inlet differential pressure sensor | Pa | 0-500 | 1min | Pression différentielle entrée |
| damper_position | damper position sensor | % | 0-100 | 1min | Position registre (si aéraulique) |
| valve_position | valve position sensor | % | 0-100 | 1min | Position vanne eau (si hydraulique) |
| zone_co2 | zone co2 sensor | ppm | 400-2000 | 5min | Concentration CO2 zone (optionnel) |
| fan_speed | fan speed sensor | % | 0-100 | 1min | Vitesse ventilateur (si FCU) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_sp | zone air temp sp | °C | 18-26 | Consigne | Consigne température zone |
| damper_cmd | damper cmd | % | 0-100 | Actionneur | Commande position registre |
| valve_cmd | valve cmd | % | 0-100 | Actionneur | Commande position vanne |
| fan_speed_cmd | fan speed cmd | % | 0-100 | Actionneur | Commande vitesse ventilateur |
| enable_cmd | enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| heating_mode | heating mode status | Boolean | true/false | Mode chauffage actif |
| cooling_mode | cooling mode status | Boolean | true/false | Mode refroidissement actif |
| zone_occupied | zone occupied status | Boolean | true/false | Zone occupée |
| damper_fault | damper fault alarm | Boolean | true/false | Défaut registre/vanne |
| unit_fault | unit fault alarm | Boolean | true/false | Défaut général unité |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_temp | AI:1 | 40001 (HR) | 1/1/1 |
| discharge_temp | AI:2 | 40002 (HR) | 1/1/2 |
| supply_flow | AI:3 | 40003 (HR) | 1/1/3 |
| supply_dp | AI:4 | 40004 (HR) | 1/1/4 |
| damper_position | AI:5 | 40005 (HR) | 1/1/5 |
| valve_position | AI:6 | 40006 (HR) | 1/1/6 |
| zone_co2 | AI:7 | 40007 (HR) | 1/1/7 |
| fan_speed | AI:8 | 40008 (HR) | 1/1/8 |
| zone_temp_sp | AV:1 | 40101 (HR) | 1/2/1 |
| damper_cmd | AO:1 | 40201 (HR) | 1/2/2 |
| valve_cmd | AO:2 | 40202 (HR) | 1/2/3 |
| fan_speed_cmd | AO:3 | 40203 (HR) | 1/2/4 |
| enable_cmd | BO:1 | 00001 (Coil) | 1/2/5 |
| heating_mode | BI:1 | 10001 (DI) | 1/3/1 |
| cooling_mode | BI:2 | 10002 (DI) | 1/3/2 |
| zone_occupied | BI:3 | 10003 (DI) | 1/3/3 |
| damper_fault | BI:4 | 10004 (DI) | 1/3/4 |
| unit_fault | BI:5 | 10005 (DI) | 1/3/5 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Types d'Unités Terminales

| Type | Registre | Vanne | Ventilateur | Application |
|------|----------|-------|-------------|-------------|
| VAV | Oui | Optionnel (reheat) | Non | Débit variable |
| CAV | Non | Optionnel | Non | Débit constant |
| FCU | Non | Oui | Oui | Ventilo-convecteur |
| Chilled Beam | Non | Oui | Non (induction) | Poutre froide |
| Radiant Panel | Non | Oui | Non | Panneau rayonnant |

## Points Typiques par Type

| Type Terminal | Points Mesure | Points Commande | Points État |
|---------------|---------------|-----------------|-------------|
| VAV simple | 4 | 3 | 3 |
| VAV avec reheat | 6 | 5 | 4 |
| FCU 2 tubes | 5 | 4 | 4 |
| FCU 4 tubes | 6 | 5 | 4 |

## Sources
- Project Haystack - Terminal Unit Tags
- Brick Schema - Terminal_Unit Class
- ASHRAE Guideline 36 - Terminal Unit Sequences
- BACnet Standard - Zone Terminal Equipment
