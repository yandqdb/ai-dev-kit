"""
MCP Tool Wrappers for Compute Operations

Wraps databricks-mcp-core compute functions as MCP tools.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "../../../databricks-mcp-core")
)

from databricks_mcp_core.compute import execution  # noqa: E402


def create_context_tool(arguments: dict) -> dict:
    """MCP tool: Create execution context"""
    try:
        context_id = execution.create_context(
            arguments.get("cluster_id"),
            arguments.get("language", "python")
        )
        cluster_id = arguments.get('cluster_id')
        language = arguments.get('language', 'python')
        return {
            "content": [{
                "type": "text",
                "text": f"Context created successfully!\n\n"
                       f"Context ID: {context_id}\n"
                       f"Cluster ID: {cluster_id}\n"
                       f"Language: {language}\n\n"
                       f"Use this context_id for subsequent commands."
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error creating context: {str(e)}"
            }],
            "isError": True
        }


def execute_command_with_context_tool(arguments: dict) -> dict:
    """MCP tool: Execute command with context"""
    try:
        result = execution.execute_command_with_context(
            arguments.get("cluster_id"),
            arguments.get("context_id"),
            arguments.get("code")
        )
        if result.success:
            return {"content": [{"type": "text", "text": result.output}]}
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {result.error}"
                }],
                "isError": True
            }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }


def destroy_context_tool(arguments: dict) -> dict:
    """MCP tool: Destroy execution context"""
    try:
        context_id = arguments.get('context_id')
        execution.destroy_context(
            arguments.get("cluster_id"),
            context_id
        )
        return {
            "content": [{
                "type": "text",
                "text": f"Context {context_id} destroyed successfully!"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error destroying context: {str(e)}"
            }],
            "isError": True
        }


def databricks_command_tool(arguments: dict) -> dict:
    """MCP tool: Execute one-off Databricks command"""
    try:
        result = execution.execute_databricks_command(
            arguments.get("cluster_id"),
            arguments.get("language", "python"),
            arguments.get("code"),
            arguments.get("timeout", 120)
        )
        if result.success:
            return {"content": [{"type": "text", "text": result.output}]}
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {result.error}"
                }],
                "isError": True
            }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }


# Tool handler mapping
TOOL_HANDLERS = {
    "create_context": create_context_tool,
    "execute_command_with_context": execute_command_with_context_tool,
    "destroy_context": destroy_context_tool,
    "databricks_command": databricks_command_tool,
}


def get_tool_definitions():
    """Return MCP tool definitions for compute operations"""
    return [
        {
            "name": "create_context",
            "description": "Create execution context on cluster",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cluster_id": {
                        "type": "string",
                        "description": "ID of the cluster"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language (python, scala, sql, r)",
                        "default": "python"
                    }
                },
                "required": ["cluster_id"]
            }
        },
        {
            "name": "execute_command_with_context",
            "description": "Execute code using existing context",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cluster_id": {
                        "type": "string",
                        "description": "ID of the cluster"
                    },
                    "context_id": {
                        "type": "string",
                        "description": "Context ID from create_context"
                    },
                    "code": {
                        "type": "string",
                        "description": "Code to execute"
                    }
                },
                "required": ["cluster_id", "context_id", "code"]
            }
        },
        {
            "name": "destroy_context",
            "description": "Destroy an execution context",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cluster_id": {
                        "type": "string",
                        "description": "ID of the cluster"
                    },
                    "context_id": {
                        "type": "string",
                        "description": "Context ID to destroy"
                    }
                },
                "required": ["cluster_id", "context_id"]
            }
        },
        {
            "name": "databricks_command",
            "description": "Execute one-off command (creates/destroys context)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cluster_id": {
                        "type": "string",
                        "description": "ID of the cluster"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language (python, scala, sql, r)",
                        "default": "python"
                    },
                    "code": {
                        "type": "string",
                        "description": "Code to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds",
                        "default": 120
                    }
                },
                "required": ["cluster_id", "code"]
            }
        }
    ]
