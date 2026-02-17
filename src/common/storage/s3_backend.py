from common.storage.backend import StorageBackend
import boto3
from botocore.exceptions import ClientError


class S3Backend(StorageBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s3_client = boto3.client('s3')

    def put_object(self, src, dst=""):
        src, dst = super().put_object(src, dst)
        try:
            response = self.s3_client.upload_file(src, self.shard_prefix, dst)
        except ClientError as e:
            self.LOGGGER.error(e)
            return False
        return src, dst

    def get_object(self, src, dst=""):
        src, dst = super().get_object(src, dst)
        self.s3_client.download_file(self.shard_prefix, src, dst)
        return src, dst
