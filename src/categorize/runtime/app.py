import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import threading
import random
import logging
import numpy as np

from flask import Flask
from keras.models import load_model
from keras.utils import load_img as img_from_file
from keras.utils import img_to_array
from keras.utils import disable_interactive_logging
from keras.applications.vgg19 import preprocess_input
from keras.applications.vgg19 import decode_predictions

from common.storage.storage import Storage
from common.queue.queue import Queue
from common.event.request_dto import Request
from common.event.response_dto import Response
from common.config.config import Configuration

import traceback

LOGGER = logging
app = Flask(__name__)
RESULT_MART = dict()
MODEL_EXEC = None


@app.route("/stats", methods=["GET"])
def get_request_stats():
    global RESULT_MART
    return str(RESULT_MART)


def load_image(file_name):
    img = img_from_file(file_name, target_size=(224, 224))
    img = img_to_array(img)
    img = img.reshape((1, img.shape[0], img.shape[1], img.shape[2]))
    img = preprocess_input(img)
    return img


def infer():
    global RESULT_MART
    global MODEL_EXEC

    LOGGER.info(
        "infer(): starting; backend=%s brokers=%s rcv=%s send=%s",
        QUEUE_BACKEND, QUEUE_CONFIG, QUEUE_RCV_CHANNEL, QUEUE_SEND_CHANNEL
    )

    try:
        queue = Queue(QUEUE_BACKEND, QUEUE_CONFIG)
        LOGGER.info("infer(): Queue created OK")

        for event in queue.scan_events(QUEUE_RCV_CHANNEL, Request()):
            LOGGER.info(
                "infer(): received event type=%s id=%s",
                type(event),
                event.get("_id") if isinstance(event, dict) else getattr(event, "_id", "unknown"),
            )

            resp = Response()
            resp.correlation_id = event["_id"]
            image_classes = ["foggy", "rainy", "shine"]

            try:
                image_path = STORAGE.get_file(event.image_path)
                image = load_image(image_path)
                pred = MODEL_EXEC.predict(image)  #-jc

                idx = int(np.argmax(pred[0]))  #-jc
                resp.image_class = image_classes[idx]  #-jc
            except Exception:
                LOGGER.exception("infer(): model failed, using random class")
                resp.image_class = random.choice(image_classes)

            if resp.image_class in RESULT_MART:
                RESULT_MART[resp.image_class] += 1
            else:
                RESULT_MART[resp.image_class] = 1

            LOGGER.info("infer(): publishing response id=%s", resp.correlation_id)
            queue.publish_event(QUEUE_SEND_CHANNEL, resp)

    except Exception:
        LOGGER.error(
            "infer(): FATAL exception in inference loop:\n%s",
            traceback.format_exc()
        )
        raise


if __name__ == "__main__":
    config = Configuration()
    config.load_config(config_file_path=os.getenv("CONFIG_FILE", default=None))

    # Flask configuration
    APP_HOST = config.categorize_app_host
    APP_PORT = int(config.categorize_app_port)
    LOGLEVEL_DEBUG = config.categorize_app_debug

    # App configuration
    MODEL_PATH = config.categorize_model_path

    # Integrations configuration
    STORAGE = Storage(backend=config.storage_backend)

    QUEUE_BACKEND = config.queue_backend
    QUEUE_CONFIG = config.queue_config
    QUEUE_SEND_CHANNEL = config.queue_response_channel
    QUEUE_RCV_CHANNEL = config.queue_input_channel

    MODEL_EXEC = load_model(MODEL_PATH, compile=False)
    update_thread = threading.Thread(target=infer, name="inference")
    update_thread.start()
    app.run(host=APP_HOST, port=APP_PORT, debug=LOGLEVEL_DEBUG, use_reloader=False)
