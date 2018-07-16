import sqlite3
import json
import abc

from collections import namedtuple

from OxygenRM.internals.QueryBuilder import QueryBuilder

class Field(metaclass=abc.ABCMeta):
    _attr = None

    _valid_types = []

    ''' The base class for defining a Model column.
    '''
    def __init__(self, null=False):
        self.null = null

    def get(self, model):
        ''' The getter for model fields.

            Args:
                model: The model instance. 

            Returns:
                The value of the model
        '''
        return self.value_formatter(model._field_values[self._attr])

    def set(self, model, value):
        ''' Validate and set the the value of the column.

            Args:
                model: The model instance.
                value: The value to be assigned.
        '''
        self.validate(value)
        
        model._field_values[self._attr] = self.value_processor(value)

    def validate(self, value):
        ''' Decide wheter a non-null value that wants to be set is valid.

            Args:
                value: The value to be set internally
        
            Raises:
                TypeError: If the value is invalid.
        '''
        return True

    def value_processor(self, value):
        ''' Transform the value given. Used in the setter.

            Args:
                value: The value to be processed
        
            Returns:
                A processed value
        '''
        return value

    def value_formatter(self, value):
        ''' Format the value given. Used in the getter.

            Args:
                value: The value to be processed
        
            Returns:
                A processed value
        '''
        return value

class Text(Field):
    ''' A basic Text column.
    '''
    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError('Invalid value {}. Expected str.'.format(value))

class Bool(Field):
    ''' A boolean column. Implemented as a small int.

        The possible values to be setted, in a model, are bool, 1 or 0. 
    '''
    def validate(self, value):
        if value not in (0, 1, True, False):
            raise TypeError('Invalid value {}. Expected 1, 0 or bool.'.format(value))

    # We want to keep the value internally as a 1 or 0.
    def value_processor(self, value):
        return 1 if value else 0

