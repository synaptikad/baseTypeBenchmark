# Fan Coil Unit (FCU)

## Identifiant
- **Code** : FCU
- **Haystack** : `fcu-equip`
- **Brick** : `brick:Fan_Coil_Unit`

## Description
Terminal HVAC compact qui conditionne l'air d'une zone locale en faisant circuler l'air de la pièce à travers une batterie alimentée en eau chaude et/ou eau glacée. Comprend un ventilateur, une ou deux batteries, et un filtre.

## Fonction
Assurer le conditionnement d'air (chaud/froid) d'une zone individuelle (bureau, chambre d'hôtel, salle de réunion) en recyclant principalement l'air de la zone avec apport d'air neuf minimal ou externe.

## Variantes Courantes
- **FCU 2 tubes** : Une batterie, chaud OU froid (changeover saisonnier)
- **FCU 4 tubes** : Deux batteries indépendantes, chaud ET froid simultanément
- **FCU horizontal** : Installé en faux plafond
- **FCU vertical** : Au sol ou encastré (facade units)
- **FCU console** : Sous fenêtre, visible
- **FCU cassette** : Intégré au plafond (4 voies)

## Caractéristiques Techniques Typiques
- Puissance : 1 - 15 kW
- Débit d'air : 200 - 2,000 m³/h
- Vitesses ventilateur : 2-3 vitesses ou variable continu
- Alimentation : Eau chaude/glacée (2 ou 4 tubes)
- Protocoles : BACnet, Modbus, LON (via contrôleur)
- Points de supervision : température zone, vitesse ventilateur, état vanne, alarmes

## Localisation Typique
- Bureaux individuels ou open space
- Chambres d'hôtel
- Salles de réunion
- Appartements (résidentiel haut de gamme)
- Au plafond, au sol, ou encastré

## Relations avec Autres Équipements
- **Alimente** : Zone locale (air conditionné)
- **Alimenté par** : Chiller (eau glacée), Boiler/Heat Pump (eau chaude)
- **Contrôlé par** : Thermostat de zone, Contrôleur local
- **Interagit avec** : Vannes motorisées, VFD ventilateur

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-100 unités
- Moyen (15 étages) : 200-500 unités
- Grand (30+ étages) : 500-2,000 unités

## Sources
- Haystack Project - FCU Equipment
- Brick Schema - Fan Coil Unit
- BACnet Standard - Zone Terminal Equipment
- ASHRAE Handbook - Fan Coil Systems
