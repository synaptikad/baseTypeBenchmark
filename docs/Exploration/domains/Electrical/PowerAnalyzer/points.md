# Points de Power Analyzer (Analyseur de Puissance)

## Synthèse
- **Total points mesure** : 180+
- **Total points commande** : 8
- **Total points état** : 12

## Points de Mesure (Capteurs)

### Tensions (Voltage)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| V_L1N_RMS | Tension L1-N RMS (10min avg) | V | 0-690V | volt, sensor, point, phase:"L1", phaseRef:"N", rms | Voltage_Sensor | 10min |
| V_L2N_RMS | Tension L2-N RMS (10min avg) | V | 0-690V | volt, sensor, point, phase:"L2", phaseRef:"N", rms | Voltage_Sensor | 10min |
| V_L3N_RMS | Tension L3-N RMS (10min avg) | V | 0-690V | volt, sensor, point, phase:"L3", phaseRef:"N", rms | Voltage_Sensor | 10min |
| V_L12_RMS | Tension L1-L2 RMS (10min avg) | V | 0-1200V | volt, sensor, point, line:"L12", rms | Voltage_Sensor | 10min |
| V_L23_RMS | Tension L2-L3 RMS (10min avg) | V | 0-1200V | volt, sensor, point, line:"L23", rms | Voltage_Sensor | 10min |
| V_L31_RMS | Tension L3-L1 RMS (10min avg) | V | 0-1200V | volt, sensor, point, line:"L31", rms | Voltage_Sensor | 10min |
| V_PhaseAvg_RMS | Tension moyenne phase-neutre | V | 0-690V | volt, sensor, point, phaseAvg, rms | Voltage_Sensor | 10min |
| V_LineAvg_RMS | Tension moyenne ligne-ligne | V | 0-1200V | volt, sensor, point, lineAvg, rms | Voltage_Sensor | 10min |
| V_L1N_Peak | Tension pic L1-N | V | 0-1000V | volt, sensor, point, phase:"L1", phaseRef:"N", peak | Voltage_Sensor | 200ms |
| V_L2N_Peak | Tension pic L2-N | V | 0-1000V | volt, sensor, point, phase:"L2", phaseRef:"N", peak | Voltage_Sensor | 200ms |
| V_L3N_Peak | Tension pic L3-N | V | 0-1000V | volt, sensor, point, phase:"L3", phaseRef:"N", peak | Voltage_Sensor | 200ms |
| V_L1N_CrestFactor | Facteur de crête tension L1-N | - | 1.0-5.0 | volt, sensor, point, phase:"L1", phaseRef:"N", crestFactor | Voltage_Sensor | 10min |
| V_L2N_CrestFactor | Facteur de crête tension L2-N | - | 1.0-5.0 | volt, sensor, point, phase:"L2", phaseRef:"N", crestFactor | Voltage_Sensor | 10min |
| V_L3N_CrestFactor | Facteur de crête tension L3-N | - | 1.0-5.0 | volt, sensor, point, phase:"L3", phaseRef:"N", crestFactor | Voltage_Sensor | 10min |

### Courants (Current)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| I_L1_RMS | Courant L1 RMS (10min avg) | A | 0-5000A | current, sensor, point, phase:"L1", rms | Current_Sensor | 10min |
| I_L2_RMS | Courant L2 RMS (10min avg) | A | 0-5000A | current, sensor, point, phase:"L2", rms | Current_Sensor | 10min |
| I_L3_RMS | Courant L3 RMS (10min avg) | A | 0-5000A | current, sensor, point, phase:"L3", rms | Current_Sensor | 10min |
| I_N_RMS | Courant neutre RMS | A | 0-5000A | current, sensor, point, neutral, rms | Current_Sensor | 10min |
| I_Avg_RMS | Courant moyen triphasé | A | 0-5000A | current, sensor, point, phaseAvg, rms | Current_Sensor | 10min |
| I_L1_Peak | Courant pic L1 | A | 0-10000A | current, sensor, point, phase:"L1", peak | Current_Sensor | 200ms |
| I_L2_Peak | Courant pic L2 | A | 0-10000A | current, sensor, point, phase:"L2", peak | Current_Sensor | 200ms |
| I_L3_Peak | Courant pic L3 | A | 0-10000A | current, sensor, point, phase:"L3", peak | Current_Sensor | 200ms |
| I_L1_CrestFactor | Facteur de crête courant L1 | - | 1.0-5.0 | current, sensor, point, phase:"L1", crestFactor | Current_Sensor | 10min |
| I_L2_CrestFactor | Facteur de crête courant L2 | - | 1.0-5.0 | current, sensor, point, phase:"L2", crestFactor | Current_Sensor | 10min |
| I_L3_CrestFactor | Facteur de crête courant L3 | - | 1.0-5.0 | current, sensor, point, phase:"L3", crestFactor | Current_Sensor | 10min |

