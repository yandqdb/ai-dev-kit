---
name: skill-test
description: Testing framework for evaluating Databricks skills. Use when building test cases for skills, running skill evaluations, comparing skill versions, or creating ground truth datasets with the Generate-Review-Promote (GRP) pipeline. Triggers include "test skill", "evaluate skill", "skill regression", "ground truth", "GRP pipeline", "skill quality", and "skill metrics".
command: skill-test
arguments: "[skill-name] [subcommand]"
---

# Databricks Skills Testing Framework

Offline YAML-first evaluation with human-in-the-loop review and interactive skill improvement.

## Quick References

- [Scorers](references/scorers.md) - Available scorers and quality gates
- [YAML Schemas](references/yaml-schemas.md) - Manifest and ground truth formats
- [Python API](references/python-api.md) - Programmatic usage examples

## /skill-test Command

The `/skill-test` command provides an interactive CLI for testing Databricks skills with real execution on Databricks.

### Basic Usage

```
/skill-test <skill-name> [subcommand]
```

### Subcommands

| Subcommand | Description |
|------------|-------------|
| `run` | Run evaluation against ground truth (default) |
| `regression` | Compare current results against baseline |
| `init` | Initialize test scaffolding for a new skill |
| `add` | Interactive: prompt -> invoke skill -> test -> save |
| `review` | Review pending candidates interactively |
| `review --batch` | Batch approve all pending candidates |
| `baseline` | Save current results as regression baseline |
| `mlflow` | Run full MLflow evaluation with LLM judges |
| `scorers` | List configured scorers for a skill |
| `scorers update` | Add/remove scorers or update default guidelines |
| `sync` | Sync YAML to Unity Catalog (Phase 2) |

### Examples

```
/skill-test spark-declarative-pipelines
/skill-test spark-declarative-pipelines run
/skill-test spark-declarative-pipelines regression
/skill-test spark-declarative-pipelines baseline
/skill-test spark-declarative-pipelines mlflow
/skill-test spark-declarative-pipelines scorers
/skill-test spark-declarative-pipelines scorers update --add-guideline "Must use CLUSTER BY"
/skill-test spark-declarative-pipelines review
/skill-test spark-declarative-pipelines review --batch --filter-success
/skill-test my-new-skill init
```

## Execution Instructions

### Environment Setup

```bash
uv pip install -e .test/
```

Environment variables for Databricks MLflow:
- `DATABRICKS_CONFIG_PROFILE` - Databricks CLI profile (default: "DEFAULT")
- `MLFLOW_TRACKING_URI` - Set to "databricks" for Databricks MLflow
- `MLFLOW_EXPERIMENT_NAME` - Experiment path (e.g., "/Users/{user}/skill-test")

### Running Scripts

All subcommands have corresponding scripts in `.test/scripts/`:

```bash
uv run python .test/scripts/{subcommand}.py {skill_name} [options]
```

| Subcommand | Script | Example |
|------------|--------|---------|
| `run` | `run_eval.py` | `uv run python .test/scripts/run_eval.py my-skill` |
| `regression` | `regression.py` | `uv run python .test/scripts/regression.py my-skill` |
| `init` | `init_skill.py` | `uv run python .test/scripts/init_skill.py my-skill` |
| `add` | `add.py` | `uv run python .test/scripts/add.py my-skill --prompt "..."` |
| `review` | `review.py` | `uv run python .test/scripts/review.py my-skill` |
| `review --batch` | `review.py` | `uv run python .test/scripts/review.py my-skill --batch --filter-success` |
| `baseline` | `baseline.py` | `uv run python .test/scripts/baseline.py my-skill` |
| `mlflow` | `mlflow_eval.py` | `uv run python .test/scripts/mlflow_eval.py my-skill` |
| `scorers` | `scorers.py` | `uv run python .test/scripts/scorers.py my-skill` |
| `scorers update` | `scorers_update.py` | `uv run python .test/scripts/scorers_update.py my-skill --add-guideline "..."` |
| `sync` | `sync.py` | `uv run python .test/scripts/sync.py my-skill` |
| `_routing mlflow` | `routing_eval.py` | `uv run python .test/scripts/routing_eval.py` |

Use `--help` on any script for available options.

## Command Handler

When `/skill-test` is invoked, parse arguments and execute the appropriate command.

### Argument Parsing
- `args[0]` = skill_name (required)
- `args[1]` = subcommand (optional, default: "run")

