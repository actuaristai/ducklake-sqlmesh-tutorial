import ibis  # type: ignore
from ibis.expr.operations import Namespace, UnboundTable  # type: ignore
import ibis.expr.datatypes as dt

from sqlmesh.core.macros import MacroEvaluator
from sqlmesh.core.model import model

# Map each gateway to its catalog alias.
# Both gateways expose the lakehouse as "my_lakehouse", but keeping this
# explicit makes it easy to add new gateways or rename catalogs later.
GATEWAY_CATALOG = {
    "local_gateway": "my_lakehouse",
    "motherduck": "my_lakehouse",
}


def _build_events(catalog: str) -> ibis.Table:
    """Return an ibis UnboundTable for raw.events under the given catalog.

    To refresh the schema against a live connection run:
        con = ibis.duckdb.connect(extensions="ducklake")
        con.attach("ducklake:data/catalog.ducklake", name="my_lakehouse", read_only=True)
        dict(con.table("events", database="my_lakehouse.raw").schema())
        con.disconnect()
    """
    return UnboundTable(
        name="events",
        schema={
            "event_id": dt.Int32(nullable=True),
            "user_id": dt.Int32(nullable=True),
            "event_type": dt.String(length=None, nullable=True),
            "event_timestamp": dt.Timestamp(timezone=None, scale=6, nullable=True),
            "revenue": dt.Decimal(precision=10, scale=2, nullable=True),
        },
        namespace=Namespace(catalog=catalog, database="raw"),
    ).to_expr()


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

    events = _build_events(catalog)

    # Build the query with ibis — .to_sql() keeps column-level lineage intact.
    query = events \
        .group_by("event_type") \
        .aggregate(num_events=events["event_id"].nunique()) \
        .order_by("event_type") \
        .to_sql()

    return query
