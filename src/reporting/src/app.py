from flask import Flask
import os
from common.storage.storage import Storage
from common.queue.queue import Queue
from common.event.request_dto import Request
from common.event.response_dto import Response
from common.config.config import Configuration
import threading
import psycopg2
import logging


LOGGER = logging
app = Flask(__name__)
RESULT_MART = {
    "requests": 0,
    "responses": 0
}


@app.route("/stats", methods=["GET"])
def get_request_stats():
    global RESULT_MART
    return str(RESULT_MART)


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

        sql = f"INSERT INTO {table} ({event_keys}) VALUES ({','.join(event_values)})"
        try:
            conn = psycopg2.connect(
                host=DB_DATABASE_HOST,
                port=DB_DATABASE_PORT,
                database=DB_DATABASE,
                user=DB_USERNAME,
                password=DB_PASSWORD)
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            conn.close()
            RESULT_MART[table] += 1
        except:
            pass


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
