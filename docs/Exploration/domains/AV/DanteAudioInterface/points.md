# Points de Dante Audio Interface (Interface audio Dante)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Input Channels | sensor-point | count | 0-64 | Config | Canaux entrée |
| Output Channels | sensor-point | count | 0-64 | Config | Canaux sortie |
| Sample Rate | sensor-point | kHz | 44.1/48/96 | Config | Fréquence échantillonnage |
| Latency | sensor-point | ms | 0-10 | 1s | Latence réseau |
| Clock Offset | sensor-point | ppm | -100 à +100 | 1s | Décalage horloge |
| Network Bandwidth | sensor-point | Mbps | 0-1000 | 30s | Bande passante utilisée |
| Packet Loss | sensor-point | % | 0-100% | 1min | Perte paquets |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Sample Rate Set | cmd-sp-point | kHz | 44.1/48/96 | Enum | Configuration fréquence |
| Latency Set | cmd-sp-point | ms | 0.25/0.5/1/2/5 | Enum | Configuration latence |
| Channel Gain | cmd-sp-point | dB | -80 à +20 | Analog | Gain canal |
| Channel Mute | cmd-sp-point | - | Channel bitmask | Analog | Sourdine canaux |
| Device Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Device Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Clock Status | status-point | Enum | MASTER/SLAVE/SYNCED/UNSYNCED | État horloge |
| Network Status | status-point | Enum | PRIMARY/SECONDARY/FAULT | État réseau |
| Subscription Status | status-point | Enum | OK/PENDING/FAULT | État abonnements |
| Clipping Status | status-point | Bitmask | Per channel | Écrêtage canaux |
| Signal Present | status-point | Bitmask | Per channel | Signal présent |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | Dante API |
|-------|---------------|-----------------|-----------|
| Input Channels | AI0 | 30001 | Device Query |
| Latency | AI1 | 30002 | Latency Query |
| Device Status | MSV0 | 40001 | Status Query |
| Clock Status | MSV1 | 40002 | Clock Query |
| Sample Rate Set | MSV2 | 40003 | Sample Rate Set |
| Channel Gain | AO0 | 40101 | Gain Set |

## Sources
- [AES67 Audio over IP](https://www.aes.org/)
- [Dante Protocol](https://www.audinate.com/)
- [SMPTE ST 2110-30](https://www.smpte.org/)
