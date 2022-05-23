import sqlite3


class SqliteEngine:
    def __init__(self, database_file: str):
        self.db_loc = database_file
        self.connection = None
        self.cur = None

    def connect(self):
        """
        Connects to the SQLite database
        :return: None
        """
        self.connection = sqlite3.connect(self.db_loc)
        self.cur = self.connection.cursor()

    def close_connection(self):
        """
        Closes the connection

        :return: None
        """
        if self.connection:
            self.connection.close()

    def execute_query(self, with_commit=True, *args, **kwargs, ):
        """
        Executes a query on the database
        Same syntax as cur.execute from the sqlite3 library

        :param with_commit: Whether to commit the query or not
        :param kwargs: Keyword arguments for the query
        :return: The result of the query
        """
        if with_commit:
            results = self.cur.execute(*args, **kwargs)
            self.connection.commit()
        else:
            results = self.cur.execute(*args, **kwargs)
        return results

    def execute_file(self, sql_file_path: str, with_commit=True):
        """
        Executes a file of SQL queries on the database.
        Useful to create tables or something, I guess?

        :param sql_file_path: The path to the file
        :param with_commit: Whether to commit the query or not
        :return: None
        """
        with open(sql_file_path, 'r') as f:
            sql_query = f.read()
            self.cur.execute(sql_query)
            self.connection.commit() if with_commit else None
