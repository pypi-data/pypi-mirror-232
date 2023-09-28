from typing import Literal

import boto3


class ConnectorFactory:
    """
    Manufacture connection type

    ...

    Methods
    ----------
    manufacture(resource: Literal["sqs", "dynamodb", "s3", "lambda"], **kwargs)
        Manufacture the connection based in resorce and can be a boto3.client
        or boto3.resource
    """

    @staticmethod
    def manufacture(resource: Literal["sqs", "dynamodb", "s3", "lambda"], **kwargs):
        """
        Params
        ----------
        resource
            Can be any aws service
        kwargs
            Extra params to manufacture the connection

        Returns
        ----------
        Any
            boto3.client or boto3.resource
        """
        if resource == "lambda":
            return boto3.client(resource, **kwargs)
        return boto3.resource(resource, **kwargs)
