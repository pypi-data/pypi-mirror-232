import pandas as pd

from vic_lim_wx import FileManagerBase, Vic_Custom_Logger


class FileManagerJSON(FileManagerBase):
    def __init__(self, json_file: str):
        self.logger = Vic_Custom_Logger(
            class_name=FileManagerJSON.__name__).get_logger()
        self.json_file: str = json_file
        self.logger.info("File Manager JSON instance created.")

    def convert_to_dataframe(self, **kwargs) -> pd.DataFrame:
        return pd.read_json(self.json_file)

    def convert_to_file(self, **kwargs) -> None:
        self.logger.warning("Not ready to convert to json")
        pass
