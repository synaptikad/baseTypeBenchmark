# Points de Biometric Reader (Lecteur biométrique)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Verification Count | sensor-point | count | 0-999999 | Sur événement | Compteur vérifications |
| Match Score | sensor-point | % | 0-100% | Sur événement | Score correspondance |
| False Accept Rate | sensor-point | % | 0-1% | 1h | Taux faux positifs |
| False Reject Rate | sensor-point | % | 0-5% | 1h | Taux faux négatifs |
| Enrolled Users | sensor-point | count | 0-10000 | 1h | Utilisateurs enrôlés |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Match Threshold | cmd-sp-point | % | 50-99% | Analog | Seuil correspondance |
| Enrollment Mode | cmd-point | - | ON/OFF | Binaire | Mode enrôlement |
| Reader Enable | cmd-point | - | ON/OFF | Binaire | Activation lecteur |
| Delete User | cmd-sp-point | - | User ID | Analog | Suppression utilisateur |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Reader Status | status-point | Enum | OK/FAULT | État général |
| Sensor Status | status-point | Enum | OK/DIRTY/FAULT | État capteur |
| Last Match Result | status-point | Enum | MATCH/NO_MATCH/ERROR | Dernier résultat |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| Enrollment Status | status-point | Boolean | FALSE/TRUE | Mode enrôlement actif |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSDP Protocol |
|-------|---------------|-----------------|---------------|
| Verification Count | AI0 | 30001 | - |
| Match Score | AI1 | 30002 | Biometric Data |
| Reader Status | MSV0 | 40001 | Status Poll |
| Last Match Result | MSV1 | 40002 | Match Event |
| Tamper Status | BI0 | 10001 | Tamper Event |
| Match Threshold | AO0 | 40101 | Config 0x50 |

## Sources
- [ISO 19795 Biometric Performance](https://www.iso.org/)
- [OSDP Biometric Extension](https://www.securityindustry.org/osdp/)
- [EN 50133 Access Control](https://www.en-standard.eu/)
