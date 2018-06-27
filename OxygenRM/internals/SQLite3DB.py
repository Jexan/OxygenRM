''' The database driver for using a SQLite3 connection.
    Abstracts away the basic DB operations, to make everything
    easier for dealing internally with models.
'''
import sqlite3

class SQLite3DB():
    """ Init the connection to the database

        Args:
            db_name: The path to the sqlite3 database as a string.
    """
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor     = self.connection.cursor()

    def create_table(self, table_name, **cols):
        ''' Create a table in the database with the specified columns.

            Args:
                table_name : The name of the table to be created.
                **cols : A dict with the column names as keys and column type
                    as values.
            
            Returns:
                True
        '''
        cols_parentheses = ','.join(col_name + ' ' + col_type for col_name, col_type in cols.items())
        query = 'CREATE TABLE {} ({})'.format(table_name, cols_parentheses) 

        self.execute(query)

        return True

    def table_info(self, table_name):
        ''' Get a table columns info.

            Args:
                table_name: The name of the table to be studied.

            Returns:
                A dict for every column, with the keys and associated values: 
                'cid', 'column_name', 'type', 'notnull' and 'dflt_value'. 
        '''
        keys = ['cid', 'column_name', 'type', 'notnull', 'dflt_value', 'pk']
        query = "PRAGMA table_info({})".format(table_name)

        self.execute(query)

        return [dict(zip(keys, row)) for row in self.cursor.fetchall()]

    def table_fields_types(self, table_name):
        ''' Get a table columns info.

            Args:
                table_name: The name of the table to be studied.

            Returns:
                A dict with column names as keys and column types as values.
        '''
        info = self.table_info(table_name)

        return {col['column_name']: col['type'] for col in info}

    def drop_all_tables(self):
        pass
        
    def execute(self, query, args=()):
        ''' Run a query and commit the result. 

                Args:
                    query: The query to be executed.
                    args: If the query has to be protected from sql injection,
                       the args to substitute can be passed as a tuple.
        '''
        self.cursor.execute(query, args)
        self.connection.commit()