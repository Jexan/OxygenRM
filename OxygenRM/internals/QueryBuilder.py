from collections import defaultdict, ChainMap
from itertools import chain
from copy import deepcopy

from OxygenRM.internals.SQL_builders import *
from OxygenRM.internals.ModelContainer import ModelContainer

import OxygenRM as O

class QueryBuilder:
    """ A class for building and chaining queries.
    """
    _debug = False

    def __init__(self, table_name, model=None):
        self._in_wait = defaultdict(list)
        self._in_wait['table_name'] = table_name

        self._model = model

    def reset(self):
        """ Reset the QueryBuilder prepared conditions.
        """
        table_name = self._in_wait['table_name']

        self._in_wait = defaultdict(list)
        self._in_wait['table_name'] = table_name

        return self

    @staticmethod
    def table(table_name, model=None):
        """ Prepare the table to edit.

            Args:
                table_name: The table to edit

            Returns:
                A QueryBuilder instance
        """
        return QueryBuilder(table_name, model)

    @staticmethod
    def raw(sql, values=(), model=None, save=True):
        """ Run the raw sql and return the result wrapped.

            Args:
                sql: The query as a string.
                values: An iterator with the values, if it
                model: The model to wrap the result into.
                save: Whether the operation should be saved.

            Returns:
                A model container.
        """
        if save:
            result = lambda: O.db.execute(sql, values)
        else:
            result = lambda: O.db.execute_without_saving(sql, values)
        
        if model:
            return ModelContainer(result, model)
        else:
            return result()

    def select(self, *fields):
        """ Specify which fields will be selected. 

            Args:
                *fields: The fields as string that will be used.
        """ 
        self._in_wait['select'] = True
        self._in_wait['select_fields'] = fields

        return self

    def where(self, field, symbol, value):
        """ Add an AND WHERE condition to the prepared query.

            Args: 
                field: The column name.
                symbol: The operator.
                value: The value to compare the rows.

            Returns:
                self
        """
        self._in_wait['where_cond'].append(ConditionClause('AND', field, symbol, value))
        return self

    def or_where(self, field, symbol, value):
        """ Add an OR WHERE condition to the prepared query.

            Args: 
                field: The column name.
                symbol: The operator.
                value: The value to compare the rows.

            Returns:
                self
        """
        self._in_wait['where_cond'].append(ConditionClause('OR', field, symbol, value))
        return self

    def where_in(self, field, values):
        """ Add an AND field IN values condition to the prepared query.

            Args: 
                field: The column name.
                values: An iterator with the values to check

            Returns:
                self
        """
        self._in_wait['where_cond'].append(ConditionClause('AND', field, 'IN', tuple(values)))
        return self    

    def where_not_in(self, field, values):
        """ Add an AND field NOT IN values condition to the prepared query.

            Args: 
                field: The column name.
                values: An iterator with the values to check

            Returns:
                self
        """
        self._in_wait['where_cond'].append(ConditionClause('AND', field, 'NOT IN', tuple(values)))
        return self

    def where_null(self, field):
        """ Add a condition to get records where field is NULL

            Args:
                field: The column name.

            Returns:
                self
        """
        self._in_wait['where_cond'].append(ConditionClause('AND', field, 'IS', None))
        return self

    def where_not_null(self, field):
        """ Add a condition to get records where field is NOT NULL

            Args:
                field: The column name.

            Returns:
                self
        """
        self._in_wait['where_cond'].append(ConditionClause('AND', field, 'IS NOT', None))
        return self

    def where_many(self, conditions):
        """ Add multiple AND WHERE condition to the prepared query.

            Args: 
                conditions: An iterator that yields lists/tuples, such that:
                    0: The column name.
                    1: The operator.
                    2: The value to compare the rows.

            Returns:
                self
        """
        condition_packer = lambda cond: ConditionClause('AND', *cond)

        self._in_wait['where_cond'].extend(map(condition_packer, conditions))
        return self    

    def or_where_many(self, conditions):
        """ Add multiple OR WHERE condition to the prepared query.

            Args: 
                conditions: An iterator that yields lists/tuples, such that:
                    0: The column name.
                    1: The operator.
                    2: The value to compare the rows.

            Returns:
                self
        """
        condition_packer = lambda cond: ConditionClause('OR', *cond)

        self._in_wait['where_cond'].extend(map(condition_packer, conditions))
        return self    

    def count(self):
        """ Destructive query to get the number of records that fullfills the current conditions.

            Returns:
                An int with the number of rows.
        """
        self.select('count(*)')

        return next(O.db.execute_without_saving(self.get_sql()))[0]

    def max(self, col):
        """ Return the max value of the specified table's column.

            Args:
                col: The column name.

            Returns:
                The max value.
        """
        self.select('max({})'.format(col))

        return next(O.db.execute_without_saving(self.get_sql()))[0]        

    def min(self, col):
        """ Return the minimun value of the specified table's column.

            Args:
                col: The column name.

            Returns:
                The min value.
        """
        self.select('min({})'.format(col))
        return next(O.db.execute_without_saving(self.get_sql()))[0]

    def sum(self, col):
        """ Return the sum value of the specified table's column.

            Args:
                col: The column name.

            Returns:
                The result of the sum.
        """
        self.select('sum({})'.format(col))

        return next(O.db.execute_without_saving(self.get_sql()))[0]        

    def group_by(self, field, order='ASC'):
        """ Add a GROUP BY to the prepared query.

            Args:
                fields: The field to group by.
                order: Whether to order it ASC or DESC 

            Returns:
                self
        """
        self._in_wait['group_by'].append(OrderClause(field, order))
        return self

    def having(self, field, symbol, value):
        """ Add an AND HAVING condition to the prepared query.

            Args: 
                field: The column name.
                symbol: The operator.
                value: The value to compare the rows.

            Returns:
                self
        """
        self._in_wait['having'] = ConditionClause('AND', field, symbol, value)
        return self

    def order_by(self, field, order='ASC'):
        """ Add an ORDER BY to the prepared query.

            Args:
                field: The field to order by.
                order: Either ASC or DESC

            Returns:
                self
        """
        self._in_wait['order_by'].append(OrderClause(field, order))
        return self

    def limit(self, n):
        """ Add a LIMIT to the prepared query.

            Args:
                n: The number of fields to take.

            Returns:
                self
        """
        self._in_wait['limit'] = n
        return self

    def offset(self, n):
        """ Add an OFFSET to the prepared query.

            Args:
                n: The number of fields to offset.

            Returns:
                self
        """
        self._in_wait['offset'] = n
        return self

    def distinct(self, distinct=True):
        """ Add a DISTINCT clause to the prepared query

            Args:
                distinct: A bool indicating if you want to add the distinct clause.

            Returns: 
                self
        """
        self._in_wait['distinct'] = distinct
        return self

    def join(self, table):
        """ Add an INNER JOIN to the prepared query.

            Args: 
                table: The table to join the current one.

            Returns:
                self
        """
        self._in_wait['join_type'] = 'INNER'
        self._in_wait['join_with'] = table
        return self

    def outer_join(self, table):
        """ Add an OUTER JOIN to the prepared query.

            Args: 
                table: The table to join the current one.

            Returns:
                self
        """
        self._in_wait['join_type'] = 'OUTER'
        self._in_wait['join_with'] = table
        return self

    def using(self, fields):
        """ Add a USING for a JOIN.

            Args: 
                using: The columns to compare and outer_join.

            Returns:
                self
        """
        self._in_wait['using'] = fields

        return self

    def cross_join(self, table):
        """ Add a CROSS JOIN to the prepared query.

            Args: 
                table: The table to join the current one.

            Returns:
                self
        """
        self._in_wait['join_type'] = 'CROSS'
        self._in_wait['join_with'] = table 
        return self

    def on(self, field, symbol, value):
        """ Add an ON AND condtion to the prepared query.

            Args: 
                field: The column name.
                symbol: The operator.
                value: The column to compare.

            Returns:
                self
        """
        self._in_wait['join_on'].append(ConditionClause('AND', field, symbol, value))

        return self

    def or_on(self, field, symbol, value):
        """ Add a ON OR condtion to the prepared query.

            Args: 
                field: The column name.
                symbol: The operator.
                value: The column to compare.

            Returns:
                self
        """
        self._in_wait['join_on'].append(ConditionClause('OR', field, symbol, value))

        return self

    def truncate(self):
        """ Delete the entire table records.
        """
        O.db.truncate(self._in_wait['table_name'])

    def _get_options(self):
        """ Deals with the options if the table has an alias.

            Returns:
                A defaultdict(list) with the fixed conditions.
        """
        options = self._in_wait
        if not ' ' in options['table_name']:
            return options
        else:
            alias = options['table_name'].split(' ')[1]
        
        new_options = deepcopy(options)
        new_options['select_fields'] = (alias + '.' + select_field if '.' not in select_field else select_field for select_field in options['select_fields'] )

        for field in ('where_cond', 'group_by', 'having', 'group_by'):
            if options[field]:
                new_options[field] = tuple(option._replace(field=alias + '.' + option.field) if '.' not in option.field else option for option in options[field])

        return new_options

    def get_sql(self):
        """  Craft a get sql command.

            Returns:
                A query string
        """
        options = self._get_options()

        if options['join_type']:
            table_to_select = join_clause(
                    options['join_type'], 
                    options['table_name'], 
                    options['join_with'], 
                    options['join_on'],
                    options['using']
                )
        else: 
            table_to_select = options['table_name']

        query = select_clause(table_to_select, *options['select_fields'], distinct=options['distinct'])

        if options['where_cond']:
            query += ' ' + where_clause(options['where_cond'])
        
        if options['group_by']:
            query += ' ' + group_by_clause(options['group_by'], options['having'])
            
        if options['order_by']:
            query += ' ' + order_by_clause(options['order_by'])

        if options['limit']:
            query += ' ' + limit_clause(options['limit'], options['offset'])

        if self._debug:
            print(query)

        return query

    def delete_sql(self):
        """  Craft a delete sql command.

            Returns:
                A query string
        """
        return delete_clause(self._in_wait['table_name'].split(' ')[0], self._in_wait['where_cond'])

    def update_sql(self, values):
        """ Craft a update sql command.

            Args:
                values: A dict with the keys as the fields and the values as the values to be set.
        """
        return update_clause(self._in_wait['table_name'], values.keys(), self._in_wait['where_cond'])
    
    def delete(self):
        """  Delete records according to the chained methods.
        """
        O.db.execute(self.delete_sql(), tuple(extract_values(self._in_wait['where_cond'])))

    def update(self, values={}, **kwvalues):
        """ Update records in the database according with the given values.

            Args:
                values: A dict with the keys as the fields and the values as the values to be set.
                **kwvalues: The values to update
        """
        values = ChainMap(values, kwvalues)
        values_to_prepare = chain(values.values(), extract_values(self._in_wait['where_cond']))

        O.db.execute(self.update_sql(values), tuple(values_to_prepare))

    def get(self):
        """  Get the specified records.

            Returns:
                The rows obtained.
        """
        query = self.get_sql()
        options = self._in_wait

        values_to_prepare = extract_values(options['where_cond'])

        if options['having']:
            values_to_prepare = chain(values_to_prepare, options['having'].value)

        values_to_prepare = tuple(values_to_prepare)
        result = lambda: O.db.execute_without_saving(query, values_to_prepare)
        return self._wrap_in_model(result)

    def all(self):
        """ Gets all the records.

            Returns:
                The queried rows.
        """
        result = lambda: O.db.all(self._in_wait['table_name'], self._in_wait['select_fields']) 
        return self._wrap_in_model(result)

    def first(self):
        """ Get the first record of the specified query.

            Returns:
                The first record specified.
        """
        result = self.limit(1).get()
        if self._model:
            return result.first()
        else:
            return result.fetchone()

    def first_or_fail(self):
        """ Get the first record of the specified record or fail if None returned.
        """
        value = self.first() 
        if value is None:
            raise ValueError('No record exists')
        else:
            return value

    def __iter__(self):
        """ Alias fot get.

            Returns:
                The rows obtained.
        """
        return self.get()

    def _wrap_in_model(self, result):
        """ Wrap the results of the query cursor in 
            a ModelContainer, if a model is available.

            Args:
                result: An iterator with the rows

            Return:
                An iterator with the rows
        """
        if not self._model:
            return result()
        else:
            return ModelContainer(result, self._model, relations=self._in_wait['relations'])

    """ A dict indicating which operation is pending.
    """
    _in_wait = defaultdict(list)

    def has(self, rel):
        """ Add the condition that the record has at least one related record of the specified relation.

            Args:
                rel: A string with the relation to check.

            Return:
                self
        """
        self._in_wait['table_name'] = self._model.table_name + ' oxygent'
        left_side, right_side, other_table = self._model.get_existence_conditions(rel)
        return self.select('oxygent.*').join(other_table).on(left_side, '=', right_side)

    def doesnt_have(self, rel):
        """ Add the condition that the record has no related record of the specified relation.

            Args:
                rel: A string with the relation to check.

            Return:
                self
        """
        self._in_wait['table_name'] = self._model.table_name + ' oxygent'
        left_side, right_side, other_table = self._model.get_existence_conditions(rel)
        return self.select('oxygent.*').join(other_table).on(left_side, '!=', right_side).or_on(left_side, 'IS', 'NULL')

    def with_relations(self, *relations):
        """ Make sure that the specified relations are loaded early, to avoid the
            N + 1 queries problem.

            Args:
                *relations: String names of relations to be loaded.
            
            Returns:
                self.
        """
        model = self._model
        relations_builders = {}

        if not model:
            raise ValueError('Cannot fetch relations of no model')

        for relation in relations:
            rel_instance = model.get_relation(relation)
            relations_builders[relation] = rel_instance.eager_load_builder()

        self._in_wait['relations'] = relations_builders
        return self

def extract_values(conditions):
    """ Get every value of the passed conditions.

        Args:
            conditions: An iterator of ConditionClause.

        Yields:
            The values of every condition.
    """
    for condition in conditions:
        if 'IN' in condition.symbol:
            for value in condition.value:
                yield value
        else:
            yield condition.value