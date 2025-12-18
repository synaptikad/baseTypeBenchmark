# Overhead Parking Indicator

## Identifiant
- **Code** : OVERHEAD_INDICATOR
- **Haystack** : N/A
- **Brick** : N/A

## Description
Indicateur lumineux LED individuel suspendu au-dessus de chaque place de stationnement. Affiche l'état d'occupation en temps réel (vert=libre, rouge=occupé, bleu=handicapé, jaune=réservé) basé sur données capteur de place.

## Fonction
Indication visuelle directe de l'état de chaque place. Guide conducteur vers places libres par signalisation visuelle immédiate. Complète système de guidage global en fournissant information au niveau de chaque place individuelle.

## Variantes Courantes
- **LED bicolore** : Vert/rouge uniquement (libre/occupé)
- **LED tricolore** : Vert/rouge/bleu (libre/occupé/handicapé)
- **LED avec numéro** : Affichage numéro de place en plus de couleur
- **Version low-profile** : Hauteur réduite pour parkings bas plafond

## Caractéristiques Techniques Typiques
- Technologie : LED haute luminosité
- Couleurs : Vert, rouge, bleu, jaune (selon modèle)
- Visibilité : 30-50 mètres
- Dimensions : 10-30 cm diamètre
- Alimentation : 12-24V DC, PoE (rare)
- Communication : RS485 (bus série), protocole propriétaire
- Consommation : < 5W par indicateur
- Température opération : -20°C à +60°C
- Durée vie LED : 50,000-100,000 heures

## Localisation Typique
- Au-dessus de chaque place de stationnement (plafond parking)
- Parkings souterrains multi-niveaux
- Parkings couverts
- Zones de stationnement guidées

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Distribution électrique 12-24V DC (bus d'alimentation)
- **Contrôlé par** : Parking Guidance Controller
- **Interagit avec** : Parking Sensor Ultrasonic ou Magnetic (reçoit état occupation), Parking Guidance Display (système global)

## Quantité Typique par Bâtiment
- Petit (parking 50 places avec guidage) : 50 indicateurs (1 par place)
- Moyen (parking 200 places avec guidage) : 200 indicateurs (1 par place)
- Grand (parking 1000+ places avec guidage) : 1000+ indicateurs (1 par place)

## Sources
- Documentation systèmes guidage parking
- Spécifications LED industrielles
- Standards ITS (Intelligent Transportation Systems)
