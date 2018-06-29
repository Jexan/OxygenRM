''' The database driver for using a SQLite3 connection.
    Abstracts away the basic DB operations, to make everything
    easier for dealing internally with models.
'''
import sqlite3
import logging

from itertools import chain

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

        return self.execute_without_saving(query)

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
        tables = self.execute_without_saving('SELECT * FROM sqlite_master WHERE type="table"')

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
        ''' Create a new record in the database. 

            Args:
                table_name: The table to query.
                **values: The field=value dictionary
        '''
        fields = list(values.keys())

        fields_str = ','.join(fields)
        values_str = ','.join(['?']*len(fields))

        return self.execute('INSERT INTO {} ({}) VALUES ({})'.format(table_name, fields_str, values_str),
           tuple(values.values()))   

    def create_many(self, table_name, keys, values):
        ''' Create multiple new records in the database. 

            Args:
                table_name: The table to query.
                keys: An iterator to know the keys
                values: An iterator that yield tuplables iterators, corresponding to the keys.

            Returns:
                The created record
        '''
        fields = list(keys)

        fields_str = ','.join(fields)
        values_str = ','.join(['?']*len(fields))
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(table_name, fields_str, values_str)

        return self.execute_many(query, values)

    def all(self, table_name, fields=[]):
        ''' Get every record in the table_name. 

            Args:
                table_name: The table to query.

            Returns:
                All the records
        '''
        return self.execute_without_saving(select_clause(table_name, *fields))
    
    def find_where(self, table_name, *conditions, fields=[], **equals):
        ''' Get every record that fullfills the passed conditions. 

            Args:
                table_name: The table to query.
                *conditions: Triples with the conditions ('field', 'symbol', 'value')
                fields: A list of the fields to select.
                **equals: Passing k1=v1, ... is equivalent to passing (k1, '=', v1)
            
            Returns:
                An iterator with the found records.
    
            Raises:
                ValueError: If no condition is passed.
        '''
        where_info =  where_clause(*conditions, **equals)
        query = '{} {}'.format(select_clause(table_name, *fields), where_info[0])

        return self.execute_without_saving(query, where_info[1]) 

    def update_where(self, table_name, changes, *conditions, **equals):
        ''' Update records who fulfills the conditions (or every record if no condition is given) 
            with the proposed changes.

            Args:
                table_name: The table to change.
                changes: A dict with the keys specifying the fields and the values, the new values.
                *conditions: Triples with the conditions ('field', 'symbol', 'value')
                **equals: Passing k1=v1, ... is equivalent to passing (k1, '=', v1)
            
            Raises:
                ValueError: If no WHERE condition is passed. 

            See also:
                SQLite3DB.update
        '''
        where_info = where_clause(*conditions, **equals)
        query_args = tuple(chain(changes.values(), where_info[1]))

        query = 'UPDATE {} SET {} {}'.format(
            table_name, ','.join(field +  ' = ?' for field in changes.keys()), where_info[0]
        )

        return self.execute(query, query_args)

    def update_all(self, table_name, changes):
        ''' Update every record with the proposed changes.

            Args:
                table_name: The table to change.
                changes: A dict with the keys specifying the fields and the values, the new values.

            See also:
                SQLite3DB.update_where
        '''
        query = 'UPDATE {} SET {}'.format(table_name, ','.join(field +  ' = ?' for field in changes.keys()))
        return self.execute(query, tuple(changes.values()))

    def delete_where(self, table_name, *conditions, **equals):
        ''' Delete every record that fullfil the given conditions.

            Args:
                table_name: The table to query.
                *conditions: Triples with the conditions ('field', 'symbol', 'value')
                **equals: Passing k1=v1, ... is equivalent to passing (k1, '=', v1)
            
            Returns:
                An iterator with the found records.
    
            Raises:
                ValueError: If no condition is passed.
        '''
        where_info = where_clause(*conditions, **equals)
        query = 'DELETE FROM {} {}'.format(table_name, where_info[0])

        return self.execute(query, where_info[1])

    def execute(self, query, args=()):
        ''' Run a query and commit (for Create, Update, Delete operations). 

            Args:
                query: The query to be executed.
                args: If the query has to be protected from sql injection,
                   the args to substitute can be passed as a tuple.

            Returns:
                The query result.
        '''
        result = self.cursor.execute(query, args)

        self.connection.commit()

        return result

    def execute_without_saving(self, query, args=()):
        ''' Run a query without commit (for Read operations). 

            Args:
                query: The query to be executed.
                args: If the query has to be protected from sql injection,
                   the args to substitute can be passed as a tuple.
        '''
        return self.cursor.execute(query, args)

    def execute_many(self, query, args=()):
        ''' Run a query multiple times with commit (for Create operations). 

            Args:
                query: The query to be executed.
                args: If the query has to be protected from sql injection,
                   the args to substitute can be passed as an iterator that yields tuples.
        '''
        return self.cursor.executemany(query, (tuple(field) for field in args))


def where_clause(*conditions, **equals):
    ''' Create a where clause string for SQL.

        Args:
            conditions: Triples with the conditions ('field', 'symbol', 'value')
            equals: Passing k1:v1, ... is equivalent to passing (k1, '=', v1)
        
        Returns:
            A string with the crafted clause and the values.

        Raises:
            ValueError: If no condition is passed.
    '''
    if not conditions and not equals:
        raise ValueError('No conditions passed to WHERE clause')

    conditions_list = list(conditions if conditions else ())

    for field, value in equals.items():
        conditions_list.append((field, '=', value))

    where_clause_str = 'WHERE'
    
    # This assures that inequality doesn't skip over Null valued fields 
    for index, condition in enumerate(conditions_list):
        field, symbol, value = condition
        separator = 'AND' if len(condition) == 3 else condition[3]

        if symbol == '!=' and value != None:
            where_clause_str += ' ({0} IS NULL OR {0} != ?) AND'.format(field)
        elif symbol == '=' and value == None:
            where_clause_str += ' {} IS ? AND'.format(field)
        elif symbol[-1] == '=' and value != None:
            where_clause_str += ' ({0} NOT NULL AND {0} {1} ?) AND'.format(field, symbol)
        else:
            where_clause_str += ' {} {} ? AND'.format(field, symbol)

    # Prune any extra AND/OR
    where_clause_str = where_clause_str[:-4]

    return where_clause_str, tuple(condition[2] for condition in conditions_list)

def select_clause(table_name, *fields):
    ''' Create a select from clause string for SQL.

        Args:
            table_name: The table to select from as string.
            *fields: The fields to select. 
        
        Returns:
            A string with the crafted clause.
    '''
    fields_str = ', '.join(fields) if fields else '*'

    return 'SELECT {} FROM {}'.format(fields_str, table_name)
