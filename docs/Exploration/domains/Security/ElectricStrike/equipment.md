# Electric Strike

## Identifiant
- **Code** : ELECTRIC_STRIKE
- **Haystack** : electric-strike
- **Brick** : brick:Electric_Strike

## Description
Mécanisme électrique de gâche installé dans le dormant de la porte, remplaçant la gâche fixe standard. Permet le déblocage du pêne de la serrure mécanique existante sans nécessiter de changer la serrure. Le pêne reste dans la serrure mais peut pousser la gâche pour ouvrir la porte. Peut être fail-safe ou fail-secure.

## Fonction
Déverrouillage électrique d'une serrure mécanique standard, libération temporisée du pêne, permet ouverture porte sans clé, compatible avec serrures existantes, retour d'état, modes fail-safe ou fail-secure selon configuration.

## Variantes Courantes
- **Gâche fail-safe** : Débloque en cas de coupure (sécurité incendie)
- **Gâche fail-secure** : Reste bloquée en cas de coupure (sécurité accès)
- **Gâche réversible** : Configurable fail-safe ou fail-secure
- **Gâche mortaise** : Pour serrure encastrée
- **Gâche applique** : Pour serrure en applique
- **Gâche angle variable** : Pour portes désaxées

## Caractéristiques Techniques Typiques
- Tension : 12-24V DC, 12-24V AC
- Consommation : 150-500mA selon modèle
- Type : Fail-safe, fail-secure, ou sélectionnable
- Force maintien : 300-1500 kg selon modèle
- Compatibilité : Serrures standard, anti-panique
- Montage : Mortaise ou applique
- Matériau : Acier, acier inox
- Retour d'état : Contact position gâche (optionnel)
- Certification : EN 14846 (gâches électriques)
- Temporisation : Via contrôleur

## Localisation Typique
- Portes existantes à équiper
- Portes avec serrures mécaniques
- Bureaux et salles de réunion
- Portes d'accès secondaires
- Zones de passage
- Portes coupe-feu (fail-safe)
- Entrées de services

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Door Controller, Access Controller, Power supply
- **Contrôlé par** : Door Controller, Access Controller
- **Reçoit commande de** : Badge Reader (via contrôleur), Request-to-Exit, Push Button
- **Fonctionne avec** : Serrure mécanique existante, Cylindre
- **Supervision** : Door Contact
- **Interagit avec** : Fire Alarm (si fail-safe)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-20 gâches
- Moyen (15 étages) : 20-80 gâches
- Grand (30+ étages) : 80-250 gâches

## Sources
- EN 14846 - Electric Strikes
- UL 1034 - Electric Strikes for Access Control
- Brick Schema - Electric Strike Class
