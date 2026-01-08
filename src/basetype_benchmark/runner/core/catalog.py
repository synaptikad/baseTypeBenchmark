"""Query catalog loader for Benchmark Runner V3.

Loads and parses queries/catalog.yaml to provide query metadata.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

from ..config import EngineType, ParadigmStatus, QueryCategory


class ParameterFormat(BaseModel):
    """Parameter format per dialect."""
    sql: str = Field(description="SQL format (e.g., $1)")
    cypher: str = Field(description="Cypher format (e.g., $meter_id)")
    sparql: str = Field(description="SPARQL format (e.g., ?meterId)")


class QueryParameter(BaseModel):
    """Query parameter definition."""
    name: str
    type: str = Field(default="string")
    description: str = Field(default="")
    format: ParameterFormat
    example: Optional[str | int | float] = None


class ColumnSchema(BaseModel):
    """Result column schema."""
    name: str
    type: str
    description: str = Field(default="")


class ResultSchema(BaseModel):
    """Expected result schema."""
    columns: list[ColumnSchema] = Field(default_factory=list)
    order_by: list[str] = Field(default_factory=list)


class ParadigmStatusInfo(BaseModel):
    """Status information for a paradigm."""
    status: ParadigmStatus
    note: str = Field(default="")


class QueryDefinition(BaseModel):
    """Complete query definition from catalog."""
    id: str
    name: str
    category: QueryCategory
    intention: str = Field(default="")
    use_case: str = Field(default="")
    parameters: list[QueryParameter] = Field(default_factory=list)
    relations: list[str] = Field(default_factory=list)
    max_depth: Optional[int | str] = None  # Can be int or template like "$MAX_HOPS"
    direction: Optional[str] = None
    result_schema: ResultSchema = Field(default_factory=ResultSchema)
    paradigm_status: dict[EngineType, ParadigmStatusInfo] = Field(default_factory=dict)

    def get_status(self, engine: EngineType) -> ParadigmStatus:
        """Get status for a specific paradigm."""
        info = self.paradigm_status.get(engine)
        return info.status if info else ParadigmStatus.IMPOSSIBLE

    def can_execute(self, engine: EngineType) -> bool:
        """Check if query can be executed on this paradigm."""
        return self.get_status(engine) != ParadigmStatus.IMPOSSIBLE

    def get_parameter_names(self) -> list[str]:
        """Get list of parameter names."""
        return [p.name for p in self.parameters]

    def get_parameter_format(self, param_name: str, dialect: str) -> Optional[str]:
        """Get parameter format for a specific dialect."""
        for p in self.parameters:
            if p.name == param_name:
                return getattr(p.format, dialect, None)
        return None

    @property
    def parameter_order(self) -> list[str]:
        """Get parameter names in their defined order.

        Returns:
            List of parameter names in the order they appear in the catalog.
            This order is used for positional parameter binding in SQL.
        """
        return [p.name for p in self.parameters]


class CategoryDefinition(BaseModel):
    """Query category definition."""
    description: str
    queries: list[str]


class QueryCatalog:
    """Catalog of benchmark queries.

    Loads queries/catalog.yaml and provides access to query definitions.
    """

    def __init__(self, catalog_path: Optional[Path] = None):
        """Initialize catalog.

        Args:
            catalog_path: Path to catalog.yaml. If None, uses default location.
        """
        if catalog_path is None:
            # Default: relative to this file
            catalog_path = Path(__file__).parents[4] / "queries" / "catalog.yaml"

        self.catalog_path = catalog_path
        self._queries: dict[str, QueryDefinition] = {}
        self._categories: dict[str, CategoryDefinition] = {}
        self._version: str = ""
        self._loaded = False

    def load(self) -> None:
        """Load catalog from YAML file."""
        if self._loaded:
            return

        with open(self.catalog_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self._version = data.get("version", "")

        # Load categories
        for cat_name, cat_data in data.get("categories", {}).items():
            self._categories[cat_name] = CategoryDefinition(
                description=cat_data.get("description", ""),
                queries=cat_data.get("queries", [])
            )

        # Load queries
        for query_id, query_data in data.get("queries", {}).items():
            self._queries[query_id] = self._parse_query(query_id, query_data)

        self._loaded = True

    def _parse_query(self, query_id: str, data: dict) -> QueryDefinition:
        """Parse a query definition from YAML data."""
        # Parse parameters
        parameters = []
        for p in data.get("parameters", []):
            format_data = p.get("format", {})
            parameters.append(QueryParameter(
                name=p["name"],
                type=p.get("type", "string"),
                description=p.get("description", ""),
                format=ParameterFormat(
                    sql=format_data.get("sql", ""),
                    cypher=format_data.get("cypher", ""),
                    sparql=format_data.get("sparql", "")
                ),
                example=p.get("example")
            ))

        # Parse result schema
        result_schema = ResultSchema()
        if "result_schema" in data:
            rs = data["result_schema"]
            columns = [
                ColumnSchema(
                    name=c["name"],
                    type=c["type"],
                    description=c.get("description", "")
                )
                for c in rs.get("columns", [])
            ]
            result_schema = ResultSchema(
                columns=columns,
                order_by=rs.get("order_by", [])
            )

        # Parse paradigm status
        paradigm_status = {}
        for engine_str, status_data in data.get("paradigm_status", {}).items():
            try:
                engine = EngineType(engine_str)
                paradigm_status[engine] = ParadigmStatusInfo(
                    status=ParadigmStatus(status_data.get("status", "IMPOSSIBLE")),
                    note=status_data.get("note", "")
                )
            except ValueError:
                # Unknown engine, skip
                pass

        # Parse category
        cat_str = data.get("category", "graph_only")
        try:
            category = QueryCategory(cat_str)
        except ValueError:
            category = QueryCategory.GRAPH_ONLY

        return QueryDefinition(
            id=query_id,
            name=data.get("name", query_id),
            category=category,
            intention=data.get("intention", ""),
            use_case=data.get("use_case", ""),
            parameters=parameters,
            relations=data.get("relations", []),
            max_depth=data.get("max_depth"),
            direction=data.get("direction"),
            result_schema=result_schema,
            paradigm_status=paradigm_status
        )

    @property
    def version(self) -> str:
        """Catalog version."""
        self.load()
        return self._version

    def get_query(self, query_id: str) -> Optional[QueryDefinition]:
        """Get a query definition by ID."""
        self.load()
        return self._queries.get(query_id)

    def get_all_queries(self) -> list[QueryDefinition]:
        """Get all query definitions."""
        self.load()
        return list(self._queries.values())

    def get_queries_by_category(self, category: QueryCategory) -> list[QueryDefinition]:
        """Get all queries in a category."""
        self.load()
        return [q for q in self._queries.values() if q.category == category]

    def get_query_ids(self) -> list[str]:
        """Get all query IDs."""
        self.load()
        return list(self._queries.keys())

    def get_executable_queries(self, engine: EngineType) -> list[QueryDefinition]:
        """Get queries that can be executed on a paradigm."""
        self.load()
        return [q for q in self._queries.values() if q.can_execute(engine)]

    def get_category(self, category_name: str) -> Optional[CategoryDefinition]:
        """Get a category definition."""
        self.load()
        return self._categories.get(category_name)

    def get_all_categories(self) -> dict[str, CategoryDefinition]:
        """Get all categories."""
        self.load()
        return dict(self._categories)

    def get_paradigm_matrix(self) -> dict[str, dict[EngineType, ParadigmStatus]]:
        """Get paradigm support matrix for all queries."""
        self.load()
        return {
            query_id: {
                engine: query.get_status(engine)
                for engine in EngineType
            }
            for query_id, query in self._queries.items()
        }


# Singleton instance for convenience
_catalog: Optional[QueryCatalog] = None


def get_catalog() -> QueryCatalog:
    """Get the global catalog instance."""
    global _catalog
    if _catalog is None:
        _catalog = QueryCatalog()
    return _catalog


def get_query(query_id: str) -> Optional[QueryDefinition]:
    """Get a query definition by ID (convenience function)."""
    return get_catalog().get_query(query_id)
