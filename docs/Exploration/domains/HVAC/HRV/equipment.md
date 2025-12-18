# Heat Recovery Ventilator (HRV)

## Identifiant
- **Code** : HRV
- **Haystack** : `hrv-equip`
- **Brick** : `brick:Heat_Recovery_Ventilator`

## Description
Système de ventilation avec récupération de chaleur sensible uniquement (pas d'humidité) entre l'air extrait et l'air neuf entrant. Utilise un échangeur à plaques ou rotatif imperméable à la vapeur d'eau.

## Fonction
Réduire la charge énergétique de ventilation en préchauffant (hiver) ou pré-refroidissant (été) l'air neuf grâce à l'air extrait, sans transfert d'humidité. Efficace dans les climats où le contrôle d'humidité n'est pas critique.

## Variantes Courantes
- **HRV à plaques fixes** : Échangeur contre-courant, pas de pièces mobiles
- **HRV à roue thermique** : Roue imperméable à la vapeur, transfert thermique uniquement
- **HRV avec bypass** : Désactivation si conditions extérieures favorables
- **HRV intégré dans AHU** : Composant de l'AHU
- **HRV autonome** : Unité indépendante résidentielle ou petit tertiaire

## Caractéristiques Techniques Typiques
- Débit d'air : 300 - 30,000 m³/h
- Efficacité sensible : 60-90%
- Pas de transfert d'humidité (contrairement à ERV)
- Type échangeur : Plaques contre-courant, roue thermique
- Protocoles : BACnet, Modbus
- Points de supervision : températures air neuf avant/après, air extrait avant/après, efficacité, défauts

## Localisation Typique
- Intégré dans AHU
- Local technique ventilation
- Logements individuels (résidentiel)
- Toiture

## Relations avec Autres Équipements
- **Alimente** : AHU (air neuf préchauffé/pré-refroidi)
- **Alimenté par** : Air extrait du bâtiment
- **Contrôlé par** : DDC Controller AHU, BMS
- **Interagit avec** : Dampers (bypass), Fans, Filtres

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-3 unités
- Moyen (15 étages) : 3-10 unités
- Grand (30+ étages) : 10-30 unités

## Sources
- Haystack Project - HRV Equipment
- Brick Schema - Heat Recovery Ventilator
- BACnet Standard - Heat Recovery
- ASHRAE Handbook - Heat Recovery Systems
