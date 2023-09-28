"""Module for defining the abstract Container class for use in the testing
routines of lia."""

from typing import Any
from abc import ABC, abstractmethod, abstractclassmethod


class Container(ABC):
    """Base container object to declare the necessary functionalities for
    setting up testing environments."""

    @abstractmethod
    def __init__(self, name: str, file_path: str):
        raise NotImplementedError

    @abstractmethod
    def create(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def destroy(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def execute_commands(self) -> None:
        raise NotImplementedError

    def parse_instructions(self, path_to_instructions: str) -> None:
        raise NotADirectoryError
