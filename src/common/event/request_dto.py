from common.event.event import Event


class Request(Event):
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.image_size = None
        self.image_format = None
        self.user_name = None
        self._expected_fields.append("image_path")
        self._expected_fields.append("image_size")
        self._expected_fields.append("image_format")
        self._expected_fields.append("user_name")
