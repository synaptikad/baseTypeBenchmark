# Electric Lock

## Identifiant
- **Code** : ELECTRIC_LOCK
- **Haystack** : electric-lock
- **Brick** : brick:Electric_Lock

## Description
Serrure électrique motorisée intégrée dans la porte, permettant le verrouillage et déverrouillage à distance via signal électrique. Offre haute sécurité mécanique et électronique. Peut être fail-safe (ouvre en cas de coupure) ou fail-secure (reste verrouillée). Utilisée pour portes nécessitant contrôle d'accès avec sécurité mécanique forte.

## Fonction
Verrouillage/déverrouillage électrique de porte, réponse aux commandes du contrôleur d'accès, retour d'état (verrouillé/déverrouillé), sécurité mécanique contre effraction, mode manuel de secours, intégration avec systèmes incendie (auto-déverrouillage).

## Variantes Courantes
- **Serrure motorisée** : Moteur électrique actionne pêne
- **Serrure électromécanique** : Combinaison mécanique + électrique
- **Mortaise électrique** : Encastrée dans épaisseur de porte
- **Fail-safe** : Déverrouille en cas de coupure (sécurité incendie)
- **Fail-secure** : Reste verrouillée en cas de coupure (sécurité accès)
- **Multi-points électrique** : Plusieurs points de fermeture

## Caractéristiques Techniques Typiques
- Tension : 12-24V DC
- Consommation : 200-800mA selon modèle
- Temps d'actionnement : 200-500ms
- Type : Fail-safe ou fail-secure
- Pêne : 1 ou 3/5 points
- Résistance effraction : Grade 2-5 selon norme
- Retour d'état : Contact position pêne
- Certification : EN 12209, EN 14846
- Modes : Normal, passage libre, toujours fermé
- Compatible : Cylindre européen, antipanique
- Matériau : Acier inox, laiton

## Localisation Typique
- Portes d'accès principal
- Portes de sécurité haute
- Salles serveurs
- Locaux sensibles
- Issues de secours (fail-safe)
- Zones réglementées
- Portes coupe-feu

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Door Controller, Access Controller, Power supply
- **Contrôlé par** : Door Controller, Access Controller
- **Reçoit commande de** : Badge Reader (via contrôleur), Request-to-Exit, Emergency Release
- **Supervision par** : Door Contact (état porte vs état serrure)
- **Interagit avec** : Fire Alarm (auto-unlock), Emergency System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-30 serrures
- Moyen (15 étages) : 40-120 serrures
- Grand (30+ étages) : 150-400 serrures

## Sources
- EN 12209 - Mechanically Operated Locks
- EN 14846 - Electromechanically Operated Locks
- Brick Schema - Electric Lock Class
