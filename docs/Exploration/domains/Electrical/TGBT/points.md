# Points de TGBT (Tableau Général Basse Tension)

## Synthèse
- **Total points mesure** : 48
- **Total points commande** : 8
- **Total points état** : 18
- **Total général** : 74 points

## Points de Mesure (Capteurs)

### Mesures Électriques de Base

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| V_L1N | Tension phase 1 vers neutre | V | 0-265 V | ac, volt, phase, L1, elec, sensor, point | Voltage_Sensor | 1s |
| V_L2N | Tension phase 2 vers neutre | V | 0-265 V | ac, volt, phase, L2, elec, sensor, point | Voltage_Sensor | 1s |
| V_L3N | Tension phase 3 vers neutre | V | 0-265 V | ac, volt, phase, L3, elec, sensor, point | Voltage_Sensor | 1s |
| V_L1L2 | Tension ligne 1-2 | V | 0-450 V | ac, volt, line, L1, L2, elec, sensor, point | Voltage_Sensor | 1s |
| V_L2L3 | Tension ligne 2-3 | V | 0-450 V | ac, volt, line, L2, L3, elec, sensor, point | Voltage_Sensor | 1s |
| V_L3L1 | Tension ligne 3-1 | V | 0-450 V | ac, volt, line, L3, L1, elec, sensor, point | Voltage_Sensor | 1s |
| V_Avg | Tension moyenne triphasée | V | 0-450 V | ac, volt, avg, total, elec, sensor, point | Voltage_Sensor | 1s |
| I_L1 | Courant phase 1 | A | 0-5000 A | ac, current, phase, L1, elec, sensor, point | Current_Sensor | 1s |
| I_L2 | Courant phase 2 | A | 0-5000 A | ac, current, phase, L2, elec, sensor, point | Current_Sensor | 1s |
| I_L3 | Courant phase 3 | A | 0-5000 A | ac, current, phase, L3, elec, sensor, point | Current_Sensor | 1s |
| I_N | Courant neutre | A | 0-5000 A | ac, current, neutral, elec, sensor, point | Current_Sensor | 1s |
| I_Avg | Courant moyen triphasé | A | 0-5000 A | ac, current, avg, total, elec, sensor, point | Current_Sensor | 1s |
| Freq | Fréquence réseau | Hz | 47-53 Hz | ac, freq, elec, sensor, point | Frequency_Sensor | 1s |

