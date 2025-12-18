# Instructions : Compléter les Équipements HVAC Manquants

## Objectif

Compléter les fichiers manquants (equipment.md et/ou points.md) pour les équipements HVAC.

## ÉTAPE 1 : Vérifier ce qui manque

**AVANT DE COMMENCER**, exécute cette commande pour identifier les fichiers manquants :

```bash
for equip in AirFilter ChilledBeam CondensingUnit Damper Dehumidifier DualDuctTerminal Economizer ERV ExhaustFan HeatExchanger HeatRecoveryChiller HRV Humidifier InductionUnit MAU RadiantPanel RooftopUnit TerminalUnit UnitHeater UnitVentilator Valve; do
  dir="C:/DEV/benchmark/docs/Exploration/domains/HVAC/$equip"
  eq="MANQUE"; pt="MANQUE"
  [ -f "$dir/equipment.md" ] && eq="OK"
  [ -f "$dir/points.md" ] && pt="OK"
  echo "$equip: equipment.md=$eq | points.md=$pt"
done
```

Ne crée que les fichiers qui **MANQUENT**. Ne touche pas aux fichiers existants.

## ÉTAPE 2 : Pour chaque équipement incomplet

### 2.1 Recherche Web OBLIGATOIRE

Pour chaque équipement, **FAIS UNE RECHERCHE WEB** avant de créer les fichiers :

```
Recherches à faire pour {EQUIPMENT} :
1. "{EQUIPMENT} BACnet points list"
2. "{EQUIPMENT} BMS monitoring points"
3. "{EQUIPMENT} Haystack tags"
4. "{EQUIPMENT} typical sensors actuators"
5. Site constructeur : Carrier, Trane, Daikin, Johnson Controls, Honeywell, Siemens
```

**Utilise l'outil WebSearch** pour chaque recherche et note les sources.

### 2.2 Créer equipment.md (si manquant)

Emplacement : `C:\DEV\benchmark\docs\Exploration\domains\HVAC\{EQUIPMENT}\equipment.md`

**FORMAT EXACT :**

```markdown
# {Nom Complet} ({Nom Français si différent})

## Identifiant
- **Code** : {CODE_COURT}
- **Haystack** : `{tag-haystack-equip}`
- **Brick** : `brick:{BrickClass}`

## Description
{Description détaillée de l'équipement : fonction principale, principe de fonctionnement, 2-3 phrases}

## Fonction
{Rôle dans le système HVAC, objectif principal}

## Variantes Courantes
- **{Variante 1}** : {Description courte}
- **{Variante 2}** : {Description courte}
- **{Variante 3}** : {Description courte}
{4-6 variantes typiques}

## Caractéristiques Techniques Typiques
- {Paramètre 1} : {Plage valeurs}
- {Paramètre 2} : {Plage valeurs}
- Protocoles : BACnet, Modbus, LON
- Points de supervision : {liste points clés}

## Localisation Typique
- {Emplacement 1}
- {Emplacement 2}
- {Emplacement 3}

## Relations avec Autres Équipements
- **Alimente** : {équipements alimentés}
- **Alimenté par** : {équipements sources}
- **Contrôlé par** : {contrôleurs}
- **Interagit avec** : {équipements liés}

## Quantité Typique par Bâtiment
- Petit (5 étages) : {X-Y} unités
- Moyen (15 étages) : {X-Y} unités
- Grand (30+ étages) : {X-Y} unités

## Sources
- {Source 1 avec lien si disponible}
- {Source 2}
- {Source 3}
```

### 2.3 Créer points.md (si manquant)

Emplacement : `C:\DEV\benchmark\docs\Exploration\domains\HVAC\{EQUIPMENT}\points.md`

**FORMAT EXACT :**

