from abc import ABC, abstractmethod


class IStorage(ABC):
    @abstractmethod
    def save_file(
        self,
        data: str,
        file_path: str,
        content_type: str,
        is_public: bool = False,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_file(self, file_path: str) -> str | None:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def bucket(self):
        raise NotImplementedError
