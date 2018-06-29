''' Sets of functions that help creating SQL clauses programatically
'''
from collections import namedtuple

''' Used as return value of query builders that use
    SQL prepares. The query will be the SQL and the args,
    a tuple with the args to be passed to the preparer.
'''
SQLInfo = namedtuple('SQLInfo', ['query', 'args'])

def update_clause(table_name, changes):
    ''' Create an update (with no where condition) clause string for SQL.

        Args:
            changes: A dict with the keys specifying the fields and the values, the new values.

        Returns:
            A named tuple with tho fields:
                [0] query: The crafted clause
                [1] args : A tuple with the values to be safely replaced.
    '''
    set_query = 'SET ' + ', '.join(field +  ' = ?' for field in changes.keys())
    return SQLInfo('UPDATE {} {}'.format(table_name, set_query), tuple(changes.values()))

def where_clause(*conditions, **equals):
    ''' Create a where clause string for SQL.

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

    return SQLInfo(where_clause_str, tuple(condition[2] for condition in conditions_list))

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