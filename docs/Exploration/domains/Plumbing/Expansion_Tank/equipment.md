# Expansion Tank

## Identifiant
- **Code** : EXP-TANK
- **Haystack** : `water`, `expansion`, `tank`, `equip`
- **Brick** : `brick:Expansion_Tank`

## Description
Vase d'expansion ou ballon de détente qui absorbe les variations de volume de l'eau dues aux changements de température dans les circuits fermés d'eau chaude sanitaire. Protège les installations contre les surpressions.

## Fonction
Absorber la dilatation thermique de l'eau lors du chauffage dans les circuits fermés, maintenir la pression du système dans les limites acceptables, protéger contre les coups de bélier, et éviter l'ouverture intempestive de la soupape de sécurité.

## Variantes Courantes
- **Vase à membrane** : Vessie interne séparant eau/azote, pré-gonflé
- **Vase ouvert** : Raccordé atmosphère (obsolète sauf cas particuliers)
- **Vase sous pression** : Haute pression pour circuits spéciaux
- **Vase sanitaire** : Spécial eau potable avec membrane alimentaire

## Caractéristiques Techniques Typiques
- Volume : 8 L à 500 L selon taille installation
- Pression de pré-gonflage : 1.5-4 bars (fonction hauteur statique)
- Pression de service : 3-10 bars
- Température max : 70-99°C selon modèle
- Membrane : EPDM alimentaire pour circuits ECS
- Raccordement : Taraudé ou bridé selon diamètre

## Localisation Typique
- Chaufferie à proximité DHW Tank
- Local technique ECS
- Sur circuit retour pompe circulation
- Gaine technique

## Relations avec Autres Équipements
- **Alimente** : N/A (équipement passif)
- **Alimenté par** : Raccordé circuit ECS fermé
- **Contrôlé par** : N/A (fonctionnement passif)
- **Associé à** : DHW Tank, soupape sécurité, Pressure Sensor, manomètre

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 vases (12-35 L)
- Moyen (15 étages) : 2-4 vases (35-100 L par circuit)
- Grand (30+ étages) : 4-8 vases (100-300 L) par zone hydraulique

## Sources
- Haystack Project - Tank equipment
- Brick Schema - Expansion_Tank class
- EN 12828 - Heating systems design
- Plumbing codes - Pressure relief and expansion
