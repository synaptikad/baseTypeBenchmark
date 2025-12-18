# Relais de Protection (Protection Relay / Protective Relay)

## Identifiant
- **Code** : RELAY
- **Haystack** : relay, protection
- **Brick** : N/A
- **Extension** : Protection_Relay

## Description
Dispositif électronique intelligent qui surveille en permanence les paramètres électriques (courant, tension, fréquence, puissance) et déclenche automatiquement les disjoncteurs en cas d'anomalie dangereuse. Les relais modernes intègrent des fonctions de mesure, enregistrement d'événements et communication pour supervision avancée.

## Fonction
Détecter rapidement les défauts électriques (surcharges, courts-circuits, défauts à la terre, déséquilibres) et commander l'ouverture des disjoncteurs pour protéger les personnes, équipements et installations. Fournit également des données de diagnostic et des enregistrements d'événements pour analyse post-défaut.

## Variantes Courantes
- **Relais de surintensité** : Protection contre surcharges et courts-circuits
- **Relais différentiel** : Protection terre et défaut d'isolement
- **Relais de tension** : Sur/sous-tension, déséquilibre
- **Relais directionnel** : Protection avec sens du défaut
- **Relais multifonction** : Combine plusieurs protections (50/51, 27, 59, 87, etc.)
- **Relais numérique** : Communication IEC 61850, Modbus, DNP3

## Caractéristiques Techniques Typiques
- Fonctions : ANSI 50/51 (I>), 27/59 (U</>), 67 (directionnel), 87 (différentiel)
- Précision : Classe 1 à 5
- Temps de réaction : 10-100ms selon réglages
- Communication : Modbus TCP, IEC 61850, DNP3, Profibus
- Enregistrement : Oscilloperturbographie, journaux d'événements
- Affichage : LCD avec mesures et états
- Alimentation : 24-250V DC/AC

## Localisation Typique
- TGBT (protection départs)
- Cellules MT (protection transformateur)
- Armoires de protection générateur
- Tableaux de distribution principaux
- Postes de transformation

## Relations avec Autres Équipements
- **Surveille** : Circuits électriques via TC/TT
- **Commande** : Disjoncteurs (déclenchement)
- **Connecté à** : TC (courant), TT (tension)
- **Supervisé par** : SCADA, GTB, système de gestion alarmes
- **Dialogue avec** : Autres relais (sélectivité logique)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-10
- Moyen (15 étages) : 10-25
- Grand (30+ étages) : 25-60

## Sources
- Standards IEC 61850 (communication postes électriques)
- Standards ANSI/IEEE (codes fonctions protection)
- Documentation technique protection numérique
- Standards Modbus et DNP3 pour relais
