# Payment Terminal

## Identifiant
- **Code** : PAYMENT_TERMINAL
- **Haystack** : N/A
- **Brick** : N/A

## Description
Terminal de paiement automatique pour stationnement. Accepte multiples moyens de paiement (CB, NFC, espèces, QR code), calcule le montant dû basé sur durée, et valide le ticket pour sortie.

## Fonction
Encaissement automatisé des frais de stationnement. Lecture ticket/plaque, calcul tarif selon grille horaire, acceptation paiement, validation sortie et communication transactions vers système central.

## Variantes Courantes
- **Borne intérieure** : Avant sortie, paiement pré-sortie
- **Borne extérieure** : À la sortie, paiement direct
- **Multi-paiements** : CB + NFC + espèces + mobile
- **Sans contact uniquement** : CB/NFC/mobile, pas d'espèces

## Caractéristiques Techniques Typiques
- Moyens paiement : CB EMV, NFC (Apple/Google Pay), espèces (monnayeur), QR code
- Lecteur ticket : Code-barres, QR, RFID, magnétique
- Écran : Tactile 10-15 pouces, antireflet
- Imprimante : Thermique (reçu)
- Protocoles : TCP/IP, TLS, PCI-DSS compliant
- Température opération : -20°C à +60°C (modèle extérieur)
- Protection : IP54-IP65

## Localisation Typique
- Hall d'entrée parking (pré-paiement avant sortie)
- À la sortie (paiement direct)
- Étages intermédiaires (paiement anticipé)
- Zones piétonnes (avant retour véhicule)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : 230V AC
- **Contrôlé par** : Parking Revenue Control System, Parking Management Server
- **Interagit avec** : Barrier Gate (commande ouverture après paiement), Ticket Dispenser, ANPR Camera (paiement par plaque), système bancaire (autorisation CB)

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 1-2 bornes (sortie + hall)
- Moyen (parking 200 places) : 3-6 bornes (multiples étages/sorties)
- Grand (parking 1000+ places) : 8-15 bornes (répartition zones)

## Sources
- Standards PCI-DSS (sécurité paiement)
- EMV chip card specifications
- NFC/contactless payment protocols
- Documentation systèmes revenue control parking
