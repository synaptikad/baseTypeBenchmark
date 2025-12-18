# Points de Variable Message Sign

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 7
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Display Brightness | sensor-point | % | 0-100% | 5min | Luminosité affichage actuelle |
| Power Consumption | sensor-elec-power-point | W | 0-500 W | 5min | Consommation électrique |
| Ambient Light Level | sensor-point | lux | 0-100000 lux | 1min | Niveau luminosité ambiante |
| Operating Hours | sensor-point | h | 0-100000 h | 1h | Heures fonctionnement total |
| Display Temperature | sensor-temp-point | °C | -30 à +70°C | 5min | Température interne afficheur |
| Message Change Count | sensor-point | count | 0-999999 | 1h | Nombre changements message |
| Network Bandwidth | sensor-point | kbps | 0-1000 kbps | 1min | Bande passante utilisée |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Display Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation affichage |
| Message Content | cmd-point | - | TEXT | String | Contenu message à afficher |
| Brightness Control | cmd-sp-point | % | 0-100% | Analog | Contrôle manuel luminosité |
| Auto Brightness | cmd-point | - | ENABLE/DISABLE | Binaire | Ajustement automatique luminosité |
| Display Mode | cmd-point | - | STATIC/SCROLL/FLASH | Enum | Mode d'affichage |
| Message Priority | cmd-sp-point | - | 1-10 | Analog | Priorité message |
| Test Pattern | cmd-point | - | ENABLE/DISABLE | Binaire | Affichage motif de test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Display Status | status-point | Enum | OK/FAULT/OFFLINE | État général afficheur |
| LED Matrix Status | status-point | Enum | OK/DEGRADED/FAILED | État matrice LED |
| Communication Status | status-point | Enum | CONNECTED/DISCONNECTED | État connexion réseau |
| Current Message | status-point | String | TEXT | Message affiché actuellement |
| Power Supply Status | status-point | Enum | OK/FAULT | État alimentation |
| Content Source | status-point | Enum | LOCAL/REMOTE/SCHEDULED | Source contenu actif |
| Fault Code | status-point | String | Alphanumeric | Code erreur technique |
| Last Update Time | status-point | Timestamp | ISO8601 | Horodatage dernière mise à jour |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | NTCIP |
|-------|---------------|-----------------|-------|
| Display Status | MSV0 | 40001 | dmsMessageStatus |
| Display Brightness | AI0 | 40002 | dmsIllumControl |
| Power Consumption | AI1 | 40003 | dmsPowerStatus |
| Display Temperature | AI2 | 40004 | dmsTemp |
| Ambient Light Level | AI3 | 40005 | dmsAmbientLight |
| Display Enable | BO0 | 00001 | dmsActivate |
| Brightness Control | AO0 | 40101 | dmsIllumBrightLevelCmd |
| LED Matrix Status | MSV1 | 40011 | dmsPixelService |

## Sources
- [EN 12966 Road Traffic Signs Standard](https://www.en-standard.eu/)
- [NTCIP VMS Control Protocol](https://www.ntcip.org/)
- [LED Display Technical Documentation](https://www.led-professional.com/)
