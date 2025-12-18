# Points de DSP (Processeur signal numérique)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 7
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Input Channels | sensor-point | count | 0-64 | Config | Canaux entrée |
| Output Channels | sensor-point | count | 0-64 | Config | Canaux sortie |
| DSP Load | sensor-point | % | 0-100% | 1s | Charge DSP |
| Input Level | sensor-point | dBFS | -60 à 0 | 100ms | Niveau entrée |
| Output Level | sensor-point | dBFS | -60 à 0 | 100ms | Niveau sortie |
| Temperature | sensor-temp-point | °C | 0-70°C | 30s | Température interne |
| Network Latency | sensor-point | ms | 0-100 | 1s | Latence réseau |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Preset Recall | cmd-sp-point | - | 1-100 | Analog | Rappel preset |
| Preset Save | cmd-sp-point | - | 1-100 | Analog | Sauvegarde preset |
| Input Gain | cmd-sp-point | dB | -80 à +20 | Analog | Gain entrée |
| Output Gain | cmd-sp-point | dB | -80 à +20 | Analog | Gain sortie |
| Mute Input | cmd-sp-point | - | Channel bitmask | Analog | Sourdine entrées |
| Mute Output | cmd-sp-point | - | Channel bitmask | Analog | Sourdine sorties |
| System Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| DSP Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Processing Status | status-point | Enum | RUNNING/STOPPED/OVERLOAD | État traitement |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| Current Preset | status-point | Analog | 1-100 | Preset actif |
| Clipping Status | status-point | Bitmask | Per channel | Écrêtage canaux |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | TCP/IP |
|-------|---------------|-----------------|--------|
| DSP Load | AI0 | 30001 | GET LOAD |
| Input Level | AI1 | 30002 | GET LEVEL IN |
| Temperature | AI2 | 30003 | GET TEMP |
| DSP Status | MSV0 | 40001 | GET STATUS |
| Preset Recall | AO0 | 40101 | PRESET x |
| Input Gain | AO1 | 40102 | GAIN IN x |

## Sources
- [AES3 Digital Audio Interface](https://www.aes.org/)
- [Dante Protocol](https://www.audinate.com/)
- [AVB IEEE 802.1](https://www.ieee.org/)
