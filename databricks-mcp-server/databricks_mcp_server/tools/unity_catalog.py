"""
MCP Tool Wrappers for Unity Catalog Operations

Wraps databricks-mcp-core Unity Catalog functions as MCP tools.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "../../../databricks-mcp-core")
)

from databricks_mcp_core.unity_catalog import catalogs, schemas, tables  # noqa: E402
from databricks.sdk.service.catalog import ColumnInfo, TableType  # noqa: E402


# === Catalog Tools ===

def list_catalogs_tool(arguments: dict) -> dict:
    """MCP tool: List all catalogs"""
    try:
        catalog_list = catalogs.list_catalogs()
        output = f"Found {len(catalog_list)} catalogs:\n\n"
        for catalog in catalog_list:
            output += f"📚 {catalog.name}\n"
            if catalog.comment:
                output += f"   Comment: {catalog.comment}\n"
            output += f"   Owner: {catalog.owner}\n"
            if catalog.created_at:
                output += f"   Created: {catalog.created_at}\n\n"
        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }


def get_catalog_tool(arguments: dict) -> dict:
    """MCP tool: Get catalog details"""
    try:
        catalog = catalogs.get_catalog(arguments.get("catalog_name"))
        output = f"📚 Catalog: {catalog.name}\n"
        output += f"   Full Name: {catalog.full_name}\n"
        output += f"   Owner: {catalog.owner}\n"
        output += f"   Comment: {catalog.comment or 'N/A'}\n"
        if catalog.created_at:
            output += f"   Created: {catalog.created_at}\n"
        if catalog.updated_at:
            output += f"   Updated: {catalog.updated_at}\n"
        if catalog.storage_location:
            output += f"   Storage Location: {catalog.storage_location}\n"
        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }


# === Schema Tools ===

def list_schemas_tool(arguments: dict) -> dict:
    """MCP tool: List schemas in a catalog"""
    try:
        schema_list = schemas.list_schemas(arguments.get("catalog_name"))
        catalog_name = arguments.get("catalog_name")
        output = f"Found {len(schema_list)} schemas in '{catalog_name}':\n\n"
        for schema in schema_list:
            output += f"📁 {schema.name}\n"
            if schema.comment:
                output += f"   Comment: {schema.comment}\n"
            output += f"   Owner: {schema.owner}\n"
            output += f"   Full Name: {schema.full_name}\n\n"
        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }


def get_schema_tool(arguments: dict) -> dict:
    """MCP tool: Get schema details"""
    try:
        schema = schemas.get_schema(arguments.get("full_schema_name"))
        output = f"📁 Schema: {schema.name}\n"
        output += f"   Full Name: {schema.full_name}\n"
        output += f"   Catalog: {schema.catalog_name}\n"
        output += f"   Owner: {schema.owner}\n"
        output += f"   Comment: {schema.comment or 'N/A'}\n"
        if schema.created_at:
            output += f"   Created: {schema.created_at}\n"
        if schema.updated_at:
            output += f"   Updated: {schema.updated_at}\n"
        if schema.storage_location:
            output += f"   Storage Location: {schema.storage_location}\n"
        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }


def create_schema_tool(arguments: dict) -> dict:
    """MCP tool: Create schema"""
    try:
        schema = schemas.create_schema(
            arguments.get("catalog_name"),
            arguments.get("schema_name"),
            arguments.get("comment")
        )
        output = "✅ Schema created successfully!\n\n"
        output += f"📁 Schema: {schema.name}\n"
        output += f"   Full Name: {schema.full_name}\n"
        output += f"   Catalog: {schema.catalog_name}\n"
        output += f"   Owner: {schema.owner}\n"
        if schema.comment:
            output += f"   Comment: {schema.comment}\n"
        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error creating schema: {str(e)}"
            }],
            "isError": True
        }


def update_schema_tool(arguments: dict) -> dict:
    """MCP tool: Update schema"""
    try:
        schema = schemas.update_schema(
            arguments.get("full_schema_name"),
            arguments.get("new_name"),
            arguments.get("comment"),
            arguments.get("owner")
        )
        output = "✅ Schema updated successfully!\n\n"
        output += f"📁 Schema: {schema.name}\n"
        output += f"   Full Name: {schema.full_name}\n"
        output += f"   Owner: {schema.owner}\n"
        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error updating schema: {str(e)}"
            }],
            "isError": True
        }


def delete_schema_tool(arguments: dict) -> dict:
    """MCP tool: Delete schema"""
    try:
        full_schema_name = arguments.get("full_schema_name")
        schemas.delete_schema(full_schema_name)
        output = f"✅ Schema '{full_schema_name}' deleted successfully!"
        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error deleting schema: {str(e)}"
            }],
            "isError": True
        }


# === Table Tools ===

def list_tables_tool(arguments: dict) -> dict:
    """MCP tool: List tables in a schema"""
    try:
        table_list = tables.list_tables(
            arguments.get("catalog_name"),
            arguments.get("schema_name")
        )
        catalog_name = arguments.get("catalog_name")
        schema_name = arguments.get("schema_name")
        output = f"Found {len(table_list)} tables in "
        output += f"{catalog_name}.{schema_name}:\n\n"
        for table in table_list:
            output += f"📊 {table.name}\n"
            output += f"   Type: {table.table_type}\n"
            if table.comment:
                output += f"   Comment: {table.comment}\n"
            output += f"   Owner: {table.owner}\n"
            output += f"   Full Name: {table.full_name}\n\n"
        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }


def get_table_tool(arguments: dict) -> dict:
    """MCP tool: Get table details"""
    try:
        table = tables.get_table(arguments.get("full_table_name"))
        output = f"📊 Table: {table.name}\n"
        output += f"   Full Name: {table.full_name}\n"
        output += f"   Catalog: {table.catalog_name}\n"
        output += f"   Schema: {table.schema_name}\n"
        output += f"   Type: {table.table_type}\n"
        output += f"   Owner: {table.owner}\n"
        output += f"   Comment: {table.comment or 'N/A'}\n"
        if table.created_at:
            output += f"   Created: {table.created_at}\n"
        if table.updated_at:
            output += f"   Updated: {table.updated_at}\n"
        if table.storage_location:
            output += f"   Storage Location: {table.storage_location}\n"

        # Add column information
        if table.columns:
            output += f"\n   Columns ({len(table.columns)}):\n"
            for col in table.columns:
                output += f"     - {col.name}: {col.type_name}\n"
                if col.comment:
                    output += f"       {col.comment}\n"

        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }


def create_table_tool(arguments: dict) -> dict:
    """MCP tool: Create table"""
    try:
        # Convert column dicts to ColumnInfo objects
        columns_data = arguments.get("columns", [])
        columns = [
            ColumnInfo(name=col["name"], type_name=col["type_name"])
            for col in columns_data
        ]

        # Convert table_type string to enum
        table_type_str = arguments.get("table_type", "MANAGED")
        table_type = (
            TableType.MANAGED if table_type_str == "MANAGED"
            else TableType.EXTERNAL
        )

        table = tables.create_table(
            arguments.get("catalog_name"),
            arguments.get("schema_name"),
            arguments.get("table_name"),
            columns,
            table_type,
            arguments.get("comment"),
            arguments.get("storage_location")
        )
        output = "✅ Table created successfully!\n\n"
        output += f"📊 Table: {table.name}\n"
        output += f"   Full Name: {table.full_name}\n"
        output += f"   Catalog: {table.catalog_name}\n"
        output += f"   Schema: {table.schema_name}\n"
        output += f"   Type: {table.table_type}\n"
        output += f"   Owner: {table.owner}\n"
        if table.comment:
            output += f"   Comment: {table.comment}\n"

        # Show columns
        if table.columns:
            output += f"\n   Columns ({len(table.columns)}):\n"
            for col in table.columns:
                output += f"     - {col.name}: {col.type_name}\n"

        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error creating table: {str(e)}"
            }],
            "isError": True
        }


def delete_table_tool(arguments: dict) -> dict:
    """MCP tool: Delete table"""
    try:
        full_table_name = arguments.get("full_table_name")
        tables.delete_table(full_table_name)
        output = f"✅ Table '{full_table_name}' deleted successfully!"
        return {"content": [{"type": "text", "text": output}]}
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error deleting table: {str(e)}"
            }],
            "isError": True
        }


# Tool handler mapping
TOOL_HANDLERS = {
    "list_catalogs": list_catalogs_tool,
    "get_catalog": get_catalog_tool,
    "list_schemas": list_schemas_tool,
    "get_schema": get_schema_tool,
    "create_schema": create_schema_tool,
    "update_schema": update_schema_tool,
    "delete_schema": delete_schema_tool,
    "list_tables": list_tables_tool,
    "get_table": get_table_tool,
    "create_table": create_table_tool,
    "delete_table": delete_table_tool,
}


def get_tool_definitions():
    """Return MCP tool definitions for Unity Catalog operations"""
    return [
        {
            "name": "list_catalogs",
            "description": "List all catalogs in Unity Catalog",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_catalog",
            "description": "Get detailed information about a catalog",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "catalog_name": {
                        "type": "string",
                        "description": "Name of the catalog"
                    }
                },
                "required": ["catalog_name"]
            }
        },
        {
            "name": "list_schemas",
            "description": "List all schemas in a catalog",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "catalog_name": {
                        "type": "string",
                        "description": "Name of the catalog"
                    }
                },
                "required": ["catalog_name"]
            }
        },
        {
            "name": "get_schema",
            "description": "Get detailed information about a schema",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "full_schema_name": {
                        "type": "string",
                        "description": "Full schema name (catalog.schema)"
                    }
                },
                "required": ["full_schema_name"]
            }
        },
        {
            "name": "list_tables",
            "description": "List all tables in a schema",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "catalog_name": {
                        "type": "string",
                        "description": "Name of the catalog"
                    },
                    "schema_name": {
                        "type": "string",
                        "description": "Name of the schema"
                    }
                },
                "required": ["catalog_name", "schema_name"]
            }
        },
        {
            "name": "get_table",
            "description": "Get detailed information about a table",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "full_table_name": {
                        "type": "string",
                        "description": "Full table name (catalog.schema.table)"
                    }
                },
                "required": ["full_table_name"]
            }
        },
        {
            "name": "create_schema",
            "description": "Create a new schema in Unity Catalog",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "catalog_name": {
                        "type": "string",
                        "description": "Name of the catalog"
                    },
                    "schema_name": {
                        "type": "string",
                        "description": "Name of the schema to create"
                    },
                    "comment": {
                        "type": "string",
                        "description": "Optional description of the schema"
                    }
                },
                "required": ["catalog_name", "schema_name"]
            }
        },
        {
            "name": "update_schema",
            "description": "Update an existing schema",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "full_schema_name": {
                        "type": "string",
                        "description": "Full schema name (catalog.schema)"
                    },
                    "new_name": {
                        "type": "string",
                        "description": "New name for the schema"
                    },
                    "comment": {
                        "type": "string",
                        "description": "New comment/description"
                    },
                    "owner": {
                        "type": "string",
                        "description": "New owner"
                    }
                },
                "required": ["full_schema_name"]
            }
        },
        {
            "name": "delete_schema",
            "description": "Delete a schema from Unity Catalog",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "full_schema_name": {
                        "type": "string",
                        "description": "Full schema name (catalog.schema)"
                    }
                },
                "required": ["full_schema_name"]
            }
        },
        {
            "name": "create_table",
            "description": "Create a new table in Unity Catalog",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "catalog_name": {
                        "type": "string",
                        "description": "Name of the catalog"
                    },
                    "schema_name": {
                        "type": "string",
                        "description": "Name of the schema"
                    },
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to create"
                    },
                    "columns": {
                        "type": "array",
                        "description": "List of column definitions",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Column name"
                                },
                                "type_name": {
                                    "type": "string",
                                    "description":
                                        "Column type (INT, STRING, etc.)"
                                }
                            },
                            "required": ["name", "type_name"]
                        }
                    },
                    "table_type": {
                        "type": "string",
                        "description": "Type: MANAGED or EXTERNAL",
                        "default": "MANAGED"
                    },
                    "comment": {
                        "type": "string",
                        "description": "Optional table description"
                    },
                    "storage_location": {
                        "type": "string",
                        "description": "Storage location for EXTERNAL tables"
                    }
                },
                "required": [
                    "catalog_name", "schema_name",
                    "table_name", "columns"
                ]
            }
        },
        {
            "name": "delete_table",
            "description": "Delete a table from Unity Catalog",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "full_table_name": {
                        "type": "string",
                        "description": "Full table name (catalog.schema.table)"
                    }
                },
                "required": ["full_table_name"]
            }
        },
    ]
