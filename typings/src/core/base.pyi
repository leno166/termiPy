import abc
from abc import ABC, abstractmethod
from typing import NoReturn

class TerminalIn(ABC, metaclass=abc.ABCMeta):
    @property
    @abstractmethod
    def input(self) -> NoReturn: ...
    @input.setter
    @abstractmethod
    def input(self, value: str) -> NoReturn: ...

class TerminalOut(ABC, metaclass=abc.ABCMeta):
    @property
    @abstractmethod
    def out(self) -> str: ...
    @property
    @abstractmethod
    def err(self) -> str: ...
