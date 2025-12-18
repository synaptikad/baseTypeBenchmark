# Cooling Tower (Tour de Refroidissement)

## Identifiant
- **Code** : CT / CDW
- **Haystack** : `coolingTower-equip`
- **Brick** : `brick:Cooling_Tower`

## Description
Équipement de rejet de chaleur qui refroidit l'eau du circuit condenseur du chiller en utilisant l'évaporation partielle de l'eau et le contact avec l'air ambiant. Permet au chiller d'évacuer la chaleur extraite du bâtiment.

## Fonction
Refroidir l'eau du condenseur du chiller (typiquement de 35°C à 30°C) pour maintenir les performances du cycle frigorifique. Essentiel pour les chillers refroidis par eau (water-cooled chillers).

## Variantes Courantes
- **Tour ouverte** : Eau en contact direct avec l'air (circuit ouvert)
- **Tour fermée (Dry Cooler hybride)** : Échangeur fermé + évaporation extérieure
- **Tour à tirage naturel** : Convection naturelle (rare en bâtiment)
- **Tour à tirage mécanique forcé** : Ventilateurs soufflants
- **Tour à tirage mécanique induit** : Ventilateurs aspirants (sur le dessus)
- **Tour modulante** : VFD sur ventilateurs pour optimisation énergétique

## Caractéristiques Techniques Typiques
- Puissance dissipée : 200 kW - 10 MW
- Débit d'eau : 50 - 1,000 m³/h
- Nombre de cellules : 1 - 8 cellules modulables
- Approche : 3-5°C (écart entre T° eau sortie et T° humide air)
- Pertes par évaporation : 1-2% du débit circulé
- Protocoles : BACnet, Modbus
- Points de supervision : températures eau entrée/sortie, vitesse ventilateurs, débit, alarmes

## Localisation Typique
- Toiture du bâtiment
- Sol extérieur (à proximité de la chaufferie/centrale)
- Zone avec ventilation libre

## Relations avec Autres Équipements
- **Alimente** : Chiller (circuit condenseur)
- **Alimenté par** : Pompes tour (condenser water pumps), Réseau eau d'appoint
- **Contrôlé par** : Plant Controller, BMS
- **Interagit avec** : Vannes, VFD ventilateurs, Système de traitement d'eau

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 unités
- Moyen (15 étages) : 2-4 unités
- Grand (30+ étages) : 4-8 unités (ou multi-cellules)

## Sources
- Haystack Project - Condenser Water Loop
- Brick Schema - Cooling Tower Equipment
- BACnet Standard - Central Plant
- ASHRAE Handbook - Cooling Towers
