import abc
from enum import Enum


class _EasyEDAComponent:
    @abc.abstractmethod
    def render(self) -> str:
        ...


class DocumentType(Enum):
    SCHEMATIC = 1
    SYMBOL = 2
    PCB = 3
    FOOTPRINT = 4
    SCHEMATIC_MODULE = 13
    PCB_MODULE = 14

    def __get__(self, instance, owner):
        return self.value
