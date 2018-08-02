from copy import deepcopy

from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.fields import *

import OxygenRM as O

class MetaModel(type):
    def __getattr__(cls, name):
        if not cls._set_up:
            cls._set_up_model()

        if getattr(QueryBuilder, name, None):
            return getattr(QueryBuilder.table(cls.table_name, cls), name)
        else:
            return None

class Model(metaclass=MetaModel):
    """ The model base class. It allows ORM operations, and
        it's supossed to be subclassed.
    """

    # PRIVATE
    """ The original field values of the model.
    """
    _original_values = {}

    """ Internal values of the record fields
    """
    _field_values = {}

    """ A tracker of this model associated relations
        @static
    """
    _relations = {}

    """ A tracker of this model associated fields
        @static
    """
    _fields = {}

    """ The name of the table. Used in the metaclass
        @static
    """
    _self_name = ''

    """ Bool of whether the model internal data is ready
        @static
    """
    _set_up = False

    @classmethod
    def _set_up_model(cls):
        """ Set up the internals and relations of the Model
        """
        if not cls.table_name:
            cls.table_name = cls.__name__.lower() + 's'

        cls.relations()

        cls._fields = dict()
        cls._relations = dict()
        
        primary_key = None
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
                primary_key = attr

        cls.primary_key = primary_key

        cls._set_up = True
        cls._self_name = cls.__name__

    def _convert_orig_values_to_conditions(self):
        """ Convert the internal _original_values
            to conditions, for a where condition.

            Yields:
                Tuples of the form (field, '=', value)
        """
        for field, value in self._original_values.items():
            yield (field, '=', value)

    # PUBLIC
    
    """ A string of the associated table name. Can be specified by
        subclasses. If not, it will be assumed to be the model name + s.
        @static
    """
    table_name = ''

    """ The table primary key name.
        @static
    """
    primary_key = ''

    def __init__(self, creating_new=True, **values):
        if not self._set_up:
            self.__class__._set_up_model()

        self._creating_new = creating_new

        if not creating_new:
            self._original_values = deepcopy(values)

        self._rel_queue = []
        self._field_values = {}
        for field in self._fields:
            field_val = values.get(field, None)

            self._field_values[field] = field_val

    @classmethod
    def relations(cls):
        pass
    
    @classmethod
    def craft(cls, return_model=True, **values):
        """ Create a record in the database, save it and return it
        """
        if not cls._set_up:
            cls._set_up_model()

        O.db.create(cls.table_name, **values)

        if return_model and cls.primary_key:
            return cls.where(cls.primary_key, '=', O.db.last_id()).first()
        else:
            return True

    def get_primary(self):
        """ Get the primary key value of the model.

            Return:
                The primary key value of the model
        """
        return getattr(self, self.primary_key)
                                
    def save(self):
        """ Commit the current changes to the database.

            Return:
                self
        """
        if self._creating_new:
            O.db.create(self.table_name, **self._field_values)
        else:
            self.__class__.where_many(self._convert_orig_values_to_conditions()).update(self._field_values)

        for rel_function in self._rel_queue:
            rel_function()

        self._creating_new = False
        return self

    def destroy(self):
        """ Remove the working model from the database.
        """
        if self._creating_new:
            raise Exception('Can not destroy model that doesn\'t exist in the database')

        self.__class__.where_many(self._convert_orig_values_to_conditions()).delete()

        return True

    def to_dict(self):
        """ Fetch a dict with the model values.

            Return:
                A dict with the field names and values.
        """
        return self._field_values

    @classmethod
    def set_up(cls):
        if not cls._set_up:
            cls._set_up_model()

    def __eq__(self, other_model):
        return isinstance(other_model, Model) and self._field_values == other_model._field_values