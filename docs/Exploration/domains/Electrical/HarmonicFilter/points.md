# Points - Harmonic Filter

## Résumé
- **Points de mesure** : 16
- **Points de commande** : 4
- **Points d'état** : 6
- **Total** : 26

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| AHF-THD-I-IN | THD Current Input | 1 | % | 0-100 | 5s | Distorsion harmonique courant en entrée (avant filtrage) |
| AHF-THD-I-OUT | THD Current Output | 1 | % | 0-100 | 5s | Distorsion harmonique courant en sortie (après filtrage) |
| AHF-THD-V | THD Voltage | 1 | % | 0-20 | 5s | Distorsion harmonique tension |
| AHF-I-COMP-L1 | Compensation Current L1 | 1 | A | 0-600 | 1s | Courant de compensation injecté phase L1 |
| AHF-I-COMP-L2 | Compensation Current L2 | 1 | A | 0-600 | 1s | Courant de compensation injecté phase L2 |
| AHF-I-COMP-L3 | Compensation Current L3 | 1 | A | 0-600 | 1s | Courant de compensation injecté phase L3 |
| AHF-I-LOAD-L1 | Load Current L1 | 1 | A | 0-6300 | 5s | Courant de charge phase L1 |
| AHF-I-LOAD-L2 | Load Current L2 | 1 | A | 0-6300 | 5s | Courant de charge phase L2 |
| AHF-I-LOAD-L3 | Load Current L3 | 1 | A | 0-6300 | 5s | Courant de charge phase L3 |
| AHF-HARM-H3 | Harmonic H3 | 1 | % | 0-50 | 15s | Harmonique rang 3 (180 Hz) |
| AHF-HARM-H5 | Harmonic H5 | 1 | % | 0-50 | 15s | Harmonique rang 5 (250 Hz) |
| AHF-HARM-H7 | Harmonic H7 | 1 | % | 0-50 | 15s | Harmonique rang 7 (350 Hz) |
| AHF-CAPACITY | Filter Capacity Used | 1 | % | 0-100 | 5s | Capacité de filtrage utilisée |
| AHF-TEMP | Temperature | 1 | °C | -20 à 100 | 60s | Température interne filtre actif |
| AHF-DC-VOLTAGE | DC Bus Voltage | 1 | V | 0-800 | 5s | Tension bus DC interne |
| AHF-EFFICIENCY | Filtering Efficiency | 1 | % | 0-100 | 15s | Efficacité de filtrage (réduction THD) |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| AHF-ENABLE | Enable Filter | 1 | - | 0/1 | Binary | Activation du filtre actif |
| AHF-AUTO | Auto Mode | 1 | - | 0/1 | Binary | Mode automatique (ajustement dynamique) |
| AHF-THD-TARGET | THD Target Setpoint | 1 | % | 1-10 | Analog | Consigne THD cible après filtrage |
| AHF-RESET | Reset Alarms | 1 | - | 0/1 | Binary | Réinitialisation alarmes |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| AHF-STATUS | Operating Status | Enum | OFF/STANDBY/ACTIVE/FAULT | 5s | État de fonctionnement |
| AHF-READY | Ready Status | Binary | 0=NOT READY/1=READY | 5s | Filtre prêt à compenser |
| AHF-FAULT | Fault Status | Binary | 0=OK/1=FAULT | 1s | Défaut détecté |
| AHF-ALARM | Alarm Status | Binary | 0=OK/1=ALARM | 1s | Alarme active |
| AHF-COMM | Communication Status | Binary | 0=FAULT/1=OK | 60s | État communication Modbus/BACnet |
| AHF-MODE | Operating Mode | Enum | MANUAL/AUTO/MAINTENANCE | 5s | Mode de fonctionnement actuel |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| AHF-ALM-THD-HIGH | High THD Input | WARNING | THD-IN > 20% | Harmoniques entrée excessifs |
| AHF-ALM-TARGET-FAIL | Target Not Met | WARNING | THD-OUT > Consigne | Objectif de filtrage non atteint |
| AHF-ALM-OVERLOAD | Filter Overload | CRITICAL | Capacité > 95% | Surcharge du filtre actif |
| AHF-ALM-TEMP | High Temperature | WARNING | T > 70°C | Température excessive |
| AHF-ALM-DC-BUS | DC Bus Fault | CRITICAL | VDC hors plage | Tension bus DC anormale |
| AHF-ALM-IGBT | IGBT Fault | CRITICAL | Défaut module IGBT | Défaut module de puissance IGBT |
| AHF-ALM-RESONANCE | Resonance Detected | WARNING | Résonance détectée | Risque de résonance harmonique |
| AHF-ALM-FAN | Fan Fault | WARNING | Ventilateur défaillant | Défaut ventilation |
| AHF-ALM-CT | CT Fault | CRITICAL | Erreur capteur | Défaut transformateur de courant (CT) |
| AHF-ALM-COMM | Communication Fault | WARNING | Perte liaison | Perte communication BACnet/Modbus |

## Sources
- [TCI HGA Active Harmonic Filter](https://www.transcoil.com/products/hga-5-active-harmonic-filter/)
- [Active Harmonic Filter Guide - Fuji Electric](https://www.india.fujielectric.com/resources/technical-guide/active-harmonic-filter)
- [HPS TruWave Active Harmonic Filter](https://americas.hammondpowersolutions.com/products/filters/active-harmonic-filter)
- [Powerside Active Harmonic Filter](https://powerside.com/active-harmonic-filter/)
- [NAAC Active Harmonic Filter](https://naacenergy.com/active-harmonic-filter/)
- [Harmonic Filters - EEP](https://electrical-engineering-portal.com/harmonic-filters)
