import logging
import uuid


class StorageBackend(object):
    def __init__(self, local_prefix="", remote_prefix="", shard_prefix=""):
        self.local_prefix = local_prefix
        self.remote_prefix = remote_prefix
        self.shard_prefix = shard_prefix
        self.LOGGGER = logging

    def put_object(self, src, dst=""):
        if dst == "":
            dst = self._generate_tempname()
        return src, dst

    def get_object(self, src, dst=""):
        if dst == "":
            dst = self._generate_tempname()
        return src, dst


    @staticmethod
    def _generate_tempname(extension="jpeg"):
        return f"{uuid.uuid4()}.{extension}"
