import logging

class QueueBackend(object):
    def __init__(self, config):
        self.connection = config
        self.LOGGER = logging

    def publish(self, channel, event):
        pass

    def subscribe(self, channel):
        pass
