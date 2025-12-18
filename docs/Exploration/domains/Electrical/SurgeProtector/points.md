# Points - Surge Protector

## Résumé
- **Points de mesure** : 8
- **Points de commande** : 2
- **Points d'état** : 6
- **Total** : 16

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| SPD-SURGE-COUNT | Surge Event Counter | 1 | - | 0-9999 | On event | Nombre total d'événements de surtension détectés |
| SPD-SURGE-LOW | Low Surge Events | 1 | - | 0-9999 | On event | Événements surtension faible (cat. A) |
| SPD-SURGE-MED | Medium Surge Events | 1 | - | 0-9999 | On event | Événements surtension moyenne (cat. B) |
| SPD-SURGE-HIGH | High Surge Events | 1 | - | 0-9999 | On event | Événements surtension élevée (cat. C) |
| SPD-LAST-SURGE | Last Surge Voltage | 1 | V | 0-6000 | On event | Amplitude dernière surtension captée |
| SPD-PROTECTION-L1 | Protection Level L1 | 1 | % | 0-100 | 60s | Niveau de protection restant phase L1 |
| SPD-PROTECTION-L2 | Protection Level L2 | 1 | % | 0-100 | 60s | Niveau de protection restant phase L2 |
| SPD-PROTECTION-L3 | Protection Level L3 | 1 | % | 0-100 | 60s | Niveau de protection restant phase L3 |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| SPD-RESET-COUNT | Reset Counter | 1 | - | 0/1 | Binary | Réinitialisation compteur événements |
| SPD-TEST | Test Mode | 1 | - | 0/1 | Binary | Activation auto-test SPD |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| SPD-STATUS-L1 | Protection Status L1 | Enum | OK/DEGRADED/FAILED | 5s | État protection phase L1 (varistance MOV) |
| SPD-STATUS-L2 | Protection Status L2 | Enum | OK/DEGRADED/FAILED | 5s | État protection phase L2 (varistance MOV) |
| SPD-STATUS-L3 | Protection Status L3 | Enum | OK/DEGRADED/FAILED | 5s | État protection phase L3 (varistance MOV) |
| SPD-STATUS-N | Protection Status Neutral | Enum | OK/DEGRADED/FAILED | 5s | État protection neutre |
| SPD-CONTACT | Fault Contact | Binary | 0=OK/1=FAULT | 1s | Contact de défaut (NO/NF vers GTB) |
| SPD-COMM | Communication Status | Binary | 0=FAULT/1=OK | 60s | État communication BACnet/Modbus |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| SPD-ALM-FAIL-L1 | Phase L1 Failed | CRITICAL | Protection L1 HS | Varistance L1 défaillante (circuit ouvert) |
| SPD-ALM-FAIL-L2 | Phase L2 Failed | CRITICAL | Protection L2 HS | Varistance L2 défaillante (circuit ouvert) |
| SPD-ALM-FAIL-L3 | Phase L3 Failed | CRITICAL | Protection L3 HS | Varistance L3 défaillante (circuit ouvert) |
| SPD-ALM-FAIL-N | Neutral Failed | CRITICAL | Protection N HS | Varistance neutre défaillante |
| SPD-ALM-DEGRADE-L1 | Phase L1 Degraded | WARNING | Protection L1 < 50% | Varistance L1 dégradée (remplacement recommandé) |
| SPD-ALM-DEGRADE-L2 | Phase L2 Degraded | WARNING | Protection L2 < 50% | Varistance L2 dégradée (remplacement recommandé) |
| SPD-ALM-DEGRADE-L3 | Phase L3 Degraded | WARNING | Protection L3 < 50% | Varistance L3 dégradée (remplacement recommandé) |
| SPD-ALM-EOL | End of Life | WARNING | Protection < 20% | Fin de vie SPD (remplacement urgent) |
| SPD-ALM-THERMAL | Thermal Overload | WARNING | Température excessive | Déconnexion thermique activée |
| SPD-ALM-FREQ-SURGE | Frequent Surges | WARNING | >10 surtensions/jour | Surtensions fréquentes (problème amont) |
| SPD-ALM-COMM | Communication Fault | WARNING | Perte liaison | Perte communication BACnet/Modbus |

## Sources
- [Eaton Power Xpert SPD](https://www.eaton.com/us/en-us/products/backup-power-ups-surge-it-power-distribution/surge-protection/power-xpert-spd.html)
- [Eaton SPD Series Integrated Surge Protective Device](https://www.eaton.com/us/en-us/catalog/surge-protection-devices/spd-series-integrated-surge-protective-device.html)
- [Monitoring of Surge-Protective Devices - NIST](https://www.nist.gov/document/monitoringspdspdf)
- [Techwin Intelligent SPD Monitor](https://www.techwinspd.com/products/intelligent-multifunctional-spd-monitor-and-data-acquisition-device.html)
- [Siemens SPD Power Product Guide](https://assets.new.siemens.com/siemens/assets/api/uuid:b5e13ffe-4a75-4f74-a593-bae873f12b51/s09-surge-protection-devices.pdf)
- [The Surge Protection Device - Electrical Installation Guide](https://www.electrical-installation.org/enwiki/The_Surge_Protection_Device_(SPD))
