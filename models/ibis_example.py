import ibis  # type: ignore

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
    con = ibis.duckdb.from_connection(evaluator.engine_adapter.connection)
    schema = con.table("events", database=f"{catalog}.raw").schema()
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
