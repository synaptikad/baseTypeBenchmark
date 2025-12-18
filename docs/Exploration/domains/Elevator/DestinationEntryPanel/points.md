# Points de Destination Entry Panel (Kiosk)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Request Count | sensor-point | count | 0-999999 | Sur événement | Requêtes cumulées |
| Card Read Count | sensor-point | count | 0-999999 | Sur événement | Lectures cartes cumulées |
| Touch Count | sensor-point | count | 0-9999999 | Sur événement | Touches écran cumulées |
| Response Time | sensor-point | ms | 100-5000 | Sur événement | Temps réponse système |
| Panel Temperature | sensor-temp-point | °C | 15-50°C | 5min | Température panneau |
| Ambient Light | sensor-point | lux | 0-10000 | 1min | Luminosité ambiante |
| Display Brightness | sensor-point | % | 0-100% | Sur demande | Luminosité écran |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Destination Select | cmd-point | floor | -5 à 100 | Analog | Sélection destination |
| Panel Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation panneau |
| Brightness Control | cmd-sp-point | % | 0-100% | Analog | Contrôle luminosité |
| Volume Control | cmd-sp-point | % | 0-100% | Analog | Volume audio |
| Display Message | cmd-point | - | TEXT | String | Message personnalisé |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Panel Status | status-point | Enum | OK/FAULT/OFFLINE | État général |
| Display Status | status-point | Enum | OK/FAULT | État écran |
| Touch Screen Status | status-point | Enum | OK/FAULT | État tactile |
| Card Reader Status | status-point | Enum | OK/FAULT/NOT_PRESENT | État lecteur |
| Speaker Status | status-point | Enum | OK/FAULT | État haut-parleur |
| Car Assigned | status-point | String | A-Z | Cabine assignée |
| Network Status | status-point | Enum | CONNECTED/DISCONNECTED | État réseau |
| Last Request Floor | status-point | Number | -5 à 100 | Dernière destination |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | REST API |
|-------|---------------|-----------------|----------|
| Panel Status | MSV0 | 40001 | /api/kiosk/status |
| Display Status | MSV1 | 40002 | - |
| Request Count | AI0 | 40003 | /api/kiosk/stats |
| Panel Temperature | AI1 | 40004 | - |
| Destination Select | AO0 | 40101 | /api/kiosk/call |
| Panel Enable | BO0 | 00001 | /api/kiosk/enable |
| Car Assigned | CSV0 | 40010 | /api/kiosk/assignment |

## Sources
- [EN 81-70 Accessibility](https://www.en-standard.eu/)
- [ADA Elevator Requirements](https://www.ada.gov/)
- [Destination Dispatch Standards](https://www.elevatorworld.com/)
