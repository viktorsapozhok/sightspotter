# -*- coding: utf-8 -*-

"""SQLite database communication agent
"""
__all__ = ['Commuter']

from contextlib import contextmanager

import pandas as pd
from sqlalchemy import create_engine
import sqlite3


class Commuter:
    """SQLite database communication agent.

    Implements `select`, `insert` and `execute` methods.

    Args:
        path2db:
            Path to database file.

    Attributes:
        engine:
            Instance of sqlalchemy engine.
        conn:
            sqlite3 connection object.
    """

    def __init__(self, path2db):
        self.path2db = path2db
        self.engine = self.make_engine()
        self.conn = None

    def make_engine(self):
        return create_engine('sqlite:///' + self.path2db, echo=False)

    @contextmanager
    def make_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.path2db)

        yield self.conn

        self.close_connection()

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def select(self, cmd, return_scalar=None):
        """Select data from table.

        Args:
            cmd:
                SQL query.
            return_scalar:
                Return Pandas.DataFrame if None, otherwise return
                scalar value.

        Returns:
            Query result converted to Pandas.DataFrame
        """

        with self.engine.connect() as conn:
            df = pd.read_sql_query(cmd, conn)

        if return_scalar is not None:
            if df.empty:
                return return_scalar
            else:
                return df.iloc[0, 0]

        return df

    def insert(self, table_name, data) -> None:
        """Insert data from DataFrame to the table.

        Args:
            table_name:
                Name of the database table.
            data:
                Pandas.DataFrame with the data to be inserted.
        """

        with self.engine.connect() as conn:
            data.to_sql(
                table_name,
                con=conn,
                if_exists='append',
                index=False)

    def execute(self, cmd, vars):
        """Execute SQL command and commit changes to database.

        Args:
            cmd:
                SQL-query.
            vars:
                Parameters to command,
                may be provided as sequence or mapping.
        """

        with self.make_connection() as conn:
            try:
                cur = conn.cursor()

                if vars is None:
                    cur.execute(cmd)
                else:
                    cur.execute(cmd, vars)

                conn.commit()
            except sqlite3.DatabaseError as e:
                # roll back the pending transaction
                conn.rollback()
                raise e

        self.close_connection()
