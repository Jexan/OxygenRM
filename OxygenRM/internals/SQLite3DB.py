""" The database driver for using a SQLite3 connection.
    Abstracts away the basic DB operations, to make everything
    easier for dealing internally with models.
"""
import sqlite3
import logging

logging.basicConfig(filename='test/test.log',level=logging.DEBUG)

from OxygenRM.internals.SQL_builders import *

VALID_TABLE_TYPES = [
    'integer', 
    'int', 

    'boolean', 

    'real', 

    'blob', 

    'text', 

    'datetime',
    'date',

    'json',
    'xml',
    'csv',
    'foreign'
]

SEQUENCE_TABLE = 'sqlite_sequence'

class SQLite3DB():
    """ Init the connection to the database

        Args:
            db_name: The path to the sqlite3 database as a string.
    """
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row
    
        self.cursor     = self.connection.cursor()

    def last_id(self):
        return self.cursor.lastrowid

    def create_table(self, table_name, columns):
        """ Create a table in the database with the specified columns.

            Args:
                table_name : The name of the table to be created.
                **columns : A dict with the column names as keys and a ColumnData 
                    as values. 

            Raises:
                TypeError: If a field passed is not a valid SQLite3 field.
                    | No columns passed.
        """
        columns = list(columns)

        if not columns:
            raise ValueError('Can\'t create {} without columns'.format(table_name))

        for column_data in columns:
            if not column_data.type in VALID_TABLE_TYPES:
                raise TypeError('Invalid column type: {}'.format(column_data.type))

        self.execute(create_table_clause(table_name, columns))

    def table_cols_info(self, table_name):
        """ Get a table columns info.

            Args:
                table_name: The name of the table to be studied.

            Returns:
                An iterator with every column of the table 
        """
        query = "PRAGMA table_info({})".format(table_name)

        return self.execute_without_saving(query)

    def table_fields_types(self, table_name):
        """ Get a table columns info.

            Args:
                table_name: The name of the table to be studied.

            Returns:
                A dict with column names as keys and column types as values.
        """
        info = self.table_cols_info(table_name)

        return {col['name']: col['type'] for col in info}

    def get_all_tables(self):
        """ Get every table in the database. 

            Returns:
                An iterable with all the tables names.
        """
        tables = self.connection.execute('SELECT * FROM sqlite_master WHERE type="table"')

        return (table['name'] for table in tables)

    def get_all_columns(self, table_name):
        """ Get every column of the given table.

            Args:
                table_name The name of the table whose columns will be fetched.

            Returns:
                An iterable with every column as ColumnData
        """
        table = self.execute_without_saving('SELECT sql FROM sqlite_master WHERE tbl_name=?', (table_name, ))

        return build_columns_from_sql(table.fetchone()['sql'])

    def drop_table(self, table_name):
        """ Drop a table from the database.

            Args:
                table_name: The name of the table to be dropped.
        """
        return self.execute(drop_table_clause(table_name))

    def add_column(self, table_name, column):
        """ Add columns to the table

            Args:
                table_name: The table to add the column to.
                column: A ColumnData tuple.
        """
        self.execute(add_column_clause(table_name, column))

    def rename_table(self, old_table_name, new_table_name):
        """ Rename a table of the database.

            Args:
                old_table_name: The table in database to be renamed.
                new_table_name: The new name for the table.
        """
        self.execute(rename_table_clause(old_table_name, new_table_name))

    def table_exists(self, table_name):
        """ Check if a table exist in the database.

            Args:
                table_name: The name of the table to be checked.

            Returns:
                A boolean indicating wheter the given table exists.
        """
        return any(table == table_name for table in self.get_all_tables())

    def drop_all_tables(self):
        """ Drop all the tables in the database.
        """
        # We better transform the iterator to list if we don't want messy behaviour.
        for table in list(self.get_all_tables()):
            if table != SEQUENCE_TABLE:
                self.drop_table(table)

    def create(self, table_name, **values):
        """ Create a new record in the database. 

            Args:
                table_name: The table to query.
                **values: The field=value dictionary
        """
        return self.execute(insert_clause(table_name, values) ,tuple(values.values()))   

    def create_many(self, table_name, keys, values):
        """ Create multiple new records in the database. 

            Args:
                table_name: The table to query.
                keys: An iterator to know the keys
                values: An iterator that yield tuplables iterators, corresponding to the keys.

            Returns:
                The created record
        """
        return self.execute_many(insert_clause(table_name, keys), values)

    def all(self, table_name, fields=[]):
        """ Get every record in the table_name. 

            Args:
                table_name: The table to query.

            Returns:
                All the records
        """
        return self.execute_without_saving(select_clause(table_name, *fields))
    
    def execute(self, query, args=()):
        """ Run a query and commit (for Create, Update, Delete operations). 

            Args:
                query: The query to be executed.
                args: If the query has to be protected from sql injection,
                   the args to substitute can be passed as a tuple.

            Returns:
                The query result.
        """
        result = self.cursor.execute(query, args)

        self.connection.commit()

        return result

    def execute_without_saving(self, query, args=()):
        """ Run a query without commit (for Read operations). 

            Args:
                query: The query to be executed.
                args: If the query has to be protected from sql injection,
                   the args to substitute can be passed as a tuple.
        """
        return self.cursor.execute(query, args)

    def execute_many(self, query, args=()):
        """ Run a query multiple times with commit (for Create operations). 

            Args:
                query: The query to be executed.
                args: If the query has to be protected from sql injection,
                   the args to substitute can be passed as an iterator that yields tuples.
        """
        return self.cursor.executemany(query, (tuple(field) for field in args))

    """ The name of the DB driver.
    """
    driver = 'sqlite3'