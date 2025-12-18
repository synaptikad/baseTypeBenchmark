# Smoke Detector

## Identifiant
- **Code** : SMOKE-DET
- **Haystack** : smoke-detector
- **Brick** : brick:Smoke_Detector

## Description
Dispositif de détection automatique qui identifie la présence de fumée dans l'air ambiant. Utilise des technologies optiques (photoélectriques) ou ioniques pour détecter les particules de combustion et déclencher une alarme.

## Fonction
Assure la détection précoce d'un début d'incendie en identifiant la présence de fumée, permettant une évacuation rapide et l'activation des systèmes de protection incendie.

## Variantes Courantes
- **Détecteur optique** : Utilise un faisceau lumineux pour détecter les particules de fumée
- **Détecteur ionique** : Utilise une chambre d'ionisation (moins courant actuellement)
- **Détecteur photoélectrique** : Technologie la plus répandue dans les bâtiments modernes
- **Détecteur adressable** : Communique son identité unique au panneau de contrôle
- **Détecteur conventionnel** : Signal binaire sans identification individuelle

## Caractéristiques Techniques Typiques
- Alimentation : 12-24V DC (via boucle d'alarme)
- Protocole : Analogique adressable ou conventionnel
- Sensibilité : Réglable (faible/moyenne/élevée)
- Zone de couverture : 50-100 m² selon hauteur de plafond
- Température de fonctionnement : -10°C à +55°C
- Certification : EN 54-7 (Europe), UL 268 (USA)
- LED d'état : Indication visuelle de l'état et des alarmes

## Localisation Typique
- Couloirs et circulations
- Bureaux et espaces de travail
- Locaux techniques
- Halls d'entrée
- Salles de réunion
- Chambres d'hôtel
- Zones de stockage

## Relations avec Autres Équipements
- **Alimente** : N/A (dispositif de détection)
- **Alimenté par** : Fire Alarm Panel (via boucle de détection)
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI)
- **Déclenche** : Sounder, Beacon, Smoke Extraction Fan, Fire Door Holder
- **Communique avec** : Building Management System (BMS)

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 50-80 unités
- Moyen (15 étages, 15000 m²) : 300-500 unités
- Grand (30+ étages, 50000 m²) : 1000-2000 unités

## Sources
- EN 54-7: Fire detection and fire alarm systems - Smoke detectors
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- NFPA 72: National Fire Alarm and Signaling Code
