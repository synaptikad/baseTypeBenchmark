# Points de Car Operating Panel (COP)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 5
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Button Press Count | sensor-point | count | 0-9999999 | Sur événement | Appuis boutons cumulés |
| Display Brightness | sensor-point | % | 0-100% | Sur demande | Luminosité écran actuelle |
| Panel Temperature | sensor-temp-point | °C | 15-45°C | 5min | Température panneau |
| Audio Level | sensor-point | dB | 0-100 | 1s | Niveau audio annonce |
| Fan Speed | sensor-point | RPM | 0-3000 | 1min | Vitesse ventilation cabine |
| Light Level | sensor-point | lux | 0-1000 | 1min | Éclairage cabine |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Floor Select | cmd-point | floor | -5 à 100 | Analog | Sélection étage |
| Door Open | cmd-point | - | TRIGGER | Binaire | Commande ouverture |
| Door Close | cmd-point | - | TRIGGER | Binaire | Commande fermeture |
| Emergency Call | cmd-point | - | TRIGGER | Binaire | Appel d'urgence |
| Display Message | cmd-point | - | TEXT | String | Message affichage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Panel Status | status-point | Enum | OK/FAULT/OFFLINE | État général |
| Floor Button Status | status-point | Enum | OK/STUCK/FAULT | État boutons étages |
| Door Button Status | status-point | Enum | OK/FAULT | État boutons portes |
| Display Status | status-point | Enum | OK/FAULT | État afficheur |
| Speaker Status | status-point | Enum | OK/FAULT | État haut-parleur |
| Intercom Status | status-point | Enum | OK/FAULT | État interphone |
| Emergency Button Status | status-point | Boolean | FALSE/TRUE | Bouton urgence activé |
| Key Switch Position | status-point | Enum | NORMAL/INSPECTION/FIRE | Position clé |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | CAN |
|-------|---------------|-----------------|-----|
| Panel Status | MSV0 | 40001 | 0x100 |
| Floor Button Status | MSV1 | 40002 | 0x101 |
| Display Status | MSV2 | 40003 | 0x102 |
| Floor Select | AO0 | 40101 | 0x200 |
| Door Open | BO0 | 00001 | 0x300 |
| Emergency Call | BO1 | 00002 | 0x301 |
| Key Switch Position | MSV3 | 40010 | 0x400 |

## Sources
- [EN 81-70 Accessibility](https://www.en-standard.eu/)
- [ADA Elevator Requirements](https://www.ada.gov/)
- [EN 81-28 Remote Alarm](https://www.en-standard.eu/)
