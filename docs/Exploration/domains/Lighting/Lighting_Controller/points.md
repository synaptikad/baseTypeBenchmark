# Points - Lighting Controller

## Résumé
- **Points de mesure** : 12
- **Points de commande** : 12
- **Points d'État** : 14
- **Total** : 38

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| LIGHT_CTRL_POWER_TOTAL | Puissance Totale Système | 1 | kW | 0-1000 | 1 min | Puissance totale consommée par le système d'éclairage |
| LIGHT_CTRL_ENERGY_TOTAL | Énergie Totale Système | 1 | MWh | 0-9999 | 15 min | Énergie cumulée du système d'éclairage |
| LIGHT_CTRL_ZONES_ACTIVE | Zones Actives | 1 | - | 0-1000 | 1 min | Nombre de zones d'éclairage actuellement actives |
| LIGHT_CTRL_DEVICES_TOTAL | Dispositifs Totaux | 1 | - | 0-10000 | 1 hour | Nombre total de dispositifs gérés par le contrôleur |
| LIGHT_CTRL_DEVICES_ONLINE | Dispositifs En Ligne | 1 | - | 0-10000 | 1 min | Nombre de dispositifs actuellement en ligne |
| LIGHT_CTRL_DEVICES_FAULT | Dispositifs en Défaut | 1 | - | 0-10000 | 1 min | Nombre de dispositifs signalant un défaut |
| LIGHT_CTRL_SAVINGS_DAY | Économies Journalières | 1 | kWh | 0-10000 | 1 hour | Énergie économisée aujourd'hui vs utilisation max |
| LIGHT_CTRL_SAVINGS_MONTH | Économies Mensuelles | 1 | MWh | 0-1000 | Daily | Énergie économisée ce mois vs utilisation max |
| LIGHT_CTRL_CPU_LOAD | Charge Processeur | 1 | % | 0-100 | 1 min | Charge du processeur du contrôleur |
| LIGHT_CTRL_MEM_USED | Mémoire Utilisée | 1 | % | 0-100 | 5 min | Pourcentage de mémoire RAM utilisée |
| LIGHT_CTRL_TEMP | Température Contrôleur | 1 | °C | 0-70 | 5 min | Température interne du contrôleur |
| LIGHT_CTRL_UPTIME | Temps de Fonctionnement | 1 | hour | 0-999999 | 1 hour | Heures de fonctionnement depuis démarrage |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| LIGHT_CTRL_ZONE_CMD | Commande Zone | 1-1000 | % | 0-100 | Analog | Commande de niveau d'éclairage par zone |
| LIGHT_CTRL_ZONE_ON_OFF | Marche/Arrêt Zone | 1-1000 | - | 0-1 | Digital | Commande marche/arrêt par zone |
| LIGHT_CTRL_SCENE_RECALL | Rappel Scène | 1-100 | - | 0-99 | Multi-State | Activation d'une scène d'éclairage (0-99) |
| LIGHT_CTRL_SCENE_STORE | Mémorisation Scène | 1-100 | - | 0-99 | Multi-State | Sauvegarde de la configuration actuelle comme scène |
| LIGHT_CTRL_SCHEDULE_ENABLE | Activation Programmation | 1-50 | - | 0-1 | Digital | Activation/désactivation d'un programme horaire |
| LIGHT_CTRL_OVERRIDE_ALL | Override Global | 1 | - | 0-1 | Digital | Override manuel de toutes les zones |
| LIGHT_CTRL_OVERRIDE_ZONE | Override Zone | 1-1000 | - | 0-1 | Digital | Override manuel d'une zone spécifique |
| LIGHT_CTRL_DAYLIGHT_ENABLE | Activation Daylight Harvesting | 1-50 | - | 0-1 | Digital | Activation/désactivation du daylight harvesting par zone |
| LIGHT_CTRL_OCC_ENABLE | Activation Détection Occupation | 1-50 | - | 0-1 | Digital | Activation/désactivation du contrôle par occupation |
| LIGHT_CTRL_DEMAND_LIMIT | Limite Consommation | 1 | kW | 0-1000 | Analog | Limite de consommation maximale (demand response) |
| LIGHT_CTRL_EMERGENCY_MODE | Mode Urgence | 1 | - | 0-2 | Multi-State | Mode: Normal/Test/Emergency |
| LIGHT_CTRL_REBOOT | Redémarrage | 1 | - | 0-1 | Digital | Redémarrage du contrôleur |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| LIGHT_CTRL_STATUS | État Contrôleur | Enum | Running/Stopped/Fault/Maintenance | COV | État opérationnel général du contrôleur |
| LIGHT_CTRL_COMM_STATUS | État Communication | Enum | Online/Degraded/Offline | COV | État de communication avec le BMS |
| LIGHT_CTRL_NETWORK_STATUS | État Réseau | Enum | Connected/Disconnected/Fault | COV | État de la connexion réseau Ethernet |
| LIGHT_CTRL_ZONE_STATUS | État Zones | Array[1000] | On/Off/Dimmed/Fault/Override | COV | État de chaque zone d'éclairage |
| LIGHT_CTRL_SCHEDULE_STATUS | État Programmations | Array[50] | Active/Inactive/Fault | COV | État de chaque programme horaire |
| LIGHT_CTRL_SCENE_STATUS | État Scènes | Array[100] | Configured/Empty | On Request | Configuration de chaque scène d'éclairage |
| LIGHT_CTRL_ACTIVE_SCENE | Scène Active | Integer | 0-99 | COV | Numéro de la scène actuellement active |
| LIGHT_CTRL_OVERRIDE_STATUS | État Override | Enum | None/Zone/Global/Emergency | COV | Mode override actuellement actif |
| LIGHT_CTRL_MODE | Mode Opératoire | Enum | Auto/Manual/Scheduled/Override | COV | Mode de fonctionnement actuel |
| LIGHT_CTRL_PROTOCOLS | Protocoles Actifs | Array | DALI/BACnet/Modbus/KNX/DMX | On Request | Protocoles de communication actifs |
| LIGHT_CTRL_FW_VERSION | Version Firmware | String | x.x.x | On Request | Version du firmware du contrôleur |
| LIGHT_CTRL_CONFIG_DATE | Date Configuration | DateTime | - | On Change | Date de la dernière modification de configuration |
| LIGHT_CTRL_ALARM_COUNT | Nombre Alarmes Actives | Integer | 0-9999 | COV | Nombre total d'alarmes actives |
| LIGHT_CTRL_WARNING_COUNT | Nombre Avertissements | Integer | 0-9999 | COV | Nombre total d'avertissements actifs |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| LIGHT_CTRL_ALM_SYSTEM | Alarme Système | Critique | STATUS = Fault | Défaut système du contrôleur |
| LIGHT_CTRL_ALM_COMM | Alarme Communication BMS | Majeure | COMM_STATUS = Offline > 5 min | Perte de communication avec le BMS |
| LIGHT_CTRL_ALM_NETWORK | Alarme Réseau | Majeure | NETWORK_STATUS = Fault | Défaut de connexion réseau |
| LIGHT_CTRL_ALM_DEVICE_FAULT | Alarme Dispositifs Défectueux | Mineure | DEVICES_FAULT > 5% | Nombre élevé de dispositifs en défaut |
| LIGHT_CTRL_ALM_CPU | Alarme Charge CPU | Mineure | CPU_LOAD > 90% | Charge processeur excessive |
| LIGHT_CTRL_ALM_MEMORY | Alarme Mémoire | Mineure | MEM_USED > 90% | Mémoire saturée |
| LIGHT_CTRL_ALM_TEMP | Alarme Température | Majeure | TEMP > 60°C | Température contrôleur excessive |
| LIGHT_CTRL_ALM_SCHEDULE | Alarme Programmation | Mineure | SCHEDULE_STATUS = Fault | Échec d'exécution d'un programme horaire |
| LIGHT_CTRL_ALM_ZONE_FAULT | Alarme Défaut Zone | Mineure | ZONE_STATUS = Fault | Une ou plusieurs zones en défaut |
| LIGHT_CTRL_ALM_POWER_LIMIT | Alarme Dépassement Limite | Majeure | POWER_TOTAL > DEMAND_LIMIT | Consommation dépasse la limite (demand response) |
| LIGHT_CTRL_ALM_CONFIG | Alarme Configuration | Mineure | Incohérence config détectée | Erreur ou incohérence dans la configuration |

## Sources
- [BACnet Link - Avi-on Labs](https://avi-on.com/products/network-accessories/bacnet-link/)
- [Understand BACnet communications for networked lighting - LEDs Magazine](https://www.ledsmagazine.com/smart-lighting-iot/article/16695631/understand-bacnet-communications-for-control-and-monitoring-of-networked-lighting)
- [DALION: DALI Room Lighting Application Controller - bacmove](https://bacmove.com/bacnet-dali-on/)
- [BACnet Integration - zencontrol](https://zencontrol.com/bacnet/)
- [LightLEEDer Advanced BACnet-IP Gateway - ILC](https://www.ilc-usa.com/LLABG)
- BACnet standard ASHRAE 135
- IEC 62386 - DALI standard series
