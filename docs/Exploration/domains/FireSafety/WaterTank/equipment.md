# Water Tank

## Identifiant
- **Code** : FIRE-TANK
- **Haystack** : water-tank avec tag fire
- **Brick** : brick:Fire_Water_Tank

## Description
Réservoir d'eau dédié à la réserve incendie, alimentant le système sprinkler et les RIA. Capacité calculée selon les besoins hydrauliques et la durée d'autonomie requise. Équipé de sondes de niveau supervisées.

## Fonction
Stocke le volume d'eau nécessaire pour assurer l'extinction pendant la durée réglementaire (30 à 90 minutes selon classification du risque). Garantit l'autonomie du système en cas d'indisponibilité du réseau de ville.

## Variantes Courantes
- **Enterré béton** : Sous le bâtiment
- **Aérien acier** : En toiture ou local technique
- **Enterré polyéthylène** : Préfabriqué
- **Compartimenté** : Séparation incendie / autres usages
- **Sous pression** : Avec vessie et compresseur
- **Gravitaire** : Surélévation pour pression naturelle

## Caractéristiques Techniques Typiques
- Capacité : 30-500 m³ selon bâtiment et règlement
- Matériau : Béton, acier inox, polyéthylène
- Sondes de niveau : 3 niveaux (bas, normal, haut)
- Température : Hors gel (calorifugé ou enterré)
- Remplissage : Automatique depuis réseau ville
- Supervision : Niveau bas, niveau très bas, défaut remplissage
- Aspiration pompe : Crépine + clapet anti-retour
- Certification : Conforme EN 12845, NFPA 22

## Localisation Typique
- Sous-sol du bâtiment
- Vide sanitaire
- Enterré extérieur (zone accessible pompiers)
- Toiture (réservoirs haute pression)
- Local technique dédié

## Relations avec Autres Équipements
- **Alimente** : Fire Pump (aspiration)
- **Alimenté par** : Réseau d'eau de ville (remplissage automatique)
- **Contrôlé par** : Fire Pump Controller
- **Surveille** : Level Sensor, Temperature Sensor
- **Communique avec** : Fire Alarm Panel (FACP/CMSI), Building Management System (BMS)
- **Associé à** : Fire Pump, Sprinkler System

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 0-1 réservoir (30-60 m³)
- Moyen (15 étages, 15000 m²) : 1 réservoir (100-200 m³)
- Grand (30+ étages, 50000 m²) : 1-2 réservoirs (300-500 m³)

## Sources
- EN 12845: Fixed firefighting systems - Automatic sprinkler systems
- NFPA 22: Standard for Water Tanks for Private Fire Protection
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- Règle APSAD R1: Extinction automatique à eau type sprinkler
