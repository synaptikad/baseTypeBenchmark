# Points BMS - Automatic Transfer Switch (ATS)

## Introduction

Les commutateurs automatiques de sources (ATS - Automatic Transfer Switch) sont des dispositifs critiques de sécurité qui basculent automatiquement l'alimentation électrique entre une source principale (réseau) et une source de secours (générateur). Ils intègrent des modules de communication (Modbus RTU/TCP, BACnet/IP, contacts secs) permettant la supervision temps réel et le contrôle à distance via systèmes BMS/SCADA.

Les ATS modernes effectuent une surveillance continue de la qualité électrique des deux sources (tension, fréquence, déséquilibre de phases) et intègrent des fonctions avancées comme le mesurage de puissance, la prédiction de l'usure des contacts, et la surveillance de température. Le monitoring BMS est essentiel pour garantir la disponibilité de l'équipement lors des commutations critiques.

## Points de Mesure

| Nom du Point | Description | Type | Unité | Fréquence | Plage Typique | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|-------|-----------|---------------|---------------|-------------|---------|---------|
| Source1_Voltage_L1L2 | Tension phase L1-L2 sur source 1 (réseau) | AI | V | 1-2s | 380-420V | source1, sensor, volt, elecLineToLine, phase, ac | Voltage_Sensor | AI | 30001-30002 |
| Source1_Voltage_L2L3 | Tension phase L2-L3 sur source 1 | AI | V | 1-2s | 380-420V | source1, sensor, volt, elecLineToLine, phase, ac | Voltage_Sensor | AI | 30003-30004 |
| Source1_Voltage_L3L1 | Tension phase L3-L1 sur source 1 | AI | V | 1-2s | 380-420V | source1, sensor, volt, elecLineToLine, phase, ac | Voltage_Sensor | AI | 30005-30006 |
| Source1_Voltage_L1N | Tension phase L1-neutre sur source 1 | AI | V | 1-2s | 220-240V | source1, sensor, volt, elecLineToNeutral, phase, ac | Voltage_Sensor | AI | 30007-30008 |
| Source1_Voltage_L2N | Tension phase L2-neutre sur source 1 | AI | V | 1-2s | 220-240V | source1, sensor, volt, elecLineToNeutral, phase, ac | Voltage_Sensor | AI | 30009-30010 |
| Source1_Voltage_L3N | Tension phase L3-neutre sur source 1 | AI | V | 1-2s | 220-240V | source1, sensor, volt, elecLineToNeutral, phase, ac | Voltage_Sensor | AI | 30011-30012 |
| Source1_Voltage_Avg | Tension moyenne triphasée source 1 | AI | V | 1-2s | 380-420V | source1, sensor, volt, avg, ac | Voltage_Sensor | AI | 30013-30014 |
| Source1_Frequency | Fréquence de la source 1 | AI | Hz | 1-2s | 49-51Hz | source1, sensor, freq, ac | Frequency_Sensor | AI | 30015-30016 |
| Source1_Voltage_Unbalance | Déséquilibre de tension source 1 | AI | % | 2-5s | 0-5% | source1, sensor, volt, imbalance, ac | Voltage_Sensor | AI | 30017-30018 |
| Source2_Voltage_L1L2 | Tension phase L1-L2 sur source 2 (générateur) | AI | V | 1-2s | 380-420V | source2, sensor, volt, elecLineToLine, phase, ac | Voltage_Sensor | AI | 30101-30102 |
| Source2_Voltage_L2L3 | Tension phase L2-L3 sur source 2 | AI | V | 1-2s | 380-420V | source2, sensor, volt, elecLineToLine, phase, ac | Voltage_Sensor | AI | 30103-30104 |
| Source2_Voltage_L3L1 | Tension phase L3-L1 sur source 2 | AI | V | 1-2s | 380-420V | source2, sensor, volt, elecLineToLine, phase, ac | Voltage_Sensor | AI | 30105-30106 |
| Source2_Voltage_L1N | Tension phase L1-neutre sur source 2 | AI | V | 1-2s | 220-240V | source2, sensor, volt, elecLineToNeutral, phase, ac | Voltage_Sensor | AI | 30107-30108 |
| Source2_Voltage_L2N | Tension phase L2-neutre sur source 2 | AI | V | 1-2s | 220-240V | source2, sensor, volt, elecLineToNeutral, phase, ac | Voltage_Sensor | AI | 30109-30110 |
| Source2_Voltage_L3N | Tension phase L3-neutre sur source 2 | AI | V | 1-2s | 220-240V | source2, sensor, volt, elecLineToNeutral, phase, ac | Voltage_Sensor | AI | 30111-30112 |
| Source2_Voltage_Avg | Tension moyenne triphasée source 2 | AI | V | 1-2s | 380-420V | source2, sensor, volt, avg, ac | Voltage_Sensor | AI | 30113-30114 |
| Source2_Frequency | Fréquence de la source 2 | AI | Hz | 1-2s | 49-51Hz | source2, sensor, freq, ac | Frequency_Sensor | AI | 30115-30116 |
| Source2_Voltage_Unbalance | Déséquilibre de tension source 2 | AI | % | 2-5s | 0-5% | source2, sensor, volt, imbalance, ac | Voltage_Sensor | AI | 30117-30118 |
| Load_Current_L1 | Courant phase L1 sur la charge | AI | A | 1-2s | 0-2000A | load, sensor, current, phase, ac | Current_Sensor | AI | 30201-30202 |
| Load_Current_L2 | Courant phase L2 sur la charge | AI | A | 1-2s | 0-2000A | load, sensor, current, phase, ac | Current_Sensor | AI | 30203-30204 |
| Load_Current_L3 | Courant phase L3 sur la charge | AI | A | 1-2s | 0-2000A | load, sensor, current, phase, ac | Current_Sensor | AI | 30205-30206 |
| Load_Current_Neutral | Courant sur le neutre | AI | A | 1-2s | 0-200A | load, sensor, current, neutral, ac | Current_Sensor | AI | 30207-30208 |
| Load_Current_Avg | Courant moyen triphasé | AI | A | 1-2s | 0-2000A | load, sensor, current, avg, ac | Current_Sensor | AI | 30209-30210 |
| Load_Active_Power_L1 | Puissance active phase L1 | AI | kW | 1-2s | 0-500kW | load, sensor, power, phase, ac | Power_Sensor | AI | 30211-30212 |
| Load_Active_Power_L2 | Puissance active phase L2 | AI | kW | 1-2s | 0-500kW | load, sensor, power, phase, ac | Power_Sensor | AI | 30213-30214 |
| Load_Active_Power_L3 | Puissance active phase L3 | AI | kW | 1-2s | 0-500kW | load, sensor, power, phase, ac | Power_Sensor | AI | 30215-30216 |
| Load_Active_Power_Total | Puissance active totale | AI | kW | 1-2s | 0-1500kW | load, sensor, power, total, ac | Power_Sensor | AI | 30217-30218 |
| Load_Reactive_Power_Total | Puissance réactive totale | AI | kVAR | 1-2s | -500 à +500kVAR | load, sensor, power, reactive, total, ac | Power_Sensor | AI | 30219-30220 |
| Load_Apparent_Power_Total | Puissance apparente totale | AI | kVA | 1-2s | 0-1500kVA | load, sensor, power, apparent, total, ac | Power_Sensor | AI | 30221-30222 |
| Load_Power_Factor | Facteur de puissance charge | AI | - | 2-5s | 0.0-1.0 | load, sensor, pf, ac | Power_Factor_Sensor | AI | 30223-30224 |
| Load_Active_Energy_Total | Energie active totale consommée | AI | kWh | 30-60s | 0-999999kWh | load, sensor, energy, total, ac | Energy_Sensor | Accumulator | 30225-30226 |
| Load_Reactive_Energy_Total | Energie réactive totale | AI | kVARh | 30-60s | 0-999999kVARh | load, sensor, energy, reactive, total, ac | Energy_Sensor | Accumulator | 30227-30228 |
| Contact_Temperature_Source1 | Température contacteur source 1 | AI | °C | 5-10s | 20-80°C | source1, sensor, temp, contact | Temperature_Sensor | AI | 30301-30302 |
| Contact_Temperature_Source2 | Température contacteur source 2 | AI | °C | 5-10s | 20-80°C | source2, sensor, temp, contact | Temperature_Sensor | AI | 30303-30304 |
| Enclosure_Temperature | Température interne armoire ATS | AI | °C | 10-30s | 20-60°C | sensor, temp, enclosure | Temperature_Sensor | AI | 30305-30306 |
| Contact_Wear_Source1 | Usure estimée contacts source 1 | AI | % | 60s | 0-100% | source1, sensor, contact, wear | Sensor | AI | 30307-30308 |
| Contact_Wear_Source2 | Usure estimée contacts source 2 | AI | % | 60s | 0-100% | source2, sensor, contact, wear | Sensor | AI | 30309-30310 |
| Transfer_Count_Total | Nombre de transferts total | AI | - | 60s | 0-999999 | sensor, counter, transfer | Sensor | Accumulator | 30311-30312 |
| Operating_Hours_Source1 | Heures fonctionnement sur source 1 | AI | h | 60s | 0-999999h | source1, sensor, run, hours | Sensor | Accumulator | 30313-30314 |
| Operating_Hours_Source2 | Heures fonctionnement sur source 2 | AI | h | 60s | 0-999999h | source2, sensor, run, hours | Sensor | Accumulator | 30315-30316 |

