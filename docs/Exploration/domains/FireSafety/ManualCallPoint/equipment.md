# Manual Call Point

## Identifiant
- **Code** : MCP
- **Haystack** : manual-pull-station
- **Brick** : brick:Manual_Pull_Station

## Description
Déclencheur manuel d'alarme incendie permettant à toute personne détectant un début d'incendie d'activer l'alarme générale. Équipement de couleur rouge avec vitre brisable ou membrane à enfoncer.

## Fonction
Permet le déclenchement manuel immédiat de l'alarme incendie par les occupants du bâtiment. Constitue un moyen d'alerte prioritaire et obligatoire dans tous les systèmes de sécurité incendie.

## Variantes Courantes
- **Type A vitre brisable** : Vitre à casser pour déclencher l'alarme
- **Type B à membrane** : Membrane souple à enfoncer (sans bris de verre)
- **Réarmable sur site** : Possibilité de réarmer sans changer de pièce
- **Avec couvercle de protection** : Évite les déclenchements accidentels
- **Adressable** : Identifie le point précis de déclenchement
- **Conventionnel** : Signal zone sans identification individuelle

## Caractéristiques Techniques Typiques
- Alimentation : 24V DC (via boucle d'alarme)
- Couleur : Rouge normalisé (RAL 3000)
- Force d'activation : 15-50 N selon type
- Résistance aux chocs : IK07-IK10
- Indice de protection : IP24-IP65
- Certification : EN 54-11 (Europe), UL 38 (USA)
- LED d'état : Indication de déclenchement
- Contact de sortie : Contact sec ou signal adressable

## Localisation Typique
- Sorties de secours et issues
- Cheminements d'évacuation
- Paliers d'escaliers (chaque niveau)
- Proximité des sorties de zones
- Entrées principales
- Couloirs principaux (tous les 30-40 mètres)
- Locaux à risque

## Relations avec Autres Équipements
- **Alimente** : N/A (dispositif d'activation manuelle)
- **Alimenté par** : Fire Alarm Panel (via boucle de détection)
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI)
- **Déclenche** : Alarme générale, Sounder, Beacon, évacuation
- **Communique avec** : Building Management System (BMS)

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 15-25 unités
- Moyen (15 étages, 15000 m²) : 60-100 unités
- Grand (30+ étages, 50000 m²) : 150-300 unités

## Sources
- EN 54-11: Fire detection and fire alarm systems - Manual call points
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- NFPA 72: National Fire Alarm and Signaling Code
- Règlement de sécurité contre l'incendie
