# Parking Guidance Display

## Identifiant
- **Code** : PARKING_GUIDANCE_DISPLAY
- **Haystack** : N/A
- **Brick** : N/A

## Description
Panneau d'affichage dynamique indiquant le nombre de places disponibles par zone ou étage. Guide les conducteurs vers les zones avec disponibilités en temps réel basé sur données capteurs de stationnement.

## Fonction
Affichage en temps réel du nombre de places libres par zone/étage/type. Optimise la circulation interne du parking en dirigeant les conducteurs vers zones disponibles, réduisant temps de recherche et congestion.

## Variantes Courantes
- **Afficheur LED simple** : Chiffres rouges/verts, places disponibles
- **Panneau graphique** : LCD/LED couleur, plan parking + compteurs
- **Multi-zones** : Affichage plusieurs zones/étages simultanés
- **Extérieur** : Affichage total disponibilités avant entrée

## Caractéristiques Techniques Typiques
- Technologie : LED 7-segments, matrice LED, LCD rétroéclairé
- Taille : 30-150 cm (largeur selon nombre zones)
- Visibilité : 30-100 mètres selon format
- Couleurs : Rouge (complet), vert (disponible), jaune (réservé)
- Alimentation : 12-24V DC ou 230V AC
- Protocoles : RS485, Modbus, TCP/IP, BACnet
- Température opération : -20°C à +60°C
- Protection : IP54-IP65 (usage extérieur)

## Localisation Typique
- Entrée parking (avant barrière) - total disponibilités
- Carrefours internes (choix direction étage/zone)
- Rampes d'accès inter-niveaux
- Extérieur (voirie) - pré-information conducteurs

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Distribution électrique 12-24V DC
- **Contrôlé par** : Parking Guidance Controller, Parking Management Server
- **Interagit avec** : Parking Sensor (données occupation), Overhead Parking Indicator, Variable Message Sign

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 2-4 panneaux (entrée + carrefours clés)
- Moyen (parking 200 places) : 5-10 panneaux (multiples zones)
- Grand (parking 1000+ places) : 15-30 panneaux (chaque carrefour/rampe)

## Sources
- Standards ITS (Intelligent Transportation Systems)
- Documentation systèmes guidage parking
- Spécifications afficheurs LED/LCD industriels
