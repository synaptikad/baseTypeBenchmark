# Points de Filtre à Air (Air Filter)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 1
- **Total points état** : 4

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| filter_dp | filter differential pressure sensor | Pa | 50-500 | 1min | Pression différentielle à travers le filtre |
| filter_loading | filter loading sensor | % | 0-100 | 5min | Pourcentage de colmatage du filtre |
| filter_hours | filter run hours sensor | h | 0-8760 | 15min | Heures de fonctionnement du filtre |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| filter_reset_cmd | filter reset cmd | - | 0/1 | Consigne | Remise à zéro après changement de filtre |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| filter_dirty_alarm | filter dirty alarm | Boolean | true/false | Alarme filtre colmaté (DP > seuil) |
| filter_ok | filter ok status | Boolean | true/false | État filtre OK (pression normale) |
| filter_change_required | filter maintenance alarm | Boolean | true/false | Indicateur changement requis |
| filter_bypass | filter bypass status | Boolean | true/false | Détection contournement filtre |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| filter_dp | AI:1 | 40001 (HR) | 1/1/1 |
| filter_loading | AV:1 | 40002 (HR) | 1/1/2 |
| filter_hours | AV:2 | 40003 (HR) | 1/1/3 |
| filter_reset_cmd | BO:1 | 00001 (Coil) | 1/2/1 |
| filter_dirty_alarm | BI:1 | 10001 (DI) | 1/3/1 |
| filter_ok | BI:2 | 10002 (DI) | 1/3/2 |
| filter_change_required | BI:3 | 10003 (DI) | 1/3/3 |
| filter_bypass | BI:4 | 10004 (DI) | 1/3/4 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Seuils d'Alarme Typiques

| Paramètre | Seuil Avertissement | Seuil Alarme | Source |
|-----------|---------------------|--------------|--------|
| Pression différentielle | 200-250 Pa | 300-500 Pa | ASHRAE, fabricants |
| Colmatage filtre | 70% | 90% | Pratique industrielle |
| Heures fonctionnement | 2000h | 4000h | Selon environnement |

## Sources
- [Differential Pressure Switch in BMS Systems](https://engalaxy.com/differential-pressure-switch-in-bms-systems/) - Guide complet sur les capteurs DP pour filtres
- [How DPS Works for Fan and Filter](https://bms-system.com/how-dps-differential-pressure-switch-works-for-fan-and-filter/) - Fonctionnement des capteurs de pression
- [Filter Differential Pressure Alarming](https://www.achrnews.com/articles/163608-how-to-do-filter-differential-pressure-alarming-the-right-way) - Seuils d'alarme recommandés
- [Sensirion Filter Monitoring](https://sensirion.com/products/applications/hvac/filter-monitoring) - Technologie de capteurs pour filtres
- [Haystack Tagging Ontology](http://www.vcharpenay.link/hto/doc.htm) - Tags Haystack pour filtres
