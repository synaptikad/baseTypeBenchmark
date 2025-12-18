# Heat Detector

## Identifiant
- **Code** : HEAT-DET
- **Haystack** : heat-detector
- **Brick** : brick:Heat_Detector

## Description
Dispositif de détection automatique qui réagit à l'élévation de température dans un espace. Déclenche une alarme soit à un seuil fixe de température, soit en fonction du taux de montée en température.

## Fonction
Détecte les incendies en surveillant la température ambiante. Particulièrement adapté aux environnements où les détecteurs de fumée peuvent générer de fausses alarmes (cuisines, zones poussiéreuses, garages).

## Variantes Courantes
- **Détecteur à seuil fixe** : Alarme à une température prédéfinie (typiquement 58°C ou 68°C)
- **Détecteur thermovélocimétrique** : Détecte une montée rapide de température
- **Détecteur combiné** : Combine seuil fixe et taux de montée
- **Détecteur linéaire** : Câble détecteur de chaleur pour grandes surfaces
- **Détecteur adressable** : Communique température et identité au panneau

## Caractéristiques Techniques Typiques
- Alimentation : 12-24V DC (via boucle d'alarme)
- Seuil de déclenchement : 58°C, 68°C, 88°C selon classe
- Taux de montée : 8-10°C/minute pour thermovélocimétrique
- Zone de couverture : 20-50 m² selon hauteur
- Température ambiante : -20°C à +60°C
- Certification : EN 54-5 (Europe), UL 521 (USA)
- Temps de réponse : <60 secondes

## Localisation Typique
- Cuisines et offices
- Garages et parkings
- Chaufferies et locaux techniques
- Zones de stockage poussiéreuses
- Entrepôts
- Ateliers de maintenance
- Zones fumeurs (extérieures couvertes)

## Relations avec Autres Équipements
- **Alimente** : N/A (dispositif de détection)
- **Alimenté par** : Fire Alarm Panel (via boucle de détection)
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI)
- **Déclenche** : Sounder, Beacon, Fire Suppression System
- **Communique avec** : Building Management System (BMS)

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 20-40 unités
- Moyen (15 étages, 15000 m²) : 80-150 unités
- Grand (30+ étages, 50000 m²) : 200-400 unités

## Sources
- EN 54-5: Fire detection and fire alarm systems - Heat detectors
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- NFPA 72: National Fire Alarm and Signaling Code
