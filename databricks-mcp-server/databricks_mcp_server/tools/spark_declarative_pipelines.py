"""
MCP tool wrappers for Spark Declarative Pipelines operations.
"""
from typing import Dict, Any
from databricks_mcp_core.spark_declarative_pipelines import (
    pipelines, workspace_files
)
from databricks.sdk.service.pipelines import PipelineLibrary, NotebookLibrary
import json


# Pipeline Management Tools

def create_pipeline_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new Spark Declarative Pipeline."""
    try:
        # Convert library dicts to PipelineLibrary objects
        libraries_data = arguments["libraries"]
        libraries = []
        for lib_dict in libraries_data:
            if "notebook" in lib_dict:
                path = lib_dict["notebook"]["path"]
                libraries.append(
                    PipelineLibrary(notebook=NotebookLibrary(path=path))
                )
            # Add other library types as needed

        result = pipelines.create_pipeline(
            name=arguments["name"],
            storage=arguments["storage"],
            target=arguments["target"],
            libraries=libraries,
            clusters=arguments.get("clusters"),
            configuration=arguments.get("configuration"),
            continuous=arguments.get("continuous", False),
            serverless=arguments.get("serverless")
        )

        pipeline_id = result.pipeline_id
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ Pipeline created successfully!\n\n"
                           f"Pipeline ID: {pipeline_id}\n"
                           f"Name: {arguments['name']}\n"
                           f"Target: {arguments['target']}\n"
                           f"Storage: {arguments['storage']}\n"
                           f"Continuous: {arguments.get('continuous', False)}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error creating pipeline: {str(e)}"
            }],
            "isError": True
        }


def get_pipeline_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get pipeline details and configuration."""
    try:
        result = pipelines.get_pipeline(arguments["pipeline_id"])

        name = result.name if result.name else "unknown"
        state = result.state if result.state else "unknown"
        target = result.spec.target if result.spec else "unknown"

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"📊 Pipeline Details\n\n"
                           f"Name: {name}\n"
                           f"State: {state}\n"
                           f"Target: {target}\n"
                           f"Pipeline ID: {arguments['pipeline_id']}\n\n"
                           f"Full configuration:\n{json.dumps(result.as_dict(), indent=2)}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error getting pipeline: {str(e)}"
            }],
            "isError": True
        }


def update_pipeline_config_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Update pipeline configuration (not code files)."""
    try:
        # Convert libraries if provided
        libraries = None
        if arguments.get("libraries"):
            libraries_data = arguments["libraries"]
            libraries = []
            for lib_dict in libraries_data:
                if "notebook" in lib_dict:
                    path = lib_dict["notebook"]["path"]
                    libraries.append(
                        PipelineLibrary(notebook=NotebookLibrary(path=path))
                    )

        pipelines.update_pipeline(
            pipeline_id=arguments["pipeline_id"],
            name=arguments.get("name"),
            storage=arguments.get("storage"),
            target=arguments.get("target"),
            libraries=libraries,
            clusters=arguments.get("clusters"),
            configuration=arguments.get("configuration"),
            continuous=arguments.get("continuous"),
            serverless=arguments.get("serverless")
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": "✅ Pipeline configuration updated successfully!\n\n"
                           f"Pipeline ID: {arguments['pipeline_id']}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error updating pipeline: {str(e)}"
            }],
            "isError": True
        }


def delete_pipeline_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Delete a pipeline."""
    try:
        pipelines.delete_pipeline(arguments["pipeline_id"])

        return {
            "content": [
                {
                    "type": "text",
                    "text": "✅ Pipeline deleted successfully!\n\n"
                           f"Pipeline ID: {arguments['pipeline_id']}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error deleting pipeline: {str(e)}"
            }],
            "isError": True
        }


def start_pipeline_update_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Start a pipeline update (full or incremental refresh)."""
    try:
        update_id = pipelines.start_update(
            pipeline_id=arguments["pipeline_id"],
            refresh_selection=arguments.get("refresh_selection"),
            full_refresh=arguments.get("full_refresh", False),
            full_refresh_selection=arguments.get("full_refresh_selection"),
            validate_only=False
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ Pipeline update started!\n\n"
                           f"Pipeline ID: {arguments['pipeline_id']}\n"
                           f"Update ID: {update_id}\n"
                           f"Full Refresh: {arguments.get('full_refresh', False)}\n\n"
                           f"Use get_pipeline_update_status to poll."
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error starting update: {str(e)}"
            }],
            "isError": True
        }


def validate_pipeline_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Perform dry-run validation without updating datasets."""
    try:
        update_id = pipelines.start_update(
            pipeline_id=arguments["pipeline_id"],
            refresh_selection=arguments.get("refresh_selection"),
            full_refresh=arguments.get("full_refresh", False),
            full_refresh_selection=arguments.get("full_refresh_selection"),
            validate_only=True
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": "✅ Pipeline validation started (dry-run mode)!\n\n"
                           f"Pipeline ID: {arguments['pipeline_id']}\n"
                           f"Update ID: {update_id}\n\n"
                           f"Use get_pipeline_update_status to check results."
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error starting validation: {str(e)}"
            }],
            "isError": True
        }


