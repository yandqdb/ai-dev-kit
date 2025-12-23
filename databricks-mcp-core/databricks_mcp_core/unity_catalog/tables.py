"""
Unity Catalog - Table Operations

Functions for managing tables in Unity Catalog.
"""
from typing import List, Optional
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import TableInfo, ColumnInfo, TableType, DataSourceFormat


def list_tables(catalog_name: str, schema_name: str) -> List[TableInfo]:
    """
    List all tables in a schema.

    Args:
        catalog_name: Name of the catalog
        schema_name: Name of the schema

    Returns:
        List of TableInfo objects with table metadata

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()
    return list(w.tables.list(
        catalog_name=catalog_name,
        schema_name=schema_name
    ))


def get_table(full_table_name: str) -> TableInfo:
    """
    Get detailed information about a specific table.

    Args:
        full_table_name: Full table name (catalog.schema.table format)

    Returns:
        TableInfo object with table metadata including:
        - name, full_name, catalog_name, schema_name
        - table_type, owner, comment
        - created_at, updated_at
        - storage_location, columns

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()
    return w.tables.get(full_name=full_table_name)


def create_table(
    catalog_name: str,
    schema_name: str,
    table_name: str,
    columns: List[ColumnInfo],
    table_type: TableType = TableType.MANAGED,
    comment: Optional[str] = None,
    storage_location: Optional[str] = None
) -> TableInfo:
    """
    Create a new table in Unity Catalog.

    Args:
        catalog_name: Name of the catalog
        schema_name: Name of the schema
        table_name: Name of the table to create
        columns: List of ColumnInfo objects defining table columns
                 Example: [ColumnInfo(name="id", type_name="INT"),
                          ColumnInfo(name="value", type_name="STRING")]
        table_type: TableType.MANAGED or TableType.EXTERNAL (default: TableType.MANAGED)
        comment: Optional description of the table
        storage_location: Storage location for EXTERNAL tables

    Returns:
        TableInfo object with created table metadata

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()

    # Build kwargs conditionally
    kwargs = {
        "name": table_name,
        "catalog_name": catalog_name,
        "schema_name": schema_name,
        "table_type": table_type,
        "columns": columns,
        "data_source_format": DataSourceFormat.DELTA
    }

    if comment:
        kwargs["comment"] = comment
    if storage_location and table_type == TableType.EXTERNAL:
        kwargs["storage_location"] = storage_location

    return w.tables.create(**kwargs)


def delete_table(full_table_name: str) -> None:
    """
    Delete a table from Unity Catalog.

    Args:
        full_table_name: Full table name (catalog.schema.table format)

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()
    w.tables.delete(full_name=full_table_name)
