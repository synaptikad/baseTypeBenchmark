# Fire Damper

## Identifiant
- **Code** : FIRE-DMP
- **Haystack** : fire-damper
- **Brick** : brick:Fire_Damper

## Description
Volet coupe-feu automatique installé dans les conduits de ventilation traversant les parois coupe-feu. Se ferme automatiquement en cas d'incendie pour empêcher la propagation du feu et des fumées à travers les gaines techniques.

## Fonction
Assure le compartimentage du bâtiment en maintenant l'intégrité des parois coupe-feu traversées par les réseaux de ventilation. Se déclenche par fusion d'un élément thermosensible (fusible) à une température définie ou par commande électrique.

## Variantes Courantes
- **À fusible thermique** : Déclenchement automatique par fusion à 72°C
- **Motorisé commandé** : Fermeture électrique sur ordre du FACP
- **Combiné feu/fumée** : Double fonction coupe-feu et désenfumage
- **Circulaire** : Pour conduits ronds
- **Rectangulaire** : Pour conduits rectangulaires
- **Multi-lames** : Pour grandes sections
- **Avec ressort de rappel** : Fermeture mécanique garantie

## Caractéristiques Techniques Typiques
- Résistance au feu : EI 30, EI 60, EI 90, EI 120 minutes
- Température de fusion : 72°C (fusible standard)
- Dimensions : De Ø125mm à 2000x2000mm
- Actionneur : Fusible thermique ou moteur 24V DC
- Position normale : Ouvert (passage d'air)
- Position sécurité : Fermé (étanche au feu)
- Retour d'information : Contact de position (fermé/ouvert)
- Certification : EN 15650 (Europe), UL 555 (USA)
- Installation : Dans la paroi ou adjacente (<200mm)

## Localisation Typique
- Traversées de parois coupe-feu
- Séparation entre compartiments
- Gaines techniques verticales
- Réseaux de ventilation
- Faux-plafonds techniques
- Locaux à risque particulier
- Entre niveaux (planchers coupe-feu)

## Relations avec Autres Équipements
- **Alimente** : N/A (dispositif passif/actif de compartimentage)
- **Alimenté par** : Fire Alarm Panel (si motorisé) ou fusion thermique
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI) ou détection locale température
- **Associé à** : AHU (Air Handling Unit), Extract Fan, Supply Fan
- **Communique avec** : Building Management System (BMS) via contact sec

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 30-60 unités
- Moyen (15 étages, 15000 m²) : 150-300 unités
- Grand (30+ étages, 50000 m²) : 500-1000 unités

## Sources
- EN 15650: Ventilation for buildings - Fire dampers
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- Règlement de sécurité contre l'incendie
- NFPA 80: Standard for Fire Doors and Other Opening Protectives
