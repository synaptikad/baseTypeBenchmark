# Condensing Unit (Groupe de condensation)

## Identifiant
- **Code** : CU / COND
- **Haystack** : `condensingUnit-equip`
- **Brick** : `brick:Condensing_Unit`

## Description
Ensemble compresseur + condenseur installé à l'extérieur qui rejette la chaleur du cycle frigorifique vers l'air ambiant. S'associe avec un évaporateur intérieur pour former un système split ou multi-split à détente directe (DX).

## Fonction
Comprimer le fluide frigorigène et rejeter la chaleur de condensation vers l'extérieur. Composant extérieur d'un système split pour climatisation ou réfrigération.

## Variantes Courantes
- **Groupe mono-split** : Un seul évaporateur intérieur
- **Groupe multi-split** : Plusieurs évaporateurs intérieurs
- **Groupe scroll** : Compresseur scroll (résidentiel, petit tertiaire)
- **Groupe à vis** : Compresseur à vis (moyen/grand tertiaire)
- **Groupe inverter** : Vitesse variable pour modulation capacité
- **Groupe réversible** : Pompe à chaleur air-air

## Caractéristiques Techniques Typiques
- Puissance frigorifique : 5 kW - 200 kW
- Type compresseur : Scroll, piston, vis
- Fluide frigorigène : R410A, R32, R1234ze, R513A
- Condenseur : Refroidissement par air (ventilateurs axiaux)
- EER : 2.5 - 4.0
- Protocoles : BACnet, Modbus, protocole propriétaire
- Points de supervision : état compresseur, pressions HP/BP, températures, alarmes

## Localisation Typique
- Toiture
- Sol extérieur (terrasse, jardin)
- Façade (support mural)

## Relations avec Autres Équipements
- **Alimente** : Évaporateurs intérieurs (split units, FCU DX)
- **Alimenté par** : Réseau électrique
- **Contrôlé par** : Contrôleur intégré, Télécommande, BMS (via gateway)
- **Interagit avec** : Détendeurs, Thermostats de zone

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-20 unités
- Moyen (15 étages) : 20-80 unités
- Grand (30+ étages) : 80-300 unités

## Sources
- Haystack Project - Condensing Unit Equipment
- Brick Schema - Condensing Unit
- BACnet Integration - DX Systems
- ASHRAE Handbook - DX Equipment
