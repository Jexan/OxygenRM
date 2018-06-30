''' Sets of functions that help creating SQL clauses programatically
'''
from collections import namedtuple

VALID_CONNECTORS = ('AND', 'OR')
VALID_WHERE_OPERATIONS  = ('=', '!=', 'IS', 'IS NOT', '>=', '>', '<=', '<')

''' Used as return value of query builders that have to
    modify the arguments.
'''
SQLInfo = namedtuple('SQLInfo', ['query', 'args'])

def insert_clause(table_name, keys, values=None):
    ''' Create a insert clause string for SQL.

        Args:
            table_name: The table where the insertion will happen.
            keys: The values to be
        
        Returns:
            If values are passed:
                A named tuple with tho fields:
                    [0] query: The crafted clause
                    [1] args : A tuple with the values to be safely replaced.
            Else:
                The query as a string
    '''
    fields = list(keys)

    fields_str = ', '.join(keys)
    values_str = ', '.join(['?']*len(fields))

    query = 'INSERT INTO {} ({}) VALUES ({})'.format(table_name, fields_str, values_str)
    return query if values else SQLInfo(query, tuple(values))

def update_clause(table_name, changes):
    ''' Create an update (with no where condition) clause string for SQL.

        Args:
            fields: A dict with the keys specifying the fields and the values, the new values. 
                | An array with the fields to change.

        Returns:
            The crafted SQL.
    '''
    local_fields = changes.keys() if isinstance(changes, dict) else changes

    set_query = 'SET ' + ', '.join(field +  ' = ?' for field in local_fields)
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
        elif symbol != '=' and symbol[-1] == '=' and value != None:
            condition_str = '({field} NOT NULL AND {field} {symbol} ?) {connector} '
        else:
            condition_str = '{field} {symbol} ? {connector} '

        conditions_str += condition_str.format(field=field, symbol=symbol, connector=connector)

    # Prunes the leading condition
    conditions_str = conditions_str[:-4 if connector == 'OR' else -5]
        
    return 'WHERE {}'.format(conditions_str)

def where_equals_clause(*conditions, **equals):
    ''' Create a where clause string for SQL, with the equals shorthand.

        Args:
            conditions: Triples with the conditions ('field', 'symbol', 'value')
            equals: Passing k1:v1, ... is equivalent to passing (k1, '=', v1)
        
        Returns:
            A named tuple with tho fields:
                [0] query: The crafted clause
                [1] args : A tuple with the values to be safely replaced.
        Raises:
            ValueError: If no condition is passed.
    '''
    if not conditions and not equals:
        raise ValueError('No conditions passed to WHERE clause')

    conditions_list = list(conditions if conditions else ())

    for field, value in equals.items():
        conditions_list.append((field, '=', value))

    where_equals_clause_str = 'WHERE'
    
    # This assures that inequality doesn't skip over Null valued fields 
    for index, condition in enumerate(conditions_list):
        field, symbol, value = condition
        separator = 'AND' if len(condition) == 3 else condition[3]

        if symbol == '!=' and value != None:
            where_equals_clause_str += ' ({0} IS NULL OR {0} != ?) AND'.format(field)
        elif symbol == '=' and value == None:
            where_equals_clause_str += ' {} IS ? AND'.format(field)
        elif symbol[-1] == '=' and value != None:
            where_equals_clause_str += ' ({0} NOT NULL AND {0} {1} ?) AND'.format(field, symbol)
        else:
            where_equals_clause_str += ' {} {} ? AND'.format(field, symbol)

    # Prune any extra AND/OR
    where_equals_clause_str = where_equals_clause_str[:-4]

    return SQLInfo(where_equals_clause_str, tuple(condition[2] for condition in conditions_list))

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