### Mesures de Puissance

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| P_L1 | Puissance active phase 1 | kW | -2000 à +2000 kW | ac, active, power, phase, L1, elec, sensor, point | Active_Power_Sensor | 1s |
| P_L2 | Puissance active phase 2 | kW | -2000 à +2000 kW | ac, active, power, phase, L2, elec, sensor, point | Active_Power_Sensor | 1s |
| P_L3 | Puissance active phase 3 | kW | -2000 à +2000 kW | ac, active, power, phase, L3, elec, sensor, point | Active_Power_Sensor | 1s |
| P_Total | Puissance active totale | kW | -6000 à +6000 kW | ac, active, power, total, elec, sensor, point | Active_Power_Sensor | 1s |
| Q_L1 | Puissance réactive phase 1 | kVAR | -2000 à +2000 kVAR | ac, reactive, power, phase, L1, elec, sensor, point | Reactive_Power_Sensor | 1s |
| Q_L2 | Puissance réactive phase 2 | kVAR | -2000 à +2000 kVAR | ac, reactive, power, phase, L2, elec, sensor, point | Reactive_Power_Sensor | 1s |
| Q_L3 | Puissance réactive phase 3 | kVAR | -2000 à +2000 kVAR | ac, reactive, power, phase, L3, elec, sensor, point | Reactive_Power_Sensor | 1s |
| Q_Total | Puissance réactive totale | kVAR | -6000 à +6000 kVAR | ac, reactive, power, total, elec, sensor, point | Reactive_Power_Sensor | 1s |
| S_L1 | Puissance apparente phase 1 | kVA | 0-2000 kVA | ac, apparent, power, phase, L1, elec, sensor, point | Apparent_Power_Sensor | 1s |
| S_L2 | Puissance apparente phase 2 | kVA | 0-2000 kVA | ac, apparent, power, phase, L2, elec, sensor, point | Apparent_Power_Sensor | 1s |
| S_L3 | Puissance apparente phase 3 | kVA | 0-2000 kVA | ac, active, power, phase, L3, elec, sensor, point | Apparent_Power_Sensor | 1s |
| S_Total | Puissance apparente totale | kVA | 0-6000 kVA | ac, apparent, power, total, elec, sensor, point | Apparent_Power_Sensor | 1s |
| PF_L1 | Facteur de puissance phase 1 | pf | -1.0 à +1.0 | ac, pf, phase, L1, elec, sensor, point | Power_Factor_Sensor | 1s |
| PF_L2 | Facteur de puissance phase 2 | pf | -1.0 à +1.0 | ac, pf, phase, L2, elec, sensor, point | Power_Factor_Sensor | 1s |
| PF_L3 | Facteur de puissance phase 3 | pf | -1.0 à +1.0 | ac, pf, phase, L3, elec, sensor, point | Power_Factor_Sensor | 1s |
| PF_Total | Facteur de puissance total | pf | -1.0 à +1.0 | ac, pf, total, elec, sensor, point | Power_Factor_Sensor | 1s |

### Mesures d'Énergie

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Energy_Active_Import | Énergie active importée | kWh | 0-999999999 kWh | ac, active, energy, import, elec, sensor, point | Energy_Sensor | 15min |
| Energy_Active_Export | Énergie active exportée | kWh | 0-999999999 kWh | ac, active, energy, export, elec, sensor, point | Energy_Sensor | 15min |
| Energy_Reactive_Q1 | Énergie réactive quadrant 1 | kVARh | 0-999999999 kVARh | ac, reactive, energy, quadrant, elec, sensor, point | Reactive_Energy_Sensor | 15min |
| Energy_Reactive_Q2 | Énergie réactive quadrant 2 | kVARh | 0-999999999 kVARh | ac, reactive, energy, quadrant, elec, sensor, point | Reactive_Energy_Sensor | 15min |
| Energy_Reactive_Q3 | Énergie réactive quadrant 3 | kVARh | 0-999999999 kVARh | ac, reactive, energy, quadrant, elec, sensor, point | Reactive_Energy_Sensor | 15min |
| Energy_Reactive_Q4 | Énergie réactive quadrant 4 | kVARh | 0-999999999 kVARh | ac, reactive, energy, quadrant, elec, sensor, point | Reactive_Energy_Sensor | 15min |
| Energy_Apparent | Énergie apparente | kVAh | 0-999999999 kVAh | ac, apparent, energy, elec, sensor, point | Apparent_Energy_Sensor | 15min |

### Mesures de Demande

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Demand_Active | Demande active instantanée | kW | 0-6000 kW | ac, active, demand, power, elec, sensor, point | Demand_Sensor | 15s |
| Demand_Active_Peak | Demande active de pointe | kW | 0-6000 kW | ac, active, demand, peak, power, elec, sensor, point | Peak_Demand_Sensor | 15min |
| Demand_Reactive | Demande réactive instantanée | kVAR | 0-6000 kVAR | ac, reactive, demand, power, elec, sensor, point | Demand_Sensor | 15s |
| Demand_Apparent | Demande apparente instantanée | kVA | 0-6000 kVA | ac, apparent, demand, power, elec, sensor, point | Demand_Sensor | 15s |

