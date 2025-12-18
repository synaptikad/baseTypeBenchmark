# Air Filter (Filtre à air)

## Identifiant
- **Code** : FLT / FILT
- **Haystack** : `filter-equip`
- **Brick** : `brick:Filter`

## Description
Dispositif qui capte les particules en suspension dans l'air (poussières, pollens, particules fines) pour garantir la qualité de l'air intérieur et protéger les équipements en aval. Classé selon efficacité de filtration (ISO 16890, EN779, MERV).

## Fonction
Assurer la qualité de l'air soufflé en capturant les contaminants particulaires. Protection des occupants (santé, confort) et des équipements HVAC (encrassement batteries, ventilateurs).

## Variantes Courantes
- **Filtre à poches (G4-M6)** : Filtration grossière et moyenne (ISO Coarse/ePM10)
- **Filtre à cadre rigide (F7-F9)** : Filtration fine (ISO ePM1, ePM2.5)
- **Filtre HEPA (H13-H14)** : Très haute efficacité (99.95-99.995%), salles blanches
- **Filtre à charbon actif** : Filtration moléculaire (COV, odeurs)
- **Filtre électrostatique** : Capture par charge électrique
- **Filtre à média plissé** : Compacité et surface filtrante élevée

## Caractéristiques Techniques Typiques
- Classes : ISO Coarse (G1-G4), ePM10/ePM2.5/ePM1 (M5-F9), HEPA (H10-H14)
- Efficacité : 40% - 99.995% selon classe et taille particules
- Perte de charge initiale : 50 - 250 Pa
- Perte de charge finale (colmatage) : 150 - 500 Pa
- Durée de vie : 3-12 mois selon environnement
- Points de supervision : pression différentielle (colmatage), alarme changement

## Localisation Typique
- AHU (2 ou 3 étages de filtration)
- FCU (filtre simple G4/M5)
- RTU
- Unités VRF intérieures
- Gaines d'air neuf

## Relations avec Autres Équipements
- **Alimente** : Ventilateurs, Batteries, Zones du bâtiment (air filtré)
- **Alimenté par** : N/A (élément passif)
- **Contrôlé par** : Capteur de pression différentielle, BMS (alarmes changement)
- **Interagit avec** : AHU, Fans, Dampers

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-30 filtres (2-3 par AHU/FCU)
- Moyen (15 étages) : 50-150 filtres
- Grand (30+ étages) : 200-500 filtres

## Sources
- Haystack Project - Filter Equipment
- Brick Schema - Filter Classes
- ISO 16890 - Air Filter Classification
- ASHRAE Standard 52.2 - Air Filter Testing
