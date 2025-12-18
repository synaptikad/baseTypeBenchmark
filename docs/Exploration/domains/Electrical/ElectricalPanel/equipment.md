# Tableau Divisionnaire (Electrical Panel / Distribution Board / Sub-panel)

## Identifiant
- **Code** : DIV
- **Haystack** : elec-panel, panel
- **Brick** : Electrical_Panel

## Description
Tableau électrique de distribution secondaire qui reçoit l'énergie du TGBT et la redistribue vers les circuits terminaux d'une zone, d'un étage ou d'un usage spécifique. Contient les protections (disjoncteurs), comptages et commandes pour sa zone de desserte.

## Fonction
Distribuer l'énergie électrique depuis le TGBT vers les circuits finaux (éclairage, prises, CVC, équipements). Assurer la protection, la commande et le comptage des circuits de sa zone. Point de distribution intermédiaire dans l'arborescence électrique du bâtiment.

## Variantes Courantes
- **Tableau par étage** : Distribution horizontale d'un niveau
- **Tableau par usage** : Éclairage, prises, CVC, force motrice
- **Tableau par zone** : Aile, quadrant, locataire
- **Tableau terminal** : Dernier niveau avant équipements
- **Tableau communicant** : Intégration GTB avec disjoncteurs/compteurs intelligents

## Caractéristiques Techniques Typiques
- Alimentation : 230V/400V triphasé
- Courant nominal : 63A à 630A
- Nombre de départs : 12 à 96 circuits
- Protection : Disjoncteurs modulaires communicants
- Comptage : Intégré ou externe
- Communication : Modbus RTU/TCP, KNX, BACnet
- Indice de protection : IP30 à IP65
- Type : Encastré, saillie, coffret, armoire

## Localisation Typique
- Gaines techniques verticales (un par étage)
- Locaux techniques par zone
- Couloirs techniques
- Faux-plafonds techniques (petits tableaux)
- Sous-stations électriques secondaires

## Relations avec Autres Équipements
- **Alimente** : Circuits terminaux (éclairage, prises, CVC)
- **Alimenté par** : TGBT principal ou autre tableau amont
- **Contient** : Disjoncteurs, compteurs, contacteurs, parafoudres
- **Supervisé par** : GTB/GTC via modules de communication

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-15
- Moyen (15 étages) : 20-60
- Grand (30+ étages) : 60-200

## Sources
- Brick Schema (Electrical_Panel class)
- Haystack v4 (elec-panel, panel tags)
- Standards NF C 15-100 (installations BT)
- Documentation technique distribution électrique
