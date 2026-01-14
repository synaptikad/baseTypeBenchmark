# Q27 - Evacuation Path

## Question
> **FR:** Quel est le chemin d'évacuation le plus court depuis un espace vers une sortie de secours ?
>
> **EN:** What is the shortest evacuation path from a space to an emergency exit?

## Cas d'usage / Use case
Plan d'évacuation, sécurité incendie, accessibilité.
Evacuation plan, fire safety, accessibility.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| SPACE_ID | string | ID de l'espace de départ | `space_office_301` |

## Relations
`EMERGENCY_EXIT`, `ACCESSIBLE_FROM`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ⚠️ | ⚠️ | ✅ | ✅ | ❌ |
