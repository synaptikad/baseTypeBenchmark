# Elevator Monitoring System

## Identifiant
- **Code** : ELEV_MON
- **Haystack** : elev + monitoring + system + equip
- **Brick** : brick:Elevator_Monitoring_System (subclass of brick:Monitoring_System)

## Description
Système centralisé de supervision et diagnostic de tous les équipements de transport vertical d'un bâtiment. Collecte données de performance, génère alertes, gère maintenance préventive. Interface principale entre ascenseurs et BMS.

## Fonction
Superviser en temps réel l'état, les performances et les alarmes de tous les systèmes de transport vertical. Faciliter la maintenance prédictive, optimiser les opérations et assurer la conformité réglementaire.

## Variantes Courantes
- **Système local sur site** : Serveur dédié dans le bâtiment
- **Système cloud** : Surveillance distante par Internet
- **Système hybride** : Local + cloud pour redondance
- **Système intégré BMS** : Module du système de gestion bâtiment
- **Système maintenance connectée** : Lien direct avec prestataire

## Caractéristiques Techniques Typiques
- Serveur de supervision avec IHM web
- Base de données historiques (SQL)
- Dashboard temps réel multi-écrans
- Gestion alarmes et notifications (email/SMS)
- Rapports automatiques (disponibilité, pannes)
- Intégration GMAO pour tickets maintenance
- Protocoles : BACnet/IP, Modbus TCP, OPC UA, SNMP
- API REST pour intégration tierce

## Localisation Typique
- Salle de supervision / PC Sécurité
- Local technique central
- Data center bâtiment
- Cloud (serveurs distants)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, UPS
- **Contrôlé par** : N/A
- **Supervise par** : Building Management System (niveau supérieur)
- **Supervise** : Tous Elevator Controllers, Group Controllers, Destination Dispatch System
- **Interagit avec** : CMMS, Access Control, Fire Alarm System, Emergency Response

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 système (basique ou intégré BMS)
- Moyen (15 étages) : 1 système (dédié ou module BMS)
- Grand (30+ étages) : 1-2 systèmes (redondance ou par zone)

## Sources
- Haystack Project 4.0 - Monitoring system tagging
- Brick Schema - Monitoring_System class
- ISO 8100-32 - Remote monitoring for accessibility
- Predictive maintenance standards for vertical transport