### Puissances (Power)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| P_L1_Active | Puissance active L1 | kW | -500 à +500 | active, power, sensor, point, phase:"L1" | Active_Power_Sensor | 1s |
| P_L2_Active | Puissance active L2 | kW | -500 à +500 | active, power, sensor, point, phase:"L2" | Active_Power_Sensor | 1s |
| P_L3_Active | Puissance active L3 | kW | -500 à +500 | active, power, sensor, point, phase:"L3" | Active_Power_Sensor | 1s |
| P_Total_Active | Puissance active totale | kW | -1500 à +1500 | active, power, sensor, point, total | Active_Power_Sensor | 1s |
| Q_L1_Reactive | Puissance réactive L1 | kvar | -500 à +500 | reactive, power, sensor, point, phase:"L1" | Reactive_Power_Sensor | 1s |
| Q_L2_Reactive | Puissance réactive L2 | kvar | -500 à +500 | reactive, power, sensor, point, phase:"L2" | Reactive_Power_Sensor | 1s |
| Q_L3_Reactive | Puissance réactive L3 | kvar | -500 à +500 | reactive, power, sensor, point, phase:"L3" | Reactive_Power_Sensor | 1s |
| Q_Total_Reactive | Puissance réactive totale | kvar | -1500 à +1500 | reactive, power, sensor, point, total | Reactive_Power_Sensor | 1s |
| S_L1_Apparent | Puissance apparente L1 | kVA | 0-500 | apparent, power, sensor, point, phase:"L1" | Apparent_Power_Sensor | 1s |
| S_L2_Apparent | Puissance apparente L2 | kVA | 0-500 | apparent, power, sensor, point, phase:"L2" | Apparent_Power_Sensor | 1s |
| S_L3_Apparent | Puissance apparente L3 | kVA | 0-500 | apparent, power, sensor, point, phase:"L3" | Apparent_Power_Sensor | 1s |
| S_Total_Apparent | Puissance apparente totale | kVA | 0-1500 | apparent, power, sensor, point, total | Apparent_Power_Sensor | 1s |
| P_Demand_Peak | Puissance demande max | kW | 0-1500 | active, power, demand, peak, sensor, point | Peak_Power_Demand_Sensor | 15min |
| P_Demand_Avg | Puissance demande moyenne | kW | 0-1500 | active, power, demand, avg, sensor, point | Power_Demand_Sensor | 15min |

### Facteurs de Puissance

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| PF_L1_True | Facteur puissance réel L1 (TPF) | - | -1.0 à +1.0 | pf, sensor, point, phase:"L1", truePF | Power_Factor_Sensor | 1s |
| PF_L2_True | Facteur puissance réel L2 (TPF) | - | -1.0 à +1.0 | pf, sensor, point, phase:"L2", truePF | Power_Factor_Sensor | 1s |
| PF_L3_True | Facteur puissance réel L3 (TPF) | - | -1.0 à +1.0 | pf, sensor, point, phase:"L3", truePF | Power_Factor_Sensor | 1s |
| PF_Total_True | Facteur puissance réel total (TPF) | - | -1.0 à +1.0 | pf, sensor, point, total, truePF | Power_Factor_Sensor | 1s |
| DPF_L1 | Facteur déplacement L1 (cos φ) | - | -1.0 à +1.0 | pf, sensor, point, phase:"L1", displacement, fundamental | Power_Factor_Sensor | 1s |
| DPF_L2 | Facteur déplacement L2 (cos φ) | - | -1.0 à +1.0 | pf, sensor, point, phase:"L2", displacement, fundamental | Power_Factor_Sensor | 1s |
| DPF_L3 | Facteur déplacement L3 (cos φ) | - | -1.0 à +1.0 | pf, sensor, point, phase:"L3", displacement, fundamental | Power_Factor_Sensor | 1s |
| DPF_Total | Facteur déplacement total (cos φ) | - | -1.0 à +1.0 | pf, sensor, point, total, displacement, fundamental | Power_Factor_Sensor | 1s |

