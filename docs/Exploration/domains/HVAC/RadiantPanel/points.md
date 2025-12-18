# Points de Panneau Rayonnant (Radiant Panel)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 5

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_temp | zone air temp sensor | °C | 18-28 | 1min | Température de la zone |
| zone_humidity | zone air humidity sensor | %RH | 30-70 | 1min | Humidité relative zone (anti-condensation) |
| surface_temp | surface temp sensor | °C | 15-40 | 1min | Température de surface du panneau |
| water_entering_temp | entering water temp sensor | °C | 14-55 | 1min | Température eau entrée |
| water_leaving_temp | leaving water temp sensor | °C | 16-50 | 1min | Température eau sortie |
| water_flow | water flow sensor | l/h | 0-500 | 5min | Débit d'eau dans le panneau |
| dewpoint_temp | zone dewpoint temp sensor | °C | 5-20 | 1min | Point de rosée zone |
| operative_temp | operative temp sensor | °C | 18-26 | 1min | Température opérative (radiant + air) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_sp | zone air temp sp | °C | 18-26 | Consigne | Consigne température zone |
| valve_cmd | water valve cmd | % | 0-100 | Actionneur | Position vanne eau |
| surface_temp_min_sp | surface temp min sp | °C | 16-20 | Consigne | Limite basse surface (anti-condensation) |
| water_temp_sp | water temp sp | °C | 15-50 | Consigne | Consigne température eau (si local) |
| mode_cmd | mode cmd | - | off/heat/cool | Actionneur | Commande mode chauffage/refroidissement |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| heating_mode | heating mode status | Boolean | true/false | Mode chauffage actif |
| cooling_mode | cooling mode status | Boolean | true/false | Mode refroidissement actif |
| condensation_alarm | condensation alarm | Boolean | true/false | Alarme risque condensation |
| valve_fault | valve fault alarm | Boolean | true/false | Défaut vanne motorisée |
| zone_occupied | zone occupied status | Boolean | true/false | Zone occupée |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_temp | AI:1 | 40001 (HR) | 1/1/1 |
| zone_humidity | AI:2 | 40002 (HR) | 1/1/2 |
| surface_temp | AI:3 | 40003 (HR) | 1/1/3 |
| water_entering_temp | AI:4 | 40004 (HR) | 1/1/4 |
| water_leaving_temp | AI:5 | 40005 (HR) | 1/1/5 |
| water_flow | AI:6 | 40006 (HR) | 1/1/6 |
| dewpoint_temp | AI:7 | 40007 (HR) | 1/1/7 |
| operative_temp | AV:1 | 40101 (HR) | 1/1/8 |
| zone_temp_sp | AV:2 | 40102 (HR) | 1/2/1 |
| valve_cmd | AO:1 | 40201 (HR) | 1/2/2 |
| surface_temp_min_sp | AV:3 | 40103 (HR) | 1/2/3 |
| water_temp_sp | AV:4 | 40104 (HR) | 1/2/4 |
| mode_cmd | MSV:1 | 40301 (HR) | 1/2/5 |
| heating_mode | BI:1 | 10001 (DI) | 1/3/1 |
| cooling_mode | BI:2 | 10002 (DI) | 1/3/2 |
| condensation_alarm | BI:3 | 10003 (DI) | 1/3/3 |
| valve_fault | BI:4 | 10004 (DI) | 1/3/4 |
| zone_occupied | BI:5 | 10005 (DI) | 1/3/5 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Protection Anti-Condensation

| Condition | Action | Seuil Typique |
|-----------|--------|---------------|
| T_surface < T_dewpoint + 2°C | Fermer vanne froid | Marge 2-3°C |
| HR zone > 65% | Réduire puissance froid | Limite 60-65% HR |
| T_eau_entrée < T_dewpoint + 3°C | Rehausser température eau | Eau glacée min 14-16°C |

## Températures Typiques par Mode

| Mode | Température Eau | Température Surface | Application |
|------|-----------------|---------------------|-------------|
| Chauffage plancher | 30-40°C | 25-29°C | Confort optimal |
| Chauffage plafond | 35-50°C | 28-35°C | Charge plus élevée |
| Refroidissement plafond | 14-18°C | 17-20°C | Anti-condensation |
| TABS (activation masse) | 18-25°C | 20-24°C | Inertie lente |

## Sources
- ASHRAE Handbook - Radiant Heating and Cooling
- Project Haystack - Radiant Panel Tags
- Brick Schema - Radiant_Panel Class
- ISO 11855 - Building environment design - Embedded radiant systems
