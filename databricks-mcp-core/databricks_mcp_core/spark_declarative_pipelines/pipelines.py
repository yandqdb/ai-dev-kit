"""
Spark Declarative Pipelines - Pipeline Management

Functions for managing SDP pipeline lifecycle using Databricks Pipelines API.
"""
from typing import List, Optional, Dict
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.pipelines import (
    CreatePipelineResponse,
    GetPipelineResponse,
    PipelineLibrary,
    PipelineCluster,
    PipelineEvent,
    GetUpdateResponse,
    StartUpdateResponse
)


def create_pipeline(
    name: str,
    storage: str,
    target: str,
    libraries: List[PipelineLibrary],
    clusters: Optional[List[PipelineCluster]] = None,
    configuration: Optional[Dict[str, str]] = None,
    continuous: bool = False,
    serverless: Optional[bool] = None
) -> CreatePipelineResponse:
    """
    Create a new Spark Declarative Pipeline.

    Args:
        name: Pipeline name
        storage: Storage location for pipeline data
        target: Target catalog.schema for output tables
        libraries: List of PipelineLibrary objects
                   Example: [PipelineLibrary(notebook=NotebookLibrary(
                                path="/path/to/file.py"))]
        clusters: Optional cluster configuration
        configuration: Optional Spark configuration key-value pairs
        continuous: If True, pipeline runs continuously
        serverless: If True, uses serverless compute

    Returns:
        CreatePipelineResponse with pipeline_id

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()

    return w.pipelines.create(
        name=name,
        storage=storage,
        target=target,
        libraries=libraries,
        clusters=clusters,
        configuration=configuration,
        continuous=continuous,
        serverless=serverless
    )


def get_pipeline(pipeline_id: str) -> GetPipelineResponse:
    """
    Get pipeline details and configuration.

    Args:
        pipeline_id: Pipeline ID

    Returns:
        GetPipelineResponse with full pipeline configuration and state

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()
    return w.pipelines.get(pipeline_id=pipeline_id)


def update_pipeline(
    pipeline_id: str,
    name: Optional[str] = None,
    storage: Optional[str] = None,
    target: Optional[str] = None,
    libraries: Optional[List[PipelineLibrary]] = None,
    clusters: Optional[List[PipelineCluster]] = None,
    configuration: Optional[Dict[str, str]] = None,
    continuous: Optional[bool] = None,
    serverless: Optional[bool] = None
) -> None:
    """
    Update pipeline configuration (not code files).

    Args:
        pipeline_id: Pipeline ID
        name: New pipeline name
        storage: New storage location
        target: New target catalog.schema
        libraries: New library paths
        clusters: New cluster configuration
        configuration: New Spark configuration
        continuous: New continuous mode setting
        serverless: New serverless setting

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()

    w.pipelines.update(
        pipeline_id=pipeline_id,
        name=name,
        storage=storage,
        target=target,
        libraries=libraries,
        clusters=clusters,
        configuration=configuration,
        continuous=continuous,
        serverless=serverless
    )


def delete_pipeline(pipeline_id: str) -> None:
    """
    Delete a pipeline.

    Args:
        pipeline_id: Pipeline ID

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()
    w.pipelines.delete(pipeline_id=pipeline_id)


def start_update(
    pipeline_id: str,
    refresh_selection: Optional[List[str]] = None,
    full_refresh: bool = False,
    full_refresh_selection: Optional[List[str]] = None,
    validate_only: bool = False
) -> str:
    """
    Start a pipeline update or dry-run validation.

    Args:
        pipeline_id: Pipeline ID
        refresh_selection: List of table names to refresh
        full_refresh: If True, performs full refresh
        full_refresh_selection: List of table names for full refresh
        validate_only: If True, performs dry-run validation
                      without updating datasets

    Returns:
        Update ID for polling status

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()

    response = w.pipelines.start_update(
        pipeline_id=pipeline_id,
        refresh_selection=refresh_selection,
        full_refresh=full_refresh,
        full_refresh_selection=full_refresh_selection,
        validate_only=validate_only
    )

    return response.update_id


def get_update(pipeline_id: str, update_id: str) -> GetUpdateResponse:
    """
    Get pipeline update status and results.

    Args:
        pipeline_id: Pipeline ID
        update_id: Update ID from start_update

    Returns:
        GetUpdateResponse with update status
        (state: QUEUED, RUNNING, COMPLETED, FAILED, etc.)

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()
    return w.pipelines.get_update(
        pipeline_id=pipeline_id,
        update_id=update_id
    )


def stop_pipeline(pipeline_id: str) -> None:
    """
    Stop a running pipeline.

    Args:
        pipeline_id: Pipeline ID

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()
    # SDK's stop() returns Wait object, but we don't need to wait
    w.pipelines.stop(pipeline_id=pipeline_id)


def get_pipeline_events(
    pipeline_id: str,
    max_results: int = 100
) -> List[PipelineEvent]:
    """
    Get pipeline events, issues, and error messages.

    Args:
        pipeline_id: Pipeline ID
        max_results: Maximum number of events to return

    Returns:
        List of PipelineEvent objects with error details

    Raises:
        DatabricksError: If API request fails
    """
    w = WorkspaceClient()
    # SDK returns iterator, convert to list with max_results limit
    events = w.pipelines.list_pipeline_events(
        pipeline_id=pipeline_id,
        max_results=max_results
    )
    return list(events)
