# Dual Technology Detector

## Identifiant
- **Code** : DUAL_TECH_DETECTOR
- **Haystack** : dual-tech-sensor
- **Brick** : brick:Dual_Technology_Motion_Sensor

## Description
Détecteur de mouvement combinant deux technologies différentes (généralement PIR passif infrarouge et micro-ondes actif) dans un même boîtier. Requiert détection simultanée par les deux technologies pour déclencher une alarme, réduisant drastiquement les fausses alarmes tout en maintenant une haute fiabilité de détection.

## Fonction
Détection de mouvement avec validation croisée entre deux technologies indépendantes. Algorithme de corrélation AND ou OR configurable. Compensation mutuelle des faiblesses de chaque technologie. Protection volumétrique haute fiabilité.

## Variantes Courantes
- **PIR + Micro-ondes** : Combinaison la plus courante
- **PIR + Détection choc** : Pour protection vitrages
- **Tri-tech** : Trois technologies (PIR + MW + autre)
- **Dual-tech extérieur** : Spécialisé protection périmètre
- **Dual-tech avec caméra** : Vérification visuelle intégrée

## Caractéristiques Techniques Typiques
- Technologies : PIR (passif infrarouge) + Microwave (10.525 GHz)
- Portée PIR : 12-15m typique
- Portée MW : 15-20m réglable
- Logique : AND (les deux doivent détecter) ou OR (configurable)
- Angle couverture : 90-110° horizontal
- Immunité animaux : jusqu'à 15-25kg
- Anti-masquage : Détection occultation
- Communication : Filaire (4-6 wire), sans fil 868MHz
- Alimentation : 9-16V DC
- Sensibilité : Réglable indépendamment par technologie
- Montage : Mural coin ou mur, hauteur 2-2.4m

## Localisation Typique
- Zones nécessitant haute fiabilité et faibles fausses alarmes
- Entrepôts et zones industrielles
- Espaces commerciaux
- Salles serveurs critiques
- Zones avec conditions environnementales variables
- Musées et espaces patrimoniaux
- Laboratoires

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Intrusion Alarm Panel, Power supply
- **Contrôlé par** : Intrusion Alarm Panel
- **Envoie à** : Alarm Panel (état alarme)
- **Interagit avec** : IP Camera (vérification), Siren, Lighting Controller

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-20 détecteurs
- Moyen (15 étages) : 30-80 détecteurs
- Grand (30+ étages) : 80-200 détecteurs

## Sources
- EN 50131-2-4 - PIR Detectors Requirements
- EN 50131-2-6 - Combined Detectors
- Brick Schema - Motion Sensor Class
