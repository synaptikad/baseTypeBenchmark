# Points BMS - Voltage Transformer (TT/VT/PT)

## Introduction

**IMPORTANT** : Les transformateurs de tension traditionnels sont des dispositifs **passifs** sans électronique ni communication BMS. Ils transforment simplement la tension primaire en tension secondaire normalisée (typiquement 100V ou 110V pour les applications de mesure).

Ce document couvre uniquement les **VT intelligents** et **capteurs de tension électroniques** équipés de modules de communication (Modbus, BACnet, IEC 61850) et de monitoring intégré. Ces équipements incluent :

- **VT avec monitoring intégré** : Surveillance de température, tension secondaire, état d'isolement
- **VT connectés** : Interface Modbus RTU/TCP, BACnet/IP, IEC 61850
- **Diviseurs capacitifs intelligents** : Capteurs capacitifs avec module de communication
- **Capteurs de tension électroniques** : Dispositifs à semi-conducteurs avec protocoles de communication
- **Merging Units (MU)** : Conversion analogique-numérique avec communication IEC 61850

## Points de Mesure

| Nom du Point | Description | Type | Unité | Fréquence | Plage Typique | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|-------|-----------|---------------|---------------|-------------|---------|---------|
| Primary_Voltage_L1_RMS | Tension primaire RMS phase L1 | AI | V | 1s | 0-36000V | sensor, voltage, primary, phase, ac, elec, point | Voltage_Sensor | AI-0 | 30001 |
| Primary_Voltage_L2_RMS | Tension primaire RMS phase L2 | AI | V | 1s | 0-36000V | sensor, voltage, primary, phase, ac, elec, point | Voltage_Sensor | AI-1 | 30002 |
| Primary_Voltage_L3_RMS | Tension primaire RMS phase L3 | AI | V | 1s | 0-36000V | sensor, voltage, primary, phase, ac, elec, point | Voltage_Sensor | AI-2 | 30003 |
| Primary_Voltage_L1L2 | Tension ligne à ligne L1-L2 | AI | V | 1s | 0-36000V | sensor, voltage, primary, ac, elec, point | Voltage_Sensor | AI-3 | 30004 |
| Primary_Voltage_L2L3 | Tension ligne à ligne L2-L3 | AI | V | 1s | 0-36000V | sensor, voltage, primary, ac, elec, point | Voltage_Sensor | AI-4 | 30005 |
| Primary_Voltage_L3L1 | Tension ligne à ligne L3-L1 | AI | V | 1s | 0-36000V | sensor, voltage, primary, ac, elec, point | Voltage_Sensor | AI-5 | 30006 |
| Primary_Voltage_Avg | Tension primaire moyenne triphasée | AI | V | 1s | 0-36000V | sensor, voltage, primary, avg, ac, elec, point | Voltage_Sensor | AI-6 | 30007 |
| Secondary_Voltage_L1 | Tension secondaire phase L1 | AI | V | 1s | 0-110V | sensor, voltage, secondary, phase, ac, elec, point | Voltage_Sensor | AI-7 | 30008 |
| Secondary_Voltage_L2 | Tension secondaire phase L2 | AI | V | 1s | 0-110V | sensor, voltage, secondary, phase, ac, elec, point | Voltage_Sensor | AI-8 | 30009 |
| Secondary_Voltage_L3 | Tension secondaire phase L3 | AI | V | 1s | 0-110V | sensor, voltage, secondary, phase, ac, elec, point | Voltage_Sensor | AI-9 | 30010 |
| VT_Temperature_Internal | Température interne du VT | AI | °C | 30s | -40 à 120°C | sensor, temp, equip, point | Temperature_Sensor | AI-10 | 30011 |
| VT_Temperature_Winding | Température enroulement secondaire | AI | °C | 30s | -40 à 150°C | sensor, temp, equip, point | Temperature_Sensor | AI-11 | 30012 |
| Voltage_Ratio_Factor | Facteur de rapport de transformation (%) | AI | % | 5s | 95-105% | sensor, ratio, equip, point | Sensor | AI-12 | 30013 |
| Voltage_Accuracy_Error | Erreur de précision mesurée | AI | % | 60s | -3 à +3% | sensor, accuracy, equip, point | Sensor | AI-13 | 30014 |
| Phase_Angle_L1 | Angle de phase L1 | AI | deg | 1s | 0-360° | sensor, angle, phase, ac, elec, point | Sensor | AI-14 | 30015 |
| Phase_Angle_L2 | Angle de phase L2 | AI | deg | 1s | 0-360° | sensor, angle, phase, ac, elec, point | Sensor | AI-15 | 30016 |
| Phase_Angle_L3 | Angle de phase L3 | AI | deg | 1s | 0-360° | sensor, angle, phase, ac, elec, point | Sensor | AI-16 | 30017 |
| Insulation_Resistance | Résistance d'isolement | AI | MΩ | 300s | 1-10000 MΩ | sensor, resistance, equip, point | Sensor | AI-17 | 30018 |
| Capacitance_Primary | Capacité primaire (diviseur capacitif) | AI | pF | 300s | 100-10000 pF | sensor, capacitance, equip, point | Sensor | AI-18 | 30019 |
| Frequency | Fréquence système | AI | Hz | 1s | 45-65 Hz | sensor, freq, ac, elec, point | Frequency_Sensor | AI-19 | 30020 |
| THD_Voltage_L1 | Distorsion harmonique totale L1 | AI | % | 5s | 0-20% | sensor, thd, voltage, phase, ac, elec, point | Sensor | AI-20 | 30021 |
| THD_Voltage_L2 | Distorsion harmonique totale L2 | AI | % | 5s | 0-20% | sensor, thd, voltage, phase, ac, elec, point | Sensor | AI-21 | 30022 |
| THD_Voltage_L3 | Distorsion harmonique totale L3 | AI | % | 5s | 0-20% | sensor, thd, voltage, phase, ac, elec, point | Sensor | AI-22 | 30023 |
| Burden_VA | Charge du circuit secondaire | AI | VA | 60s | 0-100 VA | sensor, load, equip, point | Sensor | AI-23 | 30024 |
| Power_Supply_Voltage | Tension alimentation électronique | AI | VDC | 30s | 18-30 VDC | sensor, voltage, dc, equip, point | Voltage_Sensor | AI-24 | 30025 |

