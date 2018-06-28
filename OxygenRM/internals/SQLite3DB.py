''' The database driver for using a SQLite3 connection.
    Abstracts away the basic DB operations, to make everything
    easier for dealing internally with models.
'''
import sqlite3

class SQLite3DB():
    ''' Init the connection to the database

        Args:
            db_name: The path to the sqlite3 database as a string.
    '''
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row

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

    def table_cols_info(self, table_name):
        ''' Get a table columns info.

            Args:
                table_name: The name of the table to be studied.

            Returns:
                An iterator with every column of the table 
        '''
        query = "PRAGMA table_info({})".format(table_name)

        return self.execute(query)

    def table_fields_types(self, table_name):
        ''' Get a table columns info.

            Args:
                table_name: The name of the table to be studied.

            Returns:
                A dict with column names as keys and column types as values.
        '''
        info = self.table_cols_info(table_name)

        return {col['name']: col['type'] for col in info}

    def get_all_tables(self):
        ''' Get every table in the database. 

            Returns:
                An iterable with all the tables names.
        '''
        tables = self.execute('SELECT * FROM sqlite_master WHERE type="table"')

        return (table[2] for table in tables)

    def create(self, table_name, **values):
        ''' Creates a new record in the database. 

            Args:
                table_name: The table to query.
                **values: The field=value dictionary

            Returns:
                The created record
        '''
        fields = list(values.keys())

        fields_str = ','.join(fields)
        values_str = ','.join(['?']*len(fields))

        return self.execute('INSERT INTO {} ({}) VALUES ({})'.format(table_name, fields_str, values_str),
           tuple(values.values()))

    def all(self, table_name):
        ''' Get every record in the table_name. 

            Args:
                table_name: The table to query.

            Returns:
                All the records
        '''
        return self.execute('SELECT * FROM {}'.format(table_name))
    
    def drop_all_tables(self):
        pass

    def execute(self, query, args=()):
        ''' Run a query and commit the result. 

            Args:
                query: The query to be executed.
                args: If the query has to be protected from sql injection,
                   the args to substitute can be passed as a tuple.
        '''
        result = self.cursor.execute(query, args)
        self.connection.commit()

        return result