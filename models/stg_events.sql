MODEL (
    name staging.stg_events,
    kind VIEW
);

SELECT
    event_id,
    user_id,
    event_type,
    event_timestamp,
    -- Extract date for incremental processing
    DATE(event_timestamp) as event_date,
    revenue
FROM
    raw.events
WHERE
    event_id IS NOT NULL;
