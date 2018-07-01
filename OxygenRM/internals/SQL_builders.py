''' Sets of functions that help creating SQL clauses programatically
'''
from collections import namedtuple
import logging

VALID_CONNECTORS = ('AND', 'OR')
VALID_WHERE_OPERATIONS  = ('=', '!=', 'IS', 'IS NOT', '>=', '>', '<=', '<')

def insert_clause(table_name, keys):
    ''' Create a insert clause string for SQL.

        Args:
            table_name: The table where the insertion will happen.
            keys: An iterator with strings specifying the fields to change.
        
        Returns:
            The query as a string
    '''
    fields = list(keys)

    fields_str = ', '.join(fields)
    values_str = ', '.join(['?']*len(fields))

    query = 'INSERT INTO {} ({}) VALUES ({})'.format(table_name, fields_str, values_str)
    return query 

def update_clause(table_name, fields):
    ''' Create an update (with no where condition) clause string for SQL.

        Args:
            fields: An iterator that yields the fields to change. 

        Returns:
            The crafted SQL.
    '''
    set_query = 'SET ' + ', '.join(field +  ' = ?' for field in fields)
    return 'UPDATE {} {}'.format(table_name, set_query)

def where_clause(conditions):
    ''' Create a where clause with the given conditions.

        Args:
            conditions: An iterator with tuples of the format (field, symbol, value, connector). The connector
            must be AND or OR.

        Returns:
            The crafted SQL.

        Raises:
            ValueError: If a connector or symbol is invalid.
                | The conditions are empty.
    '''
    conditions_str = ''
    connector  = None

    for field, symbol, value, connector in conditions:
        if connector not in VALID_CONNECTORS:
            raise ValueError('Unvalid SQL connector: {}'.format(connector))
        elif symbol not in VALID_WHERE_OPERATIONS:
            raise ValueError('Unvalid SQL operation: {}'.format(symbol))

        if symbol == '!=' and value != None:
            condition_str = '({field} IS NULL OR {field} != ?) {connector} '
        elif symbol[0] in '<>' and value != None:
            condition_str = '({field} NOT NULL AND {field} {symbol} ?) {connector} '
        else:
            condition_str = '{field} {symbol} ? {connector} '

        conditions_str += condition_str.format(field=field, symbol=symbol, connector=connector)

    if not conditions_str:
        raise ValueError('No condition passed')

    # Prunes the leading condition
    conditions_str = conditions_str[:-4 if connector == 'OR' else -5]
        
    return 'WHERE {}'.format(conditions_str)

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

def create_table_clause(table_name, cols):
    ''' Create a create table clause string for SQL.

        Args:
            table_name: The table to be created.
            cols: A dict of the format column_name: column_type. 
        
        Returns:
            A string with the crafted clause.
    '''
    columns = ', '.join(col_name + ' ' + col_type for col_name, col_type in cols.items())

    return 'CREATE TABLE {} ({})'.format(table_name, columns) 

def drop_table_clause(table_name):
    ''' Create a drop table if exists clause string for SQL.

        Args:
            table_name: The table to be dropped.
        
        Returns:
            A string with the crafted clause.
    '''
    return 'DROP TABLE IF EXISTS {}'.format(table_name) 

def equals_conditions(**equals):
    ''' A quick builder for field = value conditions arguments.

        Args:
            **equals: A dict with field = value pairs.
        f
        Yields:
            A tuple of the form (field, '=', value, 'AND') or
            (field, 'IS', value, 'AND') if value is null.
    '''    
    for field, value in equals.items():
        connector = '='
        if value == None:
            connector = 'IS'

        yield (field, connector, value, 'AND')

def connect_with(conditions, connector):
    ''' Give the conditions tuples the given connector.

        Args:
            condition: An iteratos with the format (field, condition, value)  
            connector: A logical connector. Either 'AND' or 'OR'.
        
        Yields:
            A tuple of the form (field, condition, value, connector)

        Raises:
            ValueError: If the given connector  is invalid.
    '''
    if connector not in VALID_CONNECTORS:
        raise ValueError('Invalid logical connector: {}'.format(connector))
    
    for condition in conditions:
        yield condition + (connector,)

def conditions_values(conditions):
    ''' Extract the values of the conditions, for passing it to the execute method.

        Args:
            condition: An iteratos that yields tuples like (field, condition, value, connector)  
        
        Returns:
            A tuple containing every value of the conditions.
    '''
    return tuple(value for _, _, value, _ in conditions)