### Mesures de Qualité Réseau

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| THD_V_L1 | Distorsion harmonique tension L1 | % | 0-100% | ac, volt, thd, phase, L1, elec, sensor, point | THD_Sensor | 10s |
| THD_V_L2 | Distorsion harmonique tension L2 | % | 0-100% | ac, volt, thd, phase, L2, elec, sensor, point | THD_Sensor | 10s |
| THD_V_L3 | Distorsion harmonique tension L3 | % | 0-100% | ac, volt, thd, phase, L3, elec, sensor, point | THD_Sensor | 10s |
| THD_I_L1 | Distorsion harmonique courant L1 | % | 0-100% | ac, current, thd, phase, L1, elec, sensor, point | THD_Sensor | 10s |
| THD_I_L2 | Distorsion harmonique courant L2 | % | 0-100% | ac, current, thd, phase, L2, elec, sensor, point | THD_Sensor | 10s |
| THD_I_L3 | Distorsion harmonique courant L3 | % | 0-100% | ac, current, thd, phase, L3, elec, sensor, point | THD_Sensor | 10s |
| Voltage_Unbalance | Déséquilibre de tension | % | 0-10% | ac, volt, imbalance, elec, sensor, point | Voltage_Imbalance_Sensor | 10s |
| Current_Unbalance | Déséquilibre de courant | % | 0-50% | ac, current, imbalance, elec, sensor, point | Current_Imbalance_Sensor | 10s |

### Mesures de Température

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Temp_Busbar_L1 | Température jeu de barres L1 | °C | 0-140°C | temp, busbar, L1, elec, sensor, point | Temperature_Sensor | 30s |
| Temp_Busbar_L2 | Température jeu de barres L2 | °C | 0-140°C | temp, busbar, L2, elec, sensor, point | Temperature_Sensor | 30s |
| Temp_Busbar_L3 | Température jeu de barres L3 | °C | 0-140°C | temp, busbar, L3, elec, sensor, point | Temperature_Sensor | 30s |
| Temp_Enclosure | Température intérieure armoire | °C | 0-80°C | temp, air, enclosure, elec, sensor, point | Temperature_Sensor | 60s |

## Points de Commande (Actionneurs/Consignes)

| Point | Description | Unité | Plage | Haystack Tags | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| CB_Main_Close | Fermeture disjoncteur principal | bool | 0/1 | cmd, close, breaker, main, elec, point | Close_Command |
| CB_Main_Open | Ouverture disjoncteur principal | bool | 0/1 | cmd, open, breaker, main, elec, point | Open_Command |
| LoadShed_Enable | Activation délestage | bool | 0/1 | cmd, enable, loadShed, elec, point | Enable_Command |
| LoadShed_Priority_1 | Délestage priorité 1 | bool | 0/1 | cmd, loadShed, priority, elec, point | Load_Shed_Command |
| LoadShed_Priority_2 | Délestage priorité 2 | bool | 0/1 | cmd, loadShed, priority, elec, point | Load_Shed_Command |
| LoadShed_Priority_3 | Délestage priorité 3 | bool | 0/1 | cmd, loadShed, priority, elec, point | Load_Shed_Command |
| Demand_Limit_Setpoint | Consigne limite de demande | kW | 0-6000 kW | sp, demand, limit, power, elec, point | Demand_Setpoint |
| PFC_Target_PF | Consigne facteur puissance cible | pf | 0.9-1.0 | sp, pf, target, elec, point | Power_Factor_Setpoint |

## Points d'État

### États Disjoncteurs et Interrupteurs

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| CB_Main_Status | État disjoncteur principal | 0=Ouvert, 1=Fermé | status, breaker, main, elec, point | Breaker_Status |
| CB_Main_Trip | Déclenchement disjoncteur principal | 0=Normal, 1=Déclenché | alarm, trip, breaker, main, elec, point | Trip_Status |
| CB_Incomer_1_Status | État incomer 1 | 0=Ouvert, 1=Fermé | status, breaker, incomer, elec, point | Breaker_Status |
| CB_Incomer_2_Status | État incomer 2 | 0=Ouvert, 1=Fermé | status, breaker, incomer, elec, point | Breaker_Status |
| CB_Bus_Coupler_Status | État coupleur de jeu de barres | 0=Ouvert, 1=Fermé | status, breaker, coupler, elec, point | Breaker_Status |
| Transfer_Switch_Position | Position commutateur de transfert | 0=Source1, 1=Source2 | status, transfer, switch, elec, point | Switch_Status |

