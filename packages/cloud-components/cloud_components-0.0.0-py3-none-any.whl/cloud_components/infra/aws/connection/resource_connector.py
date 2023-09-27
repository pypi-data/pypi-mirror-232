from typing import Literal

from cloud_components.infra.aws.connection.connector_factory import ConnectorFactory
from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.services.log import ILog


class ResourceConnector:
    def __init__(self, logger: ILog, env: IEnviroment) -> None:
        self.logger = logger
        self.env = env

    def connect(self, resource_name: Literal["sqs", "dynamodb", "s3", "lambda"]):
        env = self.env.get(env_name="ENV")
        localstack_url = self.env.get(env_name="LOCALSTACK_URL")
        if env == "local" and localstack_url:
            self.logger.info(
                f"Connecting to {resource_name} at local enviroment"
            )
            return ConnectorFactory.manufacture(
                resource=resource_name,
                aws_access_key_id=self.env.get(env_name="AWS_ACCESS_KEY"),
                aws_secret_access_key=self.env.get(env_name="AWS_SECRET_ACCESS_KEY"),
                endpoint_url=localstack_url,
            )
        if env == "local" and not localstack_url:
            self.logger.info(
                f"Connecting to {resource_name}"
            )
            return ConnectorFactory.manufacture(
                resource=resource_name,
                aws_access_key_id=self.env.get(env_name="AWS_ACCESS_KEY"),
                aws_secret_access_key=self.env.get(env_name="AWS_SECRET_ACCESS_KEY"),
            )
        self.logger.info(
            f"Connecting to {resource_name}"
        )
        return ConnectorFactory.manufacture(resource=resource_name)
