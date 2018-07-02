from abc import *
from collections import namedtuple

ColumnData = namedtuple('ColumnData', ['type', 'nullable', 'default', 'primary', 'auto_increment'])

class Column(metaclass=ABCMeta):
    ''' The base class for defining a Model (or Migration)
        column.
    '''
    def __init__(self, **options):
        self.null    = options.get('null', False)
        self.primary = options.get('primary', False)
        self.auto_increment = options.get('auto_increment', False)

        self.default = options.get('default', None)
        self._value = self.default

    def __set__(self, instance, value):
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
            
    def __get__(self, instance, owner):
        ''' Get the value of the column

            Returns:
                The column internal value.
        '''
        return self.pretty_value() if self._value is not None else self.pretty_none()

    def get_data(self, driver):
        ''' Get the relevant data of the column to craft

            Args:
                driver: The driver of the database, as a string.

            Returns:
                A ColumnData tuple.
        '''
        return ColumnData(self.driver_type[driver], self.null, self.default, self.primary, self.auto_increment)

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

    ''' A dict with the types this column represents
        in various database systems.
    '''
    driver_type = {}

class Text(Column):
    ''' A basic Text column.
    '''
    driver_type = {'sqlite3': 'text'}

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError('Invalid value {}. Expected str.'.format(value))

class Bool(Column):
    ''' A boolean column. Implemented as a small int.

        The possible values to be setted, in a model, are bool, 1 or 0. 
    '''
    driver_type = {'sqlite3': 'integer'}

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

class Integer(Column):
    ''' A basic integer column.
    '''
    driver_type = {'sqlite3': 'integer'}

    def validate(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError('Invalid value {}. Expected an int.'.format(value))
    
class Float(Column):
    ''' A basic float column.
    '''
    driver_type = {'sqlite3': 'real'}

    def validate(self, value):
        if type(value) not in (int, float) or isinstance(value, bool):
            raise TypeError('Invalid value {}. Expected a float or int.'.format(value))

    def value_processor(self, value):
        return float(value)

class Id(Integer):
    ''' An auto-incrementing, unsigned integer. Used as a primary key.
    '''

    null = False
    primary = True
    auto_increment = True

    def __init__(self, name='id'):
        self.name = name

    def __set__(self, *_):
        raise AttributeError('Primary key can\'t be changed')

class Rel(Column):
    def __init__(self):
        pass

class Email(Column):
    def __init__(self):
        pass

class JSON(Column):
    def __init__(self):
        pass

class Date(Column):
    pass