```markdown
# Points de {Nom Équipement}

## Synthèse
- **Total points mesure** : {X}
- **Total points commande** : {Y}
- **Total points état** : {Z}

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| {nom_point} | {tag-haystack-sensor} | {°C/Pa/%/kW/A/m³/h} | {min-max} | {30sec/1min/5min/15min} | {Description courte} |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| {nom_point_cmd} | {tag-haystack-cmd} | {%/°C/Hz} | {0-100} | {Actionneur/Consigne} | {Description} |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| {nom_status} | {tag-haystack-status} | {Boolean/Enum} | {true/false ou valeurs} | {Description} |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| {nom_point} | {AI:X / AO:X / AV:X / BI:X / BO:X / MSV:X} | {4000X (HR) / 1000X (Coil)} | {X/X/X} |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+ et 10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Sources
- [{Titre source}]({URL}) - {Description courte}
- [{Titre source 2}]({URL}) - {Description}
```

## Guide des Fréquences d'Échantillonnage

| Type de Point | Fréquence | Justification |
|---------------|-----------|---------------|
| Points sécurité (antigel, surpression) | 30sec | Réaction rapide critique |
| Température air/eau régulation | 1min | Boucle PID temps réel |
| Pression différentielle | 1min | Monitoring filtres/ventilateurs |
| Position vanne/registre | 1min | Suivi régulation |
| Vitesse ventilateur/pompe | 1min | Contrôle VFD |
| Consommation électrique | 5min | Analyse énergétique |
| État marche/arrêt | 1min | Supervision |
| Alarmes | Événement | Sécurité immédiate |
| Compteurs énergie | 15min | Facturation/reporting |
| Efficacité/rendement | 5min | Optimisation |

## Nombre de Points Typique par Complexité

| Complexité | Exemples | Mesure | Commande | État |
|------------|----------|--------|----------|------|
| Simple | AirFilter, Damper, Valve | 2-5 | 1-3 | 2-4 |
| Moyen | ExhaustFan, Humidifier, UnitHeater | 5-12 | 3-6 | 4-8 |
| Complexe | ERV, RooftopUnit, MAU | 15-30 | 8-15 | 8-15 |

## Tags Haystack Courants

### Mesures
- `{point}-temp-sensor` : Température
- `{point}-pressure-sensor` : Pression
- `{point}-flow-sensor` : Débit
- `{point}-humidity-sensor` : Humidité
- `{point}-speed-sensor` : Vitesse
- `{point}-power-sensor` : Puissance
- `{point}-current-sensor` : Courant

### Commandes
- `{point}-cmd` : Commande position/vitesse
- `{point}-sp` : Consigne (setpoint)
- `{point}-enable-cmd` : Activation

### États
- `{point}-run` : État marche
- `{point}-alarm` : Alarme
- `{point}-status` : État général
- `{point}-mode` : Mode fonctionnement

## RAPPELS IMPORTANTS

1. **TOUJOURS faire WebSearch** avant de créer un fichier
2. **VÉRIFIER** si le fichier existe déjà avant de le créer
3. **RESPECTER** le format exact (tableaux Markdown)
4. **DOCUMENTER** les sources avec URLs
5. **UTILISER** les unités SI (°C, Pa, m³/h, kW, A)
6. Points **RÉALISTES** basés sur équipements du marché

## Prompt de Lancement

Copie ce texte dans une nouvelle session Claude :

```
Tu dois compléter les fichiers equipment.md et points.md manquants pour 21 équipements HVAC.

IMPORTANT :
1. Lis d'abord C:\DEV\benchmark\docs\Exploration\PROMPT-COMPLETE-HVAC-POINTS.md
2. Vérifie quels fichiers manquent avec la commande bash fournie
3. Pour CHAQUE équipement incomplet :
   - Fais des recherches web (WebSearch) pour trouver les points BMS typiques
   - Crée equipment.md si manquant
   - Crée points.md si manquant
   - Respecte les formats exacts spécifiés

Commence par vérifier l'état actuel, puis traite les équipements un par un.
```
