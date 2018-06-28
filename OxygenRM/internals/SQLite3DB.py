''' The database driver for using a SQLite3 connection.
    Abstracts away the basic DB operations, to make everything
    easier for dealing internally with models.
'''
import sqlite3
import logging

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

            Raises:
                TypeError: If a field passed is not a valid SQLite3 field.
        '''
        for column_type in cols.values():
            if not column_type in ['text', 'integer', 'real', 'blob']:
                raise TypeError('Invalid column type: {}'.format(column_type))

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

        return (table['name'] for table in tables)

    def drop_table(self, table_name):
        ''' Drop a table from the database.

            Args:
                table_name: The name of the table to be dropped.
        '''
        return self.execute('DROP TABLE IF EXISTS {}'.format(table_name))

    def table_exists(self, table_name):
        ''' Check if a table exist in the database.

            Args:
                table_name: The name of the table to be checked.

            Returns:
                A boolean indicating wheter the given table exists.
        '''
        return any(table == table_name for table in self.get_all_tables())

    def drop_all_tables(self):
        ''' Drop all the tables in the database.
        '''
        # We better transform the iterator to list if we don't want messy behaviour.
        for table in list(self.get_all_tables()):
            self.drop_table(table)

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
    
    def find_where(self, table_name, *conditions, **equals):
        ''' Get every record that fullfills the passed conditions. 

            Args:
                table_name: The table to query.
                *conditions: Triples with the conditions ('field', 'symbol', 'value')
                **equals: Passing k1=v1, ... is equivalent to passing (k1, '=', v1)
            
            Returns:
                An iterator with the found records.

            Raises:
                valueError: If no condition is passed.
        '''
        conditions = list(conditions)

        if not len(conditions) and not equals:
            raise ValueError('No conditions passed to WHERE clause')

        for field, value in equals.items():
            conditions.append((field, '=', value))

        query = 'SELECT * FROM {} WHERE '.format(table_name)

        # This assures that inequality doesn't skip over Null valued fields 
        for index, (field, symbol, value) in enumerate(conditions):
            if symbol == '!=' and value != None:
                query += ' ({0} NOT NULL OR {0} != ?) AND'.format(field)
            elif symbol == '=' and value == None:
                query += ' {} IS ? AND'.format(field)
            elif symbol[-1] == '=' and value != None:
                query += ' ({0} NOT NULL AND {0} {1} ?) AND'.format(field, symbol)
            else:
                query += ' {} {} ? AND'.format(field, symbol)

        # Prune any extra AND/OR
        query = query[:-3]

        return self.execute(query, tuple(condition[2] for condition in conditions)) 

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