# Unit Ventilator (Ventiloconvecteur)

## Identifiant
- **Code** : UV / UVNT
- **Haystack** : `unitVentilator-equip`
- **Brick** : `brick:Unit_Ventilator`

## Description
Terminal autonome qui aspire de l'air extérieur et/ou de l'air de la zone, le filtre, le conditionne via des batteries (chaud/froid), et le souffle dans la zone. Combine ventilation et conditionnement d'air en un seul équipement de zone.

## Fonction
Assurer simultanément la ventilation (apport d'air neuf contrôlé) et le conditionnement thermique d'une zone. Utilisé principalement dans les écoles, salles de classe, et petits bureaux.

## Variantes Courantes
- **UV horizontal** : Installé sous fenêtre ou encastré
- **UV vertical** : Au sol ou mural
- **UV 2 tubes** : Chaud OU froid (changeover)
- **UV 4 tubes** : Chaud ET froid simultanés
- **UV avec économiseur** : Modulation air neuf/recyclé
- **UV électrique** : Résistances électriques pour chauffage

## Caractéristiques Techniques Typiques
- Débit d'air total : 300 - 3,000 m³/h
- Air neuf : 20-100% du débit (modulable)
- Puissance : 1 - 15 kW
- Batterie : Eau chaude, eau glacée, électrique
- Protocoles : BACnet, Modbus, LON
- Points de supervision : température zone, débit air neuf, vitesse ventilateur, vannes

## Localisation Typique
- Salles de classe (écoles)
- Bureaux individuels
- Petites salles de réunion
- Sous fenêtres ou muraux

## Relations avec Autres Équipements
- **Alimente** : Zone (air neuf conditionné)
- **Alimenté par** : Chiller (eau glacée), Boiler/Heat Pump (eau chaude), Air extérieur
- **Contrôlé par** : Thermostat de zone, Contrôleur local, BMS
- **Interagit avec** : Dampers (air neuf/recyclé), Vannes, Filtres

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-50 unités (selon usage)
- Moyen (15 étages) : 50-150 unités
- Grand (30+ étages) : 150-500 unités

## Sources
- Haystack Project - Unit Ventilator Equipment
- Brick Schema - Unit Ventilator
- BACnet Standard - Unit Ventilator Control
- ASHRAE Handbook - Unit Ventilators