### États Systèmes de Protection

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Earth_Fault_Alarm | Alarme défaut terre | 0=Normal, 1=Alarme | alarm, fault, earth, elec, point | Fault_Status |
| Ground_Fault_Current | Courant de fuite à la terre | mA (0-1000) | current, ground, fault, elec, sensor, point | Ground_Fault_Sensor |
| Differential_Prot_Status | État protection différentielle | 0=Normal, 1=Alarme | alarm, differential, protection, elec, point | Protection_Status |
| Arc_Flash_Detected | Détection arc électrique | 0=Normal, 1=Détecté | alarm, arc, flash, elec, point | Arc_Flash_Status |
| Overcurrent_L1 | Surintensité phase 1 | 0=Normal, 1=Alarme | alarm, overcurrent, phase, L1, elec, point | Overcurrent_Status |
| Overcurrent_L2 | Surintensité phase 2 | 0=Normal, 1=Alarme | alarm, overcurrent, phase, L2, elec, point | Overcurrent_Status |
| Overcurrent_L3 | Surintensité phase 3 | 0=Normal, 1=Alarme | alarm, overcurrent, phase, L3, elec, point | Overcurrent_Status |

### États de Qualité et Système

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Overvoltage_Alarm | Alarme surtension | 0=Normal, 1=Alarme | alarm, overvoltage, elec, point | Overvoltage_Status |
| Undervoltage_Alarm | Alarme sous-tension | 0=Normal, 1=Alarme | alarm, undervoltage, elec, point | Undervoltage_Status |
| Overtemp_Busbar_Alarm | Alarme surchauffe jeu de barres | 0=Normal, 1=Alarme | alarm, temp, busbar, elec, point | Temperature_Alarm |
| PFC_Capacitor_Bank_Status | État batterie condensateurs | 0=Inactif, 1-8=Étages actifs | status, pfc, capacitor, elec, point | Capacitor_Bank_Status |
| Communication_Status | État communication | 0=Défaut, 1=OK | status, comm, network, elec, point | Communication_Status |
| System_Alarm | Alarme système générale | 0=Normal, 1=Alarme | alarm, system, elec, point | System_Alarm_Status |

## Mappings Protocoles

### BACnet