## Points de Commande

| Nom du Point | Description | Type | Valeurs | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|---------------|-------------|---------|---------|
| Calibration_Mode_Enable | Activation mode calibration | BO | 0=Désactivé / 1=Activé | cmd, calibration, equip, point | Command | BO-0 | 00001 |
| Self_Test_Trigger | Déclenchement auto-test | BO | 0=Repos / 1=Déclencher | cmd, test, equip, point | Command | BO-1 | 00002 |
| Alarm_Reset | Réinitialisation des alarmes | BO | 0=Repos / 1=Reset | cmd, reset, alarm, equip, point | Command | BO-2 | 00003 |
| Communication_Reset | Réinitialisation communication | BO | 0=Repos / 1=Reset | cmd, reset, comm, equip, point | Command | BO-3 | 00004 |

## Points d'État

| Nom du Point | Description | Type | Valeurs | Fréquence | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|-----------|---------------|-------------|---------|---------|
| VT_Status_Overall | État général du VT | BI | 0=Défaut / 1=Normal | 5s | sensor, status, equip, point | Status | BI-0 | 10001 |
| Communication_Status | État communication | BI | 0=Perte / 1=OK | 5s | sensor, status, comm, equip, point | Status | BI-1 | 10002 |
| Temperature_High_Alarm | Alarme température élevée | BI | 0=Normal / 1=Alarme | 10s | sensor, alarm, temp, equip, point | Alarm | BI-2 | 10003 |
| Overvoltage_Detected | Surtension détectée | BI | 0=Normal / 1=Surtension | 1s | sensor, alarm, voltage, equip, point | Alarm | BI-3 | 10004 |
| Undervoltage_Detected | Sous-tension détectée | BI | 0=Normal / 1=Sous-tension | 1s | sensor, alarm, voltage, equip, point | Alarm | BI-4 | 10005 |
| Insulation_Fault | Défaut d'isolement | BI | 0=OK / 1=Défaut | 60s | sensor, alarm, fault, equip, point | Alarm | BI-5 | 10006 |
| Ferroresonance_Detected | Ferrorésonance détectée | BI | 0=Normal / 1=Détectée | 5s | sensor, alarm, resonance, equip, point | Alarm | BI-6 | 10007 |
| Secondary_Open_Circuit | Circuit secondaire ouvert | BI | 0=Fermé / 1=Ouvert | 5s | sensor, alarm, circuit, equip, point | Alarm | BI-7 | 10008 |
| Accuracy_Out_of_Range | Précision hors tolérance | BI | 0=OK / 1=Hors tolérance | 60s | sensor, alarm, accuracy, equip, point | Alarm | BI-8 | 10009 |
| Self_Test_Pass | Résultat auto-test | BI | 0=Échec / 1=Succès | Event | sensor, status, test, equip, point | Status | BI-9 | 10010 |
| Calibration_Valid | Calibration valide | BI | 0=Invalide / 1=Valide | 300s | sensor, status, calibration, equip, point | Status | BI-10 | 10011 |
| VT_Fuse_Blown | Fusible VT grillé | BI | 0=OK / 1=Grillé | 5s | sensor, alarm, fuse, equip, point | Alarm | BI-11 | 10012 |
| Phase_Loss_L1 | Perte phase L1 | BI | 0=Présente / 1=Perdue | 1s | sensor, alarm, phase, equip, point | Alarm | BI-12 | 10013 |
| Phase_Loss_L2 | Perte phase L2 | BI | 0=Présente / 1=Perdue | 1s | sensor, alarm, phase, equip, point | Alarm | BI-13 | 10014 |
| Phase_Loss_L3 | Perte phase L3 | BI | 0=Présente / 1=Perdue | 1s | sensor, alarm, phase, equip, point | Alarm | BI-14 | 10015 |
| Phase_Imbalance_Alarm | Alarme déséquilibre phases | BI | 0=Normal / 1=Déséquilibre | 5s | sensor, alarm, phase, equip, point | Alarm | BI-15 | 10016 |
| Power_Supply_Fault | Défaut alimentation électronique | BI | 0=OK / 1=Défaut | 10s | sensor, alarm, power, equip, point | Alarm | BI-16 | 10017 |

