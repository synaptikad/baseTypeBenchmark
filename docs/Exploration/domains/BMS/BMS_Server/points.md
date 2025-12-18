# Points - BMS Server

## Résumé
- **Points de mesure** : 15
- **Points de commande** : 6
- **Points d'état** : 12
- **Total** : 33

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| SRV_CPU | CPU Usage | percent | % | 0-100 | 5min | Utilisation processeur du serveur BMS |
| SRV_MEM | Memory Usage | percent | % | 0-100 | 5min | Utilisation mémoire RAM |
| SRV_DSK | Disk Usage | percent | % | 0-100 | 15min | Utilisation espace disque base de données |
| SRV_NET_RX | Network Receive | bandwidth | Mbps | 0-1000 | 5min | Débit réseau entrant |
| SRV_NET_TX | Network Transmit | bandwidth | Mbps | 0-1000 | 5min | Débit réseau sortant |
| SRV_TMP | Server Temperature | temperature | °C | 0-80 | 15min | Température interne du serveur |
| SRV_PTS_TOT | Total Points Count | count | - | 0-100000 | 60min | Nombre total de points gérés |
| SRV_PTS_ACT | Active Points Count | count | - | 0-100000 | 60min | Nombre de points actifs/connectés |
| SRV_CTRL_CNT | Controllers Connected | count | - | 0-500 | 15min | Nombre de contrôleurs connectés |
| SRV_ALM_ACT | Active Alarms Count | count | - | 0-1000 | 5min | Nombre d'alarmes actives |
| SRV_DB_SIZE | Database Size | storage | GB | 0-10000 | 60min | Taille base de données |
| SRV_DB_QRY | Database Query Time | time | ms | 0-5000 | 5min | Temps moyen requête SQL |
| SRV_SESS | Active Sessions | count | - | 0-100 | 15min | Nombre de sessions utilisateurs actives |
| SRV_SCAN | Scan Rate Average | time | ms | 0-10000 | 15min | Temps moyen de scan des points |
| SRV_UPS_BAT | UPS Battery Level | percent | % | 0-100 | 15min | Niveau batterie onduleur |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| SRV_CMD_RESTART | Server Restart | command | - | 0-1 | binary | Commande redémarrage serveur BMS |
| SRV_CMD_BACKUP | Database Backup | command | - | 0-1 | binary | Lancement sauvegarde base de données |
| SRV_CMD_ACKALL | Acknowledge All Alarms | command | - | 0-1 | binary | Acquittement global alarmes |
| SRV_CMD_PURGE | Log Purge Days | setpoint | days | 1-365 | analog | Purge logs plus anciens que X jours |
| SRV_CMD_SCAN | Scan Enable | command | - | 0-1 | binary | Activation/désactivation scan points |
| SRV_CMD_EXPORT | Trend Export | command | - | 0-1 | binary | Export données tendances historiques |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| SRV_STS_RUN | Server Running Status | binary | 0=Stopped, 1=Running | event | État fonctionnement serveur BMS |
| SRV_STS_DB | Database Status | binary | 0=Offline, 1=Online | event | État connexion base de données |
| SRV_STS_NET | Network Status | binary | 0=Down, 1=Up | event | État connexion réseau |
| SRV_STS_RED | Redundancy Status | enum | 0=None, 1=Active, 2=Standby, 3=Failed | event | État serveur redondant |
| SRV_STS_LIC | License Status | enum | 0=Invalid, 1=Valid, 2=Expiring, 3=Expired | event | État licence logiciel |
| SRV_STS_BACNET | BACnet Service Status | binary | 0=Stopped, 1=Running | event | État service protocole BACnet |
| SRV_STS_MODBUS | Modbus Service Status | binary | 0=Stopped, 1=Running | event | État service protocole Modbus |
| SRV_STS_WEB | Web Interface Status | binary | 0=Offline, 1=Online | event | État interface web supervision |
| SRV_STS_ALMSVC | Alarm Service Status | binary | 0=Stopped, 1=Running | event | État service gestion alarmes |
| SRV_STS_TRDSVC | Trend Service Status | binary | 0=Stopped, 1=Running | event | État service tendances/historisation |
| SRV_STS_SYNC | Time Sync Status | binary | 0=Not Synced, 1=Synced | event | État synchronisation horaire NTP |
| SRV_STS_HEALTH | Overall Health Status | enum | 0=Critical, 1=Warning, 2=Good, 3=Optimal | event | État santé global serveur |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| SRV_ALM_CPU_HIGH | High CPU Usage | warning | SRV_CPU > 80% | Utilisation CPU élevée |
| SRV_ALM_CPU_CRIT | Critical CPU Usage | critical | SRV_CPU > 95% | Utilisation CPU critique |
| SRV_ALM_MEM_HIGH | High Memory Usage | warning | SRV_MEM > 85% | Utilisation mémoire élevée |
| SRV_ALM_MEM_CRIT | Critical Memory Usage | critical | SRV_MEM > 95% | Utilisation mémoire critique |
| SRV_ALM_DSK_HIGH | High Disk Usage | warning | SRV_DSK > 80% | Espace disque faible |
| SRV_ALM_DSK_CRIT | Critical Disk Usage | critical | SRV_DSK > 90% | Espace disque critique |
| SRV_ALM_DB_SLOW | Database Slow Response | warning | SRV_DB_QRY > 1000ms | Temps réponse base de données lent |
| SRV_ALM_DB_OFF | Database Offline | critical | SRV_STS_DB = 0 | Base de données hors ligne |
| SRV_ALM_NET_DOWN | Network Down | critical | SRV_STS_NET = 0 | Connexion réseau perdue |
| SRV_ALM_CTRL_LOST | Controller Connection Lost | warning | Perte connexion contrôleur | Contrôleur de terrain déconnecté |
| SRV_ALM_RED_FAIL | Redundancy Failed | critical | SRV_STS_RED = 3 | Serveur redondant défaillant |
| SRV_ALM_LIC_EXP | License Expiring | warning | SRV_STS_LIC = 2 | Licence expire dans 30 jours |
| SRV_ALM_LIC_INV | License Invalid | critical | SRV_STS_LIC = 3 | Licence expirée ou invalide |
| SRV_ALM_UPS_LOW | UPS Battery Low | warning | SRV_UPS_BAT < 30% | Batterie onduleur faible |
| SRV_ALM_TMP_HIGH | Server Temperature High | warning | SRV_TMP > 60°C | Température serveur élevée |
| SRV_ALM_SCAN_SLOW | Scan Rate Degraded | warning | SRV_SCAN > 5000ms | Performance scan dégradée |

## Sources
- BACnet Protocol Implementation - ASHRAE Standard 135
- Building Management System Server Specifications
- BMS/SCADA Integration Guidelines
