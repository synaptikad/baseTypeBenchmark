# Pressurization Fan

## Identifiant
- **Code** : PRESS-FAN
- **Haystack** : supply-fan avec tag pressurization
- **Brick** : brick:Pressurization_Fan

## Description
Ventilateur soufflant de l'air frais dans les escaliers, sas ou couloirs pour créer une surpression et empêcher l'infiltration de fumées. Assure un cheminement protégé pour l'évacuation des occupants et l'accès des pompiers.

## Fonction
Maintient une pression positive dans les zones protégées (cages d'escaliers, sas) supérieure à celle des zones adjacentes, créant ainsi une barrière aéraulique contre les fumées. La différence de pression empêche les fumées d'entrer dans les voies d'évacuation.

## Variantes Courantes
- **À débit constant** : Débit fixe calculé
- **À pression constante** : Régulation selon nombre de portes ouvertes
- **Multi-vitesses** : 2-3 vitesses selon scénario
- **Avec variateur** : Adaptation dynamique du débit
- **Axial** : Compact, installation directe
- **Centrifuge** : Pression élevée, réseaux de gaines
- **Avec registre motorisé** : Activation sélective zones

## Caractéristiques Techniques Typiques
- Débit : 3000-25000 m³/h
- Pression différentielle cible : 50-80 Pa (portes fermées)
- Puissance moteur : 1-15 kW
- Alimentation : 230-400V AC triphasé
- Commande : Contact sec, 0-10V, Modbus
- Capteur de pression : Inclus ou déporté
- Certification : EN 12101-6 (Europe)
- Temps de démarrage : <10 secondes
- Position repos : Arrêté, registre fermé
- Position sécurité : Marche, pression contrôlée

## Localisation Typique
- Cages d'escaliers
- Sas d'entrée d'escalier
- Couloirs protégés
- Paliers d'étage
- Gaines d'ascenseur (si désenfumage)
- Zones refuge
- Issues de secours

## Relations avec Autres Équipements
- **Alimente** : Escaliers, sas, couloirs protégés
- **Alimenté par** : Alimentation électrique secourue
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI), Smoke Control Panel
- **Déclenché par** : Smoke Detector, Manual Call Point
- **Associé à** : Smoke Extraction Fan, Pressure Sensor, Smoke Damper
- **Communique avec** : Building Management System (BMS)

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 1-2 unités
- Moyen (15 étages, 15000 m²) : 3-8 unités
- Grand (30+ étages, 50000 m²) : 10-30 unités

## Sources
- EN 12101-6: Smoke and heat control systems - Specifications for pressure differential systems
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- NFPA 92: Standard for Smoke Control Systems
- Règlement de sécurité contre l'incendie - Désenfumage
