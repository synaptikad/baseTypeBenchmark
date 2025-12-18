# Dante Audio Interface

## Identifiant
- **Code** : DANTE_IF
- **Haystack** : N/A
- **Brick** : N/A

## Description
Interface réseau pour audio-over-IP utilisant le protocole Dante. Équipement communicant via Ethernet pour routage audio, monitoring réseau et configuration.

## Fonction
Conversion entre audio analogique/AES3 et audio réseau Dante. Permet le transport audio sur infrastructure Ethernet standard, le routage flexible sans câblage physique, la distribution longue distance. Élément clé des infrastructures audio modernes distribuées.

## Variantes Courantes
- **Analog-to-Dante Interface** : Convertit entrées/sorties XLR vers Dante
- **AES3-to-Dante Interface** : Bridge entre AES3 digital et Dante
- **Wall Plate Dante Interface** : Connectique murale avec Dante intégré
- **Portable Dante Interface** : Interface USB pour laptops/PCs
- **Dante AVIO Adapter** : Adaptateurs compacts pour conversion ponctuelle

## Caractéristiques Techniques Typiques
- Canaux : 2 à 64 canaux selon modèle
- Entrées/Sorties : XLR balanced, 1/4" TRS, AES3, ADAT
- Sample rates : 48kHz, 96kHz
- Bit depth : 24-bit
- Latency : <1ms typique sur réseau dédié
- Connectivité : GbE Ethernet, PoE+ option
- Contrôle : Dante Controller software, HTTP API
- Protocoles : Dante, AES67 (interop mode)
- Alimentation : PoE+, external AC adapter, redundant PSU
- Redundancy : Primary/secondary Dante network support
- Clock : Word clock I/O pour sync externe

## Localisation Typique
- Salles de réunion et visioconférence (racks)
- Locaux techniques audio
- Auditoriums (régie son)
- Distribués dans le bâtiment (wall plates)

## Relations avec Autres Équipements
- **Connecte** : DSP, Audio Amplifier, Microphone Array, Table Microphone, Ceiling Speaker (actifs), Video Conference Codec
- **Contrôlé par** : Dante Controller, DSP
- **Infrastructure** : Network switches (Dante-optimized)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-15 interfaces
- Moyen (15 étages) : 20-60 interfaces
- Grand (30+ étages) : 80-200 interfaces

## Sources
- Dante audio networking protocol specifications
- AES67 audio over IP standard
- Professional audio networking best practices
