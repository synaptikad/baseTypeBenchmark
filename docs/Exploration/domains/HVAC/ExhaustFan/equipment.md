# Exhaust Fan (Ventilateur d'extraction)

## Identifiant
- **Code** : EF / EXHF
- **Haystack** : `exhaustFan-equip`
- **Brick** : `brick:Exhaust_Fan`

## Description
Ventilateur dédié à l'évacuation de l'air vicié ou pollué vers l'extérieur. Installé en toiture ou en gaine, il extrait l'air des zones nécessitant une ventilation spécifique (sanitaires, cuisines, parkings, locaux techniques, laboratoires).

## Fonction
Évacuer l'air vicié, humide, ou contaminé du bâtiment pour maintenir la qualité d'air intérieur et la sécurité. Contribue au contrôle de la pression et au renouvellement d'air.

## Variantes Courantes
- **Ventilateur extraction sanitaires** : WC, douches
- **Ventilateur extraction cuisines** : Hottes de cuisine (forte extraction)
- **Ventilateur extraction parkings** : Évacuation CO, désenfumage
- **Ventilateur extraction laboratoires** : Sorbonnes, locaux à risque chimique
- **Ventilateur de désenfumage** : Sécurité incendie (forte température)
- **Ventilateur toiture** : Évacuation générale bâtiment

## Caractéristiques Techniques Typiques
- Débit d'air : 500 - 50,000 m³/h
- Pression statique : 100 - 800 Pa
- Type : Centrifuge, axial, hélicoïde
- Vitesse : Fixe ou variable (VFD)
- Protocoles : BACnet, Modbus (via VFD ou contrôleur)
- Points de supervision : état marche/arrêt, vitesse, débit, alarmes

## Localisation Typique
- Toiture
- Locaux techniques
- Gaines d'extraction verticales
- Parkings

## Relations avec Autres Équipements
- **Alimente** : Extérieur (air évacué)
- **Alimenté par** : Zones à ventiler (air vicié)
- **Contrôlé par** : DDC Controller, BMS, Interrupteurs locaux, Détection CO/CO2
- **Interagit avec** : MAU/AHU (équilibrage débits), Dampers, Capteurs qualité air

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-20 ventilateurs
- Moyen (15 étages) : 20-60 ventilateurs
- Grand (30+ étages) : 60-200 ventilateurs

## Sources
- Haystack Project - Exhaust Fan Equipment
- Brick Schema - Exhaust Fan Classes
- BACnet Standard - Fan Control
- ASHRAE Standard 62.1 - Exhaust Requirements