## Points de Commande

| Nom du Point | Description | Type | Valeurs | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|---------------|-------------|---------|---------|
| Operating_Mode_Select | Sélection mode de fonctionnement | MSV | 0=Auto, 1=Manual, 2=Test, 3=Off | cmd, mode, sp | Mode_Command | MSV | 40001 |
| Transfer_To_Source1_Cmd | Commande transfert forcé vers source 1 | BO | 0=Off, 1=Execute | cmd, transfer, source1 | Command | BO | Coil 00001 |
| Transfer_To_Source2_Cmd | Commande transfert forcé vers source 2 | BO | 0=Off, 1=Execute | cmd, transfer, source2 | Command | BO | Coil 00002 |
| Transfer_To_Off_Cmd | Commande position OFF (isolation complète) | BO | 0=Off, 1=Execute | cmd, transfer, isolation | Command | BO | Coil 00003 |
| Execute_Test_Transfer | Commande test de commutation | BO | 0=Off, 1=Execute | cmd, test, transfer | Command | BO | Coil 00004 |
| Alarm_Reset_Cmd | Reset alarmes actives | BO | 0=Off, 1=Execute | cmd, reset, alarm | Command | BO | Coil 00005 |
| Preferred_Source_Select | Sélection source prioritaire | MSV | 0=Source1, 1=Source2 | cmd, sp, preferred, source | Command | MSV | 40002 |
| Auto_Retransfer_Enable | Activation retour automatique sur source préférée | BO | 0=Disabled, 1=Enabled | cmd, enable, retransfer | Command | BO | Coil 00006 |
| Generator_Start_Cmd | Commande démarrage générateur (si ATS contrôle GE) | BO | 0=Off, 1=Start | cmd, start, generator | Command | BO | Coil 00007 |
| Generator_Stop_Cmd | Commande arrêt générateur (si ATS contrôle GE) | BO | 0=Off, 1=Stop | cmd, stop, generator | Command | BO | Coil 00008 |
| In_Phase_Monitor_Enable | Activation surveillance synchronisation phases | BO | 0=Disabled, 1=Enabled | cmd, enable, phase, sync | Command | BO | Coil 00009 |
| Emergency_Transfer_Enable | Autorisation transfert d'urgence (sans temporisations) | BO | 0=Disabled, 1=Enabled | cmd, enable, emergency | Command | BO | Coil 00010 |
| Load_Shed_Enable | Activation délestage charge avant transfert | BO | 0=Disabled, 1=Enabled | cmd, enable, loadshed | Command | BO | Coil 00011 |

