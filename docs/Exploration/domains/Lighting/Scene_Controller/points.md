# Points - Scene Controller

## Résumé
- **Points de mesure** : 6
- **Points de commande** : 10
- **Points d'État** : 10
- **Total** : 26

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| SCENE_ACTIVE_ID | ID Scène Active | 1 | - | 0-255 | COV | Numéro de la scène actuellement active (255=aucune) |
| SCENE_TRANSITION_PROGRESS | Progression Transition | 1 | % | 0-100 | 1 sec | Pourcentage de progression de la transition en cours |
| SCENE_BUTTON_PRESS | Bouton Pressé | 1 | - | 0-16 | COV | Numéro du bouton de scène pressé (0=aucun) |
| SCENE_RECALL_COUNT | Compteur Rappels | 1-100 | - | 0-999999 | On Change | Nombre de fois que chaque scène a été rappelée |
| SCENE_LAST_RECALL_TIME | Dernier Rappel | DateTime | - | On Change | Date/heure du dernier rappel de scène |
| SCENE_ZONES_CONTROLLED | Zones Contrôlées | 1 | - | 0-500 | On Request | Nombre de zones contrôlées par le contrôleur |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| SCENE_RECALL | Rappel Scène | 1 | - | 0-100 | Multi-State | Activation d'une scène d'éclairage (0-99, 255=off) |
| SCENE_STORE | Mémorisation Scène | 1 | - | 0-100 | Multi-State | Sauvegarde configuration actuelle dans la scène |
| SCENE_ERASE | Effacement Scène | 1 | - | 0-100 | Multi-State | Suppression d'une scène mémorisée |
| SCENE_FADE_TIME | Temps Transition Scène | 1-100 | sec | 0-60 | Analog | Durée de transition lors du rappel de scène |
| SCENE_PRIORITY | Priorité Scène | 1 | - | 1-16 | Multi-State | Niveau de priorité BACnet pour rappel de scène |
| SCENE_BUTTON_LOCK | Verrouillage Boutons | 1 | - | 0-1 | Digital | Verrouillage des boutons physiques du contrôleur |
| SCENE_BACKLIGHT | Rétroéclairage Boutons | 1 | % | 0-100 | Analog | Intensité du rétroéclairage des boutons |
| SCENE_MASTER_RAISE | Montée Globale | 1 | - | 0-1 | Digital | Augmentation globale de l'intensité de la scène |
| SCENE_MASTER_LOWER | Descente Globale | 1 | - | 0-1 | Digital | Diminution globale de l'intensité de la scène |
| SCENE_FADE_STOP | Arrêt Transition | 1 | - | 0-1 | Digital | Arrêt immédiat de la transition en cours |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| SCENE_STATUS | État Contrôleur | Enum | Ready/Transitioning/Fault/Locked | COV | État opérationnel du contrôleur de scènes |
| SCENE_CONFIG_STATUS | État Configuration Scènes | Array[100] | Configured/Empty/Invalid | On Request | État de configuration de chaque scène (0-99) |
| SCENE_BUTTON_STATUS | État Boutons | Array[16] | Normal/Pressed/Stuck/Fault | COV | État de chaque bouton physique |
| SCENE_LAST_SCENE_ID | Dernière Scène Active | Integer | 0-255 | On Change | ID de la dernière scène active avant la scène actuelle |
| SCENE_ZONES_IN_SCENE | Zones par Scène | Array[100] | 0-500 | On Request | Nombre de zones incluses dans chaque scène |
| SCENE_MODE | Mode Opératoire | Enum | Local/Remote/Locked/Override | COV | Mode de fonctionnement actuel |
| SCENE_BUTTON_LABELS | Étiquettes Boutons | Array[16] | String | On Request | Libellés configurés pour chaque bouton |
| SCENE_GROUPS_COUNT | Nombre Groupes DALI | 1 | - | 0-16 | On Request | Nombre de groupes DALI gérés (si DALI) |
| SCENE_FIRMWARE_VERSION | Version Firmware | String | x.x.x | On Request | Version du firmware du contrôleur |
| SCENE_COMM_STATUS | État Communication | Enum | Online/Offline/Fault | COV | État de communication DALI/BACnet/DMX |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| SCENE_ALM_FAULT | Alarme Défaut Contrôleur | Majeure | STATUS = Fault | Défaut système du contrôleur de scènes |
| SCENE_ALM_BUTTON | Alarme Défaut Bouton | Mineure | BUTTON_STATUS = Fault ou Stuck | Bouton défectueux ou bloqué |
| SCENE_ALM_COMM | Alarme Communication | Majeure | COMM_STATUS = Offline > 5 min | Perte de communication avec système |
| SCENE_ALM_SCENE_INVALID | Alarme Scène Invalide | Mineure | CONFIG_STATUS = Invalid | Configuration de scène corrompue ou invalide |
| SCENE_ALM_RECALL_FAIL | Alarme Échec Rappel | Mineure | Échec activation scène | Impossible d'activer la scène demandée |
| SCENE_ALM_ZONE_FAULT | Alarme Défaut Zone | Mineure | Une ou plusieurs zones ne répondent pas | Zone dans la scène en défaut |
| SCENE_ALM_TRANSITION_FAIL | Alarme Échec Transition | Mineure | Transition interrompue ou échouée | Transition de scène non complétée |

## Sources
- [DALION: DALI Room Lighting Application Controller - bacmove](https://bacmove.com/bacnet-dali-on/)
- [L-DALI: BACnet/DALI Controllers - LOYTEC](https://www.loytec.com/products/dali/56-l-dali-bacnet)
- [BACnet Integration - zencontrol](https://zencontrol.com/bacnet/)
- [DALI Scene Set Panel - Delmatic](https://delmatic.com/product/dali-scene-set-switch/)
- [LDALI-PLC4: Programmable DALI Controller - LOYTEC](https://www.loytec.com/products/dali/l-dali-wired/ldali-plc4)
- IEC 62386 - DALI scene control (Part 102, 103)
- ANSI E1.20 - RDM (Remote Device Management) for DMX
- BACnet standard ASHRAE 135
