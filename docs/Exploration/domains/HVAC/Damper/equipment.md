# Damper (Registre motorisé)

## Identifiant
- **Code** : DMP / DMR
- **Haystack** : `damper-equip`
- **Brick** : `brick:Damper`

## Description
Dispositif mécanique installé dans une gaine d'air qui contrôle le débit d'air en modulant l'ouverture d'un volet. Peut être motorisé (actionneur) pour un contrôle automatique ou manuel. Permet de réguler, mélanger, ou isoler des flux d'air.

## Fonction
Contrôler les débits et mélanges d'air dans les systèmes de ventilation et climatisation. Permet le dosage air neuf/air recyclé, l'isolation de sections, et la régulation de débit.

## Variantes Courantes
- **Damper de régulation (modulating)** : Position variable 0-100%
- **Damper tout ou rien (on/off)** : Ouvert ou fermé
- **Damper air neuf/air recyclé** : Mélange économiseur
- **Damper d'extraction** : Contrôle évacuation d'air
- **Damper coupe-feu** : Sécurité incendie (fermeture automatique)
- **Damper de bypass** : Contournement de batterie ou filtre
- **Damper de zone** : Isolation ou régulation de zone

## Caractéristiques Techniques Typiques
- Taille : 150mm - 2,000mm de diamètre/côté
- Type d'actionneur : Électrique (24VAC, 230VAC), Pneumatique
- Couple actionneur : 5 - 100 Nm
- Temps d'ouverture/fermeture : 30 - 180 secondes
- Signal de commande : 0-10V, 4-20mA, contact sec, BACnet/Modbus
- Points de supervision : position (%), état ouvert/fermé, alarmes

## Localisation Typique
- Gaines d'air (air neuf, reprise, soufflage, extraction)
- Intégré dans AHU, VAV, RTU
- Plénum de faux plafond
- Conduits de désenfumage

## Relations avec Autres Équipements
- **Alimente** : N/A (contrôle flux d'air)
- **Alimenté par** : N/A (actionné par signal électrique/pneumatique)
- **Contrôlé par** : DDC Controller, Economizer Controller, BMS
- **Interagit avec** : AHU, VAV, Fans, Capteurs de température/CO2

## Quantité Typique par Bâtiment
- Petit (5 étages) : 50-150 dampers
- Moyen (15 étages) : 200-500 dampers
- Grand (30+ étages) : 500-2,000 dampers

## Sources
- Haystack Project - Damper Equipment
- Brick Schema - Damper Classes
- BACnet Standard - Damper Control
- ASHRAE Standards - Air Distribution
