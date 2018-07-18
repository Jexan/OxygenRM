from copy import deepcopy

from OxygenRM import internal_db as db
from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.fields import *

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

    ''' The model of this instance.
    '''
    _model = None

    ''' The original values of the model.
    '''
    _original_values = {}

    '''  The fields that are subclasses of Field class
    '''
    _fields = {}

    ''' Fields values
    '''
    _field_values = {}

    @classmethod
    def _set_model_db_data(cls):
        ''' Set up the model internals that allows communication
            with the database.

            Raises:
                ValueError: If the table doesn't exist.
        '''
        if not cls.table_name:
            cls.table_name = cls.__name__.lower() + 's'

        cls._fields = dict()
        cls._relations = dict()
        primary = None

        for attr, value in cls.__dict__.items():
            if isinstance(value, Field):
                if not isinstance(value, Relation):
                    cls._fields[attr] = value
                
                value._attr = attr

                row_prop = property(fget=value.get, fset=value.set) 
                setattr(cls, attr, row_prop)

            if isinstance(value, Relation):
                cls._relations[attr] = value

            if isinstance(value, Id):
                primary = attr

        cls.primary = primary

        cls._set_up = True
        cls._self_name = cls.__name__

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

    def get_primary(self):
        return getattr(self, self.primary)

    def __init__(self, creating_new=True, **values):
        if not self._set_up:
            self.__class__._set_model_db_data()

        self._creating_new = creating_new

        if not creating_new:
            self._original_values = deepcopy(values)

        self._rel_queue = []
        self._field_values = {}
        for field in self._fields:
            field_val = None

            if not creating_new:
                field_val = values.get(field, None)

            self._field_values[field] = field_val

    # Creates a new record and saves it right away
    @staticmethod
    def create():
        pass
                                
    def save(self):
        if self._creating_new:
            db.create(self.table_name, **self._field_values)
        else:
            self.__class__.where_many(self._convert_orig_values_to_conditions()).update(self._field_values)

        for rel_function in self._rel_queue:
            rel_function()

        self._creating_new = False
        return self

    def destroy(self):
        if self._creating_new:
            raise Exception('Can not destroy model that doesn\'t exist in the database')

        self.__class__.where_many(self._convert_orig_values_to_conditions()).delete()

        return True

    def to_dict(self):
        return self._field_values

    def __eq__(self, other_model):
        return self._field_values == self._field_values