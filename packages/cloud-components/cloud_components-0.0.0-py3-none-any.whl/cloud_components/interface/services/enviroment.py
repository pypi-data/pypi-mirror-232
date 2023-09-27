from abc import ABC, abstractmethod
from typing import Any, Callable


class IEnviroment(ABC):
    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, env_name: str, cast: Callable[[str], Any] | None = None) -> Any:
        raise NotImplementedError
