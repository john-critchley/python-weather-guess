from common.event.event import Event


class Response(Event):
    def __init__(self):
        super().__init__()
        self.image_class = None
        self.correlation_id = None
        self._expected_fields.append("image_class")
        self._expected_fields.append("correlation_id")