## Points d'État

| Nom du Point | Description | Type | Valeurs | Fréquence | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|-----------|---------------|-------------|---------|---------|
| Position_Status | Position actuelle du commutateur | MSV | 0=Source1, 1=Source2, 2=Transition, 3=Off | 1s | sensor, position, status | Status | MSV | 10001 |
| Operating_Mode_Status | Mode de fonctionnement actuel | MSV | 0=Auto, 1=Manual, 2=Test, 3=Off | 1s | sensor, mode, status | Status | MSV | 10002 |
| Source1_Available | Source 1 disponible et qualité OK | BI | 0=Not Available, 1=Available | 1s | source1, sensor, available, status | Status | BI | DI 00101 |
| Source2_Available | Source 2 disponible et qualité OK | BI | 0=Not Available, 1=Available | 1s | source2, sensor, available, status | Status | BI | DI 00102 |
| Source1_Energized | Source 1 sous tension | BI | 0=De-energized, 1=Energized | 1s | source1, sensor, energized, status | Status | BI | DI 00103 |
| Source2_Energized | Source 2 sous tension | BI | 0=De-energized, 1=Energized | 1s | source2, sensor, energized, status | Status | BI | DI 00104 |
| Load_Connected_To_Source1 | Charge connectée à source 1 | BI | 0=Disconnected, 1=Connected | 1s | source1, load, sensor, connected, status | Status | BI | DI 00105 |
| Load_Connected_To_Source2 | Charge connectée à source 2 | BI | 0=Disconnected, 1=Connected | 1s | source2, load, sensor, connected, status | Status | BI | DI 00106 |
| Transfer_In_Progress | Transfert en cours | BI | 0=Idle, 1=In Progress | 1s | sensor, transfer, status | Status | BI | DI 00107 |
| Transfer_Permitted | Autorisation de transfert | BI | 0=Not Permitted, 1=Permitted | 1s | sensor, transfer, permitted, status | Status | BI | DI 00108 |
| Preferred_Source_Active | Source préférée actuellement active | BI | 0=Not Active, 1=Active | 1s | sensor, preferred, active, status | Status | BI | DI 00109 |
| Contactor_Locked_Source1 | Contacteur source 1 verrouillé (interlock) | BI | 0=Unlocked, 1=Locked | 1s | source1, sensor, locked, status | Status | BI | DI 00110 |
| Contactor_Locked_Source2 | Contacteur source 2 verrouillé (interlock) | BI | 0=Unlocked, 1=Locked | 1s | source2, sensor, locked, status | Status | BI | DI 00111 |
| Generator_Running | Générateur en fonctionnement | BI | 0=Stopped, 1=Running | 1s | generator, sensor, run, status | Status | BI | DI 00112 |
| Generator_Ready | Générateur prêt pour transfert | BI | 0=Not Ready, 1=Ready | 1s | generator, sensor, ready, status | Status | BI | DI 00113 |
| Auto_Mode_Active | Mode automatique actif | BI | 0=Inactive, 1=Active | 1s | sensor, auto, mode, status | Status | BI | DI 00114 |
| Manual_Mode_Active | Mode manuel actif | BI | 0=Inactive, 1=Active | 1s | sensor, manual, mode, status | Status | BI | DI 00115 |
| Test_Mode_Active | Mode test actif | BI | 0=Inactive, 1=Active | 1s | sensor, test, mode, status | Status | BI | DI 00116 |
| Time_Delay_Active | Temporisation transfert en cours | BI | 0=Inactive, 1=Active | 1s | sensor, delay, status | Status | BI | DI 00117 |
| Neutral_Position_Delay_Active | Temporisation position neutre active | BI | 0=Inactive, 1=Active | 1s | sensor, neutral, delay, status | Status | BI | DI 00118 |
| In_Phase_Monitor_OK | Synchronisation phases OK | BI | 0=Not Synced, 1=Synced | 1s | sensor, phase, sync, status | Status | BI | DI 00119 |
| Load_Shed_Active | Délestage charge actif | BI | 0=Inactive, 1=Active | 1s | sensor, loadshed, status | Status | BI | DI 00120 |

