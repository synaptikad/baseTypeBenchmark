# Points - Electrical Panel

## Résumé
- **Points de mesure** : 18
- **Points de commande** : 2
- **Points d'état** : 6
- **Total** : 26

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| DIV-V-L1-N | Voltage L1-N | 1 | V | 0-500 | 5s | Tension phase-neutre L1 (incomer) |
| DIV-V-L2-N | Voltage L2-N | 1 | V | 0-500 | 5s | Tension phase-neutre L2 (incomer) |
| DIV-V-L3-N | Voltage L3-N | 1 | V | 0-500 | 5s | Tension phase-neutre L3 (incomer) |
| DIV-I-L1 | Current L1 | 1 | A | 0-1000 | 5s | Courant total phase L1 (incomer) |
| DIV-I-L2 | Current L2 | 1 | A | 0-1000 | 5s | Courant total phase L2 (incomer) |
| DIV-I-L3 | Current L3 | 1 | A | 0-1000 | 5s | Courant total phase L3 (incomer) |
| DIV-KW | Active Power | 1 | kW | 0-5000 | 5s | Puissance active totale triphasée |
| DIV-KVAR | Reactive Power | 1 | kVAR | -5000 à 5000 | 5s | Puissance réactive totale |
| DIV-KVA | Apparent Power | 1 | kVA | 0-5000 | 5s | Puissance apparente totale |
| DIV-PF | Power Factor | 1 | cos φ | -1.0 à 1.0 | 5s | Facteur de puissance triphasé |
| DIV-FREQ | Frequency | 1 | Hz | 45-65 | 5s | Fréquence réseau |
| DIV-KWH | Energy Active | 1 | kWh | 0-999999 | 15min | Énergie active cumulée (consommation) |
| DIV-KVARH | Energy Reactive | 1 | kVARh | 0-999999 | 15min | Énergie réactive cumulée |
| DIV-THD-V | THD Voltage | 1 | % | 0-20 | 60s | Distorsion harmonique tension totale |
| DIV-THD-I | THD Current | 1 | % | 0-50 | 60s | Distorsion harmonique courant totale |
| DIV-DEMAND | Power Demand | 1 | kW | 0-5000 | 15min | Puissance de pointe (sliding window) |
| DIV-TEMP | Temperature | 1 | °C | 0-100 | 60s | Température interne tableau |
| DIV-HUMIDITY | Humidity | 1 | %RH | 0-100 | 300s | Humidité relative interne |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| DIV-RESET-DEMAND | Reset Demand | 1 | - | 0/1 | Binary | Réinitialisation compteur de pointe |
| DIV-RESET-ENERGY | Reset Energy | 1 | - | 0/1 | Binary | Réinitialisation compteurs d'énergie |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| DIV-INCOMER | Incomer Status | Binary | 0=OFF/1=ON | 5s | État disjoncteur général d'arrivée |
| DIV-FAULT | Fault Status | Binary | 0=OK/1=FAULT | 5s | Défaut général tableau |
| DIV-ALARM | Alarm Status | Binary | 0=OK/1=ALARM | 5s | Alarme active |
| DIV-COMM | Communication Status | Binary | 0=FAULT/1=OK | 60s | État communication Modbus/BACnet |
| DIV-DOOR | Door Status | Binary | 0=CLOSED/1=OPEN | 1s | État porte du tableau (contact) |
| DIV-BREAKER-COUNT | Active Breakers | Integer | 0-96 | 60s | Nombre de disjoncteurs en service |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| DIV-ALM-UNDERVOLT | Undervoltage | WARNING | V < 85% Vn | Sous-tension sur au moins une phase |
| DIV-ALM-OVERVOLT | Overvoltage | WARNING | V > 110% Vn | Surtension sur au moins une phase |
| DIV-ALM-OVERLOAD | Overload | WARNING | I > 80% In | Surcharge incomer (80-100%) |
| DIV-ALM-PHASE-IMBAL | Phase Imbalance | WARNING | ΔI > 20% ou ΔV > 2% | Déséquilibre de phases excessif |
| DIV-ALM-FREQ | Frequency Deviation | WARNING | f < 49.5 ou f > 50.5 Hz | Fréquence hors tolérance |
| DIV-ALM-PF-LOW | Low Power Factor | WARNING | PF < 0.85 | Facteur de puissance faible |
| DIV-ALM-THD-HIGH | High THD | WARNING | THD-I > 15% | Harmoniques excessifs |
| DIV-ALM-TEMP | High Temperature | WARNING | T > 50°C | Température excessive dans tableau |
| DIV-ALM-HUMIDITY | High Humidity | WARNING | RH > 80% | Humidité excessive (risque condensation) |
| DIV-ALM-DOOR | Door Open | INFO | Porte ouverte | Porte tableau ouverte (sécurité) |
| DIV-ALM-DEMAND | Demand Exceeded | WARNING | Demande > seuil | Dépassement de puissance souscrite |
| DIV-ALM-COMM | Communication Fault | WARNING | Perte liaison | Perte communication BACnet/Modbus |

## Sources
- [Eaton Pow-R-Line 4B Multipoint Metering Panelboards](https://www.eaton.com/us/en-us/catalog/low-voltage-power-distribution-controls-systems/pow-r-line-4B-power-xpert-multipoint-metering-distribution-panelboards.html)
- [Accuenergy Acuvim IIBN BACnet Power & Energy Meter](https://www.accuenergy.com/products/acuvim-iibn-bacnet-power-energy-meter/)
- [Eaton IQ 35M Energy Meter](https://www.eaton.com/us/en-us/catalog/low-voltage-power-distribution-controls-systems/iq-35m.html)
- [GE Multilin EPM 6010 Building Automation Power Meter](https://www.gevernova.com/grid-solutions/automation/protection-control-metering/metering/epm-6010)
- [Setra Power Meter](https://www.shop.setra.com/products/setra-power-meter)
- [Packet Power Branch Circuit Monitoring](https://www.packetpower.com/panel-board)
