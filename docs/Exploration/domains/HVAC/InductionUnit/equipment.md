# Induction Unit (Unité à induction)

## Identifiant
- **Code** : IU / INDU
- **Haystack** : `inductionUnit-equip`
- **Brick** : `brick:Induction_Unit`

## Description
Terminal qui utilise un jet d'air primaire à haute vitesse pour induire (aspirer) l'air de la zone à travers une batterie eau chaude ou eau glacée. Le rapport d'induction permet de traiter un grand volume d'air de zone avec un faible débit d'air primaire.

## Fonction
Conditionner l'air d'une zone avec un débit d'air primaire réduit (économie ventilateurs centraux) en induisant et traitant l'air local via batterie hydraulique. Précurseur des chilled beams actives.

## Variantes Courantes
- **Unité 2 tubes** : Chaud OU froid (changeover saisonnier)
- **Unité 4 tubes** : Chaud ET froid simultanés
- **Unité haute induction** : Ratio 1:4 ou 1:5 (air primaire : air induit)
- **Unité basse induction** : Ratio 1:2 ou 1:3

## Caractéristiques Techniques Typiques
- Débit air primaire : 20 - 100 l/s
- Ratio d'induction : 1:2 à 1:5
- Puissance batterie : 0.5 - 5 kW
- Température eau : Eau chaude 40-60°C, Eau glacée 6-12°C
- Protocoles : BACnet, Modbus (via vanne)
- Points de supervision : température zone, débit air primaire, vanne eau

## Localisation Typique
- Sous fenêtres (façade units)
- Faux plafond (moins courant)
- Principalement bâtiments anciens (années 1960-1980)

## Relations avec Autres Équipements
- **Alimente** : Zone (air conditionné)
- **Alimenté par** : AHU (air primaire haute pression), Chiller/Boiler (eau chaude/glacée)
- **Contrôlé par** : Thermostat de zone, Vanne motorisée
- **Interagit avec** : Pompes, Capteurs température zone

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-80 unités (si système à induction)
- Moyen (15 étages) : 80-300 unités
- Grand (30+ étages) : 300-1,000 unités

## Sources
- Haystack Project - Induction Unit Equipment
- Brick Schema - Induction Unit
- BACnet Standard - Terminal Equipment
- ASHRAE Handbook - Induction Systems (anciens systèmes)
