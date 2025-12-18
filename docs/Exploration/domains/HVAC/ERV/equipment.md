# Energy Recovery Ventilator (ERV)

## Identifiant
- **Code** : ERV
- **Haystack** : `erv-equip`
- **Brick** : `brick:Energy_Recovery_Ventilator`

## Description
Système de ventilation avec récupération d'énergie qui transfère à la fois la chaleur sensible ET la chaleur latente (humidité) entre l'air extrait et l'air neuf entrant. Utilise un échangeur rotatif ou à plaques à membrane perméable.

## Fonction
Réduire la charge énergétique de ventilation en préchauffant/pré-refroidissant et en pré-humidifiant/pré-déshumidifiant l'air neuf grâce à l'énergie de l'air extrait. Améliore l'efficacité énergétique tout en maintenant une bonne qualité d'air.

## Variantes Courantes
- **ERV à roue enthalpique** : Échangeur rotatif, transfert total (chaleur + humidité)
- **ERV à plaques à membrane** : Échangeur fixe, membrane perméable à la vapeur
- **ERV avec bypass** : Désactivation estivale/hivernale si contre-productif
- **ERV intégré dans AHU** : Composant de l'AHU
- **ERV autonome** : Unité indépendante pour ventilation de zone

## Caractéristiques Techniques Typiques
- Débit d'air : 500 - 50,000 m³/h
- Efficacité sensible : 60-85%
- Efficacité totale (latente incluse) : 50-75%
- Type échangeur : Roue enthalpique, plaques à membrane
- Protocoles : BACnet, Modbus
- Points de supervision : températures/HR air neuf avant/après, air extrait avant/après, efficacité, défauts

## Localisation Typique
- Intégré dans AHU
- Local technique ventilation
- Toiture (unités autonomes)

## Relations avec Autres Équipements
- **Alimente** : AHU (air neuf préconditionné)
- **Alimenté par** : Air extrait du bâtiment
- **Contrôlé par** : DDC Controller AHU, BMS
- **Interagit avec** : Dampers (bypass), Fans, Filtres

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-3 unités
- Moyen (15 étages) : 3-10 unités
- Grand (30+ étages) : 10-30 unités

## Sources
- Haystack Project - ERV Equipment
- Brick Schema - Energy Recovery Ventilator
- BACnet Standard - Energy Recovery
- ASHRAE Standard 90.1 - Energy Recovery Requirements
