
from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.services.log import ILog
from cloud_components.services.enviroment.dotenv import Dotenv


class EnvFactory:  # pylint: disable=C0115
    def __init__(self, logger: ILog) -> None:
        self.logger = logger

    def manufacture_dotenv(self) -> IEnviroment:  # pylint: disable=C0116
        return Dotenv(log=self.logger)
