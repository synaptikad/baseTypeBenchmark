# Points de Greywater System (Système eaux grises)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 6
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Inlet Flow Rate | sensor-flow-point | L/min | 0-100 | 10s | Débit entrée |
| Outlet Flow Rate | sensor-flow-point | L/min | 0-100 | 10s | Débit sortie traitée |
| Collection Tank Level | sensor-level-point | % | 0-100% | 1min | Niveau bac collecte |
| Treatment Tank Level | sensor-level-point | % | 0-100% | 1min | Niveau bac traitement |
| Storage Tank Level | sensor-level-point | % | 0-100% | 1min | Niveau bac stockage |
| Turbidity | sensor-point | NTU | 0-100 | 5min | Turbidité eau traitée |
| pH Level | sensor-point | pH | 6-9 | 5min | Niveau pH |
| Chlorine Level | sensor-point | mg/L | 0-5 | 10min | Niveau chlore résiduel |
| Daily Volume Treated | sensor-volume-point | m³ | 0-50 | 1h | Volume traité journalier |
| Energy Consumption | sensor-power-point | kWh | 0-100 | 1h | Consommation énergie |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Treatment Pump Enable | cmd-point | - | ON/OFF | Binaire | Activation pompe traitement |
| Distribution Pump Enable | cmd-point | - | ON/OFF | Binaire | Activation pompe distribution |
| UV Disinfection Enable | cmd-point | - | ON/OFF | Binaire | Activation UV désinfection |
| Chlorine Dosing Setpoint | cmd-sp-point | mg/L | 0-2 | Analog | Consigne dosage chlore |
| Backwash Trigger | cmd-point | - | TRIGGER | Binaire | Déclenchement lavage filtre |
| System Mode | cmd-sp-point | - | AUTO/MANUAL/OFF | Enum | Mode système |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Treatment Status | status-point | Enum | IDLE/TREATING/BACKWASH | État traitement |
| Water Quality Status | status-point | Enum | OK/MARGINAL/FAIL | Qualité eau |
| Collection Tank Alarm | status-point | Enum | OK/HIGH/LOW/OVERFLOW | Alarme bac collecte |
| Filter Status | status-point | Enum | OK/CLOGGED/MAINTENANCE | État filtre |
| UV Lamp Status | status-point | Enum | OK/DEGRADED/FAILED | État lampe UV |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Inlet Flow Rate | AI0 | 30001 |
| Collection Tank Level | AI1 | 30002 |
| Treatment Tank Level | AI2 | 30003 |
| Storage Tank Level | AI3 | 30004 |
| Turbidity | AI4 | 30005 |
| pH Level | AI5 | 30006 |
| Treatment Pump Enable | BO0 | 00001 |
| Distribution Pump Enable | BO1 | 00002 |
| System Status | MSV0 | 40001 |
| Chlorine Dosing Setpoint | AO0 | 40101 |

## Sources
- [EN 16941-1 Greywater Systems](https://www.en-standard.eu/)
- [NSF/ANSI 350 Onsite Water Reuse](https://www.nsf.org/)
- [BS 8525-1 Greywater Systems](https://www.bsigroup.com/)