## Points de Configuration

| Nom du Point | Description | Type | Valeurs | Accès | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|-------|---------------|-------------|---------|---------|
| Primary_Voltage_Nominal | Tension primaire nominale | AV | 1000-36000V | R/W | sp, voltage, primary, equip, point | Setpoint | AV-0 | 40001 |
| Secondary_Voltage_Nominal | Tension secondaire nominale | AV | 100-110V | R/W | sp, voltage, secondary, equip, point | Setpoint | AV-1 | 40002 |
| Transformation_Ratio | Rapport de transformation | AV | 10-360 | R/W | sp, ratio, equip, point | Setpoint | AV-2 | 40003 |
| Accuracy_Class | Classe de précision VT | MSV | 0=0.1 / 1=0.2 / 2=0.5 / 3=1.0 / 4=3.0 | R/W | sp, accuracy, equip, point | Parameter | MSV-0 | 40004 |
| Overvoltage_Threshold | Seuil alarme surtension | AV | 105-150% Vn | R/W | sp, alarm, voltage, high, equip, point | Limit | AV-3 | 40005 |
| Undervoltage_Threshold | Seuil alarme sous-tension | AV | 50-95% Vn | R/W | sp, alarm, voltage, low, equip, point | Limit | AV-4 | 40006 |
| Temperature_High_Setpoint | Seuil température haute | AV | 60-120°C | R/W | sp, alarm, temp, high, equip, point | Limit | AV-5 | 40007 |
| Temperature_Critical_Setpoint | Seuil température critique | AV | 80-150°C | R/W | sp, alarm, temp, critical, equip, point | Limit | AV-6 | 40008 |
| Insulation_Resistance_Min | Résistance isolement minimale | AV | 1-1000 MΩ | R/W | sp, alarm, resistance, low, equip, point | Limit | AV-7 | 40009 |
| Phase_Imbalance_Threshold | Seuil déséquilibre phases | AV | 1-10% | R/W | sp, alarm, phase, equip, point | Limit | AV-8 | 40010 |
| Modbus_Slave_Address | Adresse Modbus esclave | AV | 1-247 | R/W | sp, address, comm, equip, point | Parameter | AV-9 | 40011 |
| Modbus_Baud_Rate | Vitesse Modbus | MSV | 0=9600 / 1=19200 / 2=38400 / 3=57600 / 4=115200 | R/W | sp, baudrate, comm, equip, point | Parameter | MSV-1 | 40012 |
| Sampling_Rate | Fréquence d'échantillonnage | AV | 100-10000 Hz | R/W | sp, freq, sample, equip, point | Parameter | AV-10 | 40013 |
| Calibration_Date | Date dernière calibration | AV | Unix timestamp | R | sensor, date, calibration, equip, point | Parameter | AV-11 | 40014 |
| Calibration_Interval_Days | Intervalle calibration (jours) | AV | 30-1825 jours | R/W | sp, interval, calibration, equip, point | Parameter | AV-12 | 40015 |
| Device_Serial_Number | Numéro de série | AV | - | R | id, equip, point | Parameter | AV-13 | 40016 |
| Firmware_Version | Version firmware | AV | - | R | version, software, equip, point | Parameter | AV-14 | 40017 |
| Burden_Rating | Charge nominale secondaire | AV | 5-100 VA | R/W | sp, load, rated, equip, point | Parameter | AV-15 | 40018 |

