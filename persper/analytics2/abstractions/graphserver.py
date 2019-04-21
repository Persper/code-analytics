from abc import ABC, abstractclassmethod, abstractproperty
from typing import IO, Iterable, NoReturn


class IGraphServer(ABC):
    @abstractclassmethod
    def update_graph(self, commit_ref: str) -> None:
        pass
