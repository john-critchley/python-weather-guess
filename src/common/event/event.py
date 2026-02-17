import json
from datetime import datetime
import uuid


class Event(object):
    def __init__(self):
        self._tz_created = str(datetime.now())
        self._id = str(uuid.uuid4())
        self.correlation_id = None
        self._expected_fields = []
        self.more = None

    def load(self, event_json):
        event = event_json if isinstance(event_json, dict) else json.loads(event_json)
        for field in self.keys():
            if field in event:
                self.__dict__[field] = event[field]
            elif field not in self._expected_fields:
                pass
            else:
                raise Exception(f"Invalid event definition: {event}")

    def set_field(self, field, value):
        if field in self._as_dict().keys():
            self.__dict__[field] = value

    def dump(self, dump_format="json"):
        for key in self._expected_fields:
            if self._as_dict()[key] is None:
                raise Exception("Mismatched event dto")
        return json.dumps(self._as_dict()) if dump_format == "json" else dict(self.__dict__)

    def _as_dict(self):
        unfiltered = dict(self.__dict__)
        unfiltered.pop("_expected_fields")
        unfiltered.pop("more")
        return unfiltered

    def __getitem__(self, name):
        return self._as_dict()[name]

    def __iter__(self):
        return iter(self._as_dict())

    def keys(self):
        return self._as_dict().keys()

    def items(self):
        return self._as_dict().items()

    def values(self):
        return self._as_dict().values()