## Notes d'Implémentation

### Protocoles de Communication

#### Modbus RTU/TCP
- **Baud Rates** : 9600, 19200, 38400, 57600, 115200 bps (RTU)
- **Format** : 8N1, 8E1, 8O1
- **Fonctions supportées** :
  - 03h : Read Holding Registers (configuration)
  - 04h : Read Input Registers (mesures)
  - 05h : Write Single Coil (commandes)
  - 06h : Write Single Register (paramètres)
  - 10h : Write Multiple Registers (calibration)
- **Registres** :
  - 30001-30099 : Input Registers (mesures analogiques)
  - 40001-40099 : Holding Registers (configuration)
  - 10001-10099 : Discrete Inputs (états)
  - 00001-00099 : Coils (commandes)

#### BACnet/IP
- **Object Types** :
  - Analog Input (AI) : Mesures temps réel
  - Analog Value (AV) : Configuration et setpoints
  - Binary Input (BI) : États et alarmes
  - Binary Output (BO) : Commandes
  - Multi-State Value (MSV) : Énumérations (classe précision, baud rate)
- **Services supportés** :
  - ReadProperty
  - WriteProperty
  - SubscribeCOV (Change of Value)
  - I-Am / Who-Is
- **Port** : UDP 47808

#### IEC 61850
- **Logical Node** : TVTR (Voltage Transformer)
- **Data Classes** :
  - Vol : Voltage (mesures instantanées)
  - Tmp : Temperature
  - Hz : Frequency
  - Alm : Alarms
- **Communication** :
  - GOOSE : Generic Object Oriented Substation Event (temps réel <4ms)
  - MMS : Manufacturing Message Specification (configuration)
  - Sampled Values : Échantillons numérisés haute fréquence
- **Merging Units** : Conversion A/N avec TVTR logical node pour digitalisation

### Fréquences Recommandées

| Type de Point | Fréquence | Justification |
|--------------|-----------|---------------|
| Tensions primaires/secondaires | 1s | Surveillance temps réel, détection transitoires |
| Température | 30s | Variation lente, pas de changement rapide |
| THD et harmoniques | 5s | Détection perturbations qualité |
| Résistance isolement | 300s (5min) | Test périodique, variation lente |
| États et alarmes | 1-5s | Réactivité suffisante pour protection |
| Configuration | COV | Écriture événementielle uniquement |

### Considérations Spécifiques aux VT Intelligents

#### Ferroresonance Detection
La ferrorésonance est un phénomène oscillatoire dangereux entre l'inductance non-linéaire du VT et les capacités du réseau. Les symptômes incluent :
- Surtensions importantes (>2x tension nominale)
- Surintensités au secondaire
- Bruit excessif et vibrations
- Surchauffe des enroulements
- Distorsion importante des formes d'onde

Les VT intelligents détectent ce phénomène via l'analyse de THD, température, et forme d'onde.

#### VT Fuse Supervision
Les VT traditionnels utilisent des fusibles de protection. Les relais de supervision (VT fuse fail) détectent :
- Tension de séquence négative anormale
- Disparition tension sur une phase
- Déséquilibre triphasé important

Les VT électroniques intègrent cette supervision directement.

#### Capacitive Voltage Dividers
Les diviseurs capacitifs intelligents utilisent :
- Monitoring de capacité (détection vieillissement)
- Surveillance température (coefficient thermique)
- Communication sans fil possible (Bluetooth, ZigBee)
- Faible consommation énergétique

#### Digital Substations (IEC 61850)
Dans les postes numériques :
- Les Merging Units (MU) digitalisent les signaux VT
- Le logical node TVTR représente le transformateur
- Les Sampled Values remplacent le câblage analogique
- GOOSE messages pour états et alarmes (<4ms)
- Synchronisation temporelle critique (IEEE 1588 PTP)

