"""
Databricks MCP Server

A FastMCP server that exposes Databricks operations as MCP tools.
Simply wraps functions from databricks-tools-core.
"""

from fastmcp import FastMCP

# Create the server
mcp = FastMCP("Databricks MCP Server")

# Import and register all tools (side-effect imports: each module registers @mcp.tool decorators)
from .tools import (  # noqa: F401, E402
    sql,
    compute,
    file,
    pipelines,
    jobs,
    agent_bricks,
    aibi_dashboards,
    serving,
    unity_catalog,
    volume_files,
    genie,
    manifest,
    vector_search,
    lakebase,
)
