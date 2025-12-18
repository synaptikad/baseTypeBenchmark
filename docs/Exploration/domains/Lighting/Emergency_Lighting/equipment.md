# Emergency Lighting

## Identifiant
- **Code** : EMERG_LIGHT
- **Haystack** : luminaire, emergency, light
- **Brick** : brick:Emergency_Lighting_Equipment, brick:Luminaire

## Description
Luminaire de sécurité autonome ou centralisé conçu pour s'activer automatiquement en cas de panne de courant ou d'urgence. Équipé d'une batterie de secours, il assure l'éclairage minimal requis pour l'évacuation sécuritaire des occupants et maintient la visibilité des issues de secours et voies d'évacuation.

## Fonction
Fournir un éclairage de sécurité fiable et réglementaire lors de coupures de courant, pannes du système d'éclairage principal, ou situations d'urgence (incendie, évacuation). Permet la visibilité des parcours d'évacuation et la signalisation des sorties de secours selon les normes en vigueur.

## Variantes Courantes
- **Exit Sign Lighting** : Signalisation lumineuse des sorties de secours (pictogrammes)
- **Emergency Egress Lighting** : Éclairage des voies d'évacuation
- **Emergency Area Lighting** : Éclairage anti-panique des espaces ouverts
- **Self-Contained Emergency Light** : Batterie et contrôle intégrés dans le luminaire
- **Central Battery Emergency Light** : Alimenté par système centralisé de batteries
- **Maintained Emergency Light** : Allumé en permanence (mode normal + secours)
- **Non-Maintained Emergency Light** : S'allume uniquement en mode secours
- **Combined Emergency Light** : Éclairage normal + fonction secours
- **LED Emergency Light** : Technologie LED basse consommation
- **Addressable Emergency Light** : Communicant pour supervision et tests automatiques

## Caractéristiques Techniques Typiques
- Tension d'alimentation normale: 120-277V AC
- Tension de secours: 12-48V DC (batterie)
- Autonomie batterie: 90 minutes minimum (réglementaire), jusqu'à 3 heures
- Technologie batterie: NiCd, NiMH, Li-ion
- Puissance en mode secours: 3W à 20W
- Flux lumineux secours: 200 à 2,000 lumens
- Temps de recharge batterie: 24 heures typique
- Source lumineuse: LED (dominant), parfois fluorescent compact
- Durée de vie LED: 50,000-100,000 heures
- Test automatique: Mensuel et annuel (auto-diagnostic)
- Communication: DALI (IEC 62386-202), BACnet, Modbus, relais
- Indicateurs: LED statut (charge, défaut, test)
- Classe de protection: IP20 à IP65 selon localisation
- Certification: UL 924, EN 60598-2-22, IEC 60598-2-22

## Localisation Typique
- Toutes les issues de secours
- Couloirs et voies d'évacuation
- Cages d'escalier
- Halls et espaces de circulation
- Salles de réunion et espaces publics
- Parkings intérieurs
- Espaces techniques et salles serveur
- Zones de rassemblement
- Au-dessus des portes coupe-feu
- Points de rassemblement extérieurs

## Relations avec Autres Équipements
- **Alimente** : N/A (équipement terminal)
- **Alimenté par** : Emergency Lighting Panel, Central Battery System, Electrical Panel (normal), UPS
- **Contrôlé par** : Emergency Lighting Controller, Fire Alarm Panel, Building Automation System (monitoring)
- **Communique avec** : Emergency Lighting Test System, BMS (pour supervision et alarmes)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 100-300
- Moyen (15 étages) : 400-1,500
- Grand (30+ étages) : 2,000-10,000

## Sources
- IEC 60598-2-22 - Luminaires for emergency lighting
- IEC 62386-202 - DALI Part 202: Self-contained emergency lighting
- NFPA 101 - Life Safety Code (emergency lighting requirements)
- EN 1838 - Lighting applications - Emergency lighting
- UL 924 - Emergency lighting and power equipment
- Local building codes and fire safety regulations
