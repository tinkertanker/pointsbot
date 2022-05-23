import sqlite3


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

    def conn(self) -> sqlite3.Connection:
        """
        Returns the connection

        :return: The connection
        """
        return self._connection

    def cur(self) -> sqlite3.Cursor:
        """
        Returns the cursor
        :return: The cursor
        """
        if not self._connection:
            self.connect()
        return self._cursor

    def close_connection(self):
        """
        Closes the connection

        :return: None
        """
        if self._connection:
            self._connection.close()
