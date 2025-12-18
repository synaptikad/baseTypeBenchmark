# DC Fast Charger

## Identifiant
- **Code** : DC_FAST_CHARGER
- **Haystack** : N/A
- **Brick** : N/A

## Description
Borne de recharge rapide pour véhicules électriques en courant continu (DC), fournissant une puissance de 50 à 350 kW. Permet une recharge à 80% en 15-30 minutes. Équipement connecté OCPP pour supervision centralisée.

## Fonction
Recharge ultra-rapide des véhicules électriques en courant continu. Gestion avancée de sessions, délestage de charge, facturation dynamique et reporting énergétique temps réel vers système central.

## Variantes Courantes
- **50 kW DC** : Standard CCS/CHAdeMO, usage général
- **150 kW DC** : Charge rapide haute puissance
- **350 kW DC** : Ultra-rapide pour véhicules 800V
- **Multi-standard** : CCS + CHAdeMO + Type 2 AC combinés

## Caractéristiques Techniques Typiques
- Puissance : 50-350 kW DC
- Connecteurs : CCS Combo 2 (Europe), CHAdeMO, CCS1 (US), GB/T (Chine)
- Protocoles : OCPP 1.6/2.0.1, ISO 15118, DIN 70121
- Tension sortie : 200-920V DC
- Courant max : 200-500A
- Conversion : AC/DC intégré (PFC actif)
- Refroidissement : Liquide ou forcé par ventilation
- Communication : Ethernet, 4G/5G
- Protection : IP54, IK10
- Température opération : -30°C à +50°C

## Localisation Typique
- Parking public haute rotation
- Aires de service autoroute
- Stations de recharge dédiées
- Hubs de mobilité urbaine
- Flottes commerciales/transport

## Relations avec Autres Équipements
- **Alimente** : Véhicule électrique
- **Alimenté par** : Distribution HTA/BT, transformateur dédié, onduleur DC
- **Contrôlé par** : EV Charging Management System (OCPP backend), système de gestion énergétique
- **Interagit avec** : Payment Terminal, système de délestage, stockage énergie (batterie), compteur énergétique, système facturation

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 0-1 borne (optionnel)
- Moyen (parking 200 places) : 1-3 bornes (usage commercial)
- Grand (parking 1000+ places, hub mobilité) : 5-20 bornes (infrastructure dédiée)

## Sources
- Standard OCPP 2.0.1 (Open Charge Point Protocol)
- ISO 15118-2 et 15118-20 (Plug & Charge, V2G)
- IEC 61851-23 (DC charging stations)
- CHAdeMO Protocol specifications
- CharIN CCS standards