### Subcommand Routing

| Subcommand | Action |
|------------|--------|
| `run` | Execute `run(skill_name, ctx)` and display results |
| `regression` | Execute `regression(skill_name, ctx)` and display comparison |
| `init` | Execute `init(skill_name, ctx)` to create scaffolding |
| `add` | Prompt for test input, invoke skill, run `interactive()` |
| `review` | Execute `review(skill_name, ctx)` to review pending candidates |
| `baseline` | Execute `baseline(skill_name, ctx)` to save as regression baseline |
| `mlflow` | Execute `mlflow_eval(skill_name, ctx)` with MLflow logging |
| `scorers` | Execute `scorers(skill_name, ctx)` to list configured scorers |
| `scorers update` | Execute `scorers_update(skill_name, ctx, ...)` to modify scorers |

### Context Setup

Create CLIContext with MCP tools before calling any command. See [Python API](references/python-api.md#clicontext-setup) for details.

## Example Workflows

### Running Evaluation (default)
```
User: /skill-test spark-declarative-pipelines run

Claude: [Creates CLIContext with MCP tools]
Claude: [Calls run("spark-declarative-pipelines", ctx)]
Claude: [Displays results table showing passed/failed tests]
```

### Adding a Test Case
```
User: /skill-test spark-declarative-pipelines add

Claude: What prompt would you like to test?
User: Create a bronze ingestion pipeline for CSV files

Claude: [Invokes spark-declarative-pipelines skill with the prompt]
Claude: [Gets response from skill invocation]
Claude: [Calls interactive("spark-declarative-pipelines", prompt, response, ctx)]
Claude: [Reports: "3/3 code blocks passed. Saved to ground_truth.yaml"]
```

### Creating Baseline
```
User: /skill-test spark-declarative-pipelines baseline

Claude: [Creates CLIContext, calls baseline("spark-declarative-pipelines", ctx)]
Claude: [Displays "Baseline saved to baselines/spark-declarative-pipelines/baseline.yaml"]
```

### Checking for Regressions
```
User: /skill-test spark-declarative-pipelines regression

Claude: [Calls regression("spark-declarative-pipelines", ctx)]
Claude: [Compares current pass_rate against baseline]
Claude: [Reports any regressions or improvements]
```

### MLflow Evaluation
```
User: /skill-test spark-declarative-pipelines mlflow

Claude: [Calls mlflow_eval("spark-declarative-pipelines", ctx)]
Claude: [Runs evaluation with LLM judges, logs to MLflow]
Claude: [Displays evaluation metrics and MLflow run link]
```

### Viewing and Updating Scorers
```
User: /skill-test spark-declarative-pipelines scorers

Claude: [Shows enabled scorers, LLM scorers, and default guidelines]
```

```
User: /skill-test spark-declarative-pipelines scorers update --add-guideline "Must include CLUSTER BY"

Claude: [Updates manifest.yaml with new guideline]
```

### Reviewing Candidates
```
User: /skill-test spark-declarative-pipelines review

Claude: [Opens interactive review for pending candidates]
Claude: [For each candidate, shows prompt, response, execution results, and diagnosis]
Claude: [User selects: [a]pprove, [r]eject, [s]kip, or [e]dit]
Claude: [Approved candidates are promoted to ground_truth.yaml]
```

```
User: /skill-test spark-declarative-pipelines review --batch --filter-success

Claude: [Batch approves all candidates with execution_success=True]
Claude: [Reports: "Batch approved 5 candidates, promoted 5 to ground_truth.yaml"]
```

## Review Workflow

When test cases fail during `/skill-test add`, they are saved to `candidates.yaml` for review. The review workflow allows you to examine failures, understand issues, and decide what to do with each candidate.

### Diagnosis Output

When a test fails, the system generates diagnosis information:

```yaml
diagnosis:
  error: "AnalysisException: Table or view not found: bronze_orders"
  code_block: "SELECT * FROM bronze_orders"
  suggested_action: "ensure_table_exists"
  relevant_sections:
    - file: "SKILL.md"
      section: "## Table Creation"
      line: 142
      excerpt: "Create streaming tables before querying..."
```

### Interactive Review Options

When reviewing interactively, you have four options for each candidate:

| Option | Key | Action |
|--------|-----|--------|
| **Approve** | `a` | Mark as approved, will be promoted to ground_truth.yaml |
| **Reject** | `r` | Discard the candidate (with required reason) |
| **Skip** | `s` | Keep as pending for later review |
| **Edit** | `e` | Modify expectations before approving |

### Candidate Lifecycle

```
[add] --> candidates.yaml (status: pending)
                |
         [review]
                |
      +----+----+----+
      |    |    |    |
   approve reject skip edit
      |    |    |    |
      v    v    |    v
 (approved) (removed) (pending) (approved+edited)
      |              |    |
      +--------------+----+
                |
         [promote]
                |
                v
        ground_truth.yaml
```

### Batch Approval

For CI/automation, use batch mode to approve candidates programmatically:

```bash
# Approve all pending candidates
uv run python .test/scripts/review.py my-skill --batch

# Only approve candidates that executed successfully
uv run python .test/scripts/review.py my-skill --batch --filter-success
```

Batch approval is useful for:
- Automated pipelines where human review isn't practical
- Bulk-approving candidates that passed execution validation
- Seeding initial ground truth from successful test runs

## Interactive Workflow

When running `/skill-test <skill-name>`, the framework follows this workflow:

1. **Prompt Phase**: User provides a test prompt interactively
2. **Generate Phase**: Invoke the skill to generate a response
3. **Fixture Phase** (if test requires infrastructure):
   - Create catalog/schema via `mcp__databricks__execute_sql`
   - Create volume and upload test files via `mcp__databricks__upload_file`
   - Create any required source tables
4. **Execute Phase**:
   - Extract code blocks from response
   - Execute Python blocks via serverless compute (default) or specified cluster
   - Execute SQL blocks via `mcp__databricks__execute_sql` (auto-detected warehouse)
5. **Review Phase**:
   - If ALL blocks pass -> Auto-approve, save to `ground_truth.yaml`
   - If ANY block fails -> Save to `candidates.yaml`, enter GRP review
6. **Cleanup Phase** (if configured):
   - Teardown test infrastructure
7. **Report Phase**: Display execution summary

## File Locations

**Important:** All test files are stored at the **repository root** level, not relative to this skill's directory.

| File Type | Path |
|-----------|------|
| Ground truth | `{repo_root}/.test/skills/{skill-name}/ground_truth.yaml` |
| Candidates | `{repo_root}/.test/skills/{skill-name}/candidates.yaml` |
| Manifest | `{repo_root}/.test/skills/{skill-name}/manifest.yaml` |
| Routing tests | `{repo_root}/.test/skills/_routing/ground_truth.yaml` |
| Baselines | `{repo_root}/.test/baselines/{skill-name}/baseline.yaml` |

For example, to test `spark-declarative-pipelines` in this repository:
```
/Users/.../ai-dev-kit/.test/skills/spark-declarative-pipelines/ground_truth.yaml
```

**Not** relative to the skill definition:
```
/Users/.../ai-dev-kit/.claude/skills/skill-test/skills/...  # WRONG
```

## Directory Structure

```
.test/                          # At REPOSITORY ROOT (not skill directory)
├── pyproject.toml              # Package config (pip install -e ".test/")
├── README.md                   # Contributor documentation
├── SKILL.md                    # Source of truth (synced to .claude/skills/)
├── install_skill_test.sh       # Sync script
├── scripts/                    # Wrapper scripts
│   ├── _common.py              # Shared utilities
│   ├── run_eval.py
│   ├── regression.py
│   ├── init_skill.py
│   ├── add.py
│   ├── baseline.py
│   ├── mlflow_eval.py
│   ├── routing_eval.py
│   ├── scorers.py
│   ├── scorers_update.py
│   └── sync.py
├── src/
│   └── skill_test/             # Python package
│       ├── cli/                # CLI commands module
│       ├── fixtures/           # Test fixture setup
│       ├── scorers/            # Evaluation scorers
│       ├── grp/                # Generate-Review-Promote pipeline
│       └── runners/            # Evaluation runners
├── skills/                     # Per-skill test definitions
│   ├── _routing/               # Routing test cases
│   └── {skill-name}/           # Skill-specific tests
│       ├── ground_truth.yaml
│       ├── candidates.yaml
│       └── manifest.yaml
├── tests/                      # Unit tests
├── references/                 # Documentation references
└── baselines/                  # Regression baselines
```

## References

- [Scorers](references/scorers.md) - Available scorers and quality gates
- [YAML Schemas](references/yaml-schemas.md) - Manifest and ground truth formats
- [Python API](references/python-api.md) - Programmatic usage examples