### Énergies

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| E_Active_Import | Énergie active importée | kWh | 0-999999999 | active, energy, sensor, point, import | Energy_Sensor | 1h |
| E_Active_Export | Énergie active exportée | kWh | 0-999999999 | active, energy, sensor, point, export | Energy_Sensor | 1h |
| E_Reactive_Import | Énergie réactive importée | kvarh | 0-999999999 | reactive, energy, sensor, point, import | Reactive_Energy_Sensor | 1h |
| E_Reactive_Export | Énergie réactive exportée | kvarh | 0-999999999 | reactive, energy, sensor, point, export | Reactive_Energy_Sensor | 1h |
| E_Apparent_Total | Énergie apparente totale | kVAh | 0-999999999 | apparent, energy, sensor, point, total | Apparent_Energy_Sensor | 1h |

### Fréquence

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Freq | Fréquence réseau (10s avg) | Hz | 45.0-65.0 | freq, sensor, point | Frequency_Sensor | 10s |
| Freq_Min | Fréquence minimale | Hz | 45.0-65.0 | freq, sensor, point, min | Frequency_Sensor | 10min |
| Freq_Max | Fréquence maximale | Hz | 45.0-65.0 | freq, sensor, point, max | Frequency_Sensor | 10min |

### Harmoniques Tension (THD)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| THD_V_L1 | THD tension L1-N | % | 0-100% | volt, sensor, point, phase:"L1", phaseRef:"N", thd, harmonic | Voltage_Sensor | 10min |
| THD_V_L2 | THD tension L2-N | % | 0-100% | volt, sensor, point, phase:"L2", phaseRef:"N", thd, harmonic | Voltage_Sensor | 10min |
| THD_V_L3 | THD tension L3-N | % | 0-100% | volt, sensor, point, phase:"L3", phaseRef:"N", thd, harmonic | Voltage_Sensor | 10min |

*Note: Harmoniques individuels H1-H63 par phase disponibles (voir documentation complète)*

### Harmoniques Courant (THD)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| THD_I_L1 | THD courant L1 | % | 0-100% | current, sensor, point, phase:"L1", thd, harmonic | Current_Sensor | 10min |
| THD_I_L2 | THD courant L2 | % | 0-100% | current, sensor, point, phase:"L2", thd, harmonic | Current_Sensor | 10min |
| THD_I_L3 | THD courant L3 | % | 0-100% | current, sensor, point, phase:"L3", thd, harmonic | Current_Sensor | 10min |
| TDD_I_L1 | TDD courant L1 (IEEE 519) | % | 0-100% | current, sensor, point, phase:"L1", tdd, harmonic | Current_Sensor | 10min |
| TDD_I_L2 | TDD courant L2 (IEEE 519) | % | 0-100% | current, sensor, point, phase:"L2", tdd, harmonic | Current_Sensor | 10min |
| TDD_I_L3 | TDD courant L3 (IEEE 519) | % | 0-100% | current, sensor, point, phase:"L3", tdd, harmonic | Current_Sensor | 10min |

### Flicker

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Pst_L1 | Flicker court terme L1 (10min) | - | 0-10 | volt, sensor, point, phase:"L1", flicker, pst, shortTerm | Voltage_Sensor | 10min |
| Pst_L2 | Flicker court terme L2 (10min) | - | 0-10 | volt, sensor, point, phase:"L2", flicker, pst, shortTerm | Voltage_Sensor | 10min |
| Pst_L3 | Flicker court terme L3 (10min) | - | 0-10 | volt, sensor, point, phase:"L3", flicker, pst, shortTerm | Voltage_Sensor | 10min |
| Plt_L1 | Flicker long terme L1 (2h) | - | 0-10 | volt, sensor, point, phase:"L1", flicker, plt, longTerm | Voltage_Sensor | 2h |
| Plt_L2 | Flicker long terme L2 (2h) | - | 0-10 | volt, sensor, point, phase:"L2", flicker, plt, longTerm | Voltage_Sensor | 2h |
| Plt_L3 | Flicker long terme L3 (2h) | - | 0-10 | volt, sensor, point, phase:"L3", flicker, plt, longTerm | Voltage_Sensor | 2h |

### Déséquilibres (Unbalance)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| V_Unbalance | Déséquilibre tension (IEC) | % | 0-10% | volt, sensor, point, unbalance, negativeSeq | Voltage_Sensor | 10min |
| V_NegSeq | Tension séquence négative | V | 0-100V | volt, sensor, point, negativeSeq | Voltage_Sensor | 10min |
| I_Unbalance | Déséquilibre courant | % | 0-100% | current, sensor, point, unbalance, negativeSeq | Current_Sensor | 10min |

