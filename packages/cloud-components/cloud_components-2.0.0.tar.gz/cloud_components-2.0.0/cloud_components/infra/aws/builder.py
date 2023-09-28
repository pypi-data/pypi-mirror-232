from cloud_components.infra.aws.connection.resource_connector import ResourceConnector
from cloud_components.interface.infra.builder import IBuilder
from cloud_components.interface.infra.storage import IStorage
from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.services.log import ILog
from cloud_components.infra.aws.resources.s3 import S3


class AwsBuilder(IBuilder):
    """
    An implementation of IBuilder interface and responsible
    to build resource implementation, like S3, SQS, and many
    other services.

    ...

    Attributes
    ----------
    logger : ILog
        Logger object that share the same methods with ILog
    env : IEnviroment
        Enviroment class instance

    Methods
    ----------
    build_storage()
        Instanciate the S3 class with a connection instance from s3
        service
    """

    def __init__(self, logger: ILog, env: IEnviroment):
        self.logger = logger
        self.env = env
        self.resource = ResourceConnector(logger=self.logger, env=self.env)

    def build_storage(self) -> IStorage:
        """
        Returns
        ----------
        IStorage
            An instance of S3 class, and a implementation from IStorage
            interface
        """
        connection = self.resource.connect(resource_name="s3")
        return S3(
            connection=connection,
            logger=self.logger,
            env=self.env,
        )
