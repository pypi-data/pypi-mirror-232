from typing import Generic, TypeVar
from contextlib import AbstractContextManager
import jsonpickle

T = TypeVar("T")


class JsonReader(AbstractContextManager, Generic[T]):
    def __init__(self, file_path: str, file_encoding: str = "utf-8") -> None:
        self.__file_path = file_path
        self.__file_encoding = file_encoding
        self.__fp = None

    def __enter__(self) -> T:
        return self.open()

    def __exit__(self, *e) -> None:
        return self.close()

    def open(self) -> T:
        self.__fp = open(self.__file_path, "r",
                         encoding=self.__file_encoding)
        return jsonpickle.decode(self.__fp.read())

    def close(self) -> None:
        return self.__fp.close()