### Événements de Qualité

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Sag_L1_Count | Nombre de creux tension L1 | count | 0-9999 | volt, sensor, point, phase:"L1", sag, event, count | Voltage_Sensor | event |
| Swell_L1_Count | Nombre de pointes tension L1 | count | 0-9999 | volt, sensor, point, phase:"L1", swell, event, count | Voltage_Sensor | event |
| Interrupt_L1_Count | Nombre interruptions L1 | count | 0-9999 | volt, sensor, point, phase:"L1", interruption, event, count | Voltage_Sensor | event |

## Points de Commande (Actionneurs/Consignes)

| Point | Description | Unité | Plage | Haystack Tags | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| Cmd_ResetEnergy | Reset compteurs énergie | bool | 0/1 | energy, cmd, point, reset | Command |
| Cmd_ResetDemand | Reset demande max | bool | 0/1 | demand, cmd, point, reset | Command |
| Cmd_ResetEventLog | Effacer journal événements | bool | 0/1 | event, cmd, point, reset | Command |
| Cmd_StartWaveformCapture | Démarrer capture forme d'onde | bool | 0/1 | waveform, cmd, point, start | Command |
| Cmd_SyncTime | Synchroniser horloge | bool | 0/1 | time, cmd, point, sync | Command |
| Set_SagThreshold | Seuil détection creux tension | % | 10-90% | volt, sp, point, sag, threshold | Setpoint |
| Set_SwellThreshold | Seuil détection pointes tension | % | 110-200% | volt, sp, point, swell, threshold | Setpoint |
| Set_DemandInterval | Intervalle calcul demande | min | 5-60 | demand, sp, point, interval | Setpoint |

## Points d'État

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Status_Comm | État communication | OK/Fault/Timeout | comm, status, point | Status |
| Status_PowerSupply | État alimentation | OK/LowVoltage/Fault | power, supply, status, point | Status |
| Status_Sensor_CT1 | État capteur TC L1 | OK/Open/Short | sensor, ct, status, point, phase:"L1" | Status |
| Status_MemoryFull | Mémoire événements pleine | OK/Warning/Full | memory, status, point, full | Status |
| Alarm_VoltageOutOfRange | Alarme tension hors limites | None/Minor/Major | volt, alarm, point, outOfRange | Alarm |
| Alarm_THD_Voltage | Alarme THD tension élevé | None/Warning/Alarm | volt, thd, alarm, point | Alarm |
| Alarm_THD_Current | Alarme THD courant élevé | None/Warning/Alarm | current, thd, alarm, point | Alarm |
| Alarm_Unbalance | Alarme déséquilibre | None/Warning/Alarm | unbalance, alarm, point | Alarm |
| Alarm_PowerFactor | Alarme facteur puissance faible | None/Warning/Alarm | pf, alarm, point, low | Alarm |
| Compliance_EN50160 | Conformité EN 50160 | Compliant/NonCompliant | compliance, status, point, en50160 | Status |

## Mappings Protocoles

### BACnet

| Point | Object Type | Object Instance | Units | R/W |
|-------|-------------|-----------------|-------|-----|
| V_L1N_RMS | Analog Input | 0 | Volts | R |
| I_L1_RMS | Analog Input | 10 | Amperes | R |
| P_Total_Active | Analog Input | 20 | Kilowatts | R |
| PF_Total_True | Analog Input | 30 | No Units | R |
| E_Active_Import | Analog Input | 40 | Kilowatt-Hours | R |
| THD_V_L1 | Analog Input | 100 | Percent | R |
| Pst_L1 | Analog Input | 400 | No Units | R |

### Modbus

| Point | Type | Registre | Data Type | Unités | R/W |
|-------|------|----------|-----------|--------|-----|
| V_L1N_RMS | Holding | 0 | Float32 | V | R |
| I_L1_RMS | Holding | 100 | Float32 | A | R |
| P_Total_Active | Holding | 206 | Float32 | kW | R |
| THD_V_L1 | Holding | 500 | Float32 | % | R |

## Sources

1. IEC 61000-4-30:2015 - Power quality measurement methods
2. IEEE 519-2022 - Harmonic Control in Electric Power Systems
3. EN 50160:2010 - Voltage characteristics
4. Project Haystack - Meters Documentation
5. Brick Schema - Meters Modeling
6. Schneider Electric PM8000 Series
7. Fluke 1760 Power Quality Recorder
8. Accuenergy Acuvim 3 Series
9. Power Quality Blog
10. Dewesoft Power Quality Analysis