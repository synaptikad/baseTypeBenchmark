# Points - Protection Relay

## Résumé
- **Points de mesure** : 20
- **Points de commande** : 5
- **Points d'état** : 10
- **Total** : 35

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| RELAY-I-L1 | Current L1 | 1 | A | 0-10000 | 1s | Courant phase L1 (via TC) |
| RELAY-I-L2 | Current L2 | 1 | A | 0-10000 | 1s | Courant phase L2 (via TC) |
| RELAY-I-L3 | Current L3 | 1 | A | 0-10000 | 1s | Courant phase L3 (via TC) |
| RELAY-I-N | Current Neutral | 1 | A | 0-10000 | 1s | Courant neutre (défaut terre) |
| RELAY-V-L1-N | Voltage L1-N | 1 | V | 0-50000 | 1s | Tension phase-neutre L1 (via TT) |
| RELAY-V-L2-N | Voltage L2-N | 1 | V | 0-50000 | 1s | Tension phase-neutre L2 (via TT) |
| RELAY-V-L3-N | Voltage L3-N | 1 | V | 0-50000 | 1s | Tension phase-neutre L3 (via TT) |
| RELAY-P | Active Power | 1 | MW | -100 à 100 | 5s | Puissance active (directionnelle) |
| RELAY-Q | Reactive Power | 1 | MVAR | -100 à 100 | 5s | Puissance réactive (directionnelle) |
| RELAY-FREQ | Frequency | 1 | Hz | 45-65 | 1s | Fréquence réseau |
| RELAY-PF | Power Factor | 1 | cos φ | -1.0 à 1.0 | 5s | Facteur de puissance |
| RELAY-I-DIFF | Differential Current | 1 | A | 0-10000 | 1s | Courant différentiel (protection 87) |
| RELAY-I-SEQ-NEG | Negative Sequence Current | 1 | A | 0-1000 | 5s | Courant inverse (déséquilibre) |
| RELAY-V-SEQ-NEG | Negative Sequence Voltage | 1 | V | 0-5000 | 5s | Tension inverse (déséquilibre) |
| RELAY-TRIP-TIME | Last Trip Time | 1 | ms | 0-10000 | On event | Temps de déclenchement du dernier défaut |
| RELAY-FAULT-I | Fault Current | 1 | A | 0-50000 | On event | Courant de défaut mesuré |
| RELAY-FAULT-DIST | Fault Distance | 1 | km | 0-100 | On event | Distance estimée du défaut (ligne) |
| RELAY-EVENT-COUNT | Event Counter | 1 | - | 0-9999 | On event | Nombre d'événements enregistrés |
| RELAY-TRIP-COUNT | Trip Counter | 1 | - | 0-9999 | On event | Nombre de déclenchements |
| RELAY-TEMP | Temperature | 1 | °C | -40 à 85 | 60s | Température interne relais |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| RELAY-TRIP-CMD | Trip Command | 1 | - | 0/1 | Binary | Commande de déclenchement manuel |
| RELAY-CLOSE-CMD | Close Command | 1 | - | 0/1 | Binary | Commande de fermeture (si applicable) |
| RELAY-RESET | Reset Relay | 1 | - | 0/1 | Binary | Réinitialisation relais après défaut |
| RELAY-BLOCK | Block Protection | 1 | - | 0/1 | Binary | Blocage temporaire des protections |
| RELAY-TEST | Test Mode | 1 | - | 0/1 | Binary | Activation mode test (sans déclenchement) |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| RELAY-PROT-50-51 | Overcurrent Protection | Binary | 0=INACTIVE/1=ACTIVE | 1s | Protection surintensité (ANSI 50/51) |
| RELAY-PROT-27 | Undervoltage Protection | Binary | 0=INACTIVE/1=ACTIVE | 1s | Protection sous-tension (ANSI 27) |
| RELAY-PROT-59 | Overvoltage Protection | Binary | 0=INACTIVE/1=ACTIVE | 1s | Protection surtension (ANSI 59) |
| RELAY-PROT-87 | Differential Protection | Binary | 0=INACTIVE/1=ACTIVE | 1s | Protection différentielle (ANSI 87) |
| RELAY-PROT-67 | Directional Protection | Binary | 0=INACTIVE/1=ACTIVE | 1s | Protection directionnelle (ANSI 67) |
| RELAY-CB-STATUS | Circuit Breaker Status | Binary | 0=OPEN/1=CLOSED | 1s | État du disjoncteur associé |
| RELAY-TRIP | Trip Status | Binary | 0=OK/1=TRIPPED | 1s | Relais en état déclenché |
| RELAY-ALARM | Alarm Status | Binary | 0=OK/1=ALARM | 1s | Alarme active |
| RELAY-COMM | Communication Status | Binary | 0=FAULT/1=OK | 60s | État communication IEC 61850/Modbus |
| RELAY-HEALTHY | Relay Health | Binary | 0=FAULT/1=OK | 5s | Auto-diagnostic relais |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| RELAY-ALM-TRIP-50 | Instantaneous Overcurrent | CRITICAL | I >>> | Déclenchement surintensité instantanée (ANSI 50) |
| RELAY-ALM-TRIP-51 | Time Overcurrent | CRITICAL | I >> | Déclenchement surintensité temporisée (ANSI 51) |
| RELAY-ALM-TRIP-27 | Undervoltage Trip | CRITICAL | V < seuil | Déclenchement sous-tension (ANSI 27) |
| RELAY-ALM-TRIP-59 | Overvoltage Trip | CRITICAL | V > seuil | Déclenchement surtension (ANSI 59) |
| RELAY-ALM-TRIP-87 | Differential Trip | CRITICAL | ΔI > seuil | Déclenchement différentiel (ANSI 87) |
| RELAY-ALM-TRIP-67 | Directional Trip | CRITICAL | Défaut directionnel | Déclenchement protection directionnelle |
| RELAY-ALM-GROUND | Ground Fault | CRITICAL | In > seuil | Défaut à la terre détecté |
| RELAY-ALM-PHASE-IMBAL | Phase Imbalance | WARNING | I2 > 20% I1 | Déséquilibre de phases excessif |
| RELAY-ALM-FREQ | Frequency Deviation | WARNING | f hors limites | Fréquence hors tolérance (81 O/U) |
| RELAY-ALM-CT | CT Fault | WARNING | Défaut TC | Défaut transformateur de courant |
| RELAY-ALM-VT | VT Fault | WARNING | Défaut TT | Défaut transformateur de tension |
| RELAY-ALM-SELF-TEST | Self-Test Fault | CRITICAL | Auto-test échoué | Défaut auto-diagnostic relais |
| RELAY-ALM-COMM | Communication Fault | WARNING | Perte liaison | Perte communication IEC 61850/Modbus |
| RELAY-ALM-BATTERY | Battery Low | WARNING | Batterie faible | Batterie sauvegarde faible |

## Sources
- [IEC 61850 Practical Application - EEP](https://electrical-engineering-portal.com/download-center/books-and-guides/relays/iec-61850-practical)
- [Eaton E-Series Relays with IEC 61850 GOOSE](https://www.eaton.com/us/en-us/products/electrical-circuit-protection/protective-relays-and-predictive-devices/e-series-relays-iec-61850-goose-.html)
- [OMICRON Protection Systems with IEC 61850](https://www.omicronenergy.com/en/application/iec-61850-and-digital-substations/protection-systems-with-iec-61850/)
- [Understanding IEC 61850 Protocol - SMCint](https://smcint.com/electrical-testing/understanding-the-iec-61850-protocol-a-new-era-in-electrical-protection-and-control/)
- [IEC 61850 Communication Protocol with Protection and Control](https://www.researchgate.net/publication/341025745_IEC_61850_Communication_Protocol_with_the_Protection_and_Control_Numerical_Relays_for_Optimum_Substation_Automation_System)
