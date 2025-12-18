# Water Tank

## Identifiant
- **Code** : WATER-TANK
- **Haystack** : `water`, `tank`, `equip`
- **Brick** : `brick:Water_Tank`

## Description
Réservoir de stockage d'eau froide destiné à assurer une réserve tampon, une autonomie en cas de coupure du réseau, ou un découplage entre l'approvisionnement et la consommation. Peut servir de réserve incendie selon réglementation.

## Fonction
Stocker un volume d'eau froide pour garantir la continuité de service, stabiliser la pression du réseau interne, fournir une réserve pour les systèmes de protection incendie, et permettre une gestion optimisée de la consommation d'eau.

## Variantes Courantes
- **Tank de réserve générale** : Stockage eau potable froide en sous-sol
- **Tank de réserve incendie** : Volume dédié pompiers avec isolation réseau sanitaire
- **Tank tampon** : Découplage réseau urbain / distribution interne
- **Tank sur toiture** : Alimentation par gravité des étages supérieurs

## Caractéristiques Techniques Typiques
- Capacité : 1 m³ à 500 m³ (grands immeubles)
- Matériaux : Polyéthylène, acier vitrifié, béton (enterré)
- Pression de service : Atmosphérique ou faible pression
- Équipements : Level Sensor, trop-plein, vidange, trappe visite
- Protection : Couverture étanche, traitement anti-algues, isolation thermique

## Localisation Typique
- Sous-sol (cuve enterrée ou sur radier)
- Toiture technique (château d'eau)
- Local technique eau
- Vide sanitaire

## Relations avec Autres Équipements
- **Alimente** : Booster Pump, réseau de distribution, Fire Water Pump
- **Alimenté par** : Réseau urbain, Rainwater Harvesting Tank
- **Contrôlé par** : Level Sensor avec électrovannes remplissage
- **Associé à** : Water Meter (entrée), Potable Water Pump, UV Disinfection System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 tank (5-20 m³) si réglementation incendie
- Moyen (15 étages) : 1-2 tanks (30-100 m³) réserve + incendie
- Grand (30+ étages) : 2-4 tanks (100-500 m³) multi-zones et redondance

## Sources
- Haystack Project - Tank equipment
- Brick Schema - Water_Tank class
- Fire protection codes (NFPA, réglementations locales)
- Potable water storage regulations
