# Points de Registre Motorisé (Damper)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| damper_position_feedback | damper position sensor | % | 0-100 | 1min | Position réelle du registre (retour potentiomètre) |
| actuator_current | damper actuator current sensor | mA | 0-100 | 5min | Courant consommé par l'actionneur |
| actuator_torque | damper actuator torque sensor | Nm | 0-50 | 5min | Couple mesuré (actionneurs communicants) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| damper_position_cmd | damper cmd | % | 0-100 | Actionneur | Commande position registre |
| damper_min_position_sp | damper min position sp | % | 0-100 | Consigne | Position minimale autorisée |
| damper_max_position_sp | damper max position sp | % | 0-100 | Consigne | Position maximale autorisée |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| damper_open | damper open status | Boolean | true/false | Registre ouvert (fin de course) |
| damper_closed | damper closed status | Boolean | true/false | Registre fermé (fin de course) |
| damper_moving | damper moving status | Boolean | true/false | Registre en mouvement |
| damper_fault | damper fault alarm | Boolean | true/false | Défaut actionneur (blocage, surcouple) |
| damper_override | damper override status | Boolean | true/false | Forçage manuel actif |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| damper_position_feedback | AI:1 | 40001 (HR) | 1/1/1 |
| actuator_current | AI:2 | 40002 (HR) | 1/1/2 |
| actuator_torque | AI:3 | 40003 (HR) | 1/1/3 |
| damper_position_cmd | AO:1 | 40101 (HR) | 1/2/1 |
| damper_min_position_sp | AV:1 | 40201 (HR) | 1/2/2 |
| damper_max_position_sp | AV:2 | 40202 (HR) | 1/2/3 |
| damper_open | BI:1 | 10001 (DI) | 1/3/1 |
| damper_closed | BI:2 | 10002 (DI) | 1/3/2 |
| damper_moving | BI:3 | 10003 (DI) | 1/3/3 |
| damper_fault | BI:4 | 10004 (DI) | 1/3/4 |
| damper_override | BI:5 | 10005 (DI) | 1/3/5 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Types de Signaux de Commande

| Type Signal | Spécification | Application |
|-------------|---------------|-------------|
| Analogique | 0-10V DC ou 2-10V DC | Commande modulante standard |
| Analogique | 4-20mA | Environnement industriel |
| Tout-ou-rien | 24VAC/DC contact | Damper on/off |
| BACnet MS/TP | RS-485 | Actionneur communicant |
| Modbus RTU | RS-485 | Actionneur communicant |
| BACnet/IP | Ethernet | Actionneur IoT |

## Temps de Course Typiques

| Taille Registre | Temps Ouverture 0-100% | Application |
|-----------------|------------------------|-------------|
| < 300mm | 30-60 sec | VAV, petits registres |
| 300-600mm | 60-90 sec | Registres moyens |
| 600-1200mm | 90-150 sec | Registres AHU |
| > 1200mm | 150-180 sec | Grands registres |

## Sources
- [Belimo BACnet Interface Description](https://www.belimo.com/mam/general-documents/system_integration/BACnet/belimo_BACnet_Interface-description_Damper_actuator_V3_08_en-gb.pdf) - Documentation BACnet actionneurs
- [Belimo Damper Actuator Brochure](https://www.belimo.com/mam/americas/marketing_communication/brochures/control_valves/Belimo-Damper-Actuator-Brochure.pdf) - Gamme actionneurs
- [Greenheck BACnet Quick Start Guide](https://content.greenheck.com/public/DAMProd/Original/10017/485941_BACnet_Guide.pdf) - Points BACnet pour unités de ventilation
- [Belimo IoT Actuators](https://www.belimo.com/us/shop/en_US/Systems/IoT-Actuators/c/17707-18867) - Actionneurs connectés
