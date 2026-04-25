# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development approach

Apply test-driven development (red → green → refactor) in small, incremental steps:
1. **Red** — confirm the failure first (run the relevant `just` command or test and observe the error)
2. **Green** — make the minimal change to pass
3. **Refactor** — clean up without breaking the passing state

Never skip ahead to implementation without first verifying the failure.

## Common commands

```bash
uv sync                  # install/update dependencies
just run                 # apply full pipeline to local DuckLake gateway
just deploy              # apply pipeline to MotherDuck (requires MOTHERDUCK_TOKEN)
just plan                # preview local changes without applying
just lint                # lint all SQL models
just test                # run SQLMesh unit tests
```

`just run` is the primary local development loop — it runs `sqlmesh --gateway local_gateway plan --auto-apply`, which both applies schema changes and backfills models in one step.

## Architecture

### Dual-gateway SQLMesh pipeline

`config.yaml` defines two gateways:
- **`local_gateway`** — DuckDB + DuckLake on disk (`data/catalog.ducklake`, `data/storage/`)
- **`motherduck`** — MotherDuck cloud DuckDB (`md:my_lakehouse`); requires `MOTHERDUCK_TOKEN` env var

Both gateways expose the same logical catalog name `my_lakehouse`. The default gateway is `motherduck`; all `just` recipes pass `--gateway` explicitly so the default never matters in practice.

SQLMesh state (snapshot tracking) is stored locally in `data/sqlmesh_state.db` for both gateways. The `data/` directory is gitignored and created at runtime.

### Model pipeline (raw → staging → analytics)

| Model | Kind | Source |
|---|---|---|
| `raw.events` | SEED | `seeds/raw_events.csv` |
| `staging.stg_events` | FULL | filters nulls, adds `event_date` |
| `analytics.daily_revenue` | FULL | aggregates revenue by date |
| `staging.ibis_full_model_sql` | FULL (Python) | Ibis-generated SQL, gateway-aware |

All models use DuckDB dialect. FULL-kind models re-materialise completely on each apply — there are no INCREMENTAL models.

### DuckLake schema layout during plan apply

During `sqlmesh plan --auto-apply`, SQLMesh writes physical tables into prefixed schemas (`sqlmesh__raw`, `sqlmesh__staging`, `sqlmesh__analytics`) and only promotes them to the logical names (`raw`, `staging`, `analytics`) after all models have applied. Code that reads the logical schema path during backfill will fail with a catalog error — use fallback logic or the hardcoded schema in those cases (see `models/ibis_example.py`).

### Ibis Python model pattern

`models/ibis_example.py` demonstrates how to write a Python model that returns SQL:
- During `runtime_stage == "loading"`, uses a hardcoded schema (engine adapter is unavailable)
- During execution, tries to read the live schema via `ibis.duckdb.from_connection(evaluator.engine_adapter.connection)`, with a fallback to the hardcoded schema if the logical view isn't promoted yet

### Validation module

`validations/` contains PointBlank data quality checks run after the pipeline. `validations/connection.py` provides `get_connection()` which opens a read-only Ibis DuckDB connection to the local DuckLake catalog. Tables are accessed as `ibis_con.table("events", database="my_lakehouse.raw")`.

### DuckLake extension

The DuckLake extension is loaded automatically by SQLMesh based on the `extensions: [ducklake]` entry in `config.yaml`. In environments where the DuckDB extension server is reachable, no manual setup is needed. The `duckdb-cli` package in `pyproject.toml` provides the `duckdb` binary via `uv run duckdb`.
