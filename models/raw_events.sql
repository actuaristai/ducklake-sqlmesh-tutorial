MODEL (
    name raw.events,
    kind SEED (
        path '../seeds/raw_events.csv'
    ),
    columns (
        event_id INT,
        user_id INT,
        event_type TEXT,
        event_timestamp TIMESTAMP,
        revenue DECIMAL(10,2)
    )
);
