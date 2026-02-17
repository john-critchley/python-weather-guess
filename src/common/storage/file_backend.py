from common.storage.backend import StorageBackend
from shutil import copyfile
import os


class LocalFilesystem(StorageBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.LOGGGER.info(f"Init local filesystem with {list(*args)} {list(**kwargs)}")

        if self.remote_prefix == "":
        #-jc TODO: migrate to persistent volume path:-
            self.remote_prefix = os.environ.get("STORAGE_DIR") or "/tmp" # nosec B108 - container-local temp storage

        if self.local_prefix == "":
            self.local_prefix = os.environ.get("TMP_DIR") or self.remote_prefix

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
