# Points de Vanne Motorisée (Valve)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| valve_position | valve position sensor | % | 0-100 | 1min | Position réelle de la vanne |
| water_flow | water flow sensor | m³/h | 0-100 | 1min | Débit d'eau à travers la vanne |
| water_entering_temp | entering water temp sensor | °C | 5-80 | 1min | Température eau entrée |
| water_leaving_temp | leaving water temp sensor | °C | 5-80 | 1min | Température eau sortie |
| differential_pressure | differential pressure sensor | kPa | 0-100 | 1min | Pression différentielle aux bornes |
| actuator_torque | actuator torque sensor | Nm | 0-50 | 5min | Couple mesuré (actionneurs communicants) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| valve_cmd | valve cmd | % | 0-100 | Actionneur | Commande position vanne |
| valve_min_sp | valve min position sp | % | 0-30 | Consigne | Position minimale autorisée |
| valve_max_sp | valve max position sp | % | 70-100 | Consigne | Position maximale autorisée |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| valve_open | valve open status | Boolean | true/false | Vanne ouverte (fin de course) |
| valve_closed | valve closed status | Boolean | true/false | Vanne fermée (fin de course) |
| valve_moving | valve moving status | Boolean | true/false | Vanne en mouvement |
| valve_fault | valve fault alarm | Boolean | true/false | Défaut actionneur |
| valve_override | valve override status | Boolean | true/false | Forçage manuel actif |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| valve_position | AI:1 | 40001 (HR) | 1/1/1 |
| water_flow | AI:2 | 40002 (HR) | 1/1/2 |
| water_entering_temp | AI:3 | 40003 (HR) | 1/1/3 |
| water_leaving_temp | AI:4 | 40004 (HR) | 1/1/4 |
| differential_pressure | AI:5 | 40005 (HR) | 1/1/5 |
| actuator_torque | AI:6 | 40006 (HR) | 1/1/6 |
| valve_cmd | AO:1 | 40101 (HR) | 1/2/1 |
| valve_min_sp | AV:1 | 40201 (HR) | 1/2/2 |
| valve_max_sp | AV:2 | 40202 (HR) | 1/2/3 |
| valve_open | BI:1 | 10001 (DI) | 1/3/1 |
| valve_closed | BI:2 | 10002 (DI) | 1/3/2 |
| valve_moving | BI:3 | 10003 (DI) | 1/3/3 |
| valve_fault | BI:4 | 10004 (DI) | 1/3/4 |
| valve_override | BI:5 | 10005 (DI) | 1/3/5 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Types de Vannes et Caractéristiques

| Type | Configuration | Débit | Application |
|------|---------------|-------|-------------|
| 2 voies | Entrée/Sortie | Variable (0-100%) | Régulation terminaux, circuit variable |
| 3 voies mélange | 2 entrées/1 sortie | Constant | Mélange eau chaude/froide |
| 3 voies dérivation | 1 entrée/2 sorties | Constant | Bypass de batterie |

## Courbes de Débit

| Caractéristique | Formule | Application |
|-----------------|---------|-------------|
| Linéaire | Q = Kvs × √(ΔP) × (position/100) | Régulation simple |
| Équipourcentage | Q = Kvs × √(ΔP) × R^((position/100)-1) | Régulation température |
| Ouverture rapide | Non-linéaire | On/off avec modulation douce |

## Signaux de Commande

| Type Signal | Spécification | Application |
|-------------|---------------|-------------|
| Analogique | 0-10V DC | Standard modulant |
| Analogique | 2-10V DC | Fail-safe (ressort de rappel) |
| Analogique | 4-20mA | Environnement industriel |
| Tout-ou-rien | 24VAC | Vanne on/off |
| BACnet MS/TP | RS-485 | Actionneur communicant |
| Modbus RTU | RS-485 | Actionneur communicant |

## Temps de Course Typiques

| Type Actionneur | Temps 0-100% | Application |
|-----------------|--------------|-------------|
| Électrothermique | 3-5 min | Radiateurs, planchers |
| Électromécanique rapide | 15-30 sec | Régulation dynamique |
| Électromécanique standard | 60-120 sec | Batteries AHU/FCU |
| Pneumatique | 5-30 sec | Industrie |

## Sources
- [Belimo Valve Actuators](https://www.belimo.com/) - Documentation technique actionneurs
- ASHRAE Handbook - Hydronic Systems and Valves
- Project Haystack - Valve Tags
- Brick Schema - Valve Class
