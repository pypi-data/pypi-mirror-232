from cloud_components.interface.infra.builder import IBuilder
from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.services.log import ILog
from cloud_components.infra.aws.builder import (  # pylint: disable=C0415
            AwsBuilder,
        )


class InfraFactory:
    def __init__(self, logger: ILog, env: IEnviroment) -> None:
        self.logger = logger
        self.env = env

    def manufacture_aws(self) -> IBuilder:
        return AwsBuilder(logger=self.logger, env=self.env)
