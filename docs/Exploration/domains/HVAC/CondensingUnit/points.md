# Points de Groupe de Condensation (Condensing Unit)

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| discharge_pressure | refrig discharge pressure sensor | bar | 15-30 | 30sec | Pression haute (HP) côté refoulement |
| suction_pressure | refrig suction pressure sensor | bar | 3-8 | 30sec | Pression basse (BP) côté aspiration |
| discharge_temp | refrig discharge temp sensor | °C | 60-100 | 30sec | Température refoulement compresseur |
| suction_temp | refrig suction temp sensor | °C | 0-15 | 30sec | Température aspiration compresseur |
| liquid_line_temp | refrig liquid temp sensor | °C | 30-50 | 1min | Température ligne liquide |
| condenser_entering_temp | condenser entering air temp sensor | °C | -20-45 | 1min | Température air extérieur entrée condenseur |
| condenser_leaving_temp | condenser leaving air temp sensor | °C | 30-55 | 1min | Température air sortie condenseur |
| superheat | refrig superheat sensor | K | 5-15 | 1min | Surchauffe calculée |
| subcooling | refrig subcooling sensor | K | 3-10 | 1min | Sous-refroidissement calculé |
| compressor_current | compressor elec current sensor | A | 0-100 | 1min | Courant compresseur |
| compressor_power | compressor elec power sensor | kW | 0-50 | 5min | Puissance électrique compresseur |
| oil_pressure | compressor oil pressure sensor | bar | 1-5 | 1min | Pression huile compresseur (si applicable) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| compressor_enable_cmd | compressor enable cmd | - | 0/1 | Actionneur | Commande marche compresseur |
| compressor_speed_cmd | compressor speed cmd | % | 0-100 | Actionneur | Vitesse compresseur (inverter) |
| condenser_fan_speed_cmd | condenser fan speed cmd | % | 0-100 | Actionneur | Vitesse ventilateur condenseur |
| hp_setpoint | discharge pressure sp | bar | 18-28 | Consigne | Consigne pression haute |
| cooling_capacity_cmd | cooling capacity cmd | % | 0-100 | Actionneur | Demande capacité frigorifique |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| compressor_run | compressor run status | Boolean | true/false | État marche compresseur |
| condenser_fan_run | condenser fan run status | Boolean | true/false | État ventilateur condenseur |
| hp_alarm | high pressure alarm | Boolean | true/false | Alarme haute pression |
| lp_alarm | low pressure alarm | Boolean | true/false | Alarme basse pression |
| compressor_fault | compressor fault alarm | Boolean | true/false | Défaut compresseur |
| oil_fault | oil fault alarm | Boolean | true/false | Défaut pression huile |
| defrost_active | defrost run status | Boolean | true/false | Dégivrage actif (pompe à chaleur) |
| unit_mode | unit mode status | Enum | off/cool/heat/auto | Mode de fonctionnement |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| discharge_pressure | AI:1 | 40001 (HR) | 1/1/1 |
| suction_pressure | AI:2 | 40002 (HR) | 1/1/2 |
| discharge_temp | AI:3 | 40003 (HR) | 1/1/3 |
| suction_temp | AI:4 | 40004 (HR) | 1/1/4 |
| liquid_line_temp | AI:5 | 40005 (HR) | 1/1/5 |
| condenser_entering_temp | AI:6 | 40006 (HR) | 1/1/6 |
| condenser_leaving_temp | AI:7 | 40007 (HR) | 1/1/7 |
| superheat | AV:1 | 40101 (HR) | 1/1/8 |
| subcooling | AV:2 | 40102 (HR) | 1/1/9 |
| compressor_current | AI:8 | 40008 (HR) | 1/1/10 |
| compressor_power | AI:9 | 40009 (HR) | 1/1/11 |
| oil_pressure | AI:10 | 40010 (HR) | 1/1/12 |
| compressor_enable_cmd | BO:1 | 00001 (Coil) | 1/2/1 |
| compressor_speed_cmd | AO:1 | 40201 (HR) | 1/2/2 |
| condenser_fan_speed_cmd | AO:2 | 40202 (HR) | 1/2/3 |
| hp_setpoint | AV:3 | 40103 (HR) | 1/2/4 |
| cooling_capacity_cmd | AO:3 | 40203 (HR) | 1/2/5 |
| compressor_run | BI:1 | 10001 (DI) | 1/3/1 |
| condenser_fan_run | BI:2 | 10002 (DI) | 1/3/2 |
| hp_alarm | BI:3 | 10003 (DI) | 1/3/3 |
| lp_alarm | BI:4 | 10004 (DI) | 1/3/4 |
| compressor_fault | BI:5 | 10005 (DI) | 1/3/5 |
| oil_fault | BI:6 | 10006 (DI) | 1/3/6 |
| defrost_active | BI:7 | 10007 (DI) | 1/3/7 |
| unit_mode | MSV:1 | 40301 (HR) | 1/3/8 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Seuils d'Alarme Typiques (R410A)

| Paramètre | Seuil Avertissement | Seuil Alarme | Action |
|-----------|---------------------|--------------|--------|
| Haute pression | 28 bar | 32 bar | Arrêt compresseur |
| Basse pression | 4 bar | 2.5 bar | Arrêt compresseur |
| Température refoulement | 100°C | 115°C | Arrêt compresseur |
| Surchauffe | < 5K ou > 20K | < 3K ou > 25K | Alarme détendeur |
| Sous-refroidissement | < 2K | < 1K | Alarme charge réfrigérant |

## Sources
- [Daikin MicroTech II BACnet Protocol](https://tahoeweb.daikinapplied.com/) - Points BACnet pour contrôleurs chillers
- [Johnson Controls BACnet Points Listing](https://docs.johnsoncontrols.com/ductedsystems/r/Johnson-Controls/en-US/C-Series-CSV-Water-Cooled-Self-Contained-Units-C-Generation-R-410A-Model-CSV060C-300C/2020-12-07/BACnet-points-listing) - Liste points BACnet unités autonomes
- [Daikin MicroTech III Protocol](https://oslo.dev.daikinapplied.com/) - Documentation protocole LonWorks/BACnet
- [BAS Automation - Refrigeration Monitoring](https://basautomation.ccontrols.com/video/sedonawiresheet3.htm) - Monitoring unités frigorifiques
