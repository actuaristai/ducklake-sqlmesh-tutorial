import ibis  # type: ignore
from ibis.expr.operations import Namespace, UnboundTable  # type: ignore

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
    create table reference
    con = ibis.duckdb.connect(extensions="ducklake")
    con.attach(path="ducklake:data/catalog.ducklake",
               name='my_lakehouse', read_only=True)
    events = con.table('events', database='my_lakehouse.raw')
    con.disconnect()
    """
    events = UnboundTable(
        name="events",
        schema={"event_id": "int",
                "user_id": "int",
                "event_type": "string",
                'event_timestamp': 'string',
                'revenue': 'string'},
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
