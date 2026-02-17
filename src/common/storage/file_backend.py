from common.storage.backend import StorageBackend
from shutil import copyfile
import os


class LocalFilesystem(StorageBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.LOGGGER.info(f"Init local filesystem with {list(*args)} {list(**kwargs)}")
        if self.remote_prefix == "":
            if os.environ.get("STORAGE_DIR"):
                self.remote_prefix = os.environ.get("STORAGE_DIR")
            else:
                self.remote_prefix = "/tmp"

        if self.local_prefix == "":
            if os.environ.get("TMP_DIR"):
                self.local_prefix = os.environ.get("TMP_DIR")
            else:
                self.local_prefix = "/tmp"

    def put_object(self, src, dst=""):
        if dst == "":
            dst = os.path.join(self.remote_prefix, self._generate_tempname())
        copyfile(src, dst)
        return src, dst

    def get_object(self, src, dst=""):
        if dst == "":
            dst = os.path.join(self.local_prefix, self._generate_tempname())
        copyfile(src, dst)
        return src, dst
