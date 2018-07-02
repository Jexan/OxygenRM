''' The database driver for using a SQLite3 connection.
    Abstracts away the basic DB operations, to make everything
    easier for dealing internally with models.
'''
import sqlite3
import logging

logging.basicConfig(filename='test/test.log',level=logging.DEBUG)

from OxygenRM.internals.SQL_builders import *

class SQLite3DB():
    ''' Init the connection to the database

        Args:
            db_name: The path to the sqlite3 database as a string.
    '''
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row

        self.cursor     = self.connection.cursor()

    def create_table(self, table_name, **columns):
        ''' Create a table in the database with the specified columns.

            Args:
                table_name : The name of the table to be created.
                **columns : A dict with the column names as keys and column type
                    as values.

            Raises:
                TypeError: If a field passed is not a valid SQLite3 field.
                    | No columns passed.
        '''
        if not columns:
            raise ValueError('Can\'t create table without columns')
        for column_type in columns.values():
            if not column_type in ['text', 'integer', 'real', 'blob']:
                raise TypeError('Invalid column type: {}'.format(column_type))

        self.execute(create_table_clause(table_name, columns))

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
        return self.execute(drop_table_clause(table_name))

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
        return self.execute(insert_clause(table_name, values) ,tuple(values.values()))   

    def create_many(self, table_name, keys, values):
        ''' Create multiple new records in the database. 

            Args:
                table_name: The table to query.
                keys: An iterator to know the keys
                values: An iterator that yield tuplables iterators, corresponding to the keys.

            Returns:
                The created record
        '''
        return self.execute_many(insert_clause(table_name, keys), values)

    def all(self, table_name, fields=[]):
        ''' Get every record in the table_name. 

            Args:
                table_name: The table to query.

            Returns:
                All the records
        '''
        return self.execute_without_saving(select_clause(table_name, *fields))
    
    def find_where(self, table_name, conditions, fields=[]):
        ''' Get every record that fullfills the passed conditions. 

            Args:
                table_name: The table to query.
                conditions: Triples with the conditions (field, symbol, value, condition)
                fields: A list of the fields to select.
            
            Returns:
                An iterator with the found records.    
        '''
        conditions = list(conditions)

        where_query =  where_clause(conditions)
        query = '{} {}'.format(select_clause(table_name, *fields), where_query)

        return self.execute_without_saving(query, conditions_values(conditions)) 

    def find_equal(self, table_name, *_, fields=[], **equals):
        ''' Get every record whose fields are equal to the given values. 

            Args:
                table_name: The table to query.
                fields: A list of the fields to select.
                **equals: A dict of fields: values pairs, so the found models will be
                    those who fullfil the field == value.
            
            Returns:
                An iterator with the found records.
    
            Raises:
                ValueError: If no condition is passed.
        '''
        if not equals:
            raise ValueError('No conditions passed')

        return self.find_where(table_name, equals_conditions(**equals), fields)

    def update_where(self, table_name, changes, conditions):
        ''' Update records who fulfills the conditions with the proposed changes.

            Args:
                table_name: The table to change.
                changes: A dict with the keys specifying the fields and the values, the new values.
                conditions: An iterator that yields tuples with the conditions (field, symbol, value, connector)

            See also:
                SQLite3DB.update_all
        '''
        conditions = list(conditions)

        update = update_clause(table_name, changes) 
        where = where_clause(conditions)

        query = update + ' ' + where

        return self.execute(query, tuple(changes.values()) + conditions_values(conditions))

    def update_equal(self, table_name, changes, **equals):
        ''' Update records whose fields are equal to the given values, with the proposed changes.

            Args:
                table_name: The table to change.
                changes: A dict with the keys specifying the fields and the values, the new values.
                **equals: A dict of fields: values pairs, so the found models will be
                    those who fullfil the field == value.
            Raises:
                ValueError: If no WHERE condition is passed. 

            See also:
                SQLite3DB.update_all
        '''
        if not equals:
            raise ValueError('No conditions passed')

        return self.update_where(table_name, changes, equals_conditions(**equals))

    def update_all(self, table_name, changes):
        ''' Update every record with the proposed changes.

            Args:
                table_name: The table to change.
                changes: A dict with the keys specifying the fields and the values, the new values.

            See also:
                SQLite3DB.update_where
        '''
        return self.execute(update_clause(table_name, changes), tuple(changes.values()))

    def delete_where(self, table_name, conditions):
        ''' Delete every record that fullfil the given conditions.

            Args:
                table_name: The table to query.
                *conditions: An iterator that yields tuples of the form (field, symbol, value, conditions)
            
            Returns:
                An iterator with the found records.
        '''
        conditions = list(conditions)

        where = where_clause(conditions)
        query = 'DELETE FROM {} {}'.format(table_name, where)

        return self.execute(query, conditions_values(conditions))

    def delete_equal(self, table_name, **equals):
        ''' Delete records whose fields are equal to the given values.

            Args:
                table_name: The table to change.
                **equals: A dict of fields: values pairs, so the deleted models will be
                    those who fullfil the field == value.

            Raises:
                ValueError: If no WHERE condition is passed. 
        '''
        if not equals:
            raise ValueError('No conditions passed')

        return self.delete_where(table_name, equals_conditions(**equals))

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

    ''' The name of the DB driver.
    '''
    driver = 'sqlite3'