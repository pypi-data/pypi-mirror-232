import os
from typing import Any, Callable

from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.services.log import ILog


class Dotenv(IEnviroment):  # pylint: disable=C0115
    def __init__(self, log: ILog) -> None:
        self.log = log

    def load(self):  # pylint: disable=C0116
        self.log.info("Loading enviroment variables")
        try:
            from dotenv import load_dotenv  # pylint: disable=C0415

            load_dotenv()
        except ImportError as err:
            self.log.error(
                f"An error occurred when try to load dotenv lib. Error detail: {err}"
            )

    def get(  # pylint: disable=C0116
        self, env_name: str, cast: Callable[[str], Any] | None = None
    ) -> Any:
        value = os.getenv(env_name)
        return value if not cast else cast(value)