| Point | Object Type | Object Instance | Property | Units | R/W |
|-------|-------------|-----------------|----------|-------|-----|
| V_L1N | Analog Input | 0 | Present_Value | volts-ac | R |
| V_L2N | Analog Input | 1 | Present_Value | volts-ac | R |
| V_L3N | Analog Input | 2 | Present_Value | volts-ac | R |
| I_L1 | Analog Input | 10 | Present_Value | amperes | R |
| I_L2 | Analog Input | 11 | Present_Value | amperes | R |
| I_L3 | Analog Input | 12 | Present_Value | amperes | R |
| P_Total | Analog Input | 20 | Present_Value | kilowatts | R |
| Q_Total | Analog Input | 21 | Present_Value | kilovars | R |
| S_Total | Analog Input | 22 | Present_Value | kilovolt-amperes | R |
| PF_Total | Analog Input | 23 | Present_Value | power-factor | R |
| Freq | Analog Input | 24 | Present_Value | hertz | R |
| Energy_Active_Import | Analog Input | 30 | Present_Value | kilowatt-hours | R |
| Energy_Reactive_Q1 | Analog Input | 31 | Present_Value | kilovar-hours | R |
| Demand_Active_Peak | Analog Input | 40 | Present_Value | kilowatts | R |
| THD_V_L1 | Analog Input | 50 | Present_Value | percent | R |
| THD_I_L1 | Analog Input | 53 | Present_Value | percent | R |
| Voltage_Unbalance | Analog Input | 56 | Present_Value | percent | R |
| Temp_Busbar_L1 | Analog Input | 60 | Present_Value | degrees-celsius | R |
| CB_Main_Status | Binary Input | 100 | Present_Value | enum (0/1) | R |
| CB_Main_Trip | Binary Input | 101 | Present_Value | enum (0/1) | R |
| Earth_Fault_Alarm | Binary Input | 110 | Present_Value | enum (0/1) | R |
| Arc_Flash_Detected | Binary Input | 111 | Present_Value | enum (0/1) | R |
| Overvoltage_Alarm | Binary Input | 120 | Present_Value | enum (0/1) | R |
| Undervoltage_Alarm | Binary Input | 121 | Present_Value | enum (0/1) | R |
| CB_Main_Close | Binary Output | 200 | Present_Value | enum (0/1) | W |
| CB_Main_Open | Binary Output | 201 | Present_Value | enum (0/1) | W |
| LoadShed_Enable | Binary Output | 210 | Present_Value | enum (0/1) | W |
| Demand_Limit_Setpoint | Analog Output | 300 | Present_Value | kilowatts | W |
| PFC_Target_PF | Analog Output | 301 | Present_Value | power-factor | W |

### Modbus RTU/TCP

| Point | Function Code | Register Type | Register Address | Data Type | Unités | Scaling |
|-------|---------------|---------------|------------------|-----------|--------|---------|
| V_L1N | 04 (Read Input) | Input Register | 0 | UINT16 | V | x0.1 |
| V_L2N | 04 | Input Register | 1 | UINT16 | V | x0.1 |
| V_L3N | 04 | Input Register | 2 | UINT16 | V | x0.1 |
| I_L1 | 04 | Input Register | 10 | UINT16 | A | x0.01 |
| I_L2 | 04 | Input Register | 11 | UINT16 | A | x0.01 |
| I_L3 | 04 | Input Register | 12 | UINT16 | A | x0.01 |
| P_Total | 04 | Input Register | 20-21 | FLOAT32 | kW | x1 |
| Q_Total | 04 | Input Register | 22-23 | FLOAT32 | kVAR | x1 |
| S_Total | 04 | Input Register | 24-25 | FLOAT32 | kVA | x1 |
| PF_Total | 04 | Input Register | 26 | INT16 | pf | x0.001 |
| Freq | 04 | Input Register | 27 | UINT16 | Hz | x0.01 |
| Energy_Active_Import | 04 | Input Register | 30-31 | UINT32 | kWh | x1 |
| Energy_Reactive_Q1 | 04 | Input Register | 32-33 | UINT32 | kVARh | x1 |
| Demand_Active_Peak | 04 | Input Register | 40-41 | FLOAT32 | kW | x1 |
| THD_V_L1 | 04 | Input Register | 50 | UINT16 | % | x0.1 |
| THD_I_L1 | 04 | Input Register | 53 | UINT16 | % | x0.1 |
| Voltage_Unbalance | 04 | Input Register | 56 | UINT16 | % | x0.1 |
| Temp_Busbar_L1 | 04 | Input Register | 60 | INT16 | °C | x0.1 |
| CB_Main_Status | 02 (Read Discrete) | Discrete Input | 100 | BOOL | - | - |
| CB_Main_Trip | 02 | Discrete Input | 101 | BOOL | - | - |
| Earth_Fault_Alarm | 02 | Discrete Input | 110 | BOOL | - | - |
| Arc_Flash_Detected | 02 | Discrete Input | 111 | BOOL | - | - |
| CB_Main_Close | 05 (Write Coil) | Coil | 200 | BOOL | - | - |
| CB_Main_Open | 05 | Coil | 201 | BOOL | - | - |
| LoadShed_Enable | 05 | Coil | 210 | BOOL | - | - |
| Demand_Limit_Setpoint | 06 (Write Register) | Holding Register | 300-301 | FLOAT32 | kW | x1 |
| PFC_Target_PF | 06 | Holding Register | 302 | UINT16 | pf | x0.001 |