def get_pipeline_update_status_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get pipeline update status and results."""
    try:
        result = pipelines.get_update(
            arguments["pipeline_id"],
            arguments["update_id"]
        )

        state = result.update.state if result.update else "unknown"

        # Format based on state
        emoji = {
            "QUEUED": "⏳",
            "RUNNING": "🔄",
            "COMPLETED": "✅",
            "FAILED": "❌",
            "CANCELED": "🚫"
        }.get(state, "❓")

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"{emoji} Pipeline Update Status\n\n"
                           f"State: {state}\n"
                           f"Pipeline ID: {arguments['pipeline_id']}\n"
                           f"Update ID: {arguments['update_id']}\n\n"
                           f"Full status:\n{json.dumps(result.as_dict(), indent=2)}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error getting update status: {str(e)}"
            }],
            "isError": True
        }


def stop_pipeline_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Stop a running pipeline."""
    try:
        pipelines.stop_pipeline(arguments["pipeline_id"])

        return {
            "content": [
                {
                    "type": "text",
                    "text": "✅ Pipeline stop request sent!\n\n"
                           f"Pipeline ID: {arguments['pipeline_id']}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error stopping pipeline: {str(e)}"
            }],
            "isError": True
        }


def get_pipeline_events_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get pipeline events, issues, and error messages."""
    try:
        events = pipelines.get_pipeline_events(
            arguments["pipeline_id"],
            arguments.get("max_results", 100)
        )

        event_count = len(events)
        # Count errors - events have event_type property
        error_count = sum(
            1 for e in events
            if e.event_type and e.event_type.endswith("_failed")
        )

        # Convert to dict for JSON serialization
        events_dict = [e.as_dict() for e in events]

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"📋 Pipeline Events\n\n"
                           f"Pipeline ID: {arguments['pipeline_id']}\n"
                           f"Total Events: {event_count}\n"
                           f"Error Events: {error_count}\n\n"
                           f"Events:\n{json.dumps(events_dict, indent=2)}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error getting pipeline events: {str(e)}"
            }],
            "isError": True
        }


# Workspace File Tools

def list_pipeline_files_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """List files in pipeline workspace directory."""
    try:
        files = workspace_files.list_files(arguments["path"])

        file_count = len(files)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"📁 Files in {arguments['path']}\n\n"
                           f"Total: {file_count}\n\n"
                           + "\n".join(
                               f"- {f.path} ({f.object_type})"
                               for f in files
                           )
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error listing files: {str(e)}"
            }],
            "isError": True
        }


def get_pipeline_file_status_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get pipeline file metadata."""
    try:
        status = workspace_files.get_file_status(arguments["path"])

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"📄 File Status\n\n"
                           f"Path: {status.path}\n"
                           f"Type: {status.object_type}\n"
                           f"Language: {status.language or 'N/A'}\n"
                           f"Size: {status.size or 'N/A'} bytes"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error getting file status: {str(e)}"
            }],
            "isError": True
        }


def read_pipeline_file_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Read pipeline file contents."""
    try:
        content = workspace_files.read_file(arguments["path"])

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"📄 File: {arguments['path']}\n\n"
                           f"```\n{content}\n```"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error reading file: {str(e)}"
            }],
            "isError": True
        }


def write_pipeline_file_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Write or update pipeline file."""
    try:
        workspace_files.write_file(
            path=arguments["path"],
            content=arguments["content"],
            language=arguments.get("language", "PYTHON"),
            overwrite=arguments.get("overwrite", True)
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ File written successfully!\n\n"
                           f"Path: {arguments['path']}\n"
                           f"Language: {arguments.get('language', 'PYTHON')}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error writing file: {str(e)}"
            }],
            "isError": True
        }


