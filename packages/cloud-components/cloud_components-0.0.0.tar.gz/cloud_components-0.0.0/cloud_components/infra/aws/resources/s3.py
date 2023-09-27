import json
from typing import Any
from botocore.exceptions import ClientError

from cloud_components.interface.services.log import ILog
from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.infra.storage import IStorage


class S3(IStorage):
    _bucket = None

    def __init__(self, connection: Any, logger: ILog, env: IEnviroment) -> None:
        self.connection = connection
        self.logger = logger
        self.env = env

    @property
    def bucket(self):
        return self._bucket

    @bucket.setter
    def bucket(self, name: str):
        self._bucket = self.connection.Bucket(name)

    def save_file(
        self, data: str, file_path: str, content_type: str, is_public: bool = False
    ) -> bool:
        data = data.encode("utf-8")
        try:
            if is_public:
                self.logger.info(
                    f"Saving a file with public acl and "
                    + f"content-type as '{content_type}' in '{file_path}'"
                )
                self.bucket.put_object(
                    Key=file_path,
                    Body=data,
                    ACL="public-read",
                    ContentType=content_type,
                )
            else:
                self.logger.info(
                    f"Saving a file with content-type as '{content_type}' in '{file_path}'"
                )
                self.bucket.put_object(
                    Key=file_path, Body=data, ContentType=content_type
                )
        except ClientError as err:
            self.logger.info(
                f"An error occurred when try to save a file in S3. Error detail: {err}"
            )
            return False
        return True

    def get_file(self, file_path: str) -> str | None:
        self.logger.info(f"Getting file from '{file_path}'")
        try:
            content = self.bucket.Object(file_path)
            content = content.get()["Body"].read()
        except ClientError as err:
            self.logger.info(
                f"An error occurred when try to get a file in S3. Error detail: {err}"
            )
            return None
        return content.decode("utf-8") if content else None
