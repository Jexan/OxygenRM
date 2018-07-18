import sqlite3
from abc import *
from collections import namedtuple

ColumnData = namedtuple('ColumnData', 'name type null default primary auto_increment unique check')

class Column(metaclass=ABCMeta):
    ''' The base class for defining a Model (or Migration)
        column.
    '''
    def __init__(self, **options):
        self.null    = options.get('null', False)
        self.primary = options.get('primary', False)
        self.unique  = options.get('unique', False)
        self.check   = options.get('check', None)
        self.auto_increment = options.get('auto_increment', False)

        self.default = options.get('default', None)
        self._value = self.default

    def get_data(self, name, driver):
        ''' Get the relevant data of the column to craft

            Args:
                name: The name of the column to add.
                driver: The driver of the database, as a string.

            Returns:
                A ColumnData tuple.
        '''
        return ColumnData(
            name, self.driver_type[driver], 
            self.null, self.default, 
            self.primary, self.auto_increment,
            self.unique, self.check)


    ''' A dict with the types this column represents
        in various database systems.
    '''
    driver_type = {}

class Text(Column):
    ''' A basic Text column.
    '''
    driver_type = {'sqlite3': 'text'}

class Bool(Column):
    ''' A boolean column. Implemented as a small int.

        The possible values to be setted, in a model, are bool, 1 or 0. 
    '''
    driver_type = {'sqlite3': 'integer'}

class Integer(Column):
    ''' A basic integer column.
    '''
    driver_type = {'sqlite3': 'integer'}
    
class Float(Column):
    ''' A basic float column.
    '''
    driver_type = {'sqlite3': 'real'}

class Id(Integer):
    ''' An auto-incrementing, unsigned integer. Used as a primary key.
    '''
    null = False
    primary = True
    auto_increment = True

    def __init__(self, name='id'):
        self.name = name