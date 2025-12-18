# Points d'Unité à Induction (Induction Unit)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 4
- **Total points état** : 4

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_temp | zone air temp sensor | °C | 18-28 | 1min | Température de la zone |
| discharge_temp | discharge air temp sensor | °C | 14-35 | 1min | Température air soufflé (mélangé) |
| primary_air_temp | entering air temp sensor | °C | 12-20 | 1min | Température air primaire entrant |
| coil_water_entering_temp | entering water temp sensor | °C | 6-60 | 1min | Température eau entrée batterie |
| coil_water_leaving_temp | leaving water temp sensor | °C | 10-55 | 1min | Température eau sortie batterie |
| primary_air_flow | entering air flow sensor | l/s | 20-100 | 1min | Débit air primaire |
| induced_air_temp | induced air temp sensor | °C | 18-28 | 1min | Température air induit (zone) |
| primary_air_pressure | entering air pressure sensor | Pa | 100-500 | 1min | Pression statique air primaire |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_sp | zone air temp sp | °C | 18-26 | Consigne | Consigne température zone |
| chw_valve_cmd | chilled water valve cmd | % | 0-100 | Actionneur | Position vanne eau glacée |
| hw_valve_cmd | hot water valve cmd | % | 0-100 | Actionneur | Position vanne eau chaude |
| changeover_cmd | changeover cmd | - | heat/cool | Actionneur | Commande changement mode (2 tubes) |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| cooling_mode | cooling mode status | Boolean | true/false | Mode refroidissement actif |
| heating_mode | heating mode status | Boolean | true/false | Mode chauffage actif |
| valve_fault | valve fault alarm | Boolean | true/false | Défaut vanne motorisée |
| zone_occupied | zone occupied status | Boolean | true/false | Zone occupée |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_temp | AI:1 | 40001 (HR) | 1/1/1 |
| discharge_temp | AI:2 | 40002 (HR) | 1/1/2 |
| primary_air_temp | AI:3 | 40003 (HR) | 1/1/3 |
| coil_water_entering_temp | AI:4 | 40004 (HR) | 1/1/4 |
| coil_water_leaving_temp | AI:5 | 40005 (HR) | 1/1/5 |
| primary_air_flow | AI:6 | 40006 (HR) | 1/1/6 |
| induced_air_temp | AI:7 | 40007 (HR) | 1/1/7 |
| primary_air_pressure | AI:8 | 40008 (HR) | 1/1/8 |
| zone_temp_sp | AV:1 | 40101 (HR) | 1/2/1 |
| chw_valve_cmd | AO:1 | 40201 (HR) | 1/2/2 |
| hw_valve_cmd | AO:2 | 40202 (HR) | 1/2/3 |
| changeover_cmd | BO:1 | 00001 (Coil) | 1/2/4 |
| cooling_mode | BI:1 | 10001 (DI) | 1/3/1 |
| heating_mode | BI:2 | 10002 (DI) | 1/3/2 |
| valve_fault | BI:3 | 10003 (DI) | 1/3/3 |
| zone_occupied | BI:4 | 10004 (DI) | 1/3/4 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Configurations Hydrauliques

| Configuration | Tubes | Fonctionnement | Points Spécifiques |
|---------------|-------|----------------|-------------------|
| 2 tubes | 2 | Changeover saisonnier | changeover_cmd |
| 4 tubes | 4 | Chaud et froid simultané | chw_valve_cmd + hw_valve_cmd |

## Ratio d'Induction Typique

| Type | Ratio (primaire:induit) | Débit Zone Total | Application |
|------|-------------------------|------------------|-------------|
| Faible induction | 1:2 | 3x air primaire | Charges modérées |
| Moyenne induction | 1:3 | 4x air primaire | Standard |
| Haute induction | 1:4 à 1:5 | 5-6x air primaire | Charges élevées |

## Différences avec Autres Terminaux

| Caractéristique | Induction Unit | Chilled Beam Active | Fan Coil |
|-----------------|----------------|---------------------|----------|
| Air primaire | Haute pression | Basse pression | Optionnel |
| Ventilateur local | Non | Non | Oui |
| Ratio induction | 1:2 à 1:5 | 1:2 à 1:4 | N/A |
| Bruit | Jet air (modéré) | Faible | Ventilateur |

## Sources
- ASHRAE Handbook - Induction Systems (historique)
- Project Haystack - Induction Unit Tags
- Brick Schema - Induction_Unit Class
- Carrier / Trane - Legacy Induction Unit Documentation
