# Points BMS - Current Transformer (TC/CT)

## Introduction

**IMPORTANT** : Les transformateurs de courant traditionnels sont des dispositifs **passifs** sans électronique ni communication BMS. Ils transforment simplement le courant primaire en courant secondaire normalisé (1A ou 5A) pour alimenter des relais de protection ou des instruments de mesure.

Ce document couvre uniquement les **TC intelligents** et **capteurs de courant électroniques** équipés de modules de communication (Modbus, BACnet, IEC 61850) et de monitoring intégré. Cette catégorie inclut :

- **TC avec monitoring intégré** : Température, courant secondaire, facteur de charge
- **TC connectés** : Interface Modbus RTU/TCP, BACnet/IP, IEC 61850
- **Bobines de Rogowski électroniques** : Capteurs flexibles avec sortie numérique (RS-485, Ethernet)
- **Unités de fusion (Merging Units)** : Conversion analogique-numérique avec protocole IEC 61850-9-2 (Sampled Values)
- **TC pour protection** : Relais intégrés avec communication GOOSE

Les TC passifs conventionnels ne figurent pas dans ce document car ils ne génèrent aucun point de données BMS directement accessible.

## Points de Mesure

| Nom du Point | Description | Type | Unité | Fréquence | Plage Typique | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|-------|-----------|---------------|---------------|-------------|---------|---------|
| Primary_Current_RMS | Courant primaire efficace mesuré | AI | A | 1s-5s | 0-6000 A | sensor, current, elec, primary, rms | Current_Sensor | AI-0 | 30001 |
| Secondary_Current_RMS | Courant secondaire efficace (1A ou 5A nominal) | AI | A | 1s-5s | 0-7.5 A | sensor, current, elec, secondary, rms | Current_Sensor | AI-1 | 30002 |
| Primary_Current_Peak | Valeur crête du courant primaire | AI | A | 1s | 0-8500 A | sensor, current, elec, primary, peak | Current_Sensor | AI-2 | 30003 |
| CT_Temperature | Température interne du TC ou de l'électronique | AI | °C | 10s-30s | -40 à +85°C | sensor, temp, elec, ct | Temperature_Sensor | AI-3 | 30004 |
| Load_Factor | Facteur de charge du TC (I_primaire / I_nominal) | AI | % | 5s-10s | 0-150% | sensor, load, elec, ct | Load_Sensor | AI-4 | 30005 |
| Power_Dissipation | Puissance dissipée dans le TC | AI | W | 10s-30s | 0-50 W | sensor, power, elec, ct | Power_Sensor | AI-5 | 30006 |
| CT_Burden | Charge secondaire connectée (impédance) | AI | VA | Static | 0-30 VA | sensor, burden, elec, ct | Sensor | AI-6 | 30007 |
| Phase_Angle_Error | Erreur d'angle de phase (précision) | AI | deg | 1min | -2 à +2° | sensor, angle, elec, ct, error | Sensor | AI-7 | 30008 |
| Ratio_Error | Erreur de rapport de transformation | AI | % | 1min | -3 à +3% | sensor, ratio, elec, ct, error | Sensor | AI-8 | 30009 |
| Saturation_Level | Niveau de saturation magnétique | AI | % | 1s-5s | 0-100% | sensor, saturation, elec, ct | Sensor | AI-9 | 30010 |
| THD_Current | Distorsion harmonique totale du courant | AI | % | 10s-60s | 0-50% | sensor, thd, current, elec | Sensor | AI-10 | 30011 |
| Insulation_Resistance | Résistance d'isolement (diagnostic) | AI | MΩ | 1h-24h | 10-10000 MΩ | sensor, insulation, resistance, elec, ct | Sensor | AI-11 | 30012 |
| SV_Sample_Rate | Taux d'échantillonnage (IEC 61850-9-2) | AI | samples/cycle | Static | 80-256 | sensor, sample, rate, elec | Sensor | AI-12 | 30013 |
| Communication_Quality | Qualité du signal de communication (RSSI pour sans fil) | AI | dBm | 30s-60s | -100 à -30 dBm | sensor, comm, quality | Sensor | AI-13 | 30014 |
| Operating_Hours | Heures de fonctionnement cumulées | ACC | h | On change | 0-200000 h | sensor, runtime, elec, ct | Sensor | ACC-0 | 40001 |

## Points de Commande