## Points d'Alarme

| Nom du Point | Description | Type | Valeurs | Fréquence | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|-----------|---------------|-------------|---------|---------|
| Source1_Loss_Alarm | Perte source 1 | BI | 0=Normal, 1=Alarm | 1s | source1, alarm, loss | Alarm | BI | DI 01001 |
| Source2_Loss_Alarm | Perte source 2 | BI | 0=Normal, 1=Alarm | 1s | source2, alarm, loss | Alarm | BI | DI 01002 |
| Source1_Undervoltage_Alarm | Sous-tension source 1 | BI | 0=Normal, 1=Alarm | 1s | source1, alarm, volt, low | Alarm | BI | DI 01003 |
| Source1_Overvoltage_Alarm | Surtension source 1 | BI | 0=Normal, 1=Alarm | 1s | source1, alarm, volt, high | Alarm | BI | DI 01004 |
| Source2_Undervoltage_Alarm | Sous-tension source 2 | BI | 0=Normal, 1=Alarm | 1s | source2, alarm, volt, low | Alarm | BI | DI 01005 |
| Source2_Overvoltage_Alarm | Surtension source 2 | BI | 0=Normal, 1=Alarm | 1s | source2, alarm, volt, high | Alarm | BI | DI 01006 |
| Source1_Underfreq_Alarm | Sous-fréquence source 1 | BI | 0=Normal, 1=Alarm | 1s | source1, alarm, freq, low | Alarm | BI | DI 01007 |
| Source1_Overfreq_Alarm | Sur-fréquence source 1 | BI | 0=Normal, 1=Alarm | 1s | source1, alarm, freq, high | Alarm | BI | DI 01008 |
| Source2_Underfreq_Alarm | Sous-fréquence source 2 | BI | 0=Normal, 1=Alarm | 1s | source2, alarm, freq, low | Alarm | BI | DI 01009 |
| Source2_Overfreq_Alarm | Sur-fréquence source 2 | BI | 0=Normal, 1=Alarm | 1s | source2, alarm, freq, high | Alarm | BI | DI 01010 |
| Source1_Phase_Loss_Alarm | Perte phase source 1 | BI | 0=Normal, 1=Alarm | 1s | source1, alarm, phase, loss | Alarm | BI | DI 01011 |
| Source2_Phase_Loss_Alarm | Perte phase source 2 | BI | 0=Normal, 1=Alarm | 1s | source2, alarm, phase, loss | Alarm | BI | DI 01012 |
| Source1_Phase_Reversal_Alarm | Inversion phases source 1 | BI | 0=Normal, 1=Alarm | 1s | source1, alarm, phase, reversal | Alarm | BI | DI 01013 |
| Source2_Phase_Reversal_Alarm | Inversion phases source 2 | BI | 0=Normal, 1=Alarm | 1s | source2, alarm, phase, reversal | Alarm | BI | DI 01014 |
| Source1_Voltage_Unbalance_Alarm | Déséquilibre tension source 1 | BI | 0=Normal, 1=Alarm | 1s | source1, alarm, volt, imbalance | Alarm | BI | DI 01015 |
| Source2_Voltage_Unbalance_Alarm | Déséquilibre tension source 2 | BI | 0=Normal, 1=Alarm | 1s | source2, alarm, volt, imbalance | Alarm | BI | DI 01016 |
| Transfer_Failure_Alarm | Échec transfert | BI | 0=Normal, 1=Alarm | 1s | alarm, transfer, failure | Alarm | BI | DI 01017 |
| Transfer_Timeout_Alarm | Timeout lors du transfert | BI | 0=Normal, 1=Alarm | 1s | alarm, transfer, timeout | Alarm | BI | DI 01018 |
| Load_Overcurrent_Alarm | Surintensité charge | BI | 0=Normal, 1=Alarm | 1s | load, alarm, current, high | Alarm | BI | DI 01019 |
| Load_Overload_Alarm | Surcharge puissance | BI | 0=Normal, 1=Alarm | 1s | load, alarm, power, high | Alarm | BI | DI 01020 |
| Short_Circuit_Alarm | Court-circuit détecté | BI | 0=Normal, 1=Alarm | 1s | alarm, shortcircuit | Alarm | BI | DI 01021 |
| Ground_Fault_Alarm | Défaut à la terre | BI | 0=Normal, 1=Alarm | 1s | alarm, groundfault | Alarm | BI | DI 01022 |
| Contact_Temp_High_Alarm | Température contacteur excessive | BI | 0=Normal, 1=Alarm | 1s | alarm, temp, contact, high | Alarm | BI | DI 01023 |
| Enclosure_Temp_High_Alarm | Température armoire excessive | BI | 0=Normal, 1=Alarm | 1s | alarm, temp, enclosure, high | Alarm | BI | DI 01024 |
| Contact_Wear_Warning | Usure contacts - maintenance requise | BI | 0=Normal, 1=Warning | 1s | alarm, contact, wear | Alarm | BI | DI 01025 |
| Contact_End_Of_Life_Alarm | Fin de vie contacts - remplacement urgent | BI | 0=Normal, 1=Alarm | 1s | alarm, contact, eol | Alarm | BI | DI 01026 |
| Mechanical_Fault_Alarm | Défaut mécanique commutateur | BI | 0=Normal, 1=Alarm | 1s | alarm, mechanical | Alarm | BI | DI 01027 |
| Control_Power_Loss_Alarm | Perte alimentation contrôle | BI | 0=Normal, 1=Alarm | 1s | alarm, power, control, loss | Alarm | BI | DI 01028 |
| Communication_Fault_Alarm | Défaut communication BMS | BI | 0=Normal, 1=Alarm | 1s | alarm, comm | Alarm | BI | DI 01029 |
| Generator_Fail_To_Start_Alarm | Échec démarrage générateur | BI | 0=Normal, 1=Alarm | 1s | generator, alarm, start, failure | Alarm | BI | DI 01030 |
| Sync_Failure_Alarm | Échec synchronisation phases | BI | 0=Normal, 1=Alarm | 1s | alarm, sync, failure, phase | Alarm | BI | DI 01031 |
| Interlock_Violation_Alarm | Violation verrouillage mécanique | BI | 0=Normal, 1=Alarm | 1s | alarm, interlock | Alarm | BI | DI 01032 |
| Emergency_Stop_Active_Alarm | Arrêt d'urgence activé | BI | 0=Normal, 1=Alarm | 1s | alarm, emergency, stop | Alarm | BI | DI 01033 |
| Lockout_Mode_Active | Mode verrouillage actif (nécessite intervention) | BI | 0=Normal, 1=Lockout | 1s | alarm, lockout | Alarm | BI | DI 01034 |

