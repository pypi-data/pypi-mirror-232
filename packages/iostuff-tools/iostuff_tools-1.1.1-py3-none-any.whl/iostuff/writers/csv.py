from typing import Any, Iterable, Self
from contextlib import AbstractContextManager
from _csv import writer


class CSVWriter(AbstractContextManager):
    def __init__(self, file_path: str, file_encoding: str = "utf-8") -> None:
        self.__file_path = file_path
        self.__file_encoding = file_encoding
        self.__fp = None
        self.__writer = None

    def __enter__(self) -> Self:
        return self.open()

    def __exit__(self, *e) -> None:
        return self.close()

    def open(self) -> Self:
        self.__fp = open(self.__file_path, "w",
                         encoding=self.__file_encoding, newline='')
        self.__writer = writer(self.__fp)
        return self

    def close(self) -> None:
        return self.__fp.close()

    def write_row(self, row: Iterable[Any]) -> None:
        self.__writer.writerow(row)

    def write_rows(self, rows: Iterable[Iterable[Any]]) -> None:
        self.__writer.writerows(rows)
