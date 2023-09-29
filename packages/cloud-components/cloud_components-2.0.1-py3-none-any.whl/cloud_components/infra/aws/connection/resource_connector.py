from typing import Literal

from cloud_components.infra.aws.connection.connector_factory import ConnectorFactory
from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.services.log import ILog


class ResourceConnector:
    """
    This class create a connection with AWS and created to be
    used in all service implementations

    ...

    Attributes
    ----------
    logger : ILog
        Logger object that share the same methods with ILog
    env : IEnviroment
        Enviroment class instance

    Methods
    ----------
    connect(self, resource_name: Literal["sqs", "dynamodb", "s3", "lambda"])
        Build a connection resource or connection client from boto3 using a
        connector factory
    """

    def __init__(self, logger: ILog, env: IEnviroment) -> None:
        self.logger = logger
        self.env = env

    def connect(self, resource_name: Literal["sqs", "dynamodb", "s3", "lambda"]):
        """
        Params
        ----------
        resource_name
            Can be any aws service

        Returns
        ----------
        Any:
            An object from boto3.resource or boto3.client based in resource name
        """
        env = self.env.get(env_name="ENV")
        localstack_url = self.env.get(env_name="LOCALSTACK_URL")
        if env == "local" and localstack_url:
            self.logger.info(f"Connecting to {resource_name} at local enviroment")
            return ConnectorFactory.manufacture(
                resource=resource_name,
                aws_access_key_id=self.env.get(env_name="AWS_ACCESS_KEY"),
                aws_secret_access_key=self.env.get(env_name="AWS_SECRET_ACCESS_KEY"),
                endpoint_url=localstack_url,
            )
        if env == "local" and not localstack_url:
            self.logger.info(f"Connecting to {resource_name}")
            return ConnectorFactory.manufacture(
                resource=resource_name,
                aws_access_key_id=self.env.get(env_name="AWS_ACCESS_KEY"),
                aws_secret_access_key=self.env.get(env_name="AWS_SECRET_ACCESS_KEY"),
            )
        self.logger.info(f"Connecting to {resource_name}")
        return ConnectorFactory.manufacture(resource=resource_name)