## Points de Configuration

| Nom du Point | Description | Type | Valeurs | Accès | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|-------|---------------|-------------|---------|---------|
| Source1_Undervolt_Pickup_SP | Seuil reprise sous-tension source 1 | AO | 90-95% Vnom | R/W | source1, sp, volt, low, pickup | Setpoint | AO | 40101-40102 |
| Source1_Undervolt_Dropout_SP | Seuil déclenchement sous-tension source 1 | AO | 70-90% Vnom | R/W | source1, sp, volt, low, dropout | Setpoint | AO | 40103-40104 |
| Source1_Overvolt_Pickup_SP | Seuil reprise surtension source 1 | AO | 105-110% Vnom | R/W | source1, sp, volt, high, pickup | Setpoint | AO | 40105-40106 |
| Source1_Overvolt_Dropout_SP | Seuil déclenchement surtension source 1 | AO | 110-120% Vnom | R/W | source1, sp, volt, high, dropout | Setpoint | AO | 40107-40108 |
| Source2_Undervolt_Pickup_SP | Seuil reprise sous-tension source 2 | AO | 90-95% Vnom | R/W | source2, sp, volt, low, pickup | Setpoint | AO | 40109-40110 |
| Source2_Undervolt_Dropout_SP | Seuil déclenchement sous-tension source 2 | AO | 70-90% Vnom | R/W | source2, sp, volt, low, dropout | Setpoint | AO | 40111-40112 |
| Source2_Overvolt_Pickup_SP | Seuil reprise surtension source 2 | AO | 105-110% Vnom | R/W | source2, sp, volt, high, pickup | Setpoint | AO | 40113-40114 |
| Source2_Overvolt_Dropout_SP | Seuil déclenchement surtension source 2 | AO | 110-120% Vnom | R/W | source2, sp, volt, high, dropout | Setpoint | AO | 40115-40116 |
| Source1_Underfreq_Pickup_SP | Seuil reprise sous-fréquence source 1 | AO | 90-95% Fnom | R/W | source1, sp, freq, low, pickup | Setpoint | AO | 40117-40118 |
| Source1_Underfreq_Dropout_SP | Seuil déclenchement sous-fréquence source 1 | AO | 75-90% Fnom | R/W | source1, sp, freq, low, dropout | Setpoint | AO | 40119-40120 |
| Source1_Overfreq_Pickup_SP | Seuil reprise sur-fréquence source 1 | AO | 103-105% Fnom | R/W | source1, sp, freq, high, pickup | Setpoint | AO | 40121-40122 |
| Source1_Overfreq_Dropout_SP | Seuil déclenchement sur-fréquence source 1 | AO | 105-110% Fnom | R/W | source1, sp, freq, high, dropout | Setpoint | AO | 40123-40124 |
| Source2_Underfreq_Pickup_SP | Seuil reprise sous-fréquence source 2 | AO | 90-95% Fnom | R/W | source2, sp, freq, low, pickup | Setpoint | AO | 40125-40126 |
| Source2_Underfreq_Dropout_SP | Seuil déclenchement sous-fréquence source 2 | AO | 75-90% Fnom | R/W | source2, sp, freq, low, dropout | Setpoint | AO | 40127-40128 |
| Source2_Overfreq_Pickup_SP | Seuil reprise sur-fréquence source 2 | AO | 103-105% Fnom | R/W | source2, sp, freq, high, pickup | Setpoint | AO | 40129-40130 |
| Source2_Overfreq_Dropout_SP | Seuil déclenchement sur-fréquence source 2 | AO | 105-110% Fnom | R/W | source2, sp, freq, high, dropout | Setpoint | AO | 40131-40132 |
| Voltage_Unbalance_Threshold_SP | Seuil déséquilibre tension | AO | 2-10% | R/W | sp, volt, imbalance, threshold | Setpoint | AO | 40133-40134 |
| Transfer_To_Source2_Delay | Temporisation avant transfert vers source 2 | AO | 0-60s | R/W | source2, sp, delay, transfer | Setpoint | AO | 40135-40136 |
| Retransfer_To_Source1_Delay | Temporisation retour vers source 1 | AO | 0-1800s | R/W | source1, sp, delay, retransfer | Setpoint | AO | 40137-40138 |
| Neutral_Position_Delay | Temporisation position neutre (break-before-make) | AO | 0-10s | R/W | sp, delay, neutral | Setpoint | AO | 40139-40140 |
| Engine_Start_Signal_Delay | Temporisation signal démarrage générateur | AO | 0-60s | R/W | generator, sp, delay, start | Setpoint | AO | 40141-40142 |
| Engine_Cool_Down_Delay | Temporisation refroidissement générateur | AO | 0-600s | R/W | generator, sp, delay, cooldown | Setpoint | AO | 40143-40144 |
| Load_Pickup_Delay | Temporisation reprise charge | AO | 0-30s | R/W | load, sp, delay, pickup | Setpoint | AO | 40145-40146 |
| Sync_Window_Voltage_SP | Fenêtre synchronisation tension | AO | 1-10% | R/W | sp, sync, volt, window | Setpoint | AO | 40147-40148 |
| Sync_Window_Frequency_SP | Fenêtre synchronisation fréquence | AO | 0.1-1Hz | R/W | sp, sync, freq, window | Setpoint | AO | 40149-40150 |
| Sync_Window_Phase_SP | Fenêtre synchronisation phase | AO | 5-30° | R/W | sp, sync, phase, window | Setpoint | AO | 40151-40152 |
| Overcurrent_Threshold_SP | Seuil surintensité alarme | AO | 100-120% Inom | R/W | sp, current, high, threshold | Setpoint | AO | 40153-40154 |
| Contact_Temp_Alarm_SP | Seuil température contacteur alarme | AO | 60-90°C | R/W | sp, temp, contact, high | Setpoint | AO | 40155-40156 |
| Contact_Wear_Warning_SP | Seuil usure contacts avertissement | AO | 70-90% | R/W | sp, contact, wear, warning | Setpoint | AO | 40157-40158 |
| Contact_Wear_Alarm_SP | Seuil usure contacts alarme | AO | 85-95% | R/W | sp, contact, wear, alarm | Setpoint | AO | 40159-40160 |