class Integer(Field):
    ''' A basic integer column.
    '''
    def validate(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError('Invalid value {}. Expected an int.'.format(value))
    
class Float(Field):
    ''' A basic float column.
    '''
    def validate(self, value):
        if type(value) not in (int, float) or isinstance(value, bool):
            raise TypeError('Invalid value {}. Expected a float or int.'.format(value))

    def value_processor(self, value):
        return float(value)

class Id(Integer):
    ''' An auto-incrementing, unsigned integer. Used as a primary key.
    '''
    def __init__(self):
        self.null = False

class Date(Field):
    pass

class Datetime(Field):
    pass

class Has(Field):
    ''' Define a 'has' relationship with another database table.

        Args:
            how_much: Either 'one' or 'many'
            model: The related model class
            on_other_col: The name of the related model column to use for the join.
                By default it will be the #{lower case model name}_id
            on_self_col: The name of the own column, for use in the join.
                By the default it will be the id column.
    '''
    def __init__(self, how_much, model, on_other_col='', on_self_col='id'):
        if how_much not in ('many', 'one'):
            raise ValueError('Invalid relation {}. Expected "many" or "one"'.format(how_much))

        self.model = model
        self.how_much = how_much

        self.on_self_col = on_self_col if not on_self_col else 'id' 
        self.on_other_col = on_other_col  

    def get(self, starting_model):
        if not self.on_other_col:
            self.on_other_col = starting_model.__class__.__name__.lower() + '_id'
        
        qb = QueryBuilder(self.model.table_name, self.model).where(self.on_other_col, '=', getattr(starting_model, self.on_self_col))
        
        if self.how_much == 'many':
            return qb.get()
        else:
            return qb.first()

    def set(self, *_):
        raise NotImplementedError('Setting relationship models not yet allowed')

class BelongsTo(Field):
    ''' Define a 'belongs to' relationship with another database table.

        Args:
            how_much: Either 'one' or 'many'
            model: The related model class
            on_other_col: The name of the related model column to use for the join.
                By default it will be the #{lower case model name}_id
            on_self_col: The name of the own column, for use in the join.
                By the default it will be the id column.
    '''
    def __init__(self, how_much, model, on_other_col='id', on_self_col=''):
        if how_much not in ('many', 'one'):
            raise ValueError('Invalid relation {}. Expected "many" or "one"'.format(how_much))

        self.model = model
        self.how_much = how_much

        self.on_self_col = on_self_col 
        self.on_other_col = on_other_col  

    def get(self, starting_model):
        if not self.on_self_col:
            self.on_self_col = starting_model.__class__.__name__.tolower() + '_id'
        
        qb = QueryBuilder(self.model.table_name, self.model).where(self.on_other_col, '=', getattr(starting_model, self.on_self_col))
        
        if self.how_much == 'many':
            return qb.get()
        else:
            return qb.limit(1).get().first_or_none()

    def set(self):
        raise NotImplementedError('Setting relationship models not yet allowed')
    
class Multiple(Field):
    ''' Define a 'many to many' relationship with another database table.

        Args:
            model: The related model class
            table: The name of the table to use for the join.
                By default, it will be the tables names, sorted alphabetically,
                with an underscore as a separation.
            on_other_id: The name of the related model column to use for the join.
                By default it will be the #{lower case model name}_id
            on_self: The name of the own column, for use in the join.
                By the default it will be the id column.
    '''
    def __init__(self, model, table=None, on_other_col='id', 
            on_self_col='id', on_other_middle_col=None, on_self_middle_col=None):
        self.model = model
        self.table = table
        self.on_other_col = on_other_col
        self.on_self_col = on_self_col
        self.on_self_middle_col = on_self_middle_col
        
        if not on_other_middle_col:
            self.on_other_middle_col = model.__name__.lower() + '_id'
        else:
            self.on_other_middle_col = on_other_middle_col
            
        self._setted_up = False

    def get(self, current_model):
        if not self._setted_up:
            self._set_up()

        qb = QueryBuilder.table(self.model.table_name, self.model)
        qb.where(current_model.table_name + '.' + self.on_self_col, '=', self.table + '.' + self.on_self_middle_col)
        qb.where(self.model.table_name + '.' + self.on_other_col, '=', self.table + '.' + self.on_other_middle_col)

        print(qb.get_sql())

    def _set_up(self, parting_model):
        if not self.table:
            self.table = '_'.join(sorted((self.model.table_name, current_model.table_name)))

        if not self.on_self_middle_col is None:
            self.on_self_middle_col = parting_model.__class__.__name__.tolower() + '_id'  

        self._setted_up = True

class Email(Field):
    pass

class Password(Field):
    pass

class JSON(Field):
    ''' A field for dealing with JSON strings boilerplate.
    '''

    class JSONableDict(dict):
        ''' A dict that makes easier the conversion to JSON.
        '''    
        def __str__(self):
            return self.to_json()

        def to_json(self, *args):
            return json.dumps(self, *args)

        def __conform__(self, protocol):
            if protocol is sqlite3.PrepareProtocol:
                return str(self)

    def get(self, model):
        original_val = super().get(model)
        
        if not isinstance(original_val, dict):
            super().set(model, self.JSONableDict())
            return super().get(model)
        else:
            return original_val

    def validate(self, value):
        if not isinstance(value, (dict, str)):
            raise TypeError('Invalid value {}. Expected a dict or string.'.format(value))

    def value_processor(self, value):
        return self.JSONableDict(value)

class XML(Field):
    pass

class CSV(Field):
    pass

class Pickle(Field):
    pass

field_types = {
    'sqlite3': {
        'text': Text,
        
        'real': Float,
        
        'integer': Integer,
        'int': Integer,

        'boolean': Bool,

        'datetime': Datetime,
        'date': Date,

        'json': JSON,
        'xml': XML,
        'csv': CSV,
    }
}