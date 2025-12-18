# Points de Variateur de Fréquence (VFD)

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| output_freq | vfd output freq sensor | Hz | 0-60 | 1min | Fréquence de sortie |
| motor_speed | motor speed sensor | rpm | 0-3600 | 1min | Vitesse moteur |
| speed_ref | vfd speed ref sensor | % | 0-100 | 1min | Référence vitesse (%) |
| output_current | vfd output current sensor | A | 0-500 | 1min | Courant de sortie |
| output_voltage | vfd output voltage sensor | V | 0-480 | 1min | Tension de sortie |
| input_power | vfd input power sensor | kW | 0-500 | 1min | Puissance absorbée |
| output_power | vfd output power sensor | kW | 0-500 | 1min | Puissance moteur |
| motor_torque | motor torque sensor | % | 0-150 | 1min | Couple moteur |
| dc_bus_voltage | vfd dc bus voltage sensor | V | 0-800 | 5min | Tension bus DC |
| heatsink_temp | vfd heatsink temp sensor | °C | 20-80 | 5min | Température dissipateur |
| energy | vfd energy sensor | kWh | 0-999999 | 15min | Énergie consommée cumul |
| run_hours | run hours sensor | h | 0-99999 | 15min | Heures de fonctionnement |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| enable_cmd | vfd enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |
| speed_cmd | vfd speed cmd | % | 0-100 | Actionneur | Consigne vitesse (0-100%) |
| freq_cmd | vfd freq cmd | Hz | 0-60 | Actionneur | Consigne fréquence directe |
| direction_cmd | vfd direction cmd | - | 0/1 | Actionneur | Sens de rotation (FWD/REV) |
| reset_cmd | vfd reset cmd | - | 0/1 | Actionneur | Réarmement défaut |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| run_status | vfd run status | Boolean | true/false | Variateur en marche |
| ready_status | vfd ready status | Boolean | true/false | Prêt à démarrer |
| at_speed | vfd at speed status | Boolean | true/false | Vitesse consigne atteinte |
| direction_status | vfd direction status | Boolean | FWD/REV | Sens de rotation actuel |
| overload_alarm | vfd overload alarm | Boolean | true/false | Alarme surcharge |
| overcurrent_alarm | vfd overcurrent alarm | Boolean | true/false | Alarme surintensité |
| overheat_alarm | vfd overheat alarm | Boolean | true/false | Alarme surchauffe |
| general_fault | vfd fault alarm | Boolean | true/false | Défaut général |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| output_freq | AI:1 | 40001 (HR) |
| motor_speed | AI:2 | 40002 (HR) |
| speed_ref | AI:3 | 40003 (HR) |
| output_current | AI:4 | 40004 (HR) |
| output_voltage | AI:5 | 40005 (HR) |
| input_power | AI:6 | 40006 (HR) |
| output_power | AI:7 | 40007 (HR) |
| motor_torque | AI:8 | 40008 (HR) |
| dc_bus_voltage | AI:9 | 40009 (HR) |
| heatsink_temp | AI:10 | 40010 (HR) |
| energy | AI:11 | 40011 (HR) |
| run_hours | AI:12 | 40012 (HR) |
| enable_cmd | BO:1 | 00001 (Coil) |
| speed_cmd | AO:1 | 40201 (HR) |
| freq_cmd | AO:2 | 40202 (HR) |
| direction_cmd | BO:2 | 00002 (Coil) |
| reset_cmd | BO:3 | 00003 (Coil) |
| run_status | BI:1 | 10001 (DI) |
| ready_status | BI:2 | 10002 (DI) |
| at_speed | BI:3 | 10003 (DI) |
| direction_status | BI:4 | 10004 (DI) |
| overload_alarm | BI:5 | 10005 (DI) |
| overcurrent_alarm | BI:6 | 10006 (DI) |
| overheat_alarm | BI:7 | 10007 (DI) |
| general_fault | BI:8 | 10008 (DI) |

## Registres Modbus Standards (ABB/Danfoss)

| Fonction | Registre ABB | Registre Danfoss |
|----------|--------------|------------------|
| Control word | 1 | 49999 |
| Speed reference | 2 | 50009 |
| Status word | 3 | 50099 |
| Actual speed | 4 | 50109 |
| Output frequency | 5 | 16120 |
| Output current | 6 | 16134 |
| Motor power | 7 | 16135 |

## Loi d'Affinité (Charges Centrifuges)

| Paramètre | Relation | Exemple 50% vitesse |
|-----------|----------|---------------------|
| Débit (Q) | Q ∝ n | 50% du débit nominal |
| Pression (H) | H ∝ n² | 25% de la pression nominale |
| Puissance (P) | P ∝ n³ | 12.5% de la puissance nominale |

## Codes Défaut Typiques

| Code | Description | Action |
|------|-------------|--------|
| F001 | Surintensité | Vérifier charge moteur |
| F002 | Surtension | Vérifier alimentation |
| F003 | Sous-tension | Vérifier alimentation |
| F004 | Surchauffe | Vérifier ventilation |
| F005 | Défaut terre | Vérifier câblage moteur |
| F006 | Surcharge | Réduire charge ou vitesse |

## Sources
- IEC 61800 - Adjustable Speed Electrical Power Drive Systems
- ASHRAE Handbook - HVAC Applications
- Project Haystack - VFD Tags
- Brick Schema - Variable_Frequency_Drive Class
- ABB / Danfoss / Siemens - VFD Communication Manuals
