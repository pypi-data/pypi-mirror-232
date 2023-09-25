import pandas as pd

from vic_lim_wx import FileManagerBase, Vic_Custom_Logger


class FileManagerCSV(FileManagerBase):
    def __init__(self, csv_file: str):
        self.logger = Vic_Custom_Logger(
            class_name=FileManagerCSV.__name__).get_logger()
        self.csv_file = csv_file
        self.logger.info("File Manager CSV instance created.")

    def convert_to_dataframe(self, **kwargs) -> pd.DataFrame:
        return pd.read_csv(self.csv_file)

    def convert_to_file(self, **kwargs) -> None:
        self.logger.warning("Not ready to convert to csv")
        pass
