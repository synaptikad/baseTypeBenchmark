# Points de Parking Guidance Display

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 6
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Display Brightness | sensor-point | % | 0-100% | 5min | Luminosité affichage actuelle |
| Power Consumption | sensor-elec-power-point | W | 0-200 W | 5min | Consommation électrique |
| Operating Hours | sensor-point | h | 0-100000 h | 1h | Heures fonctionnement total |
| Ambient Light Level | sensor-point | lux | 0-100000 lux | 1min | Niveau luminosité ambiante |
| Display Temperature | sensor-temp-point | °C | -20 à +60°C | 5min | Température interne afficheur |
| Update Rate | sensor-point | Hz | 0-5 Hz | 1min | Fréquence actualisation affichage |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Display Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation affichage |
| Brightness Control | cmd-sp-point | % | 0-100% | Analog | Contrôle manuel luminosité |
| Auto Brightness | cmd-point | - | ENABLE/DISABLE | Binaire | Ajustement automatique luminosité |
| Display Content | cmd-point | - | JSON/TEXT | String | Contenu à afficher |
| Display Mode | cmd-point | - | NORMAL/FLASHING/OFF | Enum | Mode d'affichage |
| Test Pattern | cmd-point | - | ENABLE/DISABLE | Binaire | Affichage motif de test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Display Status | status-point | Enum | OK/FAULT/OFFLINE | État général afficheur |
| LED Panel Status | status-point | Enum | OK/DEGRADED/FAILED | État panneaux LED |
| Communication Status | status-point | Enum | CONNECTED/DISCONNECTED | État connexion réseau |
| Current Displayed Value | status-point | Number | 0-9999 | Valeur affichée (places libres) |
| Display Color | status-point | Enum | GREEN/RED/YELLOW | Couleur affichage actuelle |
| Power Supply Status | status-point | Enum | OK/FAULT | État alimentation |
| Fault Code | status-point | String | Alphanumeric | Code erreur technique |
| Last Update Time | status-point | Timestamp | ISO8601 | Horodatage dernière mise à jour |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Display Status | MSV0 | 40001 |
| Display Brightness | AI0 | 40002 |
| Power Consumption | AI1 | 40003 |
| Display Temperature | AI2 | 40004 |
| Display Enable | BO0 | 00001 |
| Brightness Control | AO0 | 40101 |
| Current Displayed Value | AI3 | 40011 |
| Display Color | MSV1 | 40012 |

## Sources
- [ITS Standards for VMS](https://www.standards.its.dot.gov/)
- [LED Display Specifications](https://www.led-professional.com/)
- [Parking Guidance Display Documentation](https://www.parking-guidance.com/)
