''' Sets of functions that help creating SQL clauses programatically
'''
from collections import namedtuple
import logging

from OxygenRM.internals.columns import ColumnData

VALID_CONNECTORS = ('AND', 'OR')
VALID_WHERE_OPERATIONS  = ('=', '!=', 'IS', 'IS NOT', '>=', '>', '<=', '<')

ConditionClause = namedtuple('ConditionClause', 'connector field symbol value')
OrderClause = namedtuple('OrderClause', 'field order')

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

def update_clause(table_name, fields, where=None):
    ''' Create an update (with no where condition) clause string for SQL.

        Args:
            fields: An iterator that yields the fields to change. 

        Returns:
            The crafted SQL.
    '''
    set_query = 'SET ' + ', '.join(field +  ' = ?' for field in fields)
    update_str = 'UPDATE {} {}'.format(table_name, set_query)
    
    if where:
        update_str += ' {}'.format(where_clause(where))

    return update_str

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
    return 'WHERE {}'.format(conditions_gen(conditions))

def select_clause(table_name, *fields, distinct=False):
    ''' Create a select from clause string for SQL.

        Args:
            table_name: The table to select from as string.
            *fields: The fields to select. 
        
        Returns:
            A string with the crafted clause.
    '''
    select = 'SELECT'
    
    if distinct:
        select += ' DISTINCT'

    fields_str = ', '.join(fields) if fields else '*'

    return '{} {} FROM {}'.format(select, fields_str, table_name)

def delete_clause(table_name, conditions=None):
    ''' Create a DELETE WHERE clause

        Args:
            table_name: The name of the table to delete from.
            conditions: An iterator of ConditionClauses.

        Returns:
            The constructed query.
    '''
    delete_str = 'DELETE FROM {}'.format(table_name)

    if conditions:
        delete_str += ' {}'.format(where_clause(conditions))

    return delete_str

def create_table_clause(table_name, cols): 
    ''' Create a create table clause string for SQL.

        Args:
            table_name: The table to be created.
            cols: An iterator of ColumnData.
        
        Returns:
            A string with the crafted clause.
    '''
    return 'CREATE TABLE {} ({})'.format(table_name, column_gen(cols)) 

def drop_table_clause(table_name):
    ''' Create a drop table if exists clause string for SQL.

        Args:
            table_name: The table to be dropped.
        
        Returns:
            A string with the crafted clause.
    '''
    return 'DROP TABLE IF EXISTS {}'.format(table_name) 

def order_by_clause(conditions):
    ''' Generate an ORDER BY clause.

        Args: 
            conditions: An iterator that yields OrderClauses

        Returns:
            The sql clause.
    '''
    return 'ORDER BY {}'.format(order_gen(condtions))

def limit_clause(n, offset=None):
    ''' Generate an LIMIT clause, with OFFSET if provided.

        Args:
            n: The number of rows to get.
            offset: The offset number. If None, no offset is added.

        Return:
            The completed clause
    '''
    limit_str = 'LIMIT {}'.format(n)

    if offset:
        limit_str += ' OFFSET {}'.format(offset)
    
    return limit_str

def group_by_clause(fields, having=None):
    ''' Generate an GROUP BY clause

        Args:
            fields: An iterator with the groupped by fields.
            having: A ConditionClause with the having condition. 
                If falsy, no HAVING condition will be added. 

        Return:
            The completed clause
    '''
    group_by_str = 'GROUP BY {}'.format(order_gen(fields))

    if having:
        group_by_str += ' HAVING {field} {symbol} ?'.format(**having._asdict())

    return group_by_str

def join_clause(join_type, table1, table2, on=None, using=None):
    ''' Generate a NATURAL JOIN clause.

        Args: 
            join_type: Either outer or inner.
            table1, table2: The tables to join
            on: An iterator that yields ConditionClause tuples, with the condtions.
            using: An iterator that yields the columns to use.

        Returns:
            The sql clause.
    '''
    join_table = '{} JOIN {}'.format(join_type, table2)

    if not on and not using:
        if join_type == 'CROSS':
            return '{} {}'.format(table1, join_table)

        return '{} NATURAL {}'.format(table1, join_table)

    if on:
        return '{} {} ON {}'.format(table1, join_table, conditions_gen(on, False))
    elif using:
        return '{} {} USING ({})'.format(table1, join_table, ', '.join(using))

def rename_table_clause(old_table, new_table):
    ''' Create a RENAME table clause string for SQL.

        Args:
            old_table: The table to be renamed.
            new_table: The new table name.
        
        Returns:
            A string with the crafted clause.
    '''
    return 'ALTER TABLE {} RENAME TO {}'.format(old_table, new_table)

def add_column_clause(table_name, column):
    ''' Create a ADD COLUMN clause string for SQL.

        Args:
            table_name: The table target of the query.
            column: A ColumnData of the columns to add.
        
        Returns:
            A string with the crafted clause.
    '''
    return 'ALTER TABLE {} ADD COLUMN {}'.format(table_name, column_gen((column,)))

def column_gen(columns):
    ''' Create a column fields data, comma separated, for use in column adding builders.

        Args:
            columns: An iterator of ColumnData
    '''
    column_sql = []
    
    for col in columns:
        col_str = '{} {}'.format(col.name, col.type)

        if col.primary:
            col_str += ' PRIMARY KEY'

            if col.auto_increment:
                col_str += ' AUTOINCREMENT'

        if not col.null:
            col_str += ' NOT NULL'

        if col.default:
            default = col.default

            if type(col.default) not in (bool, float):
                default = '"{}"'.format(col.default)

            col_str += ' DEFAULT {}'.format(default)

        if col.unique:
            col_str += ' UNIQUE'

        if col.check:
            col_str += ' CHECK({})'.format(col.check)

        column_sql.append(col_str)

    return ', '.join(column_sql)

def conditions_gen(conditions, safe=True):
    ''' Generate comma separated conditions.

        Args: 
            conditions: An iterator that yields ConditionClause tuples. 

        Returns:
            The string of the query.
    '''
    conditions_str = ''
    connector  = None
    
    for index, condition in enumerate(conditions):
        if condition.connector not in VALID_CONNECTORS:
            raise ValueError('Unvalid SQL connector: {}'.format(condition.connector))
        elif condition.symbol not in VALID_WHERE_OPERATIONS:
            raise ValueError('Unvalid SQL operation: {}'.format(condition.symbol))

        if safe:
            value = '?'
        else:
            value = condition.value

        condition_str = '' if index == 0 else condition.connector + ' '

        if condition.symbol == '!=' and condition.value and safe:
            condition_str += '({field} IS NULL OR {field} != {value}) '
        elif condition.symbol[0] in '<>' and condition.value and safe:
            condition_str += '({field} NOT NULL AND {field} {symbol} {value}) '
        elif condition.symbol == '=' and not condition.value and safe:
            condition_str += '{field} IS {value} '
        else:
            condition_str += '{field} {symbol} {value} '

        conditions_str += condition_str.format(
                field=condition.field, symbol=condition.symbol, value=value)

    if not conditions_str:
        raise ValueError('No condition passed')

    return conditions_str[:-1]

def order_gen(conditions):
    ''' Create comma separated Order conditions

        Args:
            conditions: An iterator of OrderClauses.

        Returns:
            The values as a string
    '''
    return ', '.join(condition.field + ' ' + condition.order for condition in conditions)