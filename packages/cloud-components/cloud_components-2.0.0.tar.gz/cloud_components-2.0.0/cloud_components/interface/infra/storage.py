from abc import ABC, abstractmethod


class IStorage(ABC):  # pylint: disable=C0115
    @abstractmethod
    def save_file(  # pylint: disable=C0116
        self,
        data: str,
        file_path: str,
        content_type: str,
        is_public: bool = False,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_file(self, file_path: str) -> str | None:  # pylint: disable=C0116
        raise NotImplementedError

    @property
    @abstractmethod
    def bucket(self):  # pylint: disable=C0116
        raise NotImplementedError
