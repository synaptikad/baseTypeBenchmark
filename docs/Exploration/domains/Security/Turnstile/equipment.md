# Turnstile

## Identifiant
- **Code** : TURNSTILE
- **Haystack** : turnstile
- **Brick** : brick:Turnstile

## Description
Barrière de contrôle d'accès piéton mécanique à bras rotatifs (tripodes ou quadripodes) permettant le passage d'une seule personne à la fois. Intègre lecteur de badges, contrôle de rotation et détection de passage. Empêche le passage non autorisé et l'anti-passback physique.

## Fonction
Contrôle et comptage des passages, validation du credential avant autorisation de rotation, détection de forçage ou tailgating, comptage entrées/sorties, intégration avec système de contrôle d'accès, gestion de modes (libre, contrôlé, bloqué).

## Variantes Courantes
- **Tripode demi-hauteur** : Bras rotatifs hauteur 1m, économique
- **Tripode pleine hauteur** : Bras jusqu'au plafond (2m+), haute sécurité
- **Tourniquet à tambour** : Rotation complète, anti-tailgating
- **Tourniquet rapide** : Bras rétractables, passage rapide
- **Tourniquet bidirectionnel** : Entrée et sortie sur même équipement
- **Tourniquet PMR** : Passage élargi pour personnes à mobilité réduite
- **Tourniquet extérieur** : Résistant intempéries (IP65)

## Caractéristiques Techniques Typiques
- Débit : 20-40 passages/minute selon modèle
- Hauteur bras : 1m (demi) ou 2-2.2m (plein)
- Largeur passage : 550-600mm standard, 900mm PMR
- Sens : Unidirectionnel ou bidirectionnel
- Lecteur intégré : RFID, biométrique, QR code
- Communication : TCP/IP, RS-485, Wiegand (sortie vers contrôleur)
- Alimentation : 110-230V AC, 24V DC
- Détection : Anti-tailgating, anti-retour, détection passage
- Modes : Libre passage, contrôlé, bloqué, sortie libre
- Interface : LED, affichage, buzzer
- Matériau : Acier inox, aluminium
- Protection : IP20-IP65 selon modèle

## Localisation Typique
- Entrées principales de bâtiments
- Halls d'accueil
- Zones de réception
- Accès parkings
- Zones sensibles (salles serveurs, laboratoires)
- Stades et sites industriels
- Transports en commun (métro, trains)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Power supply, UPS
- **Contrôlé par** : Access Controller, Turnstile Controller
- **Intègre** : Badge Reader, Biometric Reader, QR Scanner
- **Envoie à** : Access Controller (événements passage, comptage)
- **Interagit avec** : Fire Alarm (free exit mode), Emergency System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-6 tourniquets
- Moyen (15 étages) : 6-15 tourniquets
- Grand (30+ étages) : 15-40 tourniquets

## Sources
- Access Control Standards
- Brick Schema - Turnstile Class
- Building Security Equipment Specifications