| Nom du Point | Description | Type | Valeurs | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|---------------|-------------|---------|---------|
| Reset_Alarms | Réinitialisation des alarmes actives | BO | 0=Idle, 1=Reset | cmd, reset, alarm, ct | Command | BO-0 | 00001 |
| Calibration_Mode | Activation du mode calibration | BO | 0=Normal, 1=Calibration | cmd, calibration, mode, ct | Command | BO-1 | 00002 |
| Self_Test_Trigger | Déclenchement auto-test diagnostique | BO | 0=Idle, 1=Test | cmd, test, trigger, ct | Command | BO-2 | 00003 |
| Data_Logging_Enable | Activation enregistrement données | BO | 0=Disabled, 1=Enabled | cmd, enable, logging, ct | Command | BO-3 | 00004 |

## Points d'État

| Nom du Point | Description | Type | Valeurs | Fréquence | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|-----------|---------------|-------------|---------|---------|
| CT_Status | État opérationnel général du TC | MSV | 0=Normal, 1=Warning, 2=Alarm, 3=Fault | 5s-10s | sensor, status, ct, elec | Status | MSV-0 | 10001 |
| Communication_Status | État de la communication réseau | BI | 0=Offline, 1=Online | 5s-10s | sensor, comm, status, ct | Status | BI-0 | 10002 |
| Overload_Alarm | Alarme de surcharge détectée | BI | 0=Normal, 1=Overload | 1s-5s | sensor, alarm, overload, ct | Alarm | BI-1 | 10003 |
| Temperature_Alarm | Alarme température excessive | BI | 0=Normal, 1=High Temp | 10s-30s | sensor, alarm, temp, ct | Alarm | BI-2 | 10004 |
| Saturation_Alarm | Alarme saturation magnétique | BI | 0=Normal, 1=Saturated | 1s-5s | sensor, alarm, saturation, ct | Alarm | BI-3 | 10005 |
| Insulation_Fault | Défaut d'isolement détecté | BI | 0=Normal, 1=Fault | 1h-24h | sensor, alarm, insulation, ct | Alarm | BI-4 | 10006 |
| Secondary_Open_Circuit | Circuit secondaire ouvert (danger) | BI | 0=Closed, 1=Open | 1s-5s | sensor, alarm, open, circuit, ct | Alarm | BI-5 | 10007 |
| Calibration_Status | État de calibration | BI | 0=Valid, 1=Expired | 1h-24h | sensor, status, calibration, ct | Status | BI-6 | 10008 |
| Self_Test_Status | Résultat du dernier auto-test | MSV | 0=Pass, 1=Fail, 2=Not Run | On change | sensor, status, test, ct | Status | MSV-1 | 10009 |
| Power_Supply_Status | État de l'alimentation électronique | BI | 0=Normal, 1=Low Voltage | 10s-30s | sensor, status, power, supply, ct | Status | BI-7 | 10010 |
| GOOSE_Heartbeat | Battement de cœur GOOSE (IEC 61850) | BI | 0=Missing, 1=Active | 1s | sensor, status, goose, heartbeat | Status | BI-8 | 10011 |
| Data_Quality | Qualité des données mesurées | MSV | 0=Good, 1=Uncertain, 2=Bad | 5s-10s | sensor, status, quality, ct | Status | MSV-2 | 10012 |

## Points de Configuration

| Nom du Point | Description | Type | Valeurs | Accès | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|-------|---------------|-------------|---------|---------|
| CT_Ratio_Primary | Courant nominal primaire | AO | 1-10000 A | R/W | sp, ratio, primary, ct | Setpoint | AO-0 | 40002 |
| CT_Ratio_Secondary | Courant nominal secondaire | AO | 1A, 5A | R/W | sp, ratio, secondary, ct | Setpoint | AO-1 | 40003 |
| Overload_Threshold | Seuil d'alarme surcharge | AO | 50-200% | R/W | sp, alarm, overload, threshold, ct | Setpoint | AO-2 | 40004 |
| Temperature_Threshold | Seuil d'alarme température | AO | 50-100°C | R/W | sp, alarm, temp, threshold, ct | Setpoint | AO-3 | 40005 |
| Sampling_Rate | Fréquence d'échantillonnage | AO | 80-256 samples/cycle | R/W | sp, sample, rate, ct | Setpoint | AO-4 | 40006 |
| IP_Address | Adresse IP (pour TC Ethernet) | String | xxx.xxx.xxx.xxx | R/W | sp, network, ip, address, ct | Setpoint | CSV-0 | 40007-40010 |
| Modbus_Slave_Address | Adresse Modbus RTU | AO | 1-247 | R/W | sp, modbus, address, ct | Setpoint | AO-5 | 40011 |
| Baud_Rate | Vitesse de communication série | MSV | 0=9600, 1=19200, 2=38400, 3=57600, 4=115200 | R/W | sp, baud, rate, ct | Setpoint | MSV-3 | 40012 |
| Alarm_Delay | Délai avant déclenchement alarme | AO | 0-300 s | R/W | sp, alarm, delay, ct | Setpoint | AO-6 | 40013 |
| Calibration_Date | Date dernière calibration | String | ISO 8601 | R | sp, calibration, date, ct | Setpoint | CSV-1 | 40014-40017 |
| Calibration_Factor | Facteur de correction calibration | AO | 0.9-1.1 | R/W | sp, calibration, factor, ct | Setpoint | AO-7 | 40018 |
| Device_Serial_Number | Numéro de série du TC | String | Alphanumeric | R | sp, serial, number, ct | Setpoint | CSV-2 | 40019-40022 |
| Firmware_Version | Version du firmware | String | x.x.x | R | sp, firmware, version, ct | Setpoint | CSV-3 | 40023-40026 |

