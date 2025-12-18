# Motorized Valve

## Identifiant
- **Code** : MOTOR-VALVE
- **Haystack** : `water`, `valve`, `motorized`, `equip`
- **Brick** : `brick:Valve` avec `brick:Motor_Position_Command`

## Description
Vanne équipée d'un actionneur motorisé permettant un contrôle automatique de l'ouverture et de la fermeture. Utilisée pour réguler les débits d'eau dans les circuits de plomberie et d'eau chaude sanitaire.

## Fonction
Contrôler automatiquement le débit d'eau dans les circuits hydrauliques en réponse aux commandes du système de supervision. Permet l'isolation de circuits, la régulation de température par mélange, et le contrôle de distribution.

## Variantes Courantes
- **Vanne 2 voies** : Ouverture/fermeture d'un circuit unique
- **Vanne 3 voies mélangeuse** : Mélange de deux flux pour régulation température
- **Vanne 3 voies divergente** : Répartition d'un flux vers deux sorties
- **Vanne papillon motorisée** : Grande section, faible perte de charge
- **Vanne à boisseau** : Quart de tour, isolation étanche

## Caractéristiques Techniques Typiques
- Diamètre : DN15 à DN300
- Type d'actionneur : Électrique 24-230V, pneumatique
- Temps de course : 15s à 150s selon taille
- Commande : TOR (tout/rien), modulante 0-10V/4-20mA
- Position feedback : Potentiomètre, switches fin de course
- Matériaux : Laiton, bronze, inox (eau potable)

## Localisation Typique
- Chaufferie (circuits ECS)
- Départ colonnes montantes
- Local technique étage
- Gaine technique

## Relations avec Autres Équipements
- **Alimente** : Circuits secondaires, émetteurs
- **Alimenté par** : DHW Tank, réseau primaire, Booster Pump
- **Contrôlé par** : Contrôleur DDC, régulation PID
- **Associé à** : Temperature Sensor, Pressure Sensor, Flow Meter

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-10 vannes (circuits principaux)
- Moyen (15 étages) : 15-40 vannes (par zone et circuit)
- Grand (30+ étages) : 40-100 vannes (contrôle détaillé multi-zones)

## Sources
- Haystack Project - Valve equipment tags
- Brick Schema - Valve and Actuator classes
- ASHRAE Standards - Valve sizing and control
- BACnet/Modbus control protocols
