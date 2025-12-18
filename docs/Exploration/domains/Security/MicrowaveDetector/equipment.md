# Microwave Detector

## Identifiant
- **Code** : MW_DETECTOR
- **Haystack** : microwave-sensor
- **Brick** : brick:Microwave_Motion_Sensor

## Description
Détecteur de mouvement utilisant l'effet Doppler sur des ondes électromagnétiques micro-ondes (généralement 10.525 GHz). Émet des ondes qui traversent matériaux non métalliques et détecte les variations causées par le mouvement d'objets. Plus sensible que PIR mais aussi plus sujet aux fausses alarmes.

## Fonction
Détection volumétrique de mouvement par analyse Doppler, capacité de détection à travers cloisons légères, vitrages, portes non métalliques. Utilisé seul ou en combinaison avec PIR (dual-tech) pour réduction fausses alarmes.

## Variantes Courantes
- **Micro-ondes seul** : Détection pure micro-ondes
- **Dual-tech (MW + PIR)** : Combinaison avec PIR pour validation croisée
- **Micro-ondes extérieur** : Spécialisé protection périmétrique
- **Rideau micro-ondes** : Protection en nappe verticale
- **Portée réglable** : Ajustement zone de détection

## Caractéristiques Techniques Typiques
- Fréquence : 10.525 GHz (X-band) typique
- Portée : 10-30m selon modèle et réglage
- Portée réglable : Par ajustement potentiomètre
- Sensibilité : Réglable, détecte mouvements lents
- Pénétration : Traverse bois, verre, plastique, cloisons légères
- Communication : Filaire (4-wire), BUS RS-485
- Alimentation : 9-16V DC
- Montage : Mural, coin de pièce
- Protection : Détection sabotage, anti-masquage

## Localisation Typique
- Espaces avec variations thermiques importantes (où PIR moins fiable)
- Entrepôts et zones industrielles
- Zones avec cloisons vitrées
- Couloirs et passages
- Locaux techniques
- Protection périmétrique extérieure
- Espaces commerciaux

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Intrusion Alarm Panel, Power supply
- **Contrôlé par** : Intrusion Alarm Panel
- **Envoie à** : Alarm Panel (état alarme)
- **Combiné avec** : PIR Detector (dual-tech)
- **Interagit avec** : IP Camera, Siren, Alarm Keypad

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-15 détecteurs
- Moyen (15 étages) : 20-60 détecteurs
- Grand (30+ étages) : 50-150 détecteurs

## Sources
- EN 50131 - Alarm Systems Standards
- Microwave Detection Technology Standards
- Brick Schema - Motion Sensor Class
