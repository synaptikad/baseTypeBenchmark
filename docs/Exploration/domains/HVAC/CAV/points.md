# Points de Terminal à Débit Constant (CAV)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 4
- **Total points état** : 4

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_temp | zone air temp sensor | °C | 18-28 | 1min | Température de la zone |
| discharge_temp | discharge air temp sensor | °C | 14-35 | 1min | Température air soufflé |
| supply_flow | supply air flow sensor | m³/h | 100-5000 | 1min | Débit d'air soufflé |
| supply_dp | inlet differential pressure sensor | Pa | 50-300 | 1min | Pression différentielle entrée |
| reheat_valve_position | reheat valve position sensor | % | 0-100 | 1min | Position vanne réchauffage |
| reheat_coil_temp | reheat coil leaving temp sensor | °C | 20-40 | 1min | Température après réchauffage |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_sp | zone air temp sp | °C | 18-26 | Consigne | Consigne température zone |
| reheat_valve_cmd | reheat valve cmd | % | 0-100 | Actionneur | Commande vanne réchauffage |
| design_flow_sp | design air flow sp | m³/h | 100-5000 | Consigne | Débit nominal de conception |
| damper_manual_sp | damper manual sp | % | 0-100 | Consigne | Position manuelle registre (réglage) |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| heating_active | heating run status | Boolean | true/false | Réchauffage actif |
| zone_occupied | zone occupied status | Boolean | true/false | Zone occupée |
| flow_alarm | flow alarm | Boolean | true/false | Alarme débit hors plage |
| valve_fault | valve fault alarm | Boolean | true/false | Défaut vanne réchauffage |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_temp | AI:1 | 40001 (HR) | 1/1/1 |
| discharge_temp | AI:2 | 40002 (HR) | 1/1/2 |
| supply_flow | AI:3 | 40003 (HR) | 1/1/3 |
| supply_dp | AI:4 | 40004 (HR) | 1/1/4 |
| reheat_valve_position | AI:5 | 40005 (HR) | 1/1/5 |
| reheat_coil_temp | AI:6 | 40006 (HR) | 1/1/6 |
| zone_temp_sp | AV:1 | 40101 (HR) | 1/2/1 |
| reheat_valve_cmd | AO:1 | 40201 (HR) | 1/2/2 |
| design_flow_sp | AV:2 | 40102 (HR) | 1/2/3 |
| damper_manual_sp | AV:3 | 40103 (HR) | 1/2/4 |
| heating_active | BI:1 | 10001 (DI) | 1/3/1 |
| zone_occupied | BI:2 | 10002 (DI) | 1/3/2 |
| flow_alarm | BI:3 | 10003 (DI) | 1/3/3 |
| valve_fault | BI:4 | 10004 (DI) | 1/3/4 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input
- Modbus : HR = Holding Register (40001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Comparaison CAV vs VAV

| Caractéristique | CAV | VAV |
|-----------------|-----|-----|
| Débit d'air | Constant | Variable |
| Régulation température | Par réchauffage | Par débit + réchauffage |
| Économie d'énergie ventilation | Non | Oui |
| Complexité | Simple | Plus complexe |
| Application | Charges stables | Charges variables |

## Séquence de Contrôle Typique

| Condition | Action Réchauffage | Débit |
|-----------|-------------------|-------|
| T_zone < SP - 1°C | Réchauffage 100% | Constant |
| T_zone = SP | Réchauffage modulé | Constant |
| T_zone > SP + 1°C | Réchauffage 0% | Constant |

## Sources
- ASHRAE Handbook - Air Distribution Systems
- Project Haystack - CAV Terminal Tags
- Brick Schema - CAV Class
- ASHRAE Guideline 36 - CAV Sequences (where applicable)
