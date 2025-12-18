# Compteur d'Énergie (Energy Meter / Electrical Meter)

## Identifiant
- **Code** : METER
- **Haystack** : elec-meter, meter
- **Brick** : Electrical_Meter, Energy_Meter

## Description
Appareil de mesure multifonction qui enregistre la consommation d'énergie électrique (kWh) et de multiples paramètres électriques (tension, courant, puissance, facteur de puissance, harmoniques). Élément clé des systèmes de gestion d'énergie et de facturation.

## Fonction
Mesurer et enregistrer la consommation d'énergie électrique globale ou par zone. Fournir des données précises pour la facturation, l'analyse énergétique, la détection d'anomalies et l'optimisation de la consommation. Assure également la surveillance de la qualité de l'énergie.

## Variantes Courantes
- **Compteur principal** : Mesure globale du bâtiment (comptage fournisseur)
- **Compteur divisionnaire** : Mesure par zone, étage ou usage
- **Compteur classe A** : Haute précision (±0.5%) pour facturation
- **Compteur classe B** : Précision standard (±1%) pour monitoring
- **Compteur communicant** : Avec interface Modbus/BACnet/M-Bus

## Caractéristiques Techniques Typiques
- Précision : Classe 0.5S à 1 (IEC 62053)
- Mesures : Énergie active/réactive, puissances, U, I, cos φ, THD
- Fréquence d'échantillonnage : 1 à 60 mesures/minute
- Communication : Modbus RTU/TCP, M-Bus, BACnet, IEC 61850
- Montage : Rail DIN, panneau frontal
- Afficheur : LCD rétroéclairé multifonction
- Mémoire : Enregistrement des courbes de charge

## Localisation Typique
- TGBT principal (comptage global)
- Tableaux divisionnaires (comptage par zone)
- Départ circuits importants (CVC, éclairage, prises)
- Armoires électriques par étage
- Locaux techniques

## Relations avec Autres Équipements
- **Mesure** : Consommation de tous équipements en aval
- **Alimenté par** : Circuit de mesure (via TC/TT)
- **Connecté à** : Transformateurs de courant (TC), Transformateurs de tension (TT)
- **Supervisé par** : Système EMS, GTB/GTC, plateforme IoT énergie

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-15
- Moyen (15 étages) : 20-50
- Grand (30+ étages) : 50-200

## Sources
- Brick Schema (Electrical_Meter, Energy_Meter classes)
- Haystack v4 (elec-meter, meter tags)
- Standards BACnet pour compteurs d'énergie
- IEC 62053 (compteurs électriques)
- Protocole M-Bus (EN 13757)
