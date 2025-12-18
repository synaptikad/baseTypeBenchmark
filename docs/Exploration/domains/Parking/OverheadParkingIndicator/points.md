# Points de Overhead Parking Indicator

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 5
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| LED Power Consumption | sensor-elec-power-point | W | 0-10 W | 5min | Consommation électrique LED |
| Brightness Level | sensor-point | % | 0-100% | Sur demande | Niveau luminosité actuel |
| Operating Hours | sensor-point | h | 0-100000 h | 1h | Heures fonctionnement total |
| State Change Count | sensor-point | count | 0-999999 | 1h | Nombre changements d'état |
| Communication Latency | sensor-point | ms | 0-500 ms | 1min | Latence communication bus |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| LED Color | cmd-point | - | GREEN/RED/BLUE/YELLOW/OFF | Enum | Couleur LED indicateur |
| Brightness Control | cmd-sp-point | % | 0-100% | Analog | Contrôle intensité lumineuse |
| Blink Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation mode clignotant |
| Blink Rate | cmd-sp-point | Hz | 0.5-5 Hz | Analog | Fréquence clignotement |
| Test Mode | cmd-point | - | ENABLE/DISABLE | Binaire | Mode test cyclique couleurs |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Indicator Status | status-point | Enum | OK/FAULT/OFFLINE | État général indicateur |
| Current Color | status-point | Enum | GREEN/RED/BLUE/YELLOW/OFF | Couleur affichée actuellement |
| LED Health | status-point | Enum | OK/DEGRADED/FAILED | État santé LED |
| Communication Status | status-point | Enum | CONNECTED/DISCONNECTED | État connexion bus série |
| Parking Space Status | status-point | Enum | FREE/OCCUPIED/RESERVED/DISABLED | État place associée |
| Fault Code | status-point | String | Alphanumeric | Code erreur technique |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Indicator Status | MSV0 | 40001 |
| LED Power Consumption | AI0 | 40002 |
| Brightness Level | AI1 | 40003 |
| Operating Hours | AI2 | 40004-40005 |
| LED Color | MSV1 | 40101 |
| Brightness Control | AO0 | 40102 |
| Current Color | MSV2 | 40011 |
| Parking Space Status | MSV3 | 40012 |

## Sources
- [Parking Guidance System Documentation](https://www.parking-guidance.com/)
- [LED Industrial Specifications](https://www.led-professional.com/)
