"""Simple stub of aiosqlite for testing without external dependency."""

import asyncio
import sqlite3

DatabaseError = sqlite3.DatabaseError
Error = sqlite3.Error
IntegrityError = sqlite3.IntegrityError
NotSupportedError = sqlite3.NotSupportedError
OperationalError = sqlite3.OperationalError
ProgrammingError = sqlite3.ProgrammingError
sqlite_version = sqlite3.sqlite_version
sqlite_version_info = sqlite3.sqlite_version_info
PARSE_COLNAMES = sqlite3.PARSE_COLNAMES
PARSE_DECLTYPES = sqlite3.PARSE_DECLTYPES
Binary = sqlite3.Binary


class AsyncCursor:
    def __init__(self, conn: sqlite3.Connection):
        self._cursor = conn.cursor()

    @property
    def description(self):
        return self._cursor.description

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    async def execute(self, operation, parameters=None):
        if parameters is None:
            return self._cursor.execute(operation)
        return self._cursor.execute(operation, parameters)

    async def executemany(self, operation, seq_of_parameters):
        return self._cursor.executemany(operation, seq_of_parameters)

    async def fetchall(self):
        return self._cursor.fetchall()

    async def close(self):
        return self._cursor.close()


class AsyncConnection:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self.daemon = True

    def __await__(self):
        async def _wrapper():
            return self

        return _wrapper().__await__()

    @property
    def isolation_level(self):
        return self._conn.isolation_level

    @isolation_level.setter
    def isolation_level(self, value):
        self._conn.isolation_level = value

    async def cursor(self):
        return AsyncCursor(self._conn)

    async def execute(self, *args, **kwargs):
        return self._conn.execute(*args, **kwargs)

    async def commit(self):
        return self._conn.commit()

    async def rollback(self):
        return self._conn.rollback()

    async def close(self):
        return self._conn.close()

    async def create_function(self, *args, **kwargs):
        return self._conn.create_function(*args, **kwargs)


def connect(*args, **kwargs):
    kwargs.setdefault("check_same_thread", False)
    conn = sqlite3.connect(*args, **kwargs)
    return AsyncConnection(conn)
