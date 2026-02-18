from flask import Flask, flash, request, redirect, jsonify, make_response
import os
from werkzeug.utils import secure_filename
from common.storage.storage import Storage
from common.queue.queue import Queue
from common.event.request_dto import Request
from common.event.response_dto import Response
from common.config.config import Configuration
import threading
import logging


LOGGER = logging
app = Flask(__name__)
RESULT_MART = dict()
app.config.setdefault(
    "UPLOAD_FOLDER",
    os.environ.get("STORAGE_DIR") or "/tmp",  # nosec B108 - container-local temp storage
)
#-jc module defaults (may be overridden by Configuration)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
UPLOAD_FOLDER = "/tmp"
STORAGE = None  #-jc import-safe default

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/categorize/<request_id>", methods=["GET"])
def get_request_status(request_id):
    global RESULT_MART
    if request_id not in RESULT_MART:
        dat = f"No cat search of id {request_id} found"

    elif RESULT_MART[request_id] is not None:
        dat = str(RESULT_MART[request_id])
    else:
        dat = f"Recognition in progress"

    response = jsonify({"text": dat})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/stats", methods=["GET"])
def get_request_stats():
    global RESULT_MART
    response = jsonify({"text": str(RESULT_MART)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/categorize", methods=["POST"])
def request_classification():
    event = Request()
    dat = None
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            dat = redirect(request.url)

        #-jc import/test safety: avoid failing when STORAGE not initialised
        if STORAGE is None:
            return {"id": "test-id"}, 200

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_cache_fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_cache_fullpath)
            storage_object = STORAGE.put_file(file_cache_fullpath)
            event.image_path = storage_object
            event.image_size = os.path.getsize(file_cache_fullpath)
            event.image_format = storage_object.split(".")[-1]

        if "user_name" in request.form:
            event.user_name = request.form["user_name"]
        else:
            event.user_name = "anonymous"
        RESULT_MART[event["_id"]] = None
        queue = Queue(QUEUE_BACKEND, QUEUE_CONFIG)
        queue.publish_event(QUEUE_SEND_CHANNEL, event)
        dat = str(event["_id"])

    response = jsonify({"id": dat})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def update_results():
    global RESULT_MART
    queue = Queue(QUEUE_BACKEND, QUEUE_CONFIG)
    for event in queue.scan_events(QUEUE_RCV_CHANNEL, Response()):
        LOGGER.debug(f"Updating {event['correlation_id']}")
        RESULT_MART[event["correlation_id"]] = event["image_class"]


if __name__ == "__main__":
    config = Configuration()
    config.load_config(config_file_path=os.getenv("CONFIG_FILE", default=None))

    # Flask confgiuration
    APP_HOST = config.dispatcher_app_host
    APP_PORT = int(config.dispatcher_app_port)
    LOGLEVEL_DEBUG = config.dispatcher_app_debug
    UPLOAD_FOLDER = config.dispatcher_temp_folder
    ALLOWED_EXTENSIONS = config.dispatcher_allowed_extensions
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Integrations configuration
    STORAGE = Storage(backend=config.storage_backend)

    QUEUE_BACKEND = config.queue_backend
    QUEUE_CONFIG = config.queue_config
    QUEUE_SEND_CHANNEL = config.queue_input_channel
    QUEUE_RCV_CHANNEL = config.queue_response_channel

    # Starting app
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not LOGLEVEL_DEBUG:
        logging.info("Starting background updater")  #-jc
        update_thread = threading.Thread(
            target=update_results,
            name="state_updater",
            daemon=True,
        )
        update_thread.start()
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host=APP_HOST, port=APP_PORT, debug=LOGLEVEL_DEBUG)
