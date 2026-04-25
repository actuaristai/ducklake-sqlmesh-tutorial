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

def _build_table(
    evaluator: MacroEvaluator,
    catalog: str,
    table: str,
    database: str,
) -> ibis.Table:
    """Return an ibis unbound table for building queries against the events table.

    During the loading stage the engine adapter is unavailable (SQLMesh restriction),
    so a hardcoded schema is used. During execution the live schema is read from the
    already-attached catalog via SQLMesh's own connection, avoiding a second file lock.
    """
    # Hardcoded schema kept in sync with raw_events.sql — used during loading
    # and as a fallback during plan apply before logical views are promoted.
    fallback_schema = ibis.Schema(
        {
            "event_id": "int32",
            "user_id": "int32",
            "event_type": "string",
            "event_timestamp": "timestamp",
            "revenue": "decimal(10,2)",
        }
    )
    if evaluator.runtime_stage == "loading":
        schema = fallback_schema
    else:
        # Reuse SQLMesh's connection — my_lakehouse is already attached, so no
        # second DuckLake file lock is created. Falls back to hardcoded schema
        # during plan apply before the logical view is promoted.
        try:
            con = ibis.duckdb.from_connection(evaluator.engine_adapter.connection)
            schema = con.table(table, database=f"{catalog}.{database}").schema()
        except Exception:
            schema = fallback_schema
    return ibis.table(schema=schema, name=table, catalog=catalog, database=database)


@model(
    "staging.ibis_full_model_sql",
    is_sql=True,
    kind="FULL",
    description="This model uses ibis to generate and return a SQL string",
)
def entrypoint(evaluator: MacroEvaluator) -> str:
    """To run this interactively to debug:
    con = ibis.duckdb.connect(extensions=["ducklake"])
    con.attach(path="ducklake:data/catalog.ducklake",
               name='my_lakehouse', read_only=True)
    events = con.table('events', database='my_lakehouse.raw')
    con.disconnect()
    """
    # Resolve catalog from the active gateway; fall back to local_gateway.
    gateway = evaluator.gateway or "local_gateway"
    catalog = GATEWAY_CATALOG.get(gateway, "my_lakehouse")

    events = _build_table(evaluator, catalog, table="events", database="raw")

    # Build the query with ibis — .to_sql() keeps column-level lineage intact.
    query = events \
        .group_by("event_type") \
        .aggregate(num_events=events["event_id"].nunique()) \
        .order_by("event_type") \
        .to_sql()

    return query
