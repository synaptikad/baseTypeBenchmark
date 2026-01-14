# Q16 - Semantic Tag Search

## Question
> **FR:** Quels équipements correspondent à un pattern de tags Brick/Haystack donné ?
>
> **EN:** What equipment matches a given Brick/Haystack tag pattern?

## Cas d'usage / Use case
Interopérabilité ontologies, recherche sémantique.
Ontology interoperability, semantic search.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| TAG_PATTERN | string | Pattern regex pour filtrer les tags | `^brick:` |

## JSONB Path
`data->'tags'`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ✅ | ✅ | ✅ |
