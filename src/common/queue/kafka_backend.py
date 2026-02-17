from common.queue.backend import QueueBackend
from confluent_kafka import Producer, Consumer
import uuid
import time

class KafkaBackend(QueueBackend):
    def __init__(self, config):
        super().__init__(config)
        self.group_id = config["group_id"] if "group_id" in config else f"abyrvalg-{str(uuid.uuid4())}"
        self.brokers = config["connection"] if "connection" in config else "kafka:29092"
        self.LOGGER.info("KafkaBackend init: brokers=%r group_id=%r", self.brokers, self.group_id)

    def publish(self, channel, event):
        super().publish(channel, event)
        conf = {'bootstrap.servers': self.brokers}
        self.LOGGER.info(f"Sending {event} to kafka topic {channel} of cluster {conf}")
        # #-jc TEMP DEBUG: inspect payload type before Kafka
        self.LOGGER.info("Kafka publish: topic=%r type=%s bytes=%s",
                 channel, type(event), (len(event) if hasattr(event, "__len__") else None))

        #-jc TEMP DEBUG END
        producer = Producer(conf)
        producer.produce(channel, value=event)
        producer.flush()

    def subscribe(self, channel):
        super().subscribe(channel)
        conf = {'bootstrap.servers': self.brokers,
                'group.id': self.group_id,
                'auto.offset.reset': 'earliest'}
        self.LOGGER.info(f"Starting kafka consumer on {channel} with config {conf}")
        consumer = Consumer(conf)
        consumer.subscribe([channel])
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            yield str(msg.value().decode("utf-8"))