## Notes d'Implémentation

### Protocoles de Communication

#### Modbus RTU/TCP
- **Holding Registers (400001+)** : Configuration, setpoints (lecture/écriture)
- **Input Registers (300001+)** : Mesures analogiques (lecture seule)
- **Coils (000001+)** : Commandes binaires (lecture/écriture)
- **Discrete Inputs (100001+)** : États binaires (lecture seule)
- **Vitesses standard** : 9600, 19200, 38400, 57600, 115200 bps
- **Format** : 8N1 (8 bits données, pas de parité, 1 bit stop)

#### BACnet/IP
- **Object Types** : Analog Input (AI), Binary Input (BI), Analog Output (AO), Binary Output (BO), Multi-State Value (MSV), Accumulator (ACC), CharacterString Value (CSV)
- **Port standard** : UDP 47808
- **COV (Change of Value)** : Recommandé pour alarmes et états critiques
- **Priority Array** : Niveaux 1-16 pour commandes (niveau 8 = opérateur manuel)

#### IEC 61850
- **GOOSE (Generic Object-Oriented Substation Event)** : Échange rapide d'événements binaires et d'états (temps de réponse < 4 ms)
- **Sampled Values (SV) - IEC 61850-9-2** : Transmission numérique des échantillons de courant instantanés
  - **9-2LE (Light Edition)** : 80 échantillons/cycle (50/60 Hz)
  - **9-2 Full** : 256 échantillons/cycle pour protection haute performance
- **MMS (Manufacturing Message Specification)** : Lecture/écriture de données de configuration
- **Logical Nodes** : TCTR (Current Transformer), MMXU (Measurement), XCBR (Circuit Breaker)

### Fréquences d'Échantillonnage Recommandées

| Catégorie | Point | Fréquence | Justification |
|-----------|-------|-----------|---------------|
| **Critique** | Primary_Current_RMS | 1s | Protection et contrôle temps réel |
| **Critique** | Overload_Alarm | 1s | Sécurité - détection rapide surcharge |
| **Critique** | Secondary_Open_Circuit | 1s | Danger immédiat (surtension) |
| **Important** | CT_Temperature | 10s-30s | Surveillance thermique |
| **Important** | Saturation_Level | 5s | Précision de mesure |
| **Normal** | Load_Factor | 10s | Monitoring opérationnel |
| **Normal** | THD_Current | 60s | Qualité d'énergie |
| **Bas** | Insulation_Resistance | 24h | Diagnostic préventif |
| **Événementiel** | Communication_Status | COV | Changement d'état uniquement |

### Architecture Système

#### TC Intelligents Traditionnels
```
[TC avec électronique] → [RS-485 Modbus RTU] → [Passerelle Modbus/BACnet] → [BMS]
```

#### TC avec Bobines de Rogowski
```
[Bobine Rogowski] → [Intégrateur électronique] → [Ethernet Modbus TCP] → [BMS]
```

#### Substations Numériques (IEC 61850)
```
[TC conventionnel] → [Merging Unit] → [Sampled Values Ethernet] → [IED de protection]
                                    → [GOOSE Messages] → [BMS / SCADA]
```

### Considérations de Sécurité

#### Circuit Secondaire
- **DANGER** : Ne JAMAIS ouvrir le circuit secondaire d'un TC traditionnel sous charge (risque de surtension mortelle > 1000V)
- **Alarme critique** : `Secondary_Open_Circuit` doit déclencher une action immédiate
- Les TC avec électronique intégrée incluent souvent une protection automatique

#### Cyber-sécurité
- **IEC 61850** : Utiliser IEC 62351 pour authentification et chiffrement
- **Modbus TCP** : Implémenter firewall et VLANs dédiés (pas de sécurité native)
- **BACnet/IP** : BACnet Secure Connect (BSC) pour chiffrement TLS