## Notes d'Implémentation

### Protocoles de Communication

#### Modbus RTU/TCP
- **Port série (RTU)** : RS-485, 9600-38400 bauds, 8N1 (8 data bits, no parity, 1 stop bit)
- **Adresse esclave** : Configurable 1-247 (typiquement 1-10)
- **Function codes** :
  - **FC01** : Read Coils (états binaires de sortie)
  - **FC02** : Read Discrete Inputs (états binaires d'entrée, alarmes)
  - **FC03** : Read Holding Registers (valeurs configurables, consignes)
  - **FC04** : Read Input Registers (mesures analogiques)
  - **FC05** : Write Single Coil (commandes binaires)
  - **FC06** : Write Single Register (écriture consigne unique)
  - **FC16** : Write Multiple Registers (écriture multiple consignes)
- **Registres** :
  - **30001-30399** : Input Registers (AI) - Mesures tension, courant, puissance, température
  - **10001-10099** : Input Registers (MSV status)
  - **00001-00200** : Discrete Inputs (BI) - États et alarmes
  - **40001-40200** : Holding Registers (AO/MSV) - Commandes et configuration
  - **Coils 00001-00020** : Coils (BO) - Commandes binaires
- **Limites** : Maximum 125 registres par requête de lecture

#### BACnet/IP
- **Device Profile** : B-BC (BACnet Building Controller) ou B-ASC (Application Specific Controller)
- **Object types supportés** :
  - **Analog Input (AI)** : Mesures électriques (tension, courant, puissance, fréquence, température, énergie)
  - **Binary Input (BI)** : États et alarmes
  - **Analog Output (AO)** : Setpoints configurables
  - **Binary Output (BO)** : Commandes binaires
  - **Multi-State Value (MSV)** : Mode opération, position, sélections multiples
  - **Accumulator** : Énergies cumulées, compteurs
- **Services BACnet** : ReadProperty, WriteProperty, SubscribeCOV, WhoIs, I-Am
- **Port** : UDP 47808
- **BTL Certification** : Recommandée pour garantir l'interopérabilité

#### Contacts Secs (Dry Contacts)
- Utilisés pour signaux critiques nécessitant isolation galvanique
- **Sorties** : Position contacteur (Source1/Source2/Off), alarmes majeures
- **Entrées** : Commandes de transfert d'urgence, arrêt d'urgence externe
- **Type** : Normalement ouvert (NO) ou normalement fermé (NC), configurable
- **Tension** : 24-48VDC typique, isolation 2500V

### Fréquences de Scrutation Recommandées

- **Mesures électriques critiques** (tensions sources, fréquences) : **1-2s** (temps réel)
- **Mesures de charge** (courant, puissance) : **1-2s**
- **États de position** (Source1/Source2/Transition) : **1s** (temps réel critique)
- **Alarmes critiques** : **1s** (notification immédiate)
- **Températures** : **5-10s** (contacteurs), **10-30s** (armoire)
- **Énergies cumulées** : **30-60s**
- **Compteurs et statistiques** : **60s**
- **Configuration/setpoints** : Sur événement ou **300s**

### Séquence de Transfert Typique (Auto)

1. **Détection défaut source 1** : Sous-tension, sous-fréquence, ou perte phase
2. **Temporisation validation défaut** : 1-5s (éviter faux déclenchement sur transitoire)
3. **Signal démarrage générateur** : Si générateur pas déjà en marche
4. **Attente stabilisation générateur** : Typiquement 10-15s
   - Vérification tension dans plage acceptable
   - Vérification fréquence dans plage acceptable
   - Vérification pas d'alarmes générateur
5. **Synchronisation (si ATS avec couplage)** : Vérification phase, tension, fréquence dans fenêtres
6. **Transfert vers source 2** :
   - **Break-before-make** : Ouverture contacteur S1 → Délai neutre (100-300ms) → Fermeture contacteur S2
   - **Make-before-break** (si couplage autorisé) : Fermeture S2 → Transfert charge → Ouverture S1
7. **Confirmation transfert** : Vérification charge bien alimentée par S2
8. **Détection retour source 1** : Source 1 revient, qualité OK
9. **Temporisation retour** : 30-600s (configurable, éviter retour prématuré)
10. **Retransfer vers source 1** : Séquence inverse si mode auto-retransfer activé
11. **Refroidissement générateur** : 5-10 min après retransfer avant arrêt GE

### Séquence de Transfert d'Urgence

En cas de besoin immédiat (commande manuelle ou défaut critique) :
- **Pas de temporisation** de validation ou retour
- **Transfert immédiat** dès que source cible disponible
- **Synchronisation minimale** ou inexistante
- Utilisé pour maintenance, tests, ou situations critiques

### Interlocking Mécanique et Électrique

- **Verrouillage mécanique** : Empêche fermeture simultanée S1 et S2 (risque court-circuit entre sources)
- **Verrouillage électrique** : Logique contrôleur double la protection mécanique
- **Position neutre obligatoire** : Break-before-make avec délai configurable
- **Vérification position** : Capteurs de position confirmant état contacteurs avant autorisation transfert

### Gestion des Alarmes

- **Alarmes critiques** : Déclenchent transfert immédiat (perte source, court-circuit)
- **Alarmes majeures** : Nécessitent attention mais pas de transfert automatique (usure contacts)
- **Avertissements** : Informations préventives (température élevée mais acceptable)
- **Reset alarmes** : Certaines alarmes auto-reset après disparition défaut, d'autres nécessitent reset manuel

### Considérations de Sécurité

- **Priorité absolue** : Continuité alimentation charges critiques
- **Tests réguliers** : Commutation test mensuelle recommandée (NFPA 110)
- **Maintenance préventive** : Surveillance usure contacts, température, compteurs cycles
- **Redondance communication** : Contacts secs en parallèle de Modbus/BACnet pour alarmes critiques
- **Logs et historiques** : Enregistrement de tous les transferts et alarmes pour audit et analyse

### Mapping Haystack Tags

Comme Project Haystack ne définit pas actuellement de tags standardisés spécifiques aux ATS, les recommandations suivantes s'appuient sur les tags électriques existants :

- **Équipement** : `ats-equip`, `switch-equip`, `elec-equip`
- **Sources** : `source1`, `source2` (tags personnalisés mais logiques)
- **Charge** : `load` (existant pour charge électrique)
- **Mesures** : `sensor`, `volt`, `current`, `power`, `energy`, `freq`, `pf`, `temp`
- **Qualificatifs phases** : `elecLineToLine`, `elecLineToNeutral`, `phase`, `neutral`, `avg`
- **Commandes** : `cmd`, `sp` (setpoint)
- **États** : `status`, `available`, `energized`, `connected`, `run`, `enable`
- **Alarmes** : `alarm`, avec qualificatifs `low`, `high`, `loss`, `imbalance`

### Mapping Brick Schema Classes

Brick Schema v1.1 ne définit pas de classe spécifique `Transfer_Switch`. Recommandations :

- **Équipement ATS** : Extension sous `Electrical_Equipment` → `Switchgear` ou créer `Transfer_Switch`
- **Capteurs** :
  - `Voltage_Sensor` : Mesures de tension
  - `Current_Sensor` : Mesures de courant
  - `Power_Sensor` : Mesures de puissance
  - `Energy_Sensor` : Mesures d'énergie
  - `Frequency_Sensor` : Mesures de fréquence
  - `Temperature_Sensor` : Températures contacteurs et armoire
  - `Power_Factor_Sensor` : Facteur de puissance
  - `Sensor` (générique) : Pour compteurs, usure, statuts
- **Commandes et Statuts** :
  - `Command` : Commandes de transfert, reset
  - `Status` : États de position, disponibilité, verrouillage
  - `Setpoint` : Consignes configurables
  - `Alarm` : Alarmes et avertissements
  - `Mode_Command` : Sélection mode opération

## Sources

1. https://www.eaton.com/content/dam/eaton/products/low-voltage-power-distribution-controls-systems/ats/resources/atscm3p-ib140004en.pdf - Eaton ATC-300 Modbus Communications Guide
2. https://library.e.abb.com/public/3d277efa119e42c488b58f1cf6b1a797/1SDH000760R0002.pdf - ABB ATS022 Automatic Transfer Switch Manual
3. https://www.se.com/us/en/download/document/asc-ug-modmap/ - ASCO 300 Series Modbus Mapping Documentation (Schneider Electric)
4. https://www.eaton.com/content/dam/eaton/products/low-voltage-power-distribution-controls-systems/ats/resources/atscm3p-66a7787.pdf - Eaton ATC-300+ Modbus Communication Guide
5. https://cdn.standards.iteh.ai/samples/101725/7af7898750cd4831bb71ba16b1eb5e10/IEC-60947-6-1-2021.pdf - IEC 60947-6-1:2021 Transfer Switching Equipment Standard
6. https://project-haystack.org/doc/appendix/tags - Project Haystack Tag Definitions
7. https://brickschema.org/ontology/1.1/classes/Electrical_Equipment/ - Brick Schema Electrical Equipment Classes
8. https://www.packetpower.com/generator-transfer-switch-monitoring - Generator & Transfer Switch Monitoring Best Practices
9. https://www.tdworld.com/test-and-measurement/article/20970591/automatic-transfer-switch-has-built-in-sensors-controllers-and-connectivity - Modern ATS with Predictive Maintenance Capabilities
10. https://www.eaton.com/content/dam/eaton/products/low-voltage-power-distribution-controls-systems/ats/pa01602020e.pdf - Eaton Remote Monitoring and Control for Multiple Transfer Switches
11. https://emc.cat.com/pubdirect.ashx?media_string_id=LEHE0833- - Caterpillar ATC-900 ATS Controller with Contact Wear Monitoring
12. https://www.novapwr.com/ats-monitoring/ - Importance of Automatic Transfer Switch Monitoring for Facilities
