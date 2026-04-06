import ibis  # type: ignore
from pathlib import Path

from sqlmesh.core.macros import MacroEvaluator
from sqlmesh.core.model import model

# Map each gateway to its catalog alias.
# Both gateways expose the lakehouse as "my_lakehouse", but keeping this
# explicit makes it easy to add new gateways or rename catalogs later.
GATEWAY_CATALOG = {
    "local_gateway": "my_lakehouse",
    "motherduck": "my_lakehouse",
}


def _build_events(evaluator: MacroEvaluator, catalog: str) -> ibis.Table:
    """Return an ibis unbound table for raw.events with schema auto-detected from the live connection."""
    if evaluator.runtime_stage != "loading":
        # At runtime the engine_adapter is available and already has catalogs attached.
        con = ibis.duckdb.from_connection(evaluator.engine_adapter.connection)
        schema = con.table("events", database=f"{catalog}.raw").schema()
    else:
        # During loading the engine_adapter is not yet available — open a
        # read-only local connection just to detect the schema.
        # Walk up from this file to find data/catalog.ducklake (handles worktrees).
        current = Path(__file__).resolve().parent
        while current != current.parent:
            candidate = current / "data" / "catalog.ducklake"
            if candidate.exists():
                break
            current = current.parent
        else:
            raise FileNotFoundError("Could not locate data/catalog.ducklake")
        con = ibis.duckdb.connect(extensions=["ducklake"])
        con.attach(f"ducklake:{candidate}", name="my_lakehouse", read_only=True)
        schema = con.table("events", database="my_lakehouse.raw").schema()
        con.disconnect()
    return ibis.table(schema=schema, name="events", catalog=catalog, database="raw")


@model(
    "staging.ibis_full_model_sql",
    is_sql=True,
    kind="FULL",
    description="This model uses ibis to generate and return a SQL string",
)
def entrypoint(evaluator: MacroEvaluator) -> str:
    # Resolve catalog from the active gateway; fall back to local_gateway.
    gateway = evaluator.gateway or "local_gateway"
    catalog = GATEWAY_CATALOG.get(gateway, "my_lakehouse")

    events = _build_events(evaluator, catalog)

    # Build the query with ibis — .to_sql() keeps column-level lineage intact.
    query = events \
        .group_by("event_type") \
        .aggregate(num_events=events["event_id"].nunique()) \
        .order_by("event_type") \
        .to_sql()

    return query
