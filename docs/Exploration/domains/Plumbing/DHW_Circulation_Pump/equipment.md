# DHW Circulation Pump

## Identifiant
- **Code** : DHW-CIRC-PUMP
- **Haystack** : `domesticWater`, `hot`, `circ`, `pump`, `equip`
- **Brick** : `brick:Domestic_Hot_Water_Pump`

## Description
Pompe de circulation ou de bouclage qui maintient l'eau chaude sanitaire en mouvement dans le réseau de distribution pour garantir un accès rapide à l'eau chaude aux points d'usage éloignés. Évite les temps d'attente et le gaspillage d'eau.

## Fonction
Faire circuler en permanence (ou selon programmation) l'eau chaude dans le réseau de distribution ECS pour maintenir la température dans toutes les colonnes montantes et éviter le refroidissement. Retourne l'eau refroidie vers le ballon pour réchauffage.

## Variantes Courantes
- **Pompe simple vitesse** : Fonctionnement tout/rien avec régulation horaire
- **Pompe à vitesse variable** : Modulation selon température de retour ou delta T
- **Pompe double** : Configuration redondante ou duty/standby
- **Pompe avec désinfection thermique** : Support cycles anti-légionelles

## Caractéristiques Techniques Typiques
- Débit : 1-20 m³/h selon taille réseau
- Hauteur manométrique : 2-15 mCE
- Puissance : 50W-5kW
- Matériaux : Bronze, inox (contact eau potable)
- Régulation : Thermostat différentiel, programmateur horaire
- Communication : BACnet, Modbus, 0-10V

## Localisation Typique
- Chaufferie à proximité du DHW Tank
- Local technique ECS
- Gaine technique
- Sous-sol

## Relations avec Autres Équipements
- **Alimente** : Réseau de distribution ECS, colonnes montantes
- **Alimenté par** : DHW Tank (départ bouclage)
- **Contrôlé par** : Contrôleur DDC, régulation température
- **Associé à** : Temperature Sensor (retour bouclage), Flow Meter, Check Valve

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1 pompe (1-3 m³/h)
- Moyen (15 étages) : 1-2 pompes (5-10 m³/h) avec backup
- Grand (30+ étages) : 2-4 pompes (10-20 m³/h) par zone ou redondance

## Sources
- Haystack Project - DHW circulation systems
- Brick Schema - Pump and DHW classes
- ASHRAE Standard 188 - Legionellosis prevention
- Plumbing codes and DHW distribution best practices
