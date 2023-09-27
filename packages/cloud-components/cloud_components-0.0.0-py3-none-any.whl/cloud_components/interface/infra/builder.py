from abc import ABC, abstractmethod

from cloud_components.interface.infra.storage import IStorage


class IBuilder(ABC):
    @abstractmethod
    def build_storage(self) -> IStorage:
        raise NotImplementedError
