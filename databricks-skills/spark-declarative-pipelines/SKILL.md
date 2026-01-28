---
name: spark-declarative-pipelines
description: "Creates, configures, and updates Databricks Lakeflow Spark Declarative Pipelines (SDP/LDP) using serverless compute. ALWAYS asks user for explicit catalog and schema (no defaults). Handles streaming tables, materialized views, CDC, SCD Type 2, and Auto Loader ingestion patterns. Use when building data pipelines, working with Delta Live Tables, ingesting streaming data, implementing change data capture, or when the user mentions SDP, LDP, DLT, Lakeflow pipelines, streaming tables, or bronze/silver/gold medallion architectures."
exemple: use skill:sdp to create sdp reading from /Volumes/users/dong_qiaoyang/man_volume/syn_data/. only create bronze layer. include expectations.the pipeline default to scehma users.dong_qiaoyang. name the pipeline: abc_bronze
---

# Lakeflow Spark Declarative Pipelines (SDP)

## Official Documentation

- **[Lakeflow Spark Declarative Pipelines Overview](https://docs.databricks.com/aws/en/ldp/)** - Main documentation hub
- **[SQL Language Reference](https://docs.databricks.com/aws/en/ldp/developer/sql-dev)** - SQL syntax for streaming tables and materialized views
- **[Python Language Reference](https://docs.databricks.com/aws/en/ldp/developer/python-ref)** - `pyspark.pipelines` API
- **[Loading Data](https://docs.databricks.com/aws/en/ldp/load)** - Auto Loader, Kafka, Kinesis ingestion
- **[Change Data Capture (CDC)](https://docs.databricks.com/aws/en/ldp/cdc)** - AUTO CDC, SCD Type 1/2
- **[Developing Pipelines](https://docs.databricks.com/aws/en/ldp/develop)** - File structure, testing, validation
- **[Liquid Clustering](https://docs.databricks.com/aws/en/delta/clustering)** - Modern data layout optimization
- **[auto loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)** - auto loader

Read the official docs first. Load references/examples.md only if you need:
- Integration patterns not covered in official docs

---

## Development Workflow with MCP Tools

Use MCP tools to create, run, and iterate on **serverless SDP pipelines**. The **primary tool is `create_or_update_pipeline`** which handles the entire lifecycle.

**🚀 ALWAYS USE SERVERLESS COMPUTE (DEFAULT) 🚀**

**Serverless is the default and recommended approach for ALL SDP pipelines.** The MCP tools automatically create serverless pipelines unless explicitly overridden.

**Only use classic clusters if user explicitly requires:**
- R language (not supported in serverless)
- Spark RDD APIs (not supported in serverless)  
- JAR libraries or Maven dependencies (not supported in serverless)

**For 95% of use cases, serverless is the correct choice.**

### Step 1: Get Target Schema and Catalog + Check for Conflicts

**🚨 CRITICAL: ALWAYS ask user for explicit catalog and schema - NO DEFAULTS ALLOWED**

```python
# ❌ NEVER DO THIS - No default locations
catalog = "default_catalog"  # WRONG
schema = "default_schema"    # WRONG

# ✅ CORRECT - Always ask user explicitly
print("Please specify:")
print("1. Target catalog name: ")
print("2. Target schema name: ")
# Wait for user input before proceeding
```

**After getting catalog/schema, check for conflicts:**

```python
# MCP Tool: Check if pipeline name exists
result = find_pipeline_by_name("my_pipeline")
if result["found"]:
    # Use versioned name: my_pipeline_v2, my_pipeline_2024, etc.
    pipeline_name = "my_pipeline_v2"
else:
    pipeline_name = "my_pipeline"

# MCP Tool: Check if tables exist in user-specified location
table_check = get_table_details(
    catalog=user_specified_catalog,  # From user input
    schema=user_specified_schema,    # From user input
    table_names=["bronze_orders", "bronze_customers"]
)
# If tables exist, modify your SQL files to use different names
```

**Then create `.sql` or `.py` files in a local folder:**

```
my_pipeline/
├── bronze/
│   ├── ingest_orders.sql       # SQL (default for most cases)
│   └── ingest_events.py        # Python (for complex logic)
├── silver/
│   └── clean_orders.sql
└── gold/
    └── daily_summary.sql
```
### ⚠️ Critical Folder Structure Rules

**CORRECT Structure:**
```
my_pipeline/
├── bronze/
│   ├── customers.sql
│   └── orders.sql
├── silver/
│   └── clean_orders.sql
└── gold/
    └── daily_summary.sql
```

**INCORRECT - Never do this:**
```
my_pipeline/
├── customers.sql          ❌ Files at root level
├── orders.sql             ❌ Files at root level  
├── bronze/
│   ├── customers.sql      ❌ Duplicates
│   └── orders.sql         ❌ Duplicates
```

**Rule: SQL files must ONLY exist in layer subfolders (`bronze/`, `silver/`, `gold/`), never at the root level.**

Always validate your folder structure before proceeding. If you find duplicate files at both root and subfolder levels, remove the root-level duplicates and keep only the files in the appropriate layer subfolders.

**Language Selection:**
- **Default to SQL** unless user specifies Python or task requires it
- **Use SQL** for: Transformations, aggregations, filtering, joins (90% of use cases)
- **Use Python** for: Complex UDFs, external APIs, ML inference, dynamic paths
- **Generate ONE language** per request unless user explicitly asks for mixed pipeline

### Step 2: Upload to Databricks Workspace

```python
# MCP Tool: upload_folder
upload_folder(
    local_folder="/path/to/my_pipeline",
    workspace_folder="/Workspace/Users/user@example.com/my_pipeline"
)
```

### Step 3: Create/Update and Run Pipeline (SERVERLESS VERIFICATION REQUIRED)

Use **`create_or_update_pipeline`** - the main entry point. It:
1. Searches for an existing pipeline with the same name (or uses `id` from `extra_settings`)
2. Creates a new pipeline or updates the existing one (defaults to serverless)
3. Optionally starts a pipeline run
4. Optionally waits for completion and returns detailed results
5. **CRITICAL**: Always verify serverless compute is active after creation


```python
# MCP Tool: create_or_update_pipeline (using user-specified catalog/schema)
result = create_or_update_pipeline(
    name=pipeline_name,  # From conflict check in Step 1
    root_path="/Workspace/Users/user@example.com/my_pipeline",
    catalog=user_specified_catalog,    # ✅ From user input in Step 1 - NO DEFAULTS
    schema=user_specified_schema,      # ✅ From user input in Step 1 - NO DEFAULTS
    workspace_file_paths=[
        "/Workspace/Users/user@example.com/my_pipeline/bronze/ingest_orders.sql",
        "/Workspace/Users/user@example.com/my_pipeline/silver/clean_orders.sql",
        "/Workspace/Users/user@example.com/my_pipeline/gold/daily_summary.sql"
    ],
    start_run=True,               # Start immediately
    wait_for_completion=True,     # Wait and return final status
    full_refresh=True,            # Full refresh all tables
    timeout=1800                  # 30 minute timeout
    # ✅ CORRECT: Serverless is the DEFAULT - no extra configuration needed
    # ❌ DON'T DO: extra_settings={"serverless": False, "clusters": [...]}
)

# 🚨 CRITICAL: Always verify serverless compute after pipeline creation
pipeline_info = get_pipeline(pipeline_id=result["pipeline_id"])
assert pipeline_info["spec"]["serverless"] == True, "Pipeline must use serverless compute"
print(f"✅ Verified: Pipeline {result['pipeline_name']} is using serverless compute")
```

**Serverless Benefits:**
- **No cluster management** - automatic scaling and resource allocation
- **Cost-effective** - pay only for compute actually used
- **Modern features** - latest Spark and Delta capabilities
- **Unity Catalog integration** - seamless governance and security
- **CDC and SCD Type 2** - advanced features work out of the box

**Result contains actionable information:**
```python
{
    "success": True,                    # Did the operation succeed?
    "pipeline_id": "abc-123",           # Pipeline ID for follow-up operations
    "pipeline_name": "my_orders_pipeline",
    "created": True,                    # True if new, False if updated
    "state": "COMPLETED",               # COMPLETED, FAILED, TIMEOUT, etc.
    "catalog": "my_catalog",            # Target catalog
    "schema": "my_schema",              # Target schema
    "duration_seconds": 45.2,           # Time taken
    "message": "Pipeline created and completed successfully in 45.2s. Tables written to my_catalog.my_schema",
    "error_message": None,              # Error summary if failed
    "errors": []                        # Detailed error list if failed
}
```

### Step 4: Handle Results

**On Success:**
```python
if result["success"]:
    # Verify output tables
    stats = get_table_details(
        catalog="my_catalog",
        schema="my_schema",
        table_names=["bronze_orders", "silver_orders", "gold_daily_summary"]
    )
```

**On Failure:**
```python
if not result["success"]:
    # Message includes suggested next steps
    print(result["message"])
    # "Pipeline created but run failed. State: FAILED. Error: Column 'amount' not found.
    #  Use get_pipeline_events(pipeline_id='abc-123') for full details."

    # Get detailed errors
    events = get_pipeline_events(pipeline_id=result["pipeline_id"], max_results=50)
```

### Step 5: Iterate Until Working

1. Review errors from result or `get_pipeline_events`
2. Fix issues in local files
3. Re-upload with `upload_folder`
4. Run `create_or_update_pipeline` again (it will update, not recreate)
5. **CRITICAL: Verify serverless compute**
   ```python
   pipeline_info = get_pipeline(pipeline_id=result["pipeline_id"])
   assert pipeline_info["spec"]["serverless"] == True, "Pipeline must use serverless compute"
   ```
6. Monitor the state of the pipeline
7. Repeat until `result["success"] == True`

---

## Quick Reference: MCP Tools

### Primary Tool

| Tool | Description |
|------|-------------|
| **`create_or_update_pipeline`** | **Main entry point.** Creates or updates pipeline, optionally runs and waits. Returns detailed status with `success`, `state`, `errors`, and actionable `message`. |

### Pipeline Management

| Tool | Description |
|------|-------------|
| `find_pipeline_by_name` | Find existing pipeline by name, returns pipeline_id |
| `get_pipeline` | Get pipeline configuration and current state |
| `start_update` | Start pipeline run (`validate_only=True` for dry run) |
| `get_update` | Poll update status (QUEUED, RUNNING, COMPLETED, FAILED) |
| `stop_pipeline` | Stop a running pipeline |
| `get_pipeline_events` | Get error messages for debugging failed runs |
| `delete_pipeline` | Delete a pipeline |

### Supporting Tools

| Tool | Description |
|------|-------------|
| `upload_folder` | Upload local folder to workspace (parallel) |
| `get_table_details` | Verify output tables have expected schema and row counts |
| `execute_sql` | Run ad-hoc SQL to inspect data |

---

<!-- ## Reference Documentation (Local)

Load these for detailed patterns:

- **[1-ingestion-patterns.md](1-ingestion-patterns.md)** - Auto Loader, Kafka, Event Hub, Kinesis, file formats
- **[2-streaming-patterns.md](2-streaming-patterns.md)** - Deduplication, windowing, stateful operations, joins
- **[3-scd-patterns.md](3-scd-patterns.md)** - Querying SCD Type 2 history tables, temporal joins
- **[4-performance-tuning.md](4-performance-tuning.md)** - Liquid Clustering, optimization, state management
- **[5-python-api.md](5-python-api.md)** - Modern `dp` API vs legacy `dlt` API comparison
- **[6-dlt-migration.md](6-dlt-migration.md)** - Migrating existing DLT pipelines to SDP
- **[7-advanced-configuration.md](7-advanced-configuration.md)** - `extra_settings` parameter reference and examples
- **[8-expectations-streaming.md](8-expectations-streaming.md)** - SDP expectations, streaming aggregations, data quality patterns
- **[9-sinks-external-destinations.md](9-sinks-external-destinations.md)** - Kafka, Event Hubs, APIs, databases, custom sinks
- **[Official Sinks Documentation](https://docs.databricks.com/aws/en/ldp/sinks)** - External destinations reference -->

---

## Best Practices (2025)

### Language Selection
- **Default to SQL** unless user specifies Python or task clearly requires it
- **Use SQL** for: Transformations, aggregations, filtering, joins (most cases)
- **Use Python** for: Complex UDFs, external APIs, ML inference, dynamic paths (use modern `pyspark.pipelines as dp`)
- **Generate ONE language** per request unless user explicitly asks for mixed pipeline

### Modern Defaults (2025)
- **🚀 SERVERLESS COMPUTE ALWAYS** - Default for all SDP pipelines, no configuration needed
- **Unity Catalog REQUIRED** - Serverless pipelines always use Unity Catalog
- **CLUSTER BY** (Liquid Clustering), not PARTITION BY - see [4-performance-tuning.md](4-performance-tuning.md)
- **Raw `.sql`/`.py` files**, not notebooks
- **read_files()** for cloud storage ingestion - see [1-ingestion-patterns.md](1-ingestion-patterns.md)

**⚠️ DO NOT USE CLASSIC CLUSTERS** unless user explicitly needs R language, RDD APIs, or JAR libraries

---

## SDP Expectations (Data Quality Constraints)

**SDP Expectations** are SQL constraints that validate data quality at ingestion. They replace manual data quality checks with declarative validation rules.

### ⚠️ Critical: Always Check Source Data Before Creating Expectations

**When user asks to add expectations, you MUST first examine the actual source data values to ensure expectations match reality.**

**Step 1: Sample the source data**
```python
# MCP Tool: Check what values actually exist in source data
sample_data = execute_sql("""
  SELECT DISTINCT column_name, COUNT(*) as count
  FROM read_files('/Volumes/catalog/schema/source/', format => 'json')
  GROUP BY column_name
  ORDER BY count DESC
  LIMIT 20
""")
```

**Step 2: Create expectations based on actual data patterns**
```sql
-- ❌ WRONG - Guessing without checking data
CONSTRAINT valid_status EXPECT (status IN ('active', 'inactive')) ON VIOLATION DROP ROW

-- ✅ CORRECT - Based on actual data showing values: 'Active', 'Inactive', 'Pending' 
CONSTRAINT valid_status EXPECT (status IN ('Active', 'Inactive', 'Pending')) ON VIOLATION DROP ROW
```

**Common Data Reality Mismatches:**
- Boolean fields: Source might have `'True'/'False'` not `'true'/'false'`
- Status fields: Source might use `'Active'` not `'active'` 
- Date formats: Source might be `'YYYY-MM-DD'` not `'MM/DD/YYYY'`
- Numeric ranges: Source might have values outside expected business ranges

---

## Common Issues

### Critical: Non-Deterministic Aggregate Functions

**⚠️ AGGREGATE_FUNCTION_WITH_NONDETERMINISTIC_EXPRESSION Error:**

**Problem:** Using `current_timestamp()`, `current_date()`, or `now()` inside aggregate functions like `AVG()`, `COUNT()`, etc.

```sql
-- ❌ WRONG - This will fail
AVG(UNIX_TIMESTAMP(current_timestamp()) - UNIX_TIMESTAMP(_timestamp)) AS processing_delay

-- ✅ CORRECT - Use window timestamps for streaming aggregations  
AVG(UNIX_TIMESTAMP(window(_timestamp, "5 minutes").end) - UNIX_TIMESTAMP(_timestamp)) AS processing_delay
```

**Solutions:**
- **For streaming windows:** Use `window().start` or `window().end` instead of `current_timestamp()`
- **For batch tables:** Move `current_timestamp()` outside aggregates: `current_timestamp() AS calculated_at`
- **For processing timestamps:** Use window end time as a deterministic processing marker

**Real Example Fix:**
```sql
-- Before (fails)
SELECT 
  AVG(UNIX_TIMESTAMP(current_timestamp()) - UNIX_TIMESTAMP(bronze._timestamp)) AS avg_delay,
  current_timestamp() AS _calculated_at
FROM STREAM(bronze_table) bronze
GROUP BY window(bronze._timestamp, "5 minutes")

-- After (works)  
SELECT 
  AVG(UNIX_TIMESTAMP(window(bronze._timestamp, "5 minutes").end) - UNIX_TIMESTAMP(bronze._timestamp)) AS avg_delay,
  window(bronze._timestamp, "5 minutes").end AS _calculated_at
FROM STREAM(bronze_table) bronze  
GROUP BY window(bronze._timestamp, "5 minutes")
```

### Common Pipeline Issues

| Issue | Solution |
|-------|----------|
| **Empty output tables** | Use `get_table_details` to verify, check upstream sources |
| **Pipeline stuck INITIALIZING** | Normal for serverless, wait a few minutes |
| **"Column not found"** | Check `schemaHints` match actual data |
| **Streaming reads fail** | Use `FROM STREAM(table)` for streaming sources |
| **Timeout during run** | Increase `timeout`, or use `wait_for_completion=False` and poll with `get_update` |
| **MV doesn't refresh** | Enable row tracking on source tables |
| **SCD2 schema errors** | Let SDP infer START_AT/END_AT columns |
| **"WARN not supported"** | SDP expectations only support `DROP ROW` and `FAIL UPDATE` |
| **"Table already managed by pipeline"** | Table ownership conflict - rename tables or delete conflicting pipeline |
| **"Expectation violations dropping all rows"** | Check source data values - expectations don't match actual data patterns |
| **"Distinct aggregations not supported"** | Replace `COUNT(DISTINCT x)` with `APPROX_COUNT_DISTINCT(x)` |
| **Streaming aggregation failures** | Use streaming-compatible functions; avoid `current_timestamp()` in aggregates |
| **Table reference errors in foreach** | Use direct streaming transformations instead of external table references |
| **Sink connection failures** | Check external system connectivity, credentials, and configuration |
| **Sink schema mismatches** | Ensure external destination can handle your data schema |

### Pipeline Debugging Workflow

**When a pipeline fails:**

1. **Check update status:** `get_update(pipeline_id, update_id)` shows current state
2. **Get error details:** `get_pipeline_events(pipeline_id, max_results=5)` shows recent errors
3. **Fix issues locally:** Update your SQL/Python files 
4. **Upload fixed files:** Use `upload_file()` or `upload_folder()` to update workspace
5. **Restart pipeline:** `start_update(pipeline_id, full_refresh=True)` retries with fixes

**Auto-retry behavior:** SDP pipelines automatically retry on failure (shown as `RETRY_ON_FAILURE` cause), so fixes you make during a failed run will be picked up by the retry.

**For detailed errors**, the `result["message"]` from `create_or_update_pipeline` includes suggested next steps. Use `get_pipeline_events(pipeline_id=...)` for full stack traces.

### ⚠️ Prevention: Table Ownership Conflicts

**This issue is prevented by Step 1 conflict checking.** If you followed Step 1 properly, you won't encounter table ownership conflicts.

**If you still get this error, it means Step 1 was skipped:**
```
Table is already managed by pipeline 376b4f4d-7f89-4153-bf21-3e30b4bba2f4.
```

**Go back to Step 1 and check for conflicts before proceeding.** Always use unique table names identified during the conflict check phase.

### ⚠️ Critical: Boolean Constraint Timing Issue

**Problem:** When creating constraints on boolean fields, the constraint evaluation happens BEFORE the SELECT statement type casting.

**Example of INCORRECT approach:**
```sql
CREATE OR REFRESH STREAMING TABLE bronze_products (
  CONSTRAINT valid_active_flag EXPECT (active_flag IN ('true', 'false')) ON VIOLATION DROP ROW  -- ❌ WRONG
)
AS
SELECT
  active_flag,
  CAST(active_flag AS BOOLEAN) AS is_active  -- This cast happens AFTER constraint evaluation
FROM ...
```

**Root Cause:** The constraint checks string values like `active_flag IN ('true', 'false')`, but source data might contain `'True'`, `'TRUE'`, `'1'`, `'0'`, `'yes'`, `'no'`, etc.

**Solution:** Remove boolean constraints and let the CAST operation handle validation:
```sql
CREATE OR REFRESH STREAMING TABLE bronze_products (
  -- Remove the boolean constraint, let CAST handle it
)
AS
SELECT
  active_flag,
  CAST(active_flag AS BOOLEAN) AS is_active,  -- CAST will handle conversion and errors
  CASE 
    WHEN TRY_CAST(active_flag AS BOOLEAN) IS NULL THEN 'INVALID_BOOLEAN'
    ELSE 'VALID'
  END AS _boolean_validation_flag
FROM ...
```

---

---

## Advanced Pipeline Configuration

For advanced configuration options (development mode, continuous pipelines, custom clusters, notifications, Python dependencies, etc.), see **[7-advanced-configuration.md](7-advanced-configuration.md)**.

---

## Platform Constraints

### Serverless Pipeline Requirements (Default)
| Requirement | Details |
|-------------|---------|
| **Unity Catalog** | Required - serverless pipelines always use UC |
| **Workspace Region** | Must be in serverless-enabled region |
| **Serverless Terms** | Must accept serverless terms of use |
| **CDC Features** | Requires serverless (or Pro/Advanced with classic clusters) |

### Serverless Limitations (When Classic Clusters Required)
| Limitation | Workaround |
|------------|-----------|
| **R language** | Not supported - use classic clusters if required |
| **Spark RDD APIs** | Not supported - use classic clusters if required |
| **JAR libraries** | Not supported - use classic clusters if required |
| **Maven coordinates** | Not supported - use classic clusters if required |
| **DBFS root access** | Limited - must use Unity Catalog external locations |
| **Global temp views** | Not supported |

### General Constraints
| Constraint | Details |
|------------|---------|
| **Schema Evolution** | Streaming tables require full refresh for incompatible changes |
| **SQL Limitations** | PIVOT clause unsupported |
| **Sinks** | Multiple external targets supported - see [Sinks Documentation](https://docs.databricks.com/aws/en/ldp/sinks) |

**🚀 ALWAYS DEFAULT TO SERVERLESS COMPUTE** - MCP tools create serverless pipelines by default. Never use classic clusters unless user explicitly requires R language, Spark RDD APIs, or JAR libraries (extremely rare cases).