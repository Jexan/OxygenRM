from copy import deepcopy

from OxygenRM import internal_db as db
from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.columns import *

class MetaModel(type):
    def __getattr__(cls, name):
        if not cls._set_up:
            cls._set_model_db_data()

        if getattr(QueryBuilder, name, None):
            return getattr(QueryBuilder.table(cls.table_name, cls), name)
        else:
            raise AttributeError('The model {} has no attribute {}'.format(cls._self_name, name))

class Model(metaclass=MetaModel):
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

    ''' The model of this instance.
    '''
    _model = None
    
    ''' The values of the model per se.
    '''
    _db_values = {}

    ''' The original values of the model.
    '''
    _original_values = {}

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
        cls._set_up = True
        cls._self_name = cls.__name__

    def __getattr__(self, name):
        return self._db_values.get(name, None)

    def __setattr__(self, name, value):
        if name in self._db_fields:
            self._db_values[name] = value
        else:
            super().__setattr__(name, value)

    def _convert_orig_values_to_conditions(self):
        ''' Convert the internal _original_values
            to conditions, for a where condition.

            Yields:
                Tuples of the form (field, '=', value)
        '''
        for field, value in self._original_values.items():
            yield (field, '=', value)

    # PUBLIC
    ''' A string of the associated table name. Can be specified by
        subclasses. If not, it will be assumed to be the model name + s.
        @static
    '''
    table_name = ''

    def __init__(self, creating_new=True, **values):
        if not self._set_up:
            self.__class__._set_model_db_data()

        self._db_values = values
        self._creating_new = creating_new

        if not creating_new:
            self._original_values = deepcopy(values)

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
        if self._creating_new:
            db.create(self.table_name, **self._db_values)
        else:
            s1 = self.__class__.where_many(self._convert_orig_values_to_conditions())
            s2 = s1.update(self._db_values)

        return self

    # Converts the record to a value
    def to(self):
        pass
        
    # Converts the record to a dict
    def get_dict(self):
        pass
        