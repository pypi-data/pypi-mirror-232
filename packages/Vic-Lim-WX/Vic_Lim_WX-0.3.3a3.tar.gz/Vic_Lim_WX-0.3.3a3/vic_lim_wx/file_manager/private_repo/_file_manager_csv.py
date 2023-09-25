import pandas as pd

from ..public import FileManagerBase


class FileManagerCSV(FileManagerBase):
    def __init__(self, csv_file: str):
        self.csv_file:str = csv_file

    def convert_to_dataframe(self, **kwargs) -> pd.DataFrame:
        return pd.read_csv(self.csv_file)

    def convert_to_file(self, **kwargs) -> None:
        pass
