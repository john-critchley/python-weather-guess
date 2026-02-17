from common.event.event import Event
import logging


class Filter(object):
    def __init__(self, filters, negate=False):
        if not isinstance(filters, list):
            raise Exception
        self.filters = dict()

        for filter in filters:
            if not isinstance(filter, dict):
                raise Exception
            self.filters[filter["key"]] = None
            if "value" in filter:
                self.filters[filter["key"]] = filter["value"]
        self.negate = negate

    def validate(self, event):
        if not isinstance(event, dict):
            raise Exception
        filter_result = None
        for field in event:
            if field in self.filters:
                if self.negate:
                    filter_result = False
                    break

            if event[field] == self.filters[field]:
                filter_result = not self.negate
            else:
                filter_result = self.negate

            if filter_result is not None:
                break

        return True if filter_result is True else False


class Queue(object):
    def __init__(self, backend, config):
        if backend == "kafka":
            from common.queue.kafka_backend import KafkaBackend
            self.queue_backend = KafkaBackend(config)
        else:
            raise Exception("Queue backend not implemented")
        self.LOGGER = logging

    def publish_event(self, channel, event):
        self.queue_backend.publish(channel, event.dump())

    def wait_for_event(self, channel, dto, filter):
        for event in self.queue_backend.subscribe(channel):
            try:
                dto.load(event)
            except:
                continue
            if filter.validate(event):
                return dto

    def scan_events(self, channel, dto, filter=None):
        self.LOGGER.info(f"Starting listneing queue on channel {channel} with fileter {filter}")
        for event in self.queue_backend.subscribe(channel):
            try:
                dto.load(event)
            except:
                continue

            if filter is None:
                yield dto
            elif filter.validate(event):
                yield dto
            else:
                continue
