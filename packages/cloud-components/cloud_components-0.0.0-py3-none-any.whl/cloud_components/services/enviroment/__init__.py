from __future__ import annotations

from typing import Literal

from cloud_components.interface.services.enviroment import IEnviroment
from cloud_components.interface.services.log import ILog
from cloud_components.services.enviroment.dotenv import Dotenv


class Env:
    @classmethod
    def build(cls, env_type: Literal["dotenv"], logger: ILog) -> IEnviroment:
        match env_type:
            case "dotenv":
                return Dotenv(log=logger)
            case _:
                raise NotImplementedError(
                    f"The enviroment loader '{env_type}' is not implemented"
                )
