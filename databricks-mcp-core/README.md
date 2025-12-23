# Databricks MCP Core

High-level, AI-assistant-friendly Python functions for building Databricks projects.

## Overview

The `databricks-mcp-core` package contains reusable, opinionated functions for interacting with Databricks platform components. It is organized by product line for scalability:

- **unity_catalog/** - Unity Catalog operations (catalogs, schemas, tables)
- **compute/** - Compute and execution operations
- **spark_declarative_pipelines/** - SDP operations (coming soon)
- **agent_bricks/** - Agent Bricks operations (coming soon)
- **dabs/** - DAB generation (coming soon)

## Installation

```bash
pip install -e .
```

## Usage

All functions use the official `databricks-sdk` and create their own `WorkspaceClient` instances internally. Authentication is handled automatically via environment variables or Databricks configuration profiles.

```python
from databricks_mcp_core.unity_catalog import catalogs, schemas, tables
from databricks.sdk.service.catalog import ColumnInfo, TableType

# Set authentication (optional - defaults to standard Databricks auth)
# export DATABRICKS_CONFIG_PROFILE=my-profile
# or use DATABRICKS_HOST and DATABRICKS_TOKEN

# List catalogs (returns List[CatalogInfo])
all_catalogs = catalogs.list_catalogs()
for catalog in all_catalogs:
    print(catalog.name)

# Create a schema (returns SchemaInfo)
schema = schemas.create_schema(
    catalog_name="main",
    schema_name="my_schema",
    comment="Example schema"
)

# Create a table (returns TableInfo)
table = tables.create_table(
    catalog_name="main",
    schema_name="my_schema",
    table_name="my_table",
    columns=[
        ColumnInfo(name="id", type_name="INT"),
        ColumnInfo(name="value", type_name="STRING")
    ],
    table_type=TableType.MANAGED
)
```

## Architecture

This is a pure Python library with no dependencies on MCP protocol code. It can be used standalone in notebooks, scripts, or other Python projects.

For MCP server functionality, see the `databricks-mcp-server` package.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black databricks_mcp_core/
```
