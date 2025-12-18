# Points d'Interrupteur Connecté (Connected Switch)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 5
- **Total points état** : 4

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| power | elec power sensor | W | 0-3600 | 1min | Puissance instantanée circuit |
| energy | elec energy sensor | kWh | 0-99999 | 15min | Énergie consommée cumul |
| current | elec current sensor | A | 0-16 | 1min | Courant circuit |
| ambient_light | light level sensor | lux | 0-2000 | 5min | Luminosité ambiante (si équipé) |
| ambient_temp | zone air temp sensor | °C | 15-35 | 5min | Température ambiante (si équipé) |
| button_press_count | button press sensor | - | 0-999999 | event | Compteur appuis bouton |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| light_cmd | light cmd | - | 0/1 | Actionneur | Commande On/Off éclairage |
| dimmer_cmd | light level cmd | % | 0-100 | Actionneur | Commande variation (dimming) |
| scene_cmd | scene cmd | - | 1-16 | Actionneur | Activation scène d'éclairage |
| color_temp_cmd | light color temp cmd | K | 2700-6500 | Actionneur | Commande température couleur |
| auto_mode_cmd | auto mode cmd | - | 0/1 | Actionneur | Activation mode automatique |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| light_status | light run status | Boolean | true/false | État éclairage On/Off |
| dimmer_level | light level status | Integer | 0-100 | Niveau de variation actuel |
| occ_status | occ status | Boolean | true/false | Présence détectée (si capteur) |
| comm_fault | comm fault alarm | Boolean | true/false | Défaut communication |

## Mappings Protocoles

| Point | BACnet Object | KNX GA | DALI Command |
|-------|---------------|--------|--------------|
| power | AI:1 | 1/1/1 | Query Actual Level |
| energy | AI:2 | 1/1/2 | - |
| current | AI:3 | 1/1/3 | - |
| ambient_light | AI:4 | 1/1/4 | - |
| ambient_temp | AI:5 | 1/1/5 | - |
| light_cmd | BO:1 | 1/2/1 | DAPC / Off |
| dimmer_cmd | AO:1 | 1/2/2 | DAPC (0-254) |
| scene_cmd | MSV:1 | 1/2/3 | Go To Scene |
| color_temp_cmd | AO:2 | 1/2/4 | Set Color Temp |
| auto_mode_cmd | BO:2 | 1/2/5 | - |
| light_status | BI:1 | 1/3/1 | Query Status |
| dimmer_level | AI:6 | 1/3/2 | Query Actual Level |
| occ_status | BI:2 | 1/3/3 | - |
| comm_fault | BI:3 | 1/3/4 | - |

## Groupes KNX Typiques

| Fonction | Groupe | Type DPT |
|----------|--------|----------|
| Switch On/Off | 1/2/1 | DPT 1.001 |
| Dimming | 1/2/2 | DPT 5.001 |
| Status On/Off | 1/3/1 | DPT 1.001 |
| Status Dimmer | 1/3/2 | DPT 5.001 |
| Scene | 1/2/3 | DPT 18.001 |
| Brightness | 1/1/4 | DPT 9.004 |

## Commandes DALI

| Commande | Code | Description |
|----------|------|-------------|
| Off | 0x00 | Extinction |
| Up | 0x01 | Augmenter niveau |
| Down | 0x02 | Diminuer niveau |
| Step Up | 0x03 | Pas d'augmentation |
| Step Down | 0x04 | Pas de diminution |
| Recall Max | 0x05 | Niveau maximum |
| Recall Min | 0x06 | Niveau minimum |
| Go To Scene | 0x10-0x1F | Scène 0-15 |
| DAPC | 0xFE xx | Direct Arc Power Control |

## Scénarios d'Éclairage Typiques

| Scène | Niveau | Application |
|-------|--------|-------------|
| 1 - Full | 100% | Travail intensif |
| 2 - Working | 80% | Travail normal |
| 3 - Meeting | 60% | Réunion |
| 4 - Presentation | 30% | Présentation |
| 5 - Ambiance | 20% | Ambiance |
| 6 - Off | 0% | Extinction |

## Logique de Commande Locale

| Action utilisateur | Comportement | État résultant |
|--------------------|--------------|----------------|
| Appui court | Toggle On/Off | Inverse l'état |
| Appui long haut | Dimming up | +10% par seconde |
| Appui long bas | Dimming down | -10% par seconde |
| Double appui | Scène préférée | Niveau mémorisé |
| Triple appui | Mode manuel | Désactive auto |

## Sources
- IEC 60669 - Switches for Household and Similar Fixed Electrical Installations
- EN 15193 - Energy Performance of Buildings - Lighting
- DALI Standard (IEC 62386) - Digital Addressable Lighting Interface
- KNX Specification - Lighting Application
- Project Haystack - Lighting Switch Tags
- Brick Schema - Lighting_Switch Class