### IEC 61850 (Logical Nodes)

| Point | Logical Node | Data Object | CDC | Description |
|-------|--------------|-------------|-----|-------------|
| V_L1N, V_L2N, V_L3N | MMXU | PhV | MV | Phase-to-ground voltages |
| V_L1L2, V_L2L3, V_L3L1 | MMXU | PPV | MV | Phase-to-phase voltages |
| I_L1, I_L2, I_L3 | MMXU | A | MV | Phase currents |
| P_Total | MMXU | TotW | MV | Total active power |
| Q_Total | MMXU | TotVAr | MV | Total reactive power |
| S_Total | MMXU | TotVA | MV | Total apparent power |
| PF_Total | MMXU | TotPF | MV | Total power factor |
| Freq | MMXU | Hz | MV | Frequency |
| Energy_Active_Import | MMTR | TotWh | BCR | Total active energy |
| Energy_Reactive_Q1 | MMTR | TotVArh | BCR | Total reactive energy |
| CB_Main_Status | XCBR | Pos | DPC | Circuit breaker position |
| CB_Main_Close | XCBR | Pos | DPC | Close command |
| CB_Main_Open | XCBR | Pos | DPC | Open command |
| Earth_Fault_Alarm | PTRC | Str | ACD | Earth fault protection start |
| Overcurrent_L1 | PTOC | Str | ACD | Overcurrent protection start |

## Notes d'Implémentation

### Fréquence de Scrutation
- **Haute priorité (1s)** : Mesures électriques de base (V, I, P, Q, S, PF, Freq)
- **Moyenne priorité (10-30s)** : Qualité réseau (THD, déséquilibre), températures
- **Basse priorité (15min)** : Compteurs d'énergie, demande de pointe
- **Événements** : États et alarmes (COV - Change of Value)

### Seuils d'Alarme Typiques
- **Surtension** : >110% Vnom (>253V phase-neutre)
- **Sous-tension** : <85% Vnom (<196V phase-neutre)
- **Surintensité** : >95% Inom
- **Déséquilibre tension** : >3% (ANSI)
- **THD tension** : >5% (IEC 61000-4-7)
- **THD courant** : >20% (IEEE 519)
- **Température jeu de barres** : >100°C (alarme), >120°C (critique)
- **Facteur de puissance** : <0.92 (pénalité tarifaire)

### Intégration BMS
- Utiliser prioritairement BACnet/IP ou Modbus TCP pour éviter les gateways
- Configurer les alarmes avec COV (Change of Value) pour réduire le trafic
- Implémenter des totalisateurs d'énergie avec reset mensuel pour facturation
- Prévoir logs d'événements pour traçabilité (trip, délestage, basculement)

### Conformité Standards
- **IEC 61850** : Pour substations et smart grids
- **IEC 61000-4-30 Class A** : Qualité de mesure d'énergie
- **IEEE 519** : Limites harmoniques
- **ASHRAE 135 (BACnet)** : Intégration BMS
- **ISO 50001** : Système de management de l'énergie

## Sources

