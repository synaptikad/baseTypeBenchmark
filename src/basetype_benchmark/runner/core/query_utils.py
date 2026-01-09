"""Query utility functions for benchmark runner.

Provides helpers for:
- Comment stripping from query files
- Parameter key normalization
- Parameter ordering
"""
from __future__ import annotations

import re
from typing import Any


def strip_query_comments(query: str, dialect: str) -> str:
    """Strip comments from query text based on dialect.

    Args:
        query: Query text with potential comments
        dialect: Query dialect ("sql", "cypher", "sparql")

    Returns:
        Query text with comments removed
    """
    lines = []
    for line in query.split("\n"):
        # SQL: -- comments
        if dialect == "sql":
            if "--" in line:
                # Keep everything before --
                line = line.split("--")[0]

        # Cypher: // and -- comments
        elif dialect == "cypher":
            if "//" in line:
                line = line.split("//")[0]
            elif "--" in line:
                line = line.split("--")[0]

        # SPARQL: # comments (but not inside IRIs or strings)
        elif dialect == "sparql":
            # Only treat # as comment if it's at start of line (after whitespace)
            stripped_line = line.lstrip()
            if stripped_line.startswith("#"):
                line = ""
            else:
                # For inline comments, only strip if # is outside IRIs and strings
                in_iri = False
                in_string = False
                string_char = None
                for i, char in enumerate(line):
                    if not in_string:
                        if char == '<':
                            in_iri = True
                        elif char == '>':
                            in_iri = False
                        elif char in ('"', "'"):
                            in_string = True
                            string_char = char
                        elif char == '#' and not in_iri:
                            # Found comment start outside IRI and string
                            line = line[:i]
                            break
                    else:
                        # In string - check for end
                        if char == string_char and (i == 0 or line[i-1] != '\\'):
                            in_string = False
                            string_char = None

        # Keep line if not empty after stripping
        stripped = line.rstrip()
        if stripped:
            lines.append(stripped)

    return "\n".join(lines)


def normalize_param_keys(params: dict[str, Any], target_case: str = "lower") -> dict[str, Any]:
    """Normalize parameter key casing.

    Args:
        params: Parameter dictionary with keys to normalize
        target_case: Target case format:
            - "lower": METER_ID → meter_id
            - "camel": METER_ID → meterId
            - "upper": meter_id → METER_ID

    Returns:
        New dict with normalized keys
    """
    if target_case == "lower":
        return {k.lower(): v for k, v in params.items()}

    elif target_case == "camel":
        result = {}
        for k, v in params.items():
            # METER_ID → meterId
            # Split on underscore, lowercase all, capitalize except first
            parts = k.lower().split("_")
            camel = parts[0] + "".join(word.capitalize() for word in parts[1:])
            result[camel] = v
        return result

    elif target_case == "upper":
        return {k.upper(): v for k, v in params.items()}

    else:
        return params.copy()


def get_ordered_params(params: dict[str, Any], param_order: list[str]) -> tuple[Any, ...]:
    """Extract parameter values in specified order.

    Args:
        params: Parameter dictionary
        param_order: List of parameter names in desired order

    Returns:
        Tuple of values in the specified order

    Example:
        >>> params = {"b": 2, "a": 1, "c": 3}
        >>> get_ordered_params(params, ["a", "b", "c"])
        (1, 2, 3)
    """
    result = []
    for param_name in param_order:
        # Try exact match first
        if param_name in params:
            result.append(params[param_name])
        # Try lowercase match
        elif param_name.lower() in params:
            result.append(params[param_name.lower()])
        # Try uppercase match
        elif param_name.upper() in params:
            result.append(params[param_name.upper()])
        else:
            # Parameter not found - this will cause an error downstream
            # but we let the database driver handle it
            pass

    return tuple(result)
