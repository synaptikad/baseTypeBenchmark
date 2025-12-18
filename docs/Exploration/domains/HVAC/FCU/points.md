# Points de Fan Coil Unit (FCU)

## Synthèse
- **Total points mesure** : 14
- **Total points commande** : 12
- **Total points état** : 8

## Points de Mesure (Capteurs)

| Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|--------------|-------|---------------|-----------|-------------|
| `zone air temp sensor` | °C | 10-35 | 1 min | Température d'air de la zone contrôlée |
| `discharge air temp sensor` | °C | 5-40 | 1 min | Température d'air soufflé (après batterie) |
| `return air temp sensor` | °C | 10-35 | 1 min | Température d'air repris de la zone |
| `zone air humidity sensor` | %RH | 0-100 | 5 min | Humidité relative de la zone |
| `zone air dewpoint sensor` | °C | -10 à 30 | 5 min | Point de rosée calculé ou mesuré (protection condensation) |
| `entering water temp sensor` | °C | 5-90 | 2 min | Température eau entrante (alimentation batterie) |
| `leaving water temp sensor` | °C | 5-90 | 2 min | Température eau sortante (retour batterie) |
| `hot water supply temp sensor` | °C | 40-90 | 2 min | Température alimentation eau chaude (4-pipe) |
| `chilled water supply temp sensor` | °C | 5-15 | 2 min | Température alimentation eau glacée (4-pipe) |
| `hot water return temp sensor` | °C | 35-85 | 2 min | Température retour eau chaude (4-pipe) |
| `chilled water return temp sensor` | °C | 10-18 | 2 min | Température retour eau glacée (4-pipe) |
| `filter pressure diff sensor` | Pa | 0-500 | 10 min | Perte de charge à travers le filtre (détection encrassement) |
| `power consumption meter` | kW | 0-5 | 15 min | Puissance électrique consommée (ventilateur + contrôles) |
| `energy consumption meter` | kWh | - | 1 h | Énergie électrique cumulée |

## Points de Commande (Actionneurs/Consignes)

| Tag Haystack | Unité | Plage/Options | Type | Description |
|--------------|-------|---------------|------|-------------|
| `zone air temp sp` | °C | 16-30 | Setpoint | Consigne température zone (occupé) |
| `zone air temp cooling sp` | °C | 20-30 | Setpoint | Consigne température en mode refroidissement |
| `zone air temp heating sp` | °C | 16-26 | Setpoint | Consigne température en mode chauffage |
| `zone air temp unoccupied heating sp` | °C | 14-22 | Setpoint | Consigne chauffage inoccupé (setback) |
| `zone air temp unoccupied cooling sp` | °C | 24-32 | Setpoint | Consigne refroidissement inoccupé (setback) |
| `fan speed cmd` | - | 0/1/2/3 ou 0-100% | Command | Commande vitesse ventilateur (Off/Low/Med/High ou 0-10V) |
| `heating valve cmd` | % | 0-100 | Command | Commande ouverture vanne chauffage (2 ou 4-pipe) |
| `cooling valve cmd` | % | 0-100 | Command | Commande ouverture vanne refroidissement (4-pipe) |
| `valve cmd` | % | 0-100 | Command | Commande vanne unique (2-pipe, changeover saisonnier) |
| `occupancy mode cmd` | - | Occupied/Unoccupied/Standby/Auto | Enum | Mode occupation (manuel ou BMS) |
| `hvac mode cmd` | - | Off/Heat/Cool/Auto | Enum | Mode HVAC principal |
| `enable cmd` | - | true/false | Boolean | Activation/désactivation générale du FCU |

## Points d'État

| Tag Haystack | Type | Valeurs | Fréquence | Description |
|--------------|------|---------|-----------|-------------|
| `fan status` | Bool | On/Off | 30 s | État marche/arrêt ventilateur |
| `fan speed status` | Enum/Num | Low/Med/High ou 0-100% | 30 s | Vitesse actuelle du ventilateur |
| `heating valve status` | % | 0-100 | 1 min | Position réelle vanne chauffage |
| `cooling valve status` | % | 0-100 | 1 min | Position réelle vanne refroidissement |
| `occupancy mode status` | Enum | Occupied/Unoccupied/Standby | 1 min | Mode occupation actif |
| `hvac mode status` | Enum | Off/Heating/Cooling/Auto | 1 min | Mode HVAC actuel |
| `filter alarm` | Bool | Normal/Alarm | On change | Alarme filtre encrassé (timer ou ΔP) |
| `condensate overflow alarm` | Bool | Normal/Alarm | On change | Alarme bac condensats plein (capteur humidité) |

## Mappings Protocoles

### BACnet (ISO 16484-5)

| Point | Object Type | Property | Units | Writable |
|-------|-------------|----------|-------|----------|
| Zone Air Temperature | Analog Input (AI) | Present-Value | degrees-celsius | R |
| Zone Temp Cooling Setpoint | Analog Value (AV) | Present-Value | degrees-celsius | R/W |
| Zone Temp Heating Setpoint | Analog Value (AV) | Present-Value | degrees-celsius | R/W |
| Fan Speed Command | Analog Output (AO) | Present-Value | percent | R/W |
| Heating Valve Command | Analog Output (AO) | Present-Value | percent | R/W |
| Cooling Valve Command | Analog Output (AO) | Present-Value | percent | R/W |
| HVAC Mode | Multi-State Value (MSV) | Present-Value | enum (1=Off, 2=Heat, 3=Cool, 4=Auto) | R/W |
| Fan Status | Binary Value (BV) | Present-Value | boolean | R |
| Filter Alarm | Binary Value (BV) | Present-Value | boolean | R |

### Modbus RTU

| Point | Register Type | Address Example | Data Type | Units | R/W |
|-------|--------------|-----------------|-----------|-------|-----|
| Zone Air Temperature | Input Register | 40001-40002 | Float32 | °C × 10 | R |
| Zone Cooling Setpoint | Holding Register | 40101-40102 | Float32 | °C × 10 | R/W |
| Fan Speed Command | Holding Register | 40201 | Uint16 | 0-3 ou % | R/W |
| Heating Valve Command | Holding Register | 40202 | Uint16 | % | R/W |
| HVAC Mode | Holding Register | 40204 | Uint16 | 0=Off, 1=Heat, 2=Cool, 3=Auto | R/W |
| Fan Status | Discrete Input | 10001 | Bit | 0=Off, 1=On | R |
| Filter Alarm | Discrete Input | 10002 | Bit | 0=OK, 1=Alarm | R |

### KNX

| Point | DPT | Size | Description |
|-------|-----|------|-------------|
| Zone Air Temperature | DPT 9.001 (2-byte float) | 2 bytes | Température °C |
| Zone Temp Setpoint | DPT 9.002 (2-byte float) | 2 bytes | Consigne température °C |
| Fan Speed Control | DPT 5.001 (1-byte unsigned) | 1 byte | Vitesse 0-100% |
| Heating Valve Position | DPT 5.001 | 1 byte | Position vanne 0-100% |
| HVAC Mode | DPT 20.102 (HVAC mode) | 1 byte | Auto/Comfort/Standby/Economy |
| Fan On/Off | DPT 1.001 (boolean) | 1 bit | On/Off |

## Sources

- [Titan Products - FCU-501 BACnet Controller](https://titanproducts.com/wp-content/uploads/2017/02/SKU_225_FCU_501_BACnet_Controller.pdf)
- [Project Haystack - VRF Indoor Unit FCU](https://project-haystack.org/doc/lib-phIoT/vrf-indoorUnit-fcu)
- [Brick Schema - Fan Coil Unit Class](https://brickschema.org/ontology/1.2/classes/Fan_Coil_Unit/)
- [US Department of Veterans Affairs - Four Pipe Fan Coil Control Standard](https://www.cfm.va.gov/til/sDetail/Div23HVACSteam/SD238200-03.pdf)
- [SAUTER Controls - NRFC Modbus Fan Coil Thermostat](https://www.sauter-controls.com/wp-content/uploads/ImportPDM/1117942.pdf)
- [75F - SmartStat 4-Pipe FCU Controller](https://support.75f.io/hc/en-us/articles/14434990527763-SmartStat-4PIPE-FCU-Fan-Coil-Unit)
