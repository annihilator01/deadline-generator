import config
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


class ConnectionException(Exception):
    def __init__(self, msg):
        super(ConnectionException, self).__init__(msg)


class DatabaseManager:
    def __init__(self):
        self.connection = QSqlDatabase.addDatabase('QSQLITE')
        self.connection.setDatabaseName(config.sqliteDBPath)

        if not self.connection.open():
            raise ConnectionException(self.connection.lastError().databaseText())

        self._createTables()

    def _createTables(self):
        createTableQuery = QSqlQuery()
        createTableQuery.exec('PRAGMA foreign_keys = ON')
        createTableQuery.exec(
            f"""
            CREATE TABLE IF NOT EXISTS {config.subjectTable} (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                {config.subjectNameColumn} TEXT NOT NULL,
                {config.subjectEmojiColumn} TEXT
            )
            """
        )

        createTableQuery.exec(
            f"""
            CREATE TABLE IF NOT EXISTS {config.deadlineTable} (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                {config.deadlineNameColumn} TEXT NOT NULL,
                {config.deadlineLinkColumn} TEXT,
                {config.deadlineDateColumn} TEXT,
                
                {config.deadlineSubjectColumn} INTEGER NOT NULL,
                FOREIGN KEY ({config.deadlineSubjectColumn})
                REFERENCES {config.subjectTable} (id)
                ON DELETE CASCADE
            )
            """
        )

        createTableQuery.finish()
