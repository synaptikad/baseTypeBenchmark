# Points - Circuit Breaker

## Résumé
- **Points de mesure** : 15
- **Points de commande** : 3
- **Points d'état** : 7
- **Total** : 25

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| CB-I-L1 | Current Phase L1 | 1 | A | 0-6300 | 1s | Courant phase L1 (temps réel) |
| CB-I-L2 | Current Phase L2 | 1 | A | 0-6300 | 1s | Courant phase L2 (temps réel) |
| CB-I-L3 | Current Phase L3 | 1 | A | 0-6300 | 1s | Courant phase L3 (temps réel) |
| CB-V-L1-N | Voltage L1-N | 1 | V | 0-500 | 5s | Tension phase-neutre L1 |
| CB-V-L2-N | Voltage L2-N | 1 | V | 0-500 | 5s | Tension phase-neutre L2 |
| CB-V-L3-N | Voltage L3-N | 1 | V | 0-500 | 5s | Tension phase-neutre L3 |
| CB-KW | Active Power | 1 | kW | 0-10000 | 5s | Puissance active totale triphasée |
| CB-KWH | Energy Consumed | 1 | kWh | 0-999999 | 15min | Énergie active cumulée |
| CB-PF | Power Factor | 1 | cos φ | -1.0 à 1.0 | 5s | Facteur de puissance triphasé |
| CB-FREQ | Frequency | 1 | Hz | 45-65 | 5s | Fréquence réseau |
| CB-IMAX | Peak Current | 1 | A | 0-6300 | On event | Courant de crête (max enregistré) |
| CB-TEMP | Temperature | 1 | °C | -20 à 150 | 60s | Température des connexions/contacts |
| CB-TRIP-COUNT | Trip Counter | 1 | - | 0-99999 | On event | Nombre de déclenchements cumulés |
| CB-OP-COUNT | Operation Counter | 1 | - | 0-999999 | On event | Nombre de manoeuvres cumulées (O/C) |
| CB-REMAIN-LIFE | Remaining Life | 1 | % | 0-100 | Daily | Durée de vie résiduelle estimée |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| CB-CLOSE | Close Command | 1 | - | 0/1 | Binary | Commande de fermeture (ON) à distance |
| CB-OPEN | Open Command | 1 | - | 0/1 | Binary | Commande d'ouverture (OFF) à distance |
| CB-RESET | Reset Alarm | 1 | - | 0/1 | Binary | Réinitialisation des alarmes et compteurs reset |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| CB-POSITION | Breaker Position | Binary | 0=OPEN/1=CLOSED | 1s | Position du disjoncteur (état contacts) |
| CB-READY | Ready Status | Binary | 0=NOT READY/1=READY | 5s | Disjoncteur armé et prêt |
| CB-TRIP-CAUSE | Trip Cause | Enum | NONE/OVERLOAD/SHORT/GROUND/MANUAL/REMOTE | On event | Cause du dernier déclenchement |
| CB-FAULT | Fault Status | Binary | 0=OK/1=FAULT | 1s | Présence d'un défaut |
| CB-ALARM | Alarm Status | Binary | 0=OK/1=ALARM | 1s | Présence d'une alarme (prédéclenchement) |
| CB-COMM | Communication Status | Binary | 0=FAULT/1=OK | 60s | État communication Modbus/BACnet |
| CB-LOCAL-REMOTE | Control Mode | Enum | LOCAL/REMOTE | 5s | Mode de commande (local/distant) |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| CB-ALM-OVERLOAD | Overload Warning | WARNING | I > 80% In | Préalarme surcharge (80-100% In) |
| CB-ALM-TRIP-OVERLOAD | Overload Trip | CRITICAL | I > 100% In | Déclenchement surcharge thermique |
| CB-ALM-TRIP-SHORT | Short Circuit Trip | CRITICAL | I >> In | Déclenchement court-circuit instantané |
| CB-ALM-TRIP-GROUND | Ground Fault Trip | CRITICAL | Défaut terre détecté | Déclenchement défaut à la terre |
| CB-ALM-TEMP-HIGH | High Temperature | WARNING | T > 80°C | Température excessive connexions |
| CB-ALM-PHASE-IMBAL | Phase Imbalance | WARNING | ΔI > 20% | Déséquilibre de courant entre phases |
| CB-ALM-UNDERVOLT | Undervoltage | WARNING | V < 85% Vn | Sous-tension réseau |
| CB-ALM-OVERVOLT | Overvoltage | WARNING | V > 110% Vn | Surtension réseau |
| CB-ALM-MAINT | Maintenance Required | WARNING | Compteur seuil | Maintenance préventive requise (cycles) |
| CB-ALM-COMM | Communication Fault | WARNING | Perte liaison | Perte communication BACnet/Modbus |

## Sources
- [Eaton Power Xpert Branch Circuit Monitor](https://www.eaton.com/us/en-us/catalog/low-voltage-power-distribution-controls-systems/power-xpert-branch-circuit-monitor.html)
- [BACnet Object List for PXBCM - Eaton](https://www.eaton.com/content/dam/eaton/products/low-voltage-power-distribution-controls-systems/power-energy-meters/power-xpert-branch-circuit-monitor/bacnet-object-list-for-pxbcm-ib150029en.pdf)
- [ABB ReliaGear Lighting Panelboards with Branch Circuit Monitoring](https://electrification.us.abb.com/products/panelboards/reliagear-lighting-panels-branch-circuit-monitoring)
- [Eaton AbleEdge Smart Breakers](https://www.eaton.com/us/en-us/catalog/electrical-circuit-protection/energy-management-circuit-breaker.html)
- [Packet Power Branch Circuit Monitoring](https://www.packetpower.com/panel-board)
