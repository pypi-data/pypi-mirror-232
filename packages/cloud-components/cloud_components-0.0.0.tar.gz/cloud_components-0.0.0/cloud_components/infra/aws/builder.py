from cloud_components.infra.aws.connection.resource_connector import ResourceConnector
from cloud_components.interface.infra.builder import IBuilder
from cloud_components.interface.infra.storage import IStorage
from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.services.log import ILog
from cloud_components.infra.aws.resources.s3 import S3


class AwsBuilder(IBuilder):
    def __init__(self, logger: ILog, env: IEnviroment):
        self.logger = logger
        self.env = env

    def build_storage(self) -> IStorage:
        resource = ResourceConnector(logger=self.logger, env=self.env)
        connection = resource.connect(resource_name="s3")
        return S3(
            connection=connection,
            logger=self.logger,
            env=self.env,
        )