def create_pipeline_directory_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Create pipeline workspace directory."""
    try:
        workspace_files.create_directory(arguments["path"])

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ Directory created successfully!\n\n"
                           f"Path: {arguments['path']}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error creating directory: {str(e)}"
            }],
            "isError": True
        }


def delete_pipeline_path_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Delete pipeline file or directory."""
    try:
        workspace_files.delete_path(
            arguments["path"],
            arguments.get("recursive", False)
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ Path deleted successfully!\n\n"
                           f"Path: {arguments['path']}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error deleting path: {str(e)}"
            }],
            "isError": True
        }


# Tool handler mapping
TOOL_HANDLERS = {
    "create_pipeline": create_pipeline_tool,
    "get_pipeline": get_pipeline_tool,
    "update_pipeline_config": update_pipeline_config_tool,
    "delete_pipeline": delete_pipeline_tool,
    "start_pipeline_update": start_pipeline_update_tool,
    "validate_pipeline": validate_pipeline_tool,
    "get_pipeline_update_status": get_pipeline_update_status_tool,
    "stop_pipeline": stop_pipeline_tool,
    "get_pipeline_events": get_pipeline_events_tool,
    "list_pipeline_files": list_pipeline_files_tool,
    "get_pipeline_file_status": get_pipeline_file_status_tool,
    "read_pipeline_file": read_pipeline_file_tool,
    "write_pipeline_file": write_pipeline_file_tool,
    "create_pipeline_directory": create_pipeline_directory_tool,
    "delete_pipeline_path": delete_pipeline_path_tool,
}


def get_tool_definitions():
    """Return MCP tool definitions for SDP operations."""
    return [
        {
            "name": "create_pipeline",
            "description": "Create a new Spark Declarative Pipeline",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "storage": {"type": "string"},
                    "target": {"type": "string"},
                    "libraries": {"type": "array"},
                    "clusters": {"type": "array"},
                    "configuration": {"type": "object"},
                    "continuous": {"type": "boolean"},
                    "serverless": {"type": "boolean"}
                },
                "required": ["name", "storage", "target", "libraries"]
            }
        },
        {
            "name": "get_pipeline",
            "description": "Get pipeline details",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string"}
                },
                "required": ["pipeline_id"]
            }
        },
        {
            "name": "update_pipeline_config",
            "description": "Update pipeline configuration",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string"},
                    "name": {"type": "string"},
                    "storage": {"type": "string"},
                    "target": {"type": "string"},
                    "libraries": {"type": "array"},
                    "clusters": {"type": "array"},
                    "configuration": {"type": "object"},
                    "continuous": {"type": "boolean"},
                    "serverless": {"type": "boolean"}
                },
                "required": ["pipeline_id"]
            }
        },
        {
            "name": "delete_pipeline",
            "description": "Delete a pipeline",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string"}
                },
                "required": ["pipeline_id"]
            }
        },
        {
            "name": "start_pipeline_update",
            "description": "Start pipeline update",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string"},
                    "refresh_selection": {"type": "array"},
                    "full_refresh": {"type": "boolean"},
                    "full_refresh_selection": {"type": "array"}
                },
                "required": ["pipeline_id"]
            }
        },
        {
            "name": "validate_pipeline",
            "description": "Validate pipeline (dry-run)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string"},
                    "refresh_selection": {"type": "array"},
                    "full_refresh": {"type": "boolean"},
                    "full_refresh_selection": {"type": "array"}
                },
                "required": ["pipeline_id"]
            }
        },
        {
            "name": "get_pipeline_update_status",
            "description": "Get pipeline update status",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string"},
                    "update_id": {"type": "string"}
                },
                "required": ["pipeline_id", "update_id"]
            }
        },
        {
            "name": "stop_pipeline",
            "description": "Stop a running pipeline",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string"}
                },
                "required": ["pipeline_id"]
            }
        },
        {
            "name": "get_pipeline_events",
            "description": "Get pipeline events",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string"},
                    "max_results": {"type": "integer", "default": 100}
                },
                "required": ["pipeline_id"]
            }
        },
        {
            "name": "list_pipeline_files",
            "description": "List workspace files",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "get_pipeline_file_status",
            "description": "Get file metadata",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "read_pipeline_file",
            "description": "Read file contents",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_pipeline_file",
            "description": "Write file contents",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "language": {"type": "string", "default": "PYTHON"},
                    "overwrite": {"type": "boolean", "default": True}
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "create_pipeline_directory",
            "description": "Create directory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "delete_pipeline_path",
            "description": "Delete file or directory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "recursive": {"type": "boolean", "default": False}
                },
                "required": ["path"]
            }
        }
    ]
