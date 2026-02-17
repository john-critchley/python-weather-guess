import os
import logging


class Storage(object):
    def __init__(self, backend):
        self.LOGGER = logging
        if backend == "s3":
            if os.environ.get("S3_BUCKET") is None:
                raise Exception
            from common.storage.s3_backend import S3Backend
            self.backend = S3Backend(shard_prefix=os.environ.get("S3_BUCKET"))
        elif backend == "file":
            from common.storage.file_backend import LocalFilesystem
            self.backend = LocalFilesystem()
        else:
            raise Exception
        self.LOGGER.info(f"Selected backend: {self.backend}")

    def get_file(self, path):
        _, res = self.backend.get_object(path)
        return res

    def put_file(self, path):
        _, res = self.backend.put_object(path)
        return res
