--liquibase formatted sql

--changeset liquibase:1
--Database: postgresql
CREATE TABLE requests (
    _tz_created TIMESTAMP,
    _id VARCHAR,
    correlation_id VARCHAR,
    image_path VARCHAR,
    image_size INT,
    image_format VARCHAR,
    user_name VARCHAR,
    PRIMARY KEY (_id)
);

--changeset liquibase:2
--Database: postgresql
CREATE TABLE responses (
    _tz_created TIMESTAMP,
    _id VARCHAR,
    correlation_id VARCHAR,
    image_class VARCHAR,
    PRIMARY KEY (_id)
);
