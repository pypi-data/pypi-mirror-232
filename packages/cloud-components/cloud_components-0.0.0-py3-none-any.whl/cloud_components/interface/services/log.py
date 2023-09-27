from abc import ABC, abstractmethod


class ILog(ABC):
    @abstractmethod
    def debug(self, message: str) -> None:
        raise NotADirectoryError

    @abstractmethod
    def info(self, message: str) -> None:
        raise NotADirectoryError

    @abstractmethod
    def success(self, message: str) -> None:
        raise NotADirectoryError

    @abstractmethod
    def warning(self, message: str) -> None:
        raise NotADirectoryError

    @abstractmethod
    def error(self, message: str) -> None:
        raise NotADirectoryError
