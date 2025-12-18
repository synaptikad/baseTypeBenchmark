# Points de Audio Amplifier (Amplificateur audio)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 5
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Output Power | sensor-point | W | 0-1000 | 1s | Puissance sortie |
| Input Level | sensor-point | dBu | -60 à +20 | 100ms | Niveau entrée |
| Output Level | sensor-point | dBu | -60 à +20 | 100ms | Niveau sortie |
| Temperature | sensor-temp-point | °C | 0-100°C | 30s | Température interne |
| Load Impedance | sensor-point | Ω | 2-16 | 10s | Impédance charge |
| THD | sensor-point | % | 0-10% | 1min | Distorsion harmonique |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Power Enable | cmd-point | - | ON/OFF | Binaire | Mise sous tension |
| Volume | cmd-sp-point | dB | -80 à 0 | Analog | Volume |
| Mute | cmd-point | - | ON/OFF | Binaire | Sourdine |
| Input Select | cmd-sp-point | - | 1-8 | Analog | Sélection entrée |
| Limiter Threshold | cmd-sp-point | dB | -20 à 0 | Analog | Seuil limiteur |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Amplifier Status | status-point | Enum | OK/PROTECT/FAULT | État général |
| Channel Status | status-point | Enum | OK/CLIPPING/PROTECT | État canal |
| Thermal Status | status-point | Enum | OK/WARNING/SHUTDOWN | État thermique |
| Protection Active | status-point | Boolean | FALSE/TRUE | Protection active |
| Mute Status | status-point | Boolean | FALSE/TRUE | Sourdine active |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | Telnet/IP |
|-------|---------------|-----------------|-----------|
| Output Power | AI0 | 30001 | GET PWR |
| Temperature | AI1 | 30002 | GET TEMP |
| Amplifier Status | MSV0 | 40001 | GET STATUS |
| Power Enable | BO0 | 00001 | SET PWR |
| Volume | AO0 | 40101 | SET VOL |
| Mute | BO1 | 00002 | SET MUTE |

## Sources
- [AES17 Audio Amplifier Testing](https://www.aes.org/)
- [IEC 60268-3 Sound Amplifiers](https://webstore.iec.ch/)
