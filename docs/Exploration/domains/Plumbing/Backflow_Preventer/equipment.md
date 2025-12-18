# Backflow Preventer

## Identifiant
- **Code** : BACKFLOW-PREV
- **Haystack** : `water`, `backflow`, `preventer`, `equip`
- **Brick** : `brick:Backflow_Preventer`

## Description
Dispositif de sécurité hydraulique qui empêche le retour d'eau potentiellement contaminée vers le réseau public d'eau potable. Protège la qualité de l'eau du réseau urbain contre les risques de contamination par refoulement.

## Fonction
Assurer une protection contre le retour d'eau non potable vers le réseau de distribution publique en cas de dépression. Obligatoire aux points de raccordement selon réglementation sanitaire et codes de plomberie.

## Variantes Courantes
- **Disconnecteur à zone de pression réduite** : Protection maximale (BA type AA)
- **Clapet anti-retour contrôlable** : Protection standard (EA)
- **Disconnecteur hydraulique** : Installation en ligne, compact
- **Surverse totale** : Rupture de charge avec cuve, protection absolue

## Caractéristiques Techniques Typiques
- Diamètre : DN20 à DN150
- Pression nominale : 10-16 bars
- Zone de protection : Différentielle avec évacuation
- Test périodique : Obligatoire annuel selon réglementation
- Matériaux : Bronze, inox (contact eau potable)
- Communication : Contact sec alarme défaut (modèles supervisés)

## Localisation Typique
- Point de livraison réseau urbain
- Protection circuits à risque (chaufferie, process industriels)
- Avant réservoirs et adoucisseurs
- Séparation réseaux potable/non-potable

## Relations avec Autres Équipements
- **Alimente** : Réseau interne bâtiment
- **Alimenté par** : Réseau urbain d'eau potable
- **Contrôlé par** : Supervision alarme défaut (optionnel)
- **Associé à** : Water Meter, Pressure Sensor, vanne d'isolement

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1 disconnecteur (entrée principale)
- Moyen (15 étages) : 1-3 disconnecteurs (entrée + circuits à risque)
- Grand (30+ étages) : 2-5 disconnecteurs (multi-entrées + protections spécifiques)

## Sources
- Haystack Project - Backflow prevention
- Brick Schema - Backflow_Preventer class
- Plumbing codes (IPC, UPC)
- Water quality protection regulations
