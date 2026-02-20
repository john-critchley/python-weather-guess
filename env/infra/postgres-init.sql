CREATE TABLE IF NOT EXISTS requests (
    _id TEXT PRIMARY KEY,
    _tz_created TIMESTAMPTZ,
    correlation_id TEXT,
    image_path TEXT,
    image_size BIGINT,
    image_format TEXT,
    user_name TEXT
);

CREATE TABLE IF NOT EXISTS responses (
    _id TEXT PRIMARY KEY,
    _tz_created TIMESTAMPTZ,
    correlation_id TEXT,
    image_class TEXT
);

