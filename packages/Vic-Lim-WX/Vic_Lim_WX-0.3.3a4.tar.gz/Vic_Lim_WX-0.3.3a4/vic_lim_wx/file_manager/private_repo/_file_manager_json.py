import pandas as pd

from ..public import FileManagerBase


class FileManagerJSON(FileManagerBase):
    def __init__(self, json_file: str):
        self.json_file: str = json_file

    def convert_to_dataframe(self, **kwargs) -> pd.DataFrame:
        return pd.read_json(self.json_file)

    def convert_to_file(self, **kwargs) -> None:
        pass
