from collections import defaultdict
from OxygenRM.internals.SQL_builders import *

class QueryBuilder:
    ''' A class for building and chaining queries.
    '''
    def __init__(self, table_name):
        self._in_wait = defaultdict(list)
        self._in_wait['table_name'] = table_name

    @classmethod
    def table(cls, table_name):
        ''' Prepare the table to edit.

            Args:
                table_name: The table to edit

            Returns:
                A QueryBuilder instance
        '''
        return cls(table_name)

    def select(self, *fields):
        ''' Specify which fields will be selected. 

            Args:
                *fields: The fields as string that will be used.
        ''' 
        self._in_wait['select'] = True
        self._in_wait['select_fields'] = fields

        return self

    def where(self, field, symbol, value):
        ''' Add an AND WHERE condition to the prepared query.

            Args: 
                field: The column name.
                symbol: The operator.
                value: The value to compare the rows.

            Returns:
                self
        '''
        self._in_wait['where_cond'].append(ConditionClause('AND', field, symbol, value))
        return self

    def or_where(self, field, symbol, value):
        ''' Add an OR WHERE condition to the prepared query.

            Args: 
                field: The column name.
                symbol: The operator.
                value: The value to compare the rows.

            Returns:
                self
        '''
        self._in_wait['where_cond'].append(ConditionClause('OR', field, symbol, value))
        return self

    def group_by(self, field, order='ASC'):
        ''' Add a GROUP BY to the prepared query.

            Args:
                fields: The field to group by.
                order: Whether to order it ASC or DESC 

            Returns:
                self
        '''
        self._in_wait['group_by'].append(OrderClause(field, order))
        return self

    def having(self, field, symbol, value):
        ''' Add an AND HAVING condition to the prepared query.

            Args: 
                field: The column name.
                symbol: The operator.
                value: The value to compare the rows.

            Returns:
                self
        '''
        self._in_wait['having'] = ConditionClause('AND', field, symbol, value)
        return self

    def order_by(self, field, order='ASC'):
        ''' Add an ORDER BY to the prepared query.

            Args:
                field: The field to order by.
                order: Either ASC or DESC

            Returns:
                self
        '''
        self._in_wait['order_by'].append(OrderClause(field, order))
        return self

    def limit(self, n):
        ''' Add a LIMIT to the prepared query.

            Args:
                n: The number of fields to take.

            Returns:
                self
        '''
        self._in_wait['limit'] = n
        return self

    def offset(self, n):
        ''' Add an OFFSET to the prepared query.

            Args:
                n: The number of fields to offset.

            Returns:
                self
        '''
        self._in_wait['offset'] = n
        return self

    def distinct(self, distinct=True):
        ''' Add a DISTINCT clause to the prepared query

            Args:
                distinct: A bool indicating if you want to add the distinct clause.

            Returns: 
                self
        '''
        self._in_wait['distinct'] = distinct
        return self

    def join(self, table):
        ''' Add an INNER JOIN to the prepared query.

            Args: 
                table: The table to join the current one.

            Returns:
                self
        '''
        self._in_wait['join_type'] = 'INNER'
        self._in_wait['join_with'] = table
        return self

    def outer_join(self, table):
        ''' Add an OUTER JOIN to the prepared query.

            Args: 
                table: The table to join the current one.

            Returns:
                self
        '''
        self._in_wait['join_type'] = 'OUTER'
        self._in_wait['join_with'] = table
        return self

    def using(self, fields):
        ''' Add a USING for a JOIN.

            Args: 
                using: The columns to compare and outer_join.

            Returns:
                self
        '''
        self._in_wait['using'] = fields

        return self

    def cross_join(self, table):
        ''' Add a CROSS JOIN to the prepared query.

            Args: 
                table: The table to join the current one.

            Returns:
                self
        '''
        self._in_wait['join_type'] = 'CROSS'
        self._in_wait['join_with'] = table 
        return self

    def on(self, field, symbol, value):
        ''' Add an ON AND condtion to the prepared query.

            Args: 
                field: The column name.
                symbol: The operator.
                value: The column to compare.

            Returns:
                self
        '''
        self._in_wait['join_on'].append(ConditionClause('AND', field, symbol, value))

        return self

    def or_on(self, field, symbol, value):
        ''' Add a ON OR condtion to the prepared query.

            Args: 
                field: The column name.
                symbol: The operator.
                value: The column to compare.

            Returns:
                self
        '''
        self._in_wait['join_on'].append(ConditionClause('OR', field, symbol, value))

        return self

    def get(self):
        '''  Query the database with the prepared conditions.

            Returns:
                An iterator
        '''
        clauses = defaultdict(str)
        options = self._in_wait

        if options['join_type']:
            clauses['table_to_select'] = join_clause(
                    options['join_type'], 
                    options['table_name'], 
                    options['join_with'], 
                    options['join_on'],
                    options['using']
                )
        else: 
            clauses['table_to_select'] = options['table_name']

        query = select_clause(clauses['table_to_select'], *options['select_fields'], distinct=options['distinct'])

        if options['where_cond']:
            query += where_clause(options['where_cond'])
        
        if options['group_by']:
            query += group_by_clause(options['group_by'], options['having'])
            
        if options['order_by']:
            query += order_by_clause(options['order_by'])

        if options['limit']:
            query += limit_clause(options['limit'], options['offset'])

        return query

    def __iter__(self):
        ''' An alias for self.get. 
        '''
        return self

    ''' A dict indicating which operation is pending.
    '''
    _in_wait = defaultdict(list)