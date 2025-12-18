# Points de Ventilateur d'Extraction (Exhaust Fan)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| fan_speed | fan speed sensor | % | 0-100 | 1min | Vitesse réelle du ventilateur |
| motor_current | fan motor current sensor | A | 0-50 | 1min | Courant moteur |
| motor_power | fan motor power sensor | kW | 0-30 | 5min | Puissance électrique consommée |
| exhaust_flow | exhaust air flow sensor | m³/h | 0-50000 | 1min | Débit d'air extrait |
| exhaust_temp | exhaust air temp sensor | °C | 10-40 | 1min | Température air extrait |
| duct_static_pressure | duct pressure sensor | Pa | -200-0 | 1min | Pression statique gaine extraction |
| vfd_frequency | vfd frequency sensor | Hz | 0-60 | 1min | Fréquence variateur |
| run_hours | fan run hours sensor | h | 0-99999 | 15min | Heures de fonctionnement cumulées |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| fan_enable_cmd | fan enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |
| fan_speed_cmd | fan speed cmd | % | 0-100 | Actionneur | Commande vitesse |
| exhaust_flow_sp | exhaust air flow sp | m³/h | 500-50000 | Consigne | Consigne débit extraction |
| duct_pressure_sp | duct pressure sp | Pa | -150-0 | Consigne | Consigne pression statique |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| fan_run | fan run status | Boolean | true/false | Ventilateur en marche |
| fan_fault | fan fault alarm | Boolean | true/false | Défaut ventilateur/moteur |
| vfd_fault | vfd fault alarm | Boolean | true/false | Défaut variateur de vitesse |
| filter_dirty_alarm | filter dirty alarm | Boolean | true/false | Filtre encrassé (si présent) |
| motor_overload | motor overload alarm | Boolean | true/false | Surcharge moteur |
| local_mode | local mode status | Boolean | true/false | Mode local (non piloté BMS) |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| fan_speed | AI:1 | 40001 (HR) | 1/1/1 |
| motor_current | AI:2 | 40002 (HR) | 1/1/2 |
| motor_power | AI:3 | 40003 (HR) | 1/1/3 |
| exhaust_flow | AI:4 | 40004 (HR) | 1/1/4 |
| exhaust_temp | AI:5 | 40005 (HR) | 1/1/5 |
| duct_static_pressure | AI:6 | 40006 (HR) | 1/1/6 |
| vfd_frequency | AI:7 | 40007 (HR) | 1/1/7 |
| run_hours | AI:8 | 40008 (HR) | 1/1/8 |
| fan_enable_cmd | BO:1 | 00001 (Coil) | 1/2/1 |
| fan_speed_cmd | AO:1 | 40201 (HR) | 1/2/2 |
| exhaust_flow_sp | AV:1 | 40101 (HR) | 1/2/3 |
| duct_pressure_sp | AV:2 | 40102 (HR) | 1/2/4 |
| fan_run | BI:1 | 10001 (DI) | 1/3/1 |
| fan_fault | BI:2 | 10002 (DI) | 1/3/2 |
| vfd_fault | BI:3 | 10003 (DI) | 1/3/3 |
| filter_dirty_alarm | BI:4 | 10004 (DI) | 1/3/4 |
| motor_overload | BI:5 | 10005 (DI) | 1/3/5 |
| local_mode | BI:6 | 10006 (DI) | 1/3/6 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Applications Spécifiques

| Application | Débit Typique | Contrôle | Capteur Associé |
|-------------|---------------|----------|-----------------|
| Sanitaires | 15-30 m³/h par appareil | Horaire ou présence | Détecteur présence |
| Cuisines | 1000-5000 m³/h | Hottes, capteur chaleur | Température, graisse |
| Parkings | 6-10 vol/h | CO, horaire | Capteur CO/CO2 |
| Laboratoires | 6-15 vol/h | Continu ou sorbonnes | Qualité air |
| Désenfumage | Selon calcul incendie | Alarme incendie | Détection fumée |

## Sources
- ASHRAE Standard 62.1 - Ventilation for Acceptable Indoor Air Quality
- BACnet Standard - Fan Control Objects
- Project Haystack - Exhaust Fan Tags
- VFD Manufacturer Integration Guides (ABB, Danfoss, Siemens)