### Documentation Fabricants
1. https://media.distributordatasolutions.com/schneider_synd/2022q2/documents/36aa18613f6d1f6ee57b47d0384d0c72bceb8494.pdf - Schneider Electric PowerLogic PM5560 Datasheet
2. https://library.e.abb.com/public/8ffb418478c24c86a616aaa22169109f/1MAC306148-MB%20E%20Modbus%20point%20list%20.pdf - ABB Modbus Point List Manual
3. https://cache.industry.siemens.com/dl/files/150/26504150/att_906558/v1/A5E01168664B-04_EN-US_122016_201612221316360495.pdf - Siemens SENTRON PAC3200 Manual
4. https://assets.legrand.com/pim/DOCUMENT/legrand-guide-mesure-supervision.pdf - Legrand Guide Gestion Énergie Tableau Électrique
5. https://www.productinfo.schneider-electric.com/pm5300/5be97f3b347bdf0001d99c87/PM5300%20User%20Manual/English/EAV15107-EN11.pdf - Schneider PM5300 User Manual

### Standards et Protocoles
6. https://project-haystack.org/doc/docHaystack/Meters - Project Haystack Meters Documentation
7. https://project-haystack.org/doc/lib-phIoT/elec-meter - Project Haystack Electric Meter Tags
8. https://docs.brickschema.org/modeling/meters.html - Brick Schema Meters Documentation
9. https://product-help.schneider-electric.com/ION-Reference/content/ion%20reference/iec-61850-mmxu-module.htm - IEC 61850 MMXU Logical Node
10. https://www.bacnetinternational.net/catalog/manu/schneider%20electric/StruxureWare%20PM556x%20PICS.pdf - BACnet PICS PM5560 Series

### Qualité Réseau et Harmoniques
11. https://www.iammeter.com/blog/reactive-power-kvar-kvarh-pf - Reactive Power Parameters Explained
12. https://vitrek.com/understanding-total-harmonic-distortion-thd-and-its-impact-on-power-quality/ - Understanding THD Impact on Power Quality
13. https://www.neo-messtechnik.com/en/power-quality-explained-chapter-3-ieee-519-harmonics - IEEE 519 Harmonics Standard
14. https://library.e.abb.com/public/772bbffb5d6f41ffb88fc5d9da927dfd/LVD-EOTKN113U-EN_Three_Phase_Voltage_Imbalance_A.pdf - ABB Three-Phase Voltage Imbalance

### Protection et Sécurité
15. https://blog.comeca-group.com/en/how-to-monitor-the-temperature-of-your-electrical-switchboard - Switchboard Temperature Monitoring
16. https://cache.industry.siemens.com/dl/files/446/109745446/att_911312/v1/Temperaturemonitoring_EN_201612161353178605.pdf - Siemens SIVACON Temperature Monitoring
17. https://www.littelfuse.com/products/relays-contactors-transformers/protection-relays/arc-flash-detection - Littelfuse Arc Flash Detection Relays
18. https://selinc.com/solutions/arc-flash-solutions/ - SEL Arc-Flash Solutions
19. https://electrical-engineering-portal.com/switchgear-interlocking-system-arc-protection-design - Switchgear Interlocking System Design

### Contrôle et Délestage
20. https://betterbuildingssolutioncenter.energy.gov/sites/default/files/attachments/Demand%20Response%20in%20Industrial%20Facilities_Final.pdf - ORNL Demand Response in Industrial Facilities
21. https://www.eaton.com/content/dam/eaton/products/low-voltage-power-distribution-controls-systems/power-factor-corrections/portfolio/eaton-pfc-guide-plant-engineer-SA02607001E.pdf - Eaton Power Factor Correction Guide
22. https://electrical.theiet.org/media/1687/power-factor-correction-pfc.pdf - IEE Power Factor Correction

### Standards Techniques
23. https://www.electrical-installation.org/enwiki/Interlocks_and_conditioned_operations - Electrical Installation Guide - Interlocks
24. https://clouglobal.com/the-four-quadrant-diagram-in-electricity-metering/ - Four-Quadrant Electricity Metering
25. https://www.eit.edu.au/resources/fundamentals-of-smart-metering-kwh-and-kvarh-meters/ - Fundamentals of Smart Metering

**Dernière mise à jour** : 2025-12-18
**Version** : 1.0
**Auteur** : Documentation BMS - Electrical Domain