#### Isolation Électrique
- Vérifier régulièrement `Insulation_Resistance` (>10 MΩ minimum)
- Alarme si < 1 MΩ (risque de défaut à la terre)

### Intégration BMS

#### Priorités d'Alarmes
1. **Critique (P1)** : Secondary_Open_Circuit, Overload_Alarm > 150%
2. **Haute (P2)** : Temperature_Alarm, Saturation_Alarm, Insulation_Fault
3. **Moyenne (P3)** : Communication_Status, Calibration_Status expired
4. **Basse (P4)** : Data_Quality uncertain, Power_Supply_Status low

#### Tendances Historiques
- Conserver `Primary_Current_RMS` : 1 an minimum (analyse de charge)
- Conserver `CT_Temperature` : 1 an (dégradation thermique)
- Conserver `Operating_Hours` : Vie entière du TC (maintenance)
- Alarmes : Historique complet (traçabilité)

#### Calculs Dérivés
- **Facteur de puissance** : Combiner avec transformateurs de tension (VT)
- **Énergie consommée** : Intégration de `Primary_Current_RMS` avec tension
- **Prédiction défaillance** : ML sur `CT_Temperature`, `Load_Factor`, `Insulation_Resistance`

### Fabricants et Modèles Référencés

| Fabricant | Modèle / Série | Protocoles | Caractéristiques |
|-----------|----------------|------------|------------------|
| **Banner Engineering** | Rogowski S15S | Modbus RTU (RS-485) | 50-6000 A, bobines 50/200 mm |
| **ABB** | AccuRange CBT-S | Modbus, IEC 61850 | Précision 0.2S, monitoring intégré |
| **Schneider Electric** | Rogowski TF series | Modbus RS-485 | IP67, -15°C à +60°C, avec DIRIS |
| **Siemens** | SIPROTEC 5 CT modules | IEC 61850 (GOOSE/SV) | Protection numérique, 80-256 samples/cycle |
| **Socomec** | DIRIS A/B avec TF CT | Modbus TCP/RTU | Power monitoring, THD, énergie |
| **Qualitrol** | 118ITM (pour transformateurs) | Modbus, BACnet | Température, ventilation, SCADA |
| **Verdigris** | Smart CT | LoRaWAN, MQTT | Sans fil, cloud, machine learning |
| **MultiTech** | LoRaWAN CT Gateway | LoRaWAN, MQTT, Modbus | Passerelle cloud AWS/Azure |

### Standards et Normes

- **IEC 61869-1/2** : Transformateurs de courant (spécifications générales)
- **IEC 61850-9-2** : Sampled Values pour substations numériques
- **IEC 61850-8-1** : GOOSE messaging
- **IEC 62351** : Cybersécurité pour protocoles de substations
- **IEEE C57.13** : Standard pour instrument transformers (Amérique du Nord)
- **ANSI C12.20** : Accuracy classes pour comptage d'énergie
- **Haystack 4.x** : Tags sémantiques pour BMS (project-haystack.org)
- **Brick Schema 1.2+** : Ontologie pour bâtiments intelligents (brickschema.org)

## Sources

1. https://www.bannerengineering.com/us/en/company/new-products/rogowski-coil-current-sensors.html
2. https://www.accuenergy.com/support/reference-directory/wireless-vs-wired-current-transformers-ct/
3. https://multitech.com/current-transformer/
4. https://www.socomec.us/en-us/p/tf-flexible-sensors
5. https://media.distributordatasolutions.com/schneider2/2019q4/2880a0b1c0bebdf1245d69242c3bac9bf7487d34.pdf
6. https://www.qualitrolcorp.com/products/transformer-monitors/intelligent-transformer-monitors/qualitrol-118-intelligent-transformer-monitor/
7. https://www.siemens.com/us/en/products/energy/energy-automation-and-smart-grid/protection-relays-and-control/siprotec-5.html
8. https://en.wikipedia.org/wiki/IEC_61850
9. https://conprove.com/en/power-system-communication-testing/sampled-value-iec-61850/
10. https://scadaprotocols.com/iec-61850-goose-vs-sampled-values/
11. https://brickschema.org/ontology/1.2/classes/Current_Output_Sensor/
12. https://project-haystack.org/forum/topic/446
13. https://www.omicronenergy.com/en/products/ct-analyzer/
14. https://www.electronics-tutorials.ws/transformer/current-transformer.html
15. https://www.dynamicratings.com/transformer-monitoring-beyond-the-nameplate-red-line/

---

**Document Version** : 1.0
**Dernière mise à jour** : 2025-01-18
**Auteur** : Documentation technique BMS
**Révision** : Basée sur normes IEC 61850, Haystack 4.x, Brick Schema 1.2+
