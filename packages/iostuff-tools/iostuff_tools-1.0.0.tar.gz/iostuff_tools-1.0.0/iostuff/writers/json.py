from typing import Any
import jsonpickle


class JsonWriter:
    def __init__(self, file_path: str, unpickable: bool = True) -> None:
        self.__file_path = file_path
        self.__file_mode = "w"
        self.__file_encoding = "utf-8"
        self.__unpickable = unpickable
        self.__fp = None

    def __enter__(self):
        self.__fp = open(self.__file_path, self.__file_mode,
                         encoding=self.__file_encoding)
        return self

    def __exit__(self, type, value, traceback):
        self.__fp.close()

    def write(self, value: Any) -> None:
        self.__fp.write(jsonpickle.encode(
            value, unpicklable=self.__unpickable))
