# Fan (Ventilateur)

## Identifiant
- **Code** : FAN
- **Haystack** : `fan-equip`
- **Brick** : `brick:Fan`

## Description
Équipement mécanique qui déplace l'air dans le système HVAC. Peut être intégré dans un équipement (AHU, FCU) ou autonome (ventilateur d'extraction, de soufflage). À vitesse fixe ou variable (VFD).

## Fonction
Assurer le mouvement de l'air dans les systèmes de ventilation et de conditionnement d'air. Maintenir les débits et pressions nécessaires au confort et à la qualité d'air.

## Variantes Courantes
- **Ventilateur de soufflage (Supply Fan)** : Insuffle l'air traité dans le bâtiment
- **Ventilateur de reprise (Return Fan)** : Aspire l'air vicié des zones
- **Ventilateur d'extraction (Exhaust Fan)** : Évacue l'air vers l'extérieur
- **Ventilateur centrifuge** : Haute pression, utilisé dans AHU
- **Ventilateur axial** : Faible pression, ventilation générale
- **Ventilateur EC** : Moteur électronique à commutation (économe)

## Caractéristiques Techniques Typiques
- Débit : 500 - 100,000 m³/h
- Pression statique : 50 - 2,500 Pa
- Puissance moteur : 0.2 - 100 kW
- Vitesse : Fixe ou variable (VFD)
- Protocoles : BACnet, Modbus (via VFD ou contrôleur)
- Points de supervision : état, vitesse, débit, pression, courant moteur, alarmes

## Localisation Typique
- Intégré dans AHU, FCU, Rooftop Units
- Toiture (ventilateurs d'extraction)
- Gaines techniques (ventilateurs de désenfumage)
- Locaux techniques (ventilateurs autonomes)

## Relations avec Autres Équipements
- **Alimente** : Réseau de gaines, Zones du bâtiment
- **Alimenté par** : AHU (si intégré), Réseau électrique
- **Contrôlé par** : VFD, DDC Controller, BMS
- **Interagit avec** : Dampers, Capteurs de pression, Filtres

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-30 ventilateurs
- Moyen (15 étages) : 50-150 ventilateurs
- Grand (30+ étages) : 200-500 ventilateurs

## Sources
- Haystack Project - Fan Equipment
- Brick Schema - Fan Classes
- BACnet Standard - Fan Control
- ASHRAE Handbook - Air-Handling and Distribution
