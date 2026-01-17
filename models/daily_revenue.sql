MODEL (
    name analytics.daily_revenue,
    kind FULL,
    start '2024-01-01',
    cron '@daily',
    allow_partials TRUE,
    interval_unit 'day',
    grain event_date
);

SELECT
    event_date,
    COUNT(DISTINCT user_id) as unique_users,
    COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN revenue END), 0) as total_revenue
FROM
    staging.stg_events
GROUP BY
    event_date;
