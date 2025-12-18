# Points - Capacitor Bank

## Résumé
- **Points de mesure** : 12
- **Points de commande** : 5
- **Points d'état** : 8
- **Total** : 25

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| CONDO-PF | Power Factor | 1 | cos φ | 0.0-1.0 | 5s | Facteur de puissance mesuré en temps réel |
| CONDO-KVAR | Reactive Power | 1 | kVAR | -500 à 500 | 5s | Puissance réactive totale (capacitive/inductive) |
| CONDO-V-L1 | Voltage Phase L1 | 1 | V | 0-500 | 5s | Tension phase L1 |
| CONDO-V-L2 | Voltage Phase L2 | 1 | V | 0-500 | 5s | Tension phase L2 |
| CONDO-V-L3 | Voltage Phase L3 | 1 | V | 0-500 | 5s | Tension phase L3 |
| CONDO-I-L1 | Current Phase L1 | 1 | A | 0-1000 | 5s | Courant phase L1 |
| CONDO-I-L2 | Current Phase L2 | 1 | A | 0-1000 | 5s | Courant phase L2 |
| CONDO-I-L3 | Current Phase L3 | 1 | A | 0-1000 | 5s | Courant phase L3 |
| CONDO-KW | Active Power | 1 | kW | 0-1000 | 5s | Puissance active totale |
| CONDO-KWH | Energy Consumed | 1 | kWh | 0-999999 | 15min | Énergie totale consommée (cumulative) |
| CONDO-TEMP | Temperature | 1 | °C | -20 à 100 | 60s | Température interne de l'armoire |
| CONDO-FREQ | Frequency | 1 | Hz | 45-65 | 5s | Fréquence réseau |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| CONDO-AUTO | Auto Mode Enable | 1 | - | 0/1 | Binary | Activation du mode automatique (régulation varmétrique) |
| CONDO-MAN | Manual Mode Enable | 1 | - | 0/1 | Binary | Activation du mode manuel |
| CONDO-PF-SP | Power Factor Setpoint | 1 | cos φ | 0.90-1.0 | Analog | Consigne de facteur de puissance cible |
| CONDO-STEP-CMD | Step Command | 1 | - | 0-12 | Integer | Commande nombre de gradins actifs (mode manuel) |
| CONDO-RESET | Reset Alarms | 1 | - | 0/1 | Binary | Réinitialisation des alarmes |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| CONDO-STATUS | Operating Status | Enum | OFF/MANUAL/AUTO/FAULT | 5s | État de fonctionnement général |
| CONDO-STEP-1 | Step 1 Status | Binary | 0=OFF/1=ON | 5s | État gradin 1 (contacteur ou thyristor) |
| CONDO-STEP-2 | Step 2 Status | Binary | 0=OFF/1=ON | 5s | État gradin 2 |
| CONDO-STEP-3 | Step 3 Status | Binary | 0=OFF/1=ON | 5s | État gradin 3 |
| CONDO-STEP-4 | Step 4 Status | Binary | 0=OFF/1=ON | 5s | État gradin 4 |
| CONDO-ACTIVE-STEPS | Active Steps Count | Integer | 0-12 | 5s | Nombre de gradins actifs actuellement |
| CONDO-COMM | Communication Status | Binary | 0=FAULT/1=OK | 60s | État communication Modbus/BACnet |
| CONDO-READY | Ready Status | Binary | 0=NOT READY/1=READY | 5s | Disponibilité pour compensation |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| CONDO-ALM-PF-LOW | Low Power Factor | WARNING | PF < 0.85 | Facteur de puissance insuffisant malgré compensation |
| CONDO-ALM-OVERVOLT | Overvoltage | CRITICAL | V > 110% Vn | Surtension détectée sur au moins une phase |
| CONDO-ALM-OVERCURR | Overcurrent | CRITICAL | I > In | Surintensité sur condensateurs |
| CONDO-ALM-TEMP | High Temperature | WARNING | T > 60°C | Température excessive dans armoire |
| CONDO-ALM-STEP-FAIL | Step Failure | WARNING | Gradin ne commute pas | Défaut de commutation d'un gradin (contacteur/thyristor) |
| CONDO-ALM-FUSE | Fuse Blown | CRITICAL | Fusible grillé | Fusible de protection condensateur grillé |
| CONDO-ALM-HARM | Harmonic Overload | WARNING | THD > 8% | Harmoniques excessifs (risque résonance) |
| CONDO-ALM-COMM | Communication Fault | WARNING | Perte liaison | Perte de communication Modbus/BACnet |

## Sources
- [Troubleshooting Power Factor Correction Capacitors - Fluke](https://www.fluke.com/en-us/learn/blog/power-quality/troubleshooting-power-factor-correction-capacitors)
- [Power Factor Correction - Powerside](https://powerside.com/applications/power-factor-correction/)
- [Capacitor Bank Panel - EEP](https://electrical-engineering-portal.com/capacitor-bank-panel-power-factor-correction-calculation-schematics)
- [BACnet Power & Energy Meter - Accuenergy](https://www.accuenergy.com/products/acuvim-iibn-bacnet-power-energy-meter/)
- [BACnet Meter Integration - SATEC](https://www.satec-global.com/bacnet-meter-integration-smarter-energy-management/)
