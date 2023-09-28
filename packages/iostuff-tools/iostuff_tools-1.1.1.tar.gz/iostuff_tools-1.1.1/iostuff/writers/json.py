from typing import Generic, TypeVar, Self
from contextlib import AbstractContextManager
import jsonpickle

T = TypeVar("T")


class JsonWriter(AbstractContextManager, Generic[T]):
    def __init__(self, file_path: str, unpickable: bool = True) -> None:
        self.__file_path = file_path
        self.__file_encoding = "utf-8"
        self.__unpickable = unpickable
        self.__fp = None

    def __enter__(self) -> Self:
        return self.open()

    def __exit__(self, *e) -> None:
        return self.close()

    def open(self) -> Self:
        self.__fp = open(self.__file_path, "w",
                         encoding=self.__file_encoding)
        return self

    def close(self) -> None:
        return self.__fp.close()

    def write(self, value: T) -> None:
        self.__fp.write(jsonpickle.encode(
            value, unpicklable=self.__unpickable))
