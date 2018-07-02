from abc import *

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

        if self.validate(value):
            self._value = value

        return self

    def __get__(self, instance, owner):
        ''' Get the value of the column

            Returns:
                The column internal value.
        '''
        return self._value

    def validate(self, value):
        ''' Decide wheter a value that wants to be set is valid.

            Args:
                value: The value to be set internally
        
            Returns:
                A bool.
        '''
        return True

    ''' The value of the column itself
    '''
    _value = None

    ''' A dict with the types this column represents
        in various database systems.
    '''
    sql_type = {}

class Text(Column):
    ''' A basic Text column.
    '''
    sql_type = {'sqlite3': 'text'}

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError('Invalid value {}. Expected str.'.format(value))

        return True

class Bool(Column):
    ''' A boolean column. Implemented as a small int.
    '''
    sql_type = {'sqlite3': 'integer'}

    def validate(self, value):
        if value not in (0, 1, True, False):
            raise TypeError('Invalid value {}. Expected 1, 0 or bool.'.format(value))

        return True

class Integer(Column):
    pass

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
    
class Float(Column):
    pass

class Id(Column):
    ''' An auto-incrementing, unsigned integer. Used as a primary key.
    '''

    null = False
    primary = True
    auto_increment = True

    def __init__(self, name='id'):
        self.name = name