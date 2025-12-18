# Points de PDU (Power Distribution Unit)

## Synthèse
- **Total points mesure** : 16
- **Total points commande** : 4
- **Total points état** : 8

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| input_voltage_L1 | elec input voltage L1 sensor | V | 200-250 | 1min | Tension entrée phase L1 |
| input_voltage_L2 | elec input voltage L2 sensor | V | 200-250 | 1min | Tension entrée phase L2 |
| input_voltage_L3 | elec input voltage L3 sensor | V | 200-250 | 1min | Tension entrée phase L3 |
| input_current_L1 | elec input current L1 sensor | A | 0-63 | 1min | Courant entrée phase L1 |
| input_current_L2 | elec input current L2 sensor | A | 0-63 | 1min | Courant entrée phase L2 |
| input_current_L3 | elec input current L3 sensor | A | 0-63 | 1min | Courant entrée phase L3 |
| total_power | elec power sensor | kW | 0-60 | 1min | Puissance active totale |
| total_apparent_power | elec apparent power sensor | kVA | 0-60 | 1min | Puissance apparente totale |
| power_factor | elec power factor sensor | - | 0.8-1.0 | 1min | Facteur de puissance |
| total_energy | elec energy sensor | kWh | 0-999999 | 15min | Énergie cumulée |
| frequency | elec frequency sensor | Hz | 49-51 | 1min | Fréquence réseau |
| outlet_current | outlet elec current sensor | A | 0-16 | 1min | Courant par prise (POPS) |
| outlet_power | outlet elec power sensor | W | 0-4000 | 1min | Puissance par prise |
| thd | elec thd sensor | % | 0-20 | 5min | Distorsion harmonique totale |
| ambient_temp | ambient air temp sensor | °C | 15-40 | 1min | Température ambiante (capteur intégré) |
| ambient_humidity | ambient air humidity sensor | %RH | 20-80 | 5min | Humidité ambiante (capteur intégré) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| outlet_enable_cmd | outlet enable cmd | - | 0/1 | Actionneur | Commande on/off prise individuelle |
| outlet_cycle_cmd | outlet cycle cmd | - | 0/1 | Actionneur | Cycle power prise (off puis on) |
| overload_threshold_sp | overload threshold sp | A | 10-63 | Consigne | Seuil alarme surcharge |
| undervoltage_threshold_sp | undervoltage threshold sp | V | 180-220 | Consigne | Seuil alarme sous-tension |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| input_power_ok | input power ok status | Boolean | true/false | Alimentation entrée présente |
| outlet_status | outlet run status | Boolean | true/false | État prise (on/off) |
| overload_alarm | overload alarm | Boolean | true/false | Alarme surcharge |
| undervoltage_alarm | undervoltage alarm | Boolean | true/false | Alarme sous-tension |
| overvoltage_alarm | overvoltage alarm | Boolean | true/false | Alarme surtension |
| overcurrent_alarm | overcurrent alarm | Boolean | true/false | Alarme surintensité |
| high_temp_alarm | high temp alarm | Boolean | true/false | Alarme température élevée |
| breaker_tripped | breaker tripped alarm | Boolean | true/false | Disjoncteur déclenché |

## Mappings Protocoles

| Point | SNMP OID (exemple) | Modbus Register | BACnet Object |
|-------|-------------------|-----------------|---------------|
| input_voltage_L1 | .1.3.6.1.4.1.X.1.1 | 40001 (HR) | AI:1 |
| input_voltage_L2 | .1.3.6.1.4.1.X.1.2 | 40002 (HR) | AI:2 |
| input_voltage_L3 | .1.3.6.1.4.1.X.1.3 | 40003 (HR) | AI:3 |
| input_current_L1 | .1.3.6.1.4.1.X.2.1 | 40004 (HR) | AI:4 |
| input_current_L2 | .1.3.6.1.4.1.X.2.2 | 40005 (HR) | AI:5 |
| input_current_L3 | .1.3.6.1.4.1.X.2.3 | 40006 (HR) | AI:6 |
| total_power | .1.3.6.1.4.1.X.3.1 | 40007 (HR) | AI:7 |
| total_apparent_power | .1.3.6.1.4.1.X.3.2 | 40008 (HR) | AI:8 |
| power_factor | .1.3.6.1.4.1.X.3.3 | 40009 (HR) | AI:9 |
| total_energy | .1.3.6.1.4.1.X.4.1 | 40010 (HR) | AI:10 |
| outlet_enable_cmd | .1.3.6.1.4.1.X.5.n | 00001+ (Coil) | BO:1+ |
| overload_alarm | .1.3.6.1.4.1.X.6.1 | 10001 (DI) | BI:1 |

**Notes sur les mappings :**
- SNMP : OID spécifiques au fabricant (Raritan, APC, Server Technology)
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- BACnet : AI = Analog Input, BO = Binary Output, BI = Binary Input

## Précision de Mesure Typique

| Type PDU | Précision Courant | Précision Puissance | Niveau |
|----------|-------------------|---------------------|--------|
| Metered Basic | ±3% | ±3% | PDU |
| Monitored | ±1% | ±1% | PDU + Phase |
| Intelligent (POPS) | ±0.5% | ±0.5% | Par prise |

## Sources
- [Server Technology Monitored PDU](https://www.servertech.com/solutions/monitored-pdu/) - Documentation PDU intelligent
- [Rittal PDU Modbus Monitoring](https://blog.paessler.com/monitoring-power-consumption-on-rittal-pdus-with-modbus-tcp) - Configuration Modbus
- [Packet Power Protocols](https://www.packetpower.com/blog/energy-monitoring-systems-and-data-center-compatibility) - BACnet/Modbus/SNMP
- [BPP PDU Systems](https://www.bppmfg.com/products-solutions/power-distribution-units-pdu/) - PDU avec BACnet/Modbus
