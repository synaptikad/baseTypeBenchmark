# Smoke Extraction Fan

## Identifiant
- **Code** : SMOKE-FAN
- **Haystack** : exhaust-fan avec tag smoke
- **Brick** : brick:Smoke_Exhaust_Fan

## Description
Ventilateur spécialement conçu pour extraire les fumées et gaz chauds en cas d'incendie. Certifié pour fonctionner à haute température (400°C/2h ou 300°C/1h) et résister aux fumées corrosives. Élément clé du système de désenfumage mécanique.

## Fonction
Évacue les fumées et gaz de combustion vers l'extérieur du bâtiment en cas d'incendie, améliorant la visibilité pour l'évacuation et l'intervention des secours. Crée une dépression dans la zone sinistrée pour limiter la propagation des fumées.

## Variantes Courantes
- **400°C/2h (F400)** : Pour désenfumage zones à risque élevé
- **300°C/1h (F300)** : Standard pour désenfumage bâtiments tertiaires
- **Jet fan** : Pour parkings, crée un flux horizontal
- **Axial** : Flux direct, débits élevés
- **Centrifuge** : Pression élevée, gaines longues
- **Réversible** : Extraction ou soufflage selon besoin
- **Avec registre intégré** : Ouverture automatique sur alarme

## Caractéristiques Techniques Typiques
- Débit : 5000-50000 m³/h selon application
- Température max : 300°C/1h ou 400°C/2h
- Puissance moteur : 1.5-30 kW
- Alimentation : 230-400V AC triphasé
- Commande : Contact sec, 0-10V, Modbus
- Certification : EN 12101-3 (Europe), UL 705 (USA)
- Matériaux : Acier galvanisé, inox (zones corrosives)
- Position repos : Arrêté, registre fermé
- Position sécurité : Marche, registre ouvert

## Localisation Typique
- Toiture (exutoires de fumée)
- Parkings souterrains
- Halls et atriums
- Escaliers et cages d'ascenseur
- Locaux techniques
- Zones commerciales grande hauteur
- Voies de circulation horizontales

## Relations avec Autres Équipements
- **Alimente** : N/A (équipement d'extraction)
- **Alimenté par** : Alimentation électrique secourue
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI), Smoke Control Panel
- **Déclenché par** : Smoke Detector, Heat Detector, Manual Call Point
- **Associé à** : Smoke Damper, Smoke Exhaust Damper, Pressurization Fan
- **Communique avec** : Building Management System (BMS)

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 2-5 unités
- Moyen (15 étages, 15000 m²) : 8-20 unités
- Grand (30+ étages, 50000 m²) : 25-80 unités

## Sources
- EN 12101-3: Smoke and heat control systems - Specification for powered smoke and heat exhaust ventilators
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- NFPA 92: Standard for Smoke Control Systems
- Règlement de sécurité contre l'incendie - Désenfumage
