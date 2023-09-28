from cloud_components.interface.infra.builder import IBuilder
from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.services.log import ILog


class InfraFactory:
    """
    This class manufacture cloud implementations from infra package,
    every implementation has a builder class to make more simple your
    declaration, and all this is encapsulated in manufacture methods.

    ...

    Attributes
    ----------
    logger : ILog
        blabla
    env : IEnviroment
        blabla

    Methods
    ----------
    manufacture_aws()
        This method import and construct an AwsBuilder class. I decided
        to import the package here because the boto3 package is to much
        slow in terms of import.
    """

    def __init__(self, logger: ILog, env: IEnviroment) -> None:
        self.logger = logger
        self.env = env

    def manufacture_aws(self) -> IBuilder:
        """
        Returns
        ----------
        IBuilder
            An IBuilder implemetation called AwsBuilder
        """
        from cloud_components.infra.aws.builder import (  # pylint: disable=C0415
            AwsBuilder,
        )

        return AwsBuilder(logger=self.logger, env=self.env)