### Sécurité et Maintenance

#### Tests Périodiques
- **Ratio Test** : Vérification rapport transformation (annuel)
- **Insulation Resistance** : Test mégohmmètre 1000-5000V (annuel)
- **Tan Delta** : Test facteur de dissipation isolement (2-5 ans)
- **Burden Test** : Vérification charge secondaire (annuel)
- **Calibration** : Étalonnage précision (1-5 ans selon classe)

#### Alarmes Critiques
Les alarmes suivantes nécessitent une action immédiate :
- **Circuit secondaire ouvert** : Risque surtension dangereuse
- **Ferroresonance** : Destruction possible du VT
- **Insulation fault** : Risque court-circuit
- **Phase loss** : Fausse mesure, protection invalide

#### Limites de Charge (Burden)
Ne jamais dépasser la charge nominale secondaire (VA rating) :
- Classe 0.1-0.2 : 10-25 VA typique
- Classe 0.5-1.0 : 25-75 VA typique
- Classe 3.0 : 75-200 VA typique

### Intégration SCADA/BMS

#### Priorités de Communication
1. **Critique** (COV immédiat) : Alarmes protection, ferroresonance, phase loss
2. **Haute** (1s) : Mesures tension, fréquence
3. **Moyenne** (5-30s) : Température, THD, états
4. **Basse** (60-300s) : Résistance isolement, diagnostics

#### Historisation
- **Tendances** : Tensions (1s), Température (1min), Résistance isolement (5min)
- **Événements** : Toutes alarmes avec timestamp
- **Waveforms** : Enregistrement forme d'onde lors ferroresonance/surtension

## Sources

1. https://library.e.abb.com/public/012bb189cb694eaf96e77906eae226d6/REF615_modbuspoint_756581_ENl.pdf - ABB REF615 Modbus Point List Manual
2. https://new.abb.com/medium-voltage/apparatus/instrument-transformers-and-sensors-id/products/sensors-new - ABB Medium Voltage Electronic Sensors KEVA Series
3. https://download.schneider-electric.com/files?p_enDocType=User+guide&p_File_Name=7EN02-0248-08.pdf&p_Doc_Ref=7EN02-0248 - Schneider PowerLogic ION7650 User Guide
4. https://www.mdpi.com/1996-1073/15/24/9516 - Methods of Ferroresonance Mitigation in Voltage Transformers (MDPI Energy Journal)
5. https://electrical-engineering-portal.com/guide-voltage-transformer-circuit-supervision-techniques - Comprehensive Guide to VT Circuit Supervision Techniques
6. https://project-haystack.org/doc/proto/avg-ac-elec-volt-magnitude-sensor-point - Project Haystack Voltage Sensor Point Tags
7. https://brickschema.org/ontology/1.0.3/classes/Voltage_Sensor/ - Brick Schema Voltage_Sensor Class Definition
8. https://ieeexplore.ieee.org/document/9906629/ - IEEE Paper: Voltage Measuring Sensor Based on Capacitive Voltage Divider
9. https://library.e.abb.com/public/d9317de927099d73c2256c3e002bc491/CIGREreport.pdf - ABB CIGRE Report: Medium Voltage Sensors Technology
10. https://www.eaton.com/us/en-us/products/electrical-circuit-protection/protective-relays-and-predictive-devices/e-series-relays-iec-61850-goose-.html - Eaton E-Series Relays with IEC 61850 GOOSE Messaging
11. https://www.omicronenergy.com/en/solution/protection-testing-with-goose/ - OMICRON Protection Testing with GOOSE (IEC 61850)
12. https://www.orionitalia.com/temperature-control/tr42-modbus - Orion TR42 Transformer Temperature Monitoring with Modbus
13. https://www.qualitrolcorp.com/products/transformer-monitors/intelligent-transformer-monitors/ - Qualitrol Intelligent Transformer Monitors
14. https://www.workongrid.com/blog/transformer-voltage-monitoring - Transformer Voltage Monitoring Best Practices
15. https://www.te.com/content/dam/te-com/custom/documents/windsolutionguide/energy-rsti-capacitive-sensor-datasheet-10-18-epp3040-iec.pdf - TE Connectivity Capacitive Voltage Sensors Datasheet

## Révisions

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0 | 2025-12-18 | Claude Code | Création initiale du document |
