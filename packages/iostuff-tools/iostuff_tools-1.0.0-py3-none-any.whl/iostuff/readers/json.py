from typing import Any
import jsonpickle


class JsonReader:
    def __init__(self, file_path: str) -> None:
        self.__file_path = file_path
        self.__file_mode = "r"
        self.__file_encoding = "utf-8"
        self.__fp = None

    def __enter__(self) -> Any:
        self.__fp = open(self.__file_path, self.__file_mode,
                         encoding=self.__file_encoding)
        return jsonpickle.decode(self.__fp.read())

    def __exit__(self, type, value, traceback) -> None:
        self.__fp.close()
