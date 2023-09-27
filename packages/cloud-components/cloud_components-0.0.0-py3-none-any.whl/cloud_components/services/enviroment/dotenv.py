import os
from typing import Any, Callable

from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.services.log import ILog


class Dotenv(IEnviroment):
    def __init__(self, log: ILog) -> None:
        self.log = log

    def load(self):
        self.log.info("Loading enviroment variables")
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

    def get(self, env_name: str, cast: Callable[[str], Any] | None = None) -> Any:
        value = os.getenv(env_name)
        return value if not cast else cast(value)
