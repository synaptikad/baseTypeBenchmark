# Flow Meter

## Identifiant
- **Code** : FLOW-MTR
- **Haystack** : `water`, `flow`, `meter`, `sensor`, `equip`
- **Brick** : `brick:Water_Flow_Sensor`

## Description
Débitmètre mesurant le débit instantané et/ou volumétrique d'eau dans une canalisation. Équipement essentiel pour le monitoring des consommations, la régulation hydraulique, et la détection d'anomalies de débit.

## Fonction
Mesurer en temps réel le débit d'eau circulant dans les canalisations, transmettre les données vers le système de supervision, permettre le calcul des consommations, et détecter les anomalies de débit (fuites, surconsommations, sous-débit).

## Variantes Courantes
- **Débitmètre électromagnétique** : Haute précision, pas d'obstruction, tous fluides conducteurs
- **Débitmètre ultrasonique** : Non-intrusif (clamp-on) ou insertion, versatile
- **Débitmètre à turbine** : Pièces mobiles, bon rapport qualité/prix
- **Débitmètre vortex** : Sans pièce mobile, robuste
- **Débitmètre à effet Coriolis** : Très haute précision, mesure masse

## Caractéristiques Techniques Typiques
- Diamètre : DN15 à DN300
- Plage de mesure : 0.1-100 m³/h selon diamètre
- Précision : ±0.5% à ±2% selon technologie
- Sortie : Impulsion, 4-20mA, Modbus, BACnet
- Affichage local : LCD avec totalisateur
- Perte de charge : Minimale (électromagnétique, ultrasonique)

## Localisation Typique
- Entrée bâtiment (comptage général)
- Départ circuits ECS/EF principaux
- Boucle retour circulation ECS
- Sortie pompes (booster, circulation)
- Circuits process ou spécialisés

## Relations avec Autres Équipements
- **Alimente** : N/A (instrument de mesure)
- **Alimenté par** : N/A (sur réseau hydraulique)
- **Contrôlé par** : Système de supervision, analytics
- **Associé à** : Water Meter (corrélation), Motorized Valve (régulation), DHW Circulation Pump

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-5 débitmètres (principaux circuits)
- Moyen (15 étages) : 5-15 débitmètres (multi-circuits + zones)
- Grand (30+ étages) : 15-50 débitmètres (monitoring détaillé tous circuits)

## Sources
- Haystack Project - Flow measurement equipment
- Brick Schema - Flow_Sensor class
- ISO 5167 - Flow measurement standards
- Building automation protocols (BACnet, Modbus)
