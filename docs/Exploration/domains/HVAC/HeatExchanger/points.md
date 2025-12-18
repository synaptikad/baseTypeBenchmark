# Points d'Échangeur de Chaleur (Heat Exchanger)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 4
- **Total points état** : 4

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| primary_entering_temp | primary entering water temp sensor | °C | 5-90 | 1min | Température entrée circuit primaire |
| primary_leaving_temp | primary leaving water temp sensor | °C | 10-80 | 1min | Température sortie circuit primaire |
| secondary_entering_temp | secondary entering water temp sensor | °C | 10-70 | 1min | Température entrée circuit secondaire |
| secondary_leaving_temp | secondary leaving water temp sensor | °C | 15-85 | 1min | Température sortie circuit secondaire |
| primary_flow | primary water flow sensor | m³/h | 0-500 | 1min | Débit circuit primaire |
| secondary_flow | secondary water flow sensor | m³/h | 0-500 | 1min | Débit circuit secondaire |
| primary_dp | primary differential pressure sensor | kPa | 10-100 | 5min | Pression différentielle primaire |
| secondary_dp | secondary differential pressure sensor | kPa | 10-100 | 5min | Pression différentielle secondaire |
| heat_power | heat power sensor | kW | 0-5000 | 5min | Puissance thermique échangée (calculée) |
| efficiency | heat exchanger efficiency sensor | % | 50-95 | 5min | Efficacité de l'échangeur (calculée) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| primary_valve_cmd | primary valve cmd | % | 0-100 | Actionneur | Position vanne primaire |
| secondary_valve_cmd | secondary valve cmd | % | 0-100 | Actionneur | Position vanne secondaire |
| secondary_temp_sp | secondary leaving temp sp | °C | 20-80 | Consigne | Consigne température départ secondaire |
| heat_power_sp | heat power sp | kW | 0-5000 | Consigne | Consigne puissance thermique |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| primary_flow_ok | primary flow ok status | Boolean | true/false | Débit primaire confirmé |
| secondary_flow_ok | secondary flow ok status | Boolean | true/false | Débit secondaire confirmé |
| fouling_alarm | fouling alarm | Boolean | true/false | Alarme encrassement (DP élevé) |
| freeze_protect_active | freeze protect alarm | Boolean | true/false | Protection antigel active |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| primary_entering_temp | AI:1 | 40001 (HR) | 1/1/1 |
| primary_leaving_temp | AI:2 | 40002 (HR) | 1/1/2 |
| secondary_entering_temp | AI:3 | 40003 (HR) | 1/1/3 |
| secondary_leaving_temp | AI:4 | 40004 (HR) | 1/1/4 |
| primary_flow | AI:5 | 40005 (HR) | 1/1/5 |
| secondary_flow | AI:6 | 40006 (HR) | 1/1/6 |
| primary_dp | AI:7 | 40007 (HR) | 1/1/7 |
| secondary_dp | AI:8 | 40008 (HR) | 1/1/8 |
| heat_power | AV:1 | 40101 (HR) | 1/1/9 |
| efficiency | AV:2 | 40102 (HR) | 1/1/10 |
| primary_valve_cmd | AO:1 | 40201 (HR) | 1/2/1 |
| secondary_valve_cmd | AO:2 | 40202 (HR) | 1/2/2 |
| secondary_temp_sp | AV:3 | 40103 (HR) | 1/2/3 |
| heat_power_sp | AV:4 | 40104 (HR) | 1/2/4 |
| primary_flow_ok | BI:1 | 10001 (DI) | 1/3/1 |
| secondary_flow_ok | BI:2 | 10002 (DI) | 1/3/2 |
| fouling_alarm | BI:3 | 10003 (DI) | 1/3/3 |
| freeze_protect_active | BI:4 | 10004 (DI) | 1/3/4 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Calculs de Performance

| Paramètre | Formule | Notes |
|-----------|---------|-------|
| Puissance échangée | Q = m × Cp × ΔT | m = débit massique, Cp = 4.18 kJ/kg·K (eau) |
| Efficacité | ε = Q_réel / Q_max | Q_max basé sur différence T max possible |
| LMTD | ΔT_lm = (ΔT1 - ΔT2) / ln(ΔT1/ΔT2) | Log Mean Temperature Difference |

## Seuils de Maintenance

| Indicateur | Seuil Avertissement | Seuil Alarme | Action |
|------------|---------------------|--------------|--------|
| Perte de charge | +30% vs neuf | +50% vs neuf | Nettoyage |
| Efficacité | -10% vs design | -20% vs design | Inspection |
| Delta T secondaire | < 80% consigne | < 60% consigne | Diagnostic |

## Sources
- ASHRAE Handbook - Heat Exchangers Fundamentals
- Project Haystack - Heat Exchanger Tags
- Brick Schema - Heat_Exchanger Class
- Alfa Laval / Danfoss - Plate Heat Exchanger Selection Guides
