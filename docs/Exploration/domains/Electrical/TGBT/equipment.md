# TGBT (Tableau Général Basse Tension / Main Low Voltage Switchboard)

## Identifiant
- **Code** : TGBT
- **Haystack** : elec-meter, switchgear
- **Brick** : Switchgear, Electrical_Meter

## Description
Le TGBT est le point central de distribution électrique basse tension d'un bâtiment. Il reçoit l'alimentation depuis le poste de transformation et redistribue l'électricité vers les différents tableaux divisionnaires et circuits terminaux. C'est l'équipement maître de la distribution électrique d'un bâtiment.

## Fonction
Centralise, protège et distribue l'énergie électrique basse tension vers l'ensemble des circuits du bâtiment. Intègre généralement des fonctions de mesure d'énergie globale et de supervision de l'état de distribution.

## Variantes Courantes
- **TGBT Principal** : Distribution générale du bâtiment
- **TGBT Secours** : Alimenté par le groupe électrogène ou l'onduleur
- **TGBT par Usage** : Distribution dédiée (éclairage, prises, CVC, etc.)

## Caractéristiques Techniques Typiques
- Tension nominale : 230V/400V triphasé
- Courant nominal : 630A à 4000A
- Indice de protection : IP30 à IP55
- Communication : Modbus RTU/TCP, BACnet IP, KNX
- Comptage intégré multifonction classe A
- Protection différentielle et surcharge
- Jeu de barres cuivre ou aluminium

## Localisation Typique
- Sous-sol technique
- Local technique électrique principal
- Salle des machines
- Zone de livraison énergie (près du poste de transformation)

## Relations avec Autres Équipements
- **Alimente** : Tableaux divisionnaires, onduleurs, groupes froids, ascenseurs, éclairage, PDU datacenter
- **Alimenté par** : Transformateur MT/BT, Générateur (en secours)
- **Contrôlé par** : Automate GTB, système de gestion d'énergie (EMS)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2
- Moyen (15 étages) : 2-4
- Grand (30+ étages) : 4-8

## Sources
- Standards Haystack v4 (elec, meter, switchgear tags)
- Brick Schema (Switchgear, Electrical_Meter classes)
- Standards BACnet pour équipements électriques
- Documentation technique distribution électrique BT
