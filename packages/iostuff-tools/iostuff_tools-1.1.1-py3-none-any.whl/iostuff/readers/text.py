from __future__ import annotations
from contextlib import AbstractContextManager
from io import TextIOWrapper


class TextReader(AbstractContextManager):
    def __init__(self, file_path: str, file_encoding: str = "utf-8") -> None:
        self.__file_path = file_path
        self.__file_encoding = file_encoding
        self.__fp = None

    def __enter__(self) -> TextIOWrapper:
        return self.open()

    def __exit__(self, *e) -> None:
        return self.close()

    def open(self) -> TextIOWrapper:
        self.__fp = open(self.__file_path, "r",
                         encoding=self.__file_encoding)
        return self.__fp

    def close(self) -> None:
        return self.__fp.close()
