# Pressure Reducing Valve

## Identifiant
- **Code** : PRV
- **Haystack** : `water`, `pressure`, `reducing`, `valve`, `equip`
- **Brick** : `brick:Pressure_Reducing_Valve`

## Description
Vanne régulatrice de pression qui réduit et stabilise la pression d'eau en aval à une valeur de consigne fixe. Protège les installations contre les surpressions du réseau urbain et assure une pression uniforme dans le bâtiment.

## Fonction
Réduire automatiquement la pression d'entrée élevée (réseau urbain, étages inférieurs) à une pression de service adaptée (2-4 bars) pour protéger les équipements, réduire le bruit, limiter les fuites et assurer le confort d'utilisation.

## Variantes Courantes
- **Réducteur à action directe** : Ressort et membrane, sans énergie externe
- **Réducteur piloté** : Régulation précise avec pilote externe
- **Réducteur motorisé** : Contrôle électrique de la consigne
- **Station de réduction par étage** : Cascade de réducteurs pour immeubles de grande hauteur

## Caractéristiques Techniques Typiques
- Diamètre : DN15 à DN150
- Pression amont : 3-16 bars
- Pression aval réglable : 1-6 bars
- Précision : ±0.2 à 0.5 bar
- Débit : Fonction du diamètre (Cv/Kv)
- Communication : Capteur pression aval (modèles supervisés)

## Localisation Typique
- Entrée bâtiment (après compteur)
- Étages tous les 5-10 niveaux (immeubles de grande hauteur)
- Départ circuits sensibles
- Local technique eau

## Relations avec Autres Équipements
- **Alimente** : Réseau de distribution interne
- **Alimenté par** : Réseau urbain, Booster Pump (étages supérieurs)
- **Contrôlé par** : Auto-régulation mécanique ou superviseur (modèles intelligents)
- **Associé à** : Pressure Sensor (amont/aval), manomètre, soupape sécurité

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 réducteurs (entrée + circuits)
- Moyen (15 étages) : 2-4 réducteurs (entrée + étagement par zones)
- Grand (30+ étages) : 4-10 réducteurs (cascade verticale tous les 5-8 étages)

## Sources
- Haystack Project - Valve equipment
- Brick Schema - Pressure_Reducing_Valve class
- ASHRAE Handbook - Plumbing systems
- Plumbing codes and pressure regulations
