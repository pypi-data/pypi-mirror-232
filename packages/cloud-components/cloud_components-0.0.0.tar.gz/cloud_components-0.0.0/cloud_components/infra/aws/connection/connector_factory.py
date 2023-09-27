from typing import Literal

import boto3


class ConnectorFactory:
    @staticmethod
    def manufacture(resource: Literal["sqs", "dynamodb", "s3", "lambda"], **kwargs):
        if resource == "lambda":
            return boto3.client(resource, **kwargs)
        return boto3.resource(resource, **kwargs)
