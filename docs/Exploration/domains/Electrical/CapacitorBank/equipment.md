# Batterie de Condensateurs (Capacitor Bank / Power Factor Correction Unit)

## Identifiant
- **Code** : CONDO
- **Haystack** : capacitor, pf-correction
- **Brick** : N/A
- **Extension** : Capacitor_Bank

## Description
Ensemble de condensateurs électriques utilisés pour compenser l'énergie réactive consommée par les charges inductives (moteurs, transformateurs) et améliorer le facteur de puissance (cos φ) de l'installation. Réduit les pertes électriques et optimise la puissance souscrite.

## Fonction
Compenser l'énergie réactive pour améliorer le facteur de puissance de l'installation électrique, réduire les pertes en ligne, diminuer la facture énergétique (pénalités énergie réactive) et optimiser le dimensionnement des équipements électriques.

## Variantes Courantes
- **Batterie fixe** : Compensation permanente non régulée
- **Batterie automatique** : Régulation par relais varmétrique (gradins)
- **Batterie dynamique** : Commutation rapide par thyristors
- **Compensation globale** : En tête d'installation (TGBT)
- **Compensation locale** : Au plus près des charges (moteurs)

## Caractéristiques Techniques Typiques
- Puissance réactive : 5 à 500 kVAr
- Nombre de gradins : 4 à 12 gradins commutables
- Tension : 230V/400V
- Régulation : Relais varmétrique avec mesure cos φ
- Communication : Modbus RTU/TCP, BACnet, contacts secs
- Protection : Disjoncteurs, contacteurs, fusibles
- Temps de commutation : 1-10 secondes (contacteurs), <40ms (thyristors)

## Localisation Typique
- TGBT principal (compensation globale)
- Tableaux divisionnaires (compensation partielle)
- Départs moteurs importants
- Local technique électrique principal

## Relations avec Autres Équipements
- **Compense** : Charges inductives (moteurs, transformateurs, éclairage)
- **Alimenté par** : TGBT ou tableau divisionnaire
- **Contrôlé par** : Relais varmétrique, automate GTB
- **Mesure avec** : Analyseur de puissance, compteur d'énergie réactive

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2
- Moyen (15 étages) : 2-4
- Grand (30+ étages) : 4-8

## Sources
- Documentation technique compensation d'énergie réactive
- Standards IEC 60831 (condensateurs de puissance)
- Haystack (capacitor, pf-correction tags)
- Documentation gestion qualité de l'énergie
