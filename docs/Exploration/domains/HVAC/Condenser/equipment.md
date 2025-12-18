# Condenser (Condenseur)

## Identifiant
- **Code** : COND
- **Haystack** : `condenser-equip`
- **Brick** : `brick:Condenser`

## Description
Échangeur de chaleur qui rejette la chaleur du cycle frigorifique vers l'extérieur. Permet au fluide frigorigène de passer de l'état gazeux à l'état liquide en cédant sa chaleur à l'air (aérocondenseur) ou à l'eau (condenseur à eau).

## Fonction
Rejeter la chaleur de condensation du cycle frigorifique vers un milieu extérieur (air ou eau). Composant essentiel du côté haute pression du circuit de réfrigération.

## Variantes Courantes
- **Condenseur à air** : Refroidi par air ambiant avec ventilateurs
- **Condenseur à eau** : Refroidi par eau de tour de refroidissement
- **Condenseur évaporatif** : Combinaison air + eau pulvérisée
- **Condenseur à plaques** : Compact, eau glacée
- **Condenseur à tubes et calandre** : Grandes puissances

## Caractéristiques Techniques Typiques
- Puissance de rejet : 10 kW - 5 MW
- Température de condensation : 35-50°C (selon conditions)
- Delta T : 10-15°C (air), 5-10°C (eau)
- Type : Air-cooled, Water-cooled, Evaporative
- Protocoles : BACnet, Modbus (via contrôleur chiller)
- Points de supervision : température, pression, état ventilateurs

## Localisation Typique
- Toiture (condenseurs à air)
- Local technique (condenseurs à eau)
- Proximité des chillers

## Relations avec Autres Équipements
- **Alimente** : N/A (rejette la chaleur)
- **Alimenté par** : Compresseur (gaz chaud haute pression)
- **Contrôlé par** : Contrôleur chiller, BMS
- **Interagit avec** : Compresseur, Détendeur, Tour de refroidissement (si water-cooled)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-5 unités
- Moyen (15 étages) : 5-15 unités
- Grand (30+ étages) : 15-50 unités

## Sources
- ASHRAE Handbook - Refrigeration
- Project Haystack - Condenser Equipment
- Brick Schema - Condenser Class
- Carrier / Trane - Condenser Technical Documentation
