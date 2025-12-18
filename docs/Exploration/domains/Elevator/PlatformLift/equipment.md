# Platform Lift

## Identifiant
- **Code** : PLATFORM_LIFT
- **Haystack** : platformLift + equip
- **Brick** : brick:Platform_Lift (subclass of brick:Vertical_Transport_Equipment)

## Description
Élévateur vertical à plateforme ouverte ou semi-fermée, conçu pour l'accessibilité des personnes à mobilité réduite. Équipement communicant pour supervision et conformité réglementaire.

## Fonction
Assurer l'accessibilité verticale des personnes à mobilité réduite, fauteuils roulants et charges légères sur de faibles hauteurs. Répondre aux exigences d'accessibilité PMR.

## Variantes Courantes
- **Élévateur vertical PMR** : Plateforme fermée, jusqu'à 3m
- **Élévateur ciseaux** : Structure en ciseaux, compact
- **Élévateur incliné sur escalier** : Suit la pente d'un escalier existant
- **Élévateur extérieur** : Protection météo, accès terrasses
- **Mini-ascenseur privatif** : Pour logements individuels

## Caractéristiques Techniques Typiques
- Capacité : 250 kg à 630 kg (1-8 personnes)
- Vitesse : 0.15 m/s (très lente pour sécurité)
- Hauteur : 0.5m à 4m
- Dimensions plateforme : 1.0m x 1.25m à 1.5m x 1.5m
- Portes semi-automatiques ou automatiques
- Protocoles : Modbus, contact sec, intégration BMS limitée
- Conformité : Directive machines, normes PMR

## Localisation Typique
- Entrées de bâtiment avec marches
- Zones publiques à accès PMR obligatoire
- Scènes et podiums
- Zones techniques avec dénivelés
- Logements et maisons individuelles

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel
- **Contrôlé par** : Local Control Panel
- **Supervise par** : Building Management System (optionnel)
- **Interagit avec** : Access Control System, Emergency Call System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 élévateur (si pas d'ascenseur principal)
- Moyen (15 étages) : 0-2 élévateurs (accès PMR zones spécifiques)
- Grand (30+ étages) : 1-4 élévateurs (en complément des ascenseurs)

## Sources
- Haystack Project 4.0 - Platform lift equipment
- Brick Schema - Vertical transport subclasses
- EN 81-41:2010 - Platform lifts for persons with disabilities
- Accessibility regulations (ADA, ERP France)
