from collections import namedtuple

from OxygenRM import internal_db as db
from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.columns import *

class Model(QueryBuilder):
    ''' The model base class. It allows ORM operations, and
        it's supossed to be subclassed.
    '''

    # INTERNAL
    ''' Bool of whether the model internal data is ready
        @static
    '''
    _set_up = False

    ''' A dict with the format field name: field type
        @static
    '''
    _db_fields = None

    ''' A namedtuple class constructor, to make model editing easier.
        @static
    '''
    _Row = None

    ''' The model of this instance.
    '''
    _model = None
    
    @classmethod
    def _set_model_db_data(cls):
        ''' Set up the model internals that allows communication
            with the database.

            Raises:
                ValueError: If the table doesn't exist.
        '''
        if not cls.table_name:
            cls.table_name = cls.__name__.lower() + 's'

        if not db.table_exists(cls.table_name):
            raise ValueError('The table {} does not exist.'.format(
                cls.table_name))

        cls._db_fields = db.table_fields_types(cls.table_name)
        cls._Row = namedtuple(cls.__name__, list(cls._db_fields.keys()))
        cls._set_up = True

    # PUBLIC
    ''' A string of the associated table name. Can be specified by
        subclasses. If not, it will be assumed to be the model name + s.
        @static
    '''
    table_name = ''

    def __init__(self, **values):
        if not self._set_up:
            self.__class__._set_model_db_data()

    # Creates a new record and saves it right away
    @staticmethod
    def create():
        pass
        
    # Returns a row that matches the record
    @staticmethod
    def find():
        pass
                                
    # Saves all changes
    def save(self):
        pass
         
    # Converts the record to a value
    def to(self):
        pass
        
    # Converts the record to a dict
    def get_dict(self):
        pass
        