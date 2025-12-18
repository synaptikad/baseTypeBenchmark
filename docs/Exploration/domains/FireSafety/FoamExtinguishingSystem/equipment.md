# Foam Extinguishing System

## Identifiant
- **Code** : FOAM-EXT
- **Haystack** : foam-system
- **Brick** : N/A

## Description
Système d'extinction automatique utilisant de la mousse (mélange eau + émulseur) pour éteindre les feux de liquides inflammables. La mousse forme une couche isolante qui étouffe le feu et empêche les vapeurs inflammables. Utilisé principalement dans les zones à risques d'hydrocarbures.

## Fonction
Détecte et supprime les incendies de liquides inflammables (classe B) en créant une couverture de mousse qui sépare le combustible de l'oxygène. Particulièrement efficace sur les feux de nappes de liquides inflammables.

## Variantes Courantes
- **À bas foisonnement** : Mousse dense, feux de nappes
- **À moyen foisonnement** : Polyvalent, stockages et process
- **À haut foisonnement** : Mousse légère, inondation de volume
- **AFFF (Aqueous Film Forming Foam)** : Film aqueux, feux hydrocarbures
- **Mousse protéinique** : Base protéines, feux d'hydrocarbures
- **Déluge** : Activation simultanée de la zone
- **Sprinkler mousse** : Têtes sprinkler + proportionneur mousse

## Caractéristiques Techniques Typiques
- Taux de foisonnement : 4 à 1000 selon application
- Concentration émulseur : 1-6% selon type de mousse
- Débit : Variable selon surface à protéger
- Temps de décharge : 5-15 minutes
- Réservoir émulseur : 100-5000 litres
- Proportionneur : Venturi, pompe doseuse, bladder
- Génération mousse : Sprinkler, buses, générateurs
- Certification : EN 13565 (Europe), NFPA 11 (USA)

## Localisation Typique
- Parkings souterrains
- Zones de stockage hydrocarbures
- Hangars d'aviation
- Plateformes de chargement carburant
- Transformateurs électriques à bain d'huile
- Locaux de stockage chimiques inflammables
- Cuisines industrielles (classe F avec agent spécifique)

## Relations avec Autres Équipements
- **Alimente** : N/A (système d'extinction)
- **Alimenté par** : Fire Pump, réservoir eau + émulseur
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI), panneau dédié extinction
- **Déclenché par** : Smoke Detector, Heat Detector, Flame Detector, Manual activation
- **Déclenche** : Arrêt ventilation, coupure process
- **Communique avec** : Building Management System (BMS)

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 0-1 système (parking)
- Moyen (15 étages, 15000 m²) : 1-2 systèmes (parkings)
- Grand (30+ étages, 50000 m²) : 2-5 systèmes (parkings multi-niveaux)

## Sources
- EN 13565: Fixed firefighting systems - Foam systems
- NFPA 11: Standard for Low-, Medium-, and High-Expansion Foam
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- Règle APSAD R12: Extinction automatique à mousse
