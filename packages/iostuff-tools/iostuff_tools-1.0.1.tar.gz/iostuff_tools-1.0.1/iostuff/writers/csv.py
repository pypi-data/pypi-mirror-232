from typing import Any, Iterable
import _csv


class CSVWriter:
    def __init__(self, file_path: str, file_encoding: str = "utf-8") -> None:
        self.__file_path = file_path
        self.__file_mode = "w"
        self.__file_encoding = file_encoding
        self.__fp = None
        self.__writer = None

    def __enter__(self):
        self.__fp = open(self.__file_path, self.__file_mode,
                         encoding=self.__file_encoding, newline='')
        self.__writer = _csv.writer(self.__fp)
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.__fp.close()

    def write_row(self, row: Iterable[Any]) -> None:
        self.__writer.writerow(row)

    def write_rows(self, rows: Iterable[Iterable[Any]]) -> None:
        self.__writer.writerows(rows)
