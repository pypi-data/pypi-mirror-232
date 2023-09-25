from ..private_repo._file_manager_sqlite import FileManagerSQLite
from ..private_repo._file_manager_csv import FileManagerCSV
from ..private_repo._file_manager_json import FileManagerJSON

class FileManagerFactory:
    @staticmethod
    def create_file_manager(data_file_path: str):
        if ".db" in data_file_path:
            return FileManagerSQLite(data_file_path)
        elif ".csv" in data_file_path:
            return FileManagerCSV(data_file_path)
        elif ".json" in data_file_path:
            return FileManagerJSON(data_file_path)

        raise ValueError(
            f"{data_file_path} with extension {data_file_path.split('.')[1]}")
