import ibis
import pointblank as pb

from .connection import get_connection


def validate_raw_events(
    con: ibis.BaseBackend | None = None,
) -> pb.Validate:
    """Validate the raw.events table."""
    _con = con or get_connection()
    table = _con.table("events", database="my_lakehouse.raw")
    return (
        pb.Validate(
            data=table,
            tbl_name="raw.events",
            label="Raw Events",
        )
        .col_vals_not_null(columns="event_id")
        .col_vals_not_null(columns="user_id")
        .col_vals_not_null(columns="event_timestamp")
        .col_vals_not_null(columns="revenue")
        .col_vals_in_set(columns="event_type", set_=["page_view", "purchase"])
        .col_vals_ge(columns="revenue", value=0)
        .rows_distinct(columns_subset=["event_id"])
        .interrogate()
    )


def validate_stg_events(
    con: ibis.BaseBackend | None = None,
) -> pb.Validate:
    """Validate the staging.stg_events table."""
    _con = con or get_connection()
    table = _con.table("stg_events", database="my_lakehouse.staging")
    return (
        pb.Validate(
            data=table,
            tbl_name="staging.stg_events",
            label="Staging Events",
        )
        .col_vals_not_null(columns="event_id")
        .col_vals_not_null(columns="event_date")
        .col_vals_not_null(columns="event_type")
        .col_vals_ge(columns="revenue", value=0)
        .rows_distinct(columns_subset=["event_id"])
        .interrogate()
    )


def validate_daily_revenue(
    con: ibis.BaseBackend | None = None,
) -> pb.Validate:
    """Validate the analytics.daily_revenue table."""
    _con = con or get_connection()
    table = _con.table("daily_revenue", database="my_lakehouse.analytics")
    return (
        pb.Validate(
            data=table,
            tbl_name="analytics.daily_revenue",
            label="Daily Revenue",
        )
        .col_vals_not_null(columns="event_date")
        .col_vals_gt(columns="user_count", value=0)
        .col_vals_ge(columns="total_revenue", value=0)
        .rows_distinct(columns_subset=["event_date"])
        .interrogate()
    )
