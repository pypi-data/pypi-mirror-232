from abc import ABC, abstractmethod

from cloud_components.interface.infra.storage import IStorage


class IBuilder(ABC):  # pylint: disable=C0115
    @abstractmethod
    def build_storage(self) -> IStorage:  # pylint: disable=C0116
        raise NotImplementedError
