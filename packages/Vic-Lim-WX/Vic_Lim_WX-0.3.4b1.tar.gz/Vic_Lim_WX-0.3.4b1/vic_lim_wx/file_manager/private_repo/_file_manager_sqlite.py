import pandas as pd
import sqlite3
import sys
import traceback

from vic_lim_wx.database_manager import DatabaseManager
from ..public.file_manager_base import FileManagerBase


class FileManagerSQLite(FileManagerBase):

    def __init__(self, db_file: str):
        self.db_file = db_file

    def convert_to_dataframe(self, **kwargs):
        # ToDo : Try-Catch the kwargs
        table_name: str = kwargs.get("table_name", "")
        query: str = f"SELECT * FROM {table_name}"
        conn = sqlite3.connect(self.db_file)

        try:
            return pd.read_sql(query, conn)

        # ToDo : Incorporate exception
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        finally:
            conn.close()

    def convert_to_file(self, data: pd, table_name: str) -> None:
        db_manager = DatabaseManager(
            file_path_db=self.db_file
        )
        db_manager.connect()
        data.to_sql(table_name, db_manager.connection, if_exists='replace',
                    index=False)
        db_manager.disconnect()

        # ToDo : Create Exception if db file is not provided
        # ToDo : Create Exception if sql file is not provided
