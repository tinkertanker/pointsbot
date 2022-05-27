import sqlite3
from pathlib import Path


class SqliteEngine:
    def __init__(self, database_file: str):
        self.db_loc = database_file
        self._connection = None
        self._cursor = None

    def connect(self):
        """
        Connects to the SQLite database
        :return: None
        """
        self._connection = sqlite3.connect(self.db_loc)
        self._cursor = self._connection.cursor()

    @property
    def conn(self) -> sqlite3.Connection:
        """
        Returns the connection

        :return: The connection
        """
        if not self._connection:
            self.connect()
        return self._connection

    @property
    def cur(self) -> sqlite3.Cursor:
        """
        Returns the cursor
        :return: The cursor
        """
        if not self._connection:
            self.connect()
        return self._cursor

    def exec_script(self, script_path: Path):
        """
        Executes a script file
        :param script_path: The path to the script file
        :return: None
        """
        with open(script_path, "r") as f:
            self.cur.executescript(f.read())
        self.conn.commit()

    def close_connection(self):
        """
        Closes the connection

        :return: None
        """
        if self._connection:
            self._connection.close()
