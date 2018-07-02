from abc import *

class Column(metaclass=ABCMeta):
    ''' The base class for defining a Model (or Migration)
        column.
    '''
    def __init__(self, **options):
        self.default = options.get('default', None)
        self.null    = options.get('null', False)
        self.primary = options.get('primary', False)
        self.auto_increment = options.get('auto_increment', False)

        self._value = self.default

    def __set__(self, instance, value):
        ''' Validate the set value and change the internal 
            _value of the class 
        '''
        if not isinstance(value, self.value_class):
            raise TypeError('Property value cannot be of type: {}. \'{}\' expected'.format(
                type(value), self.value_class.__name__))

        if self.validate(value):
            self._value = value

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

    ''' The class of the value.
    '''
    value_class = None

class Text(Column):
    ''' A basic Text column.
    '''

    ''' A dict with the types this column represents
        in various database systems.
    '''
    sql_type = {'sqlite3': 'text'}

    value_class = str

class Bool(Column):
    pass

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