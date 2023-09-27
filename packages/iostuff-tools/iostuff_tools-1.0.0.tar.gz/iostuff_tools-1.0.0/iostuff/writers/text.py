from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from io import TextIOWrapper


class TextWriter:
    def __init__(self, file_path: str, file_encoding: str = "utf-8") -> None:
        self.__file_path = file_path
        self.__file_mode = "w"
        self.__file_encoding = file_encoding
        self.__fp = None

    def __enter__(self) -> TextIOWrapper:
        self.__fp = open(self.__file_path, self.__file_mode,
                         encoding=self.__file_encoding)
        return self.__fp

    def __exit__(self, type, value, traceback) -> None:
        self.__fp.close()
