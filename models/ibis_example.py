import ibis  # type: ignore
from ibis.expr.operations import Namespace, UnboundTable  # type: ignore
import ibis.expr.datatypes as dt

from sqlmesh.core.macros import MacroEvaluator
from sqlmesh.core.model import model


@model(
    "staging.ibis_full_model_sql",
    is_sql=True,
    kind="FULL",
    description="This model uses ibis to generate and return a SQL string",
)
def entrypoint(evaluator: MacroEvaluator) -> str:
    """Run the following to debug to create the UnboundTable
    # create table reference
    con = ibis.duckdb.connect(extensions="ducklake")
    con.attach(path="ducklake:data/catalog.ducklake",
               name='my_lakehouse', read_only=True)
    events = con.table('events', database='my_lakehouse.raw')
    dict(events.schema())
    con.disconnect()
    """
    events = UnboundTable(
        name="events",
        schema={'event_id': dt.Int32(nullable=True),
                'user_id': dt.Int32(nullable=True),
                'event_type': dt.String(length=None, nullable=True),
                'event_timestamp': dt.Timestamp(timezone=None, scale=6, nullable=True),
                'revenue': dt.Decimal(precision=10, scale=2, nullable=True)},
        namespace=Namespace(catalog="my_lakehouse", database="raw"),
    ).to_expr()
    # build query
    count = events['event_id'].nunique()
    aggregate = events \
        .group_by("event_type") \
        .aggregate(num_events=count)
    query = aggregate \
        .order_by("event_type") \
        .to_sql()

    return query
