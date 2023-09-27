import _csv

class CSVReader:
    def __init__(self, file_path: str, file_encoding: str = "utf-8") -> None:
        self.__file_path = file_path
        self.__file_mode = "r"
        self.__file_encoding = file_encoding
        self.__fp = None

    def __enter__(self):
        self.__fp = open(self.__file_path, self.__file_mode,
                         encoding=self.__file_encoding, newline='')
        return _csv.reader(self.__fp)

    def __exit__(self, type, value, traceback) -> None:
        self.__fp.close()