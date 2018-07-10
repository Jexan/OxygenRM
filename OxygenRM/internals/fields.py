import sqlite3
from abc import *
from collections import namedtuple

class Field(metaclass=ABCMeta):
    ''' The base class for defining a Model column.
    '''
    def __init__(self, null=False):
        self.null = null

    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            return self._value

    def set(self, value):
        ''' Validate the set value and change the internal 
            _value of the class 

            Raises: 
                Typerror: If property is not nullable and tried to be assigned a Null.
        '''
        if value is None :
            if not self.null:
                raise TypeError('Property not nullable')
            self._value = self.none_processor()
        else:
            self.validate(value)
            self._value = self.value_processor(value)

    def get(self):
        ''' Get the value of the column

            Returns:
                The column internal value.
        '''
        return self.pretty_value() if self._value is not None else self.pretty_none()

    def validate(self, value):
        ''' Decide wheter a non-null value that wants to be set is valid.

            Args:
                value: The value to be set internally
        
            Raises:
                TypeError: If the value is invalid.
        '''
        ...


    def value_processor(self, value):
        ''' Process the value given. Used when setting.

            Args:
                value: The value to be set internally
        
            Returns:
                A processed value
        '''
        return value

    def none_processor(self):
        ''' Returns a customized value to be setted if the value is none.

            Returns:
                A convenient value
        '''
        return self._value
    
    def pretty_value(self):
        ''' Filters the internal value, without changing it. Used when getting.

            Args:
                value: The value to be shown.
        
            Returns:
                A processed value
        '''
        return self._value

    def pretty_none(self):
        ''' Filters the internal value, if it's null. 
        
            Returns:
                A processed value
        '''
        return None

    ''' The value of the column itself
    '''
    _value = None

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

    # Return a boolean by itself, which is the most expected behaviour.
    # Or Null
    def pretty_value(self):
        return bool(self._value)

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

class Rel(Field):
    pass

class Has(Rel):
    ''' Define a 'has' relationship with another database table.

        Args:
            how_much: Either 'one' or 'many'
            model: The related model class
            on_other_col: The name of the related model column to use for the join.
                By default it will be the #{lower case model name}_id
            on_self_col: The name of the own column, for use in the join.
                By the default it will be the id column.
    '''
    def __init__(self, how_much, model, on_other_col=None, on_self_col='id'):
        pass

class BelongsTo(Rel):
    ''' Define a 'belongs to' relationship with another database table.

        Args:
            how_much: Either 'one' or 'many'
            model: The related model class
            on_other_col: The name of the related model column to use for the join.
                By default it will be the #{lower case model name}_id
            on_self_col: The name of the own column, for use in the join.
                By the default it will be the id column.
    '''
    def __init__(self, how_much, model, on_other_col='id', on_self_col=None):
        pass
    
class Multiple(Rel):
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
    def __init__(self, model, table=None, on_other_col='id', on_self_col=None):
        pass

class Multiple(Field):
    pass

class Email(Field):
    pass

class Password(Field):
    pass

class JSON(Field):
    pass

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
        'foreign': Rel
    }
}