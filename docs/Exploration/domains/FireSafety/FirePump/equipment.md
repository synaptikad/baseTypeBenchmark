# Fire Pump

## Identifiant
- **Code** : FIRE-PUMP
- **Haystack** : fire-pump
- **Brick** : brick:Fire_Pump

## Description
Pompe dédiée à l'alimentation en eau du système sprinkler et des RIA (Robinets d'Incendie Armés). Assure une pression et un débit suffisants lorsque le réseau d'eau de ville ne peut garantir les performances requises. Équipement critique supervisé en permanence.

## Fonction
Maintient la pression dans le réseau sprinkler et alimente le système en cas de déclenchement. Démarre automatiquement lorsque la pression chute (ouverture sprinkler) et maintient le débit nécessaire pour l'extinction. Équipé d'une pompe de maintien de pression (jockey pump).

## Variantes Courantes
- **Électrique** : Moteur électrique 400V triphasé
- **Diesel** : Moteur diesel de secours (doublement de sécurité)
- **Électrique + Diesel** : Configuration double pompe
- **Centrifuge** : Type le plus courant
- **Pompe principale + jockey** : Maintien pression + débit incendie
- **Horizontal split case** : Facilité de maintenance
- **Vertical turbine** : Aspiration directe réservoir

## Caractéristiques Techniques Typiques
- Débit : 250-2000 L/min (15-120 m³/h)
- Pression : 8-16 bar
- Puissance moteur : 15-150 kW
- Alimentation : 400V AC triphasé + source secourue
- Démarrage automatique : Pressostat ou flow switch
- Jockey pump : 2-5 L/min, maintien pression
- Supervision : Pression, débit, marche/arrêt, défaut, niveau réservoir
- Certification : EN 12845, FM, UL 448
- Autonomie diesel : 4-8 heures minimum

## Localisation Typique
- Local technique sprinkler
- Sous-sol du bâtiment
- Proximité réservoir incendie
- Zone accessible pompiers
- Local dédié résistant au feu

## Relations avec Autres Équipements
- **Alimente** : Sprinkler System, Fire Hose Reel (RIA)
- **Alimenté par** : Alimentation électrique secourue + diesel (secours)
- **Contrôlé par** : Fire Pump Controller (automate dédié)
- **Aspire depuis** : Water Tank, réseau ville
- **Surveille** : Pressure Switch, Flow Switch
- **Communique avec** : Fire Alarm Panel (FACP/CMSI), Building Management System (BMS)
- **Déclenche** : Alarme défaut pompe

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 0-1 groupe (si réseau ville insuffisant)
- Moyen (15 étages, 15000 m²) : 1-2 groupes (électrique + diesel)
- Grand (30+ étages, 50000 m²) : 2-4 groupes (redondance)

## Sources
- EN 12845: Fixed firefighting systems - Automatic sprinkler systems - Design, installation and maintenance
- NFPA 20: Standard for the Installation of Stationary Pumps for Fire Protection
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- Règle APSAD R1: Extinction automatique à eau type sprinkler
