from flask import Flask
import os
from common.storage.storage import Storage
from common.queue.queue import Queue
from common.event.request_dto import Request
from common.event.response_dto import Response
from common.config.config import Configuration
import threading
import psycopg2
import psycopg2.sql
import logging


LOGGER = logging
app = Flask(__name__)
RESULT_MART = {
    "requests": 0,
    "responses": 0
}


@app.route("/stats", methods=["GET"])
def get_request_stats():
    try:
        conn = psycopg2.connect(
            host=DB_DATABASE_HOST,
            port=DB_DATABASE_PORT,
            database=DB_DATABASE,
            user=DB_USERNAME,
            password=DB_PASSWORD,
        )

        with conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {DB_REQ_TABLE}")
                req_count = cur.fetchone()[0]

                cur.execute(f"SELECT COUNT(*) FROM {DB_RESP_TABLE}")
                resp_count = cur.fetchone()[0]

        return {
            "status": "ok",
            "requests": req_count,
            "responses": resp_count,
        }

    except Exception:
        LOGGER.exception("Stats query failed")  #-jc
        return {"status": "error"}, 500


def scan_topic(dto, channel, table):
    global RESULT_MART
    queue = Queue(QUEUE_BACKEND, QUEUE_CONFIG)
    for event in queue.scan_events(channel, dto):
        event_keys = ','.join(event.keys())
        event_values = []
        for key in event.keys():
            if isinstance(event[key], int):
                event_values.append(str(event[key]))
            else:
                event_values.append(f"'{str(event[key])}'")

        try:
            columns = list(event.keys())
            values = [event[c] for c in columns]

            query = psycopg2.sql.SQL(
                "INSERT INTO {table} ({fields}) VALUES ({placeholders})"
            ).format(
                table=psycopg2.sql.Identifier(table),
                fields=psycopg2.sql.SQL(", ").join(
                    map(psycopg2.sql.Identifier, columns)
                ),
                placeholders=psycopg2.sql.SQL(", ").join(
                    psycopg2.sql.Placeholder() for _ in columns
                ),
            )

            conn = psycopg2.connect(
                host=DB_DATABASE_HOST,
                port=DB_DATABASE_PORT,
                database=DB_DATABASE,
                user=DB_USERNAME,
                password=DB_PASSWORD,
            )

            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, values)

            RESULT_MART[table] += 1

        except psycopg2.Error as e:
            LOGGER.exception("Database insert failed")  #-jc

if __name__ == "__main__":
    config = Configuration()
    config.load_config(config_file_path=os.getenv("CONFIG_FILE", default=None))

    # Flask configuration
    APP_HOST = config.reporting_app_host
    APP_PORT = int(config.reporting_app_port)
    LOGLEVEL_DEBUG = config.reporting_app_debug

    # DB configuration
    DB_DATABASE = config.reporting_db_database_name
    DB_DATABASE_HOST = config.reporting_db_host
    DB_DATABASE_PORT = int(config.reporting_db_port)
    DB_RESP_TABLE = config.reporting_db_response_table
    DB_REQ_TABLE = config.reporting_db_request_table
    DB_USERNAME = config.reporting_db_database_user_name
    DB_PASSWORD = config.reporting_db_database_user_password

    # Integration configuration
    STORAGE = Storage(backend=config.storage_backend)

    QUEUE_BACKEND = config.queue_backend
    QUEUE_CONFIG = config.queue_config
    QUEUE_REQ_CHANNEL = config.queue_input_channel
    QUEUE_RESP_CHANNEL = config.queue_response_channel


    request_thread = threading.Thread(
        target=scan_topic, name="request", args=(Request(), QUEUE_REQ_CHANNEL, DB_REQ_TABLE,)
    )
    response_thread = threading.Thread(
        target=scan_topic, name="response", args=(Response(), QUEUE_RESP_CHANNEL, DB_RESP_TABLE,)
    )
    request_thread.start()
    response_thread.start()
    app.run(host=APP_HOST, port=APP_PORT, debug=LOGLEVEL_DEBUG)
