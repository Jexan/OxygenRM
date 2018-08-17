import warnings

from copy import deepcopy

from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.fields import *

import OxygenRM as O

class ModelHasNoPrimaryKeyError(Exception):
    def __init__(self, model, method):
        """ An error to be raised when an operation that requires a model with
            primary key is attempted, but the target model has no know related primary key.

            Args:
                model: The model whose method access triggered the exception.
                method: The infringing method where the exception was raised.
        """
        super.__init__('The model {} has no primary key column. Impossible to use method {}'.format(model.__name__, method))
        self.model = model
        self.method = method

class MetaModel(type):
    def __getattr__(cls, name):
        if not cls._set_up:
            cls._set_up_model()

        if getattr(QueryBuilder, name, None):
            return getattr(QueryBuilder.table(cls.table_name, cls), name)
        else:
            return None

class Model(metaclass=MetaModel):
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
        cls._pivot_classes = dict()
        
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
                if isinstance(value, Multiple):
                    cls._pivot_classes[attr] = value.pivot

            if isinstance(value, Id):
                primary_key = attr

        cls.primary_key = primary_key   
        cls._dumb = primary_key is None
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

    def _update_values(self, values):
        """ Update the internal model values.

            Args:
                values: A dict with the values of the model.
        """
        self._original_values = deepcopy(values)

        self._rel_queue = []
        self._field_values = {}

        for field, col in self._fields.items():
            field_val = values.get(field, None)

            self._field_values[field] = col.db_get(field_val)

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

    def __init__(self, creating_new=True, pivot_query=None, **values):
        """ The model base class. It allows ORM operations, and it's supossed 
            to be subclassed.

            Args:
                creating_new: Wheter the model is not in the database already.
                values: The values of the model to initialize.
        """
        if not self._set_up:
            self.__class__._set_up_model()

        self._creating_new = creating_new
        self._pivot_query = pivot_query
        self._pivots = {attr: None for attr in self._pivot_classes}

        self._update_values(values)

    @classmethod
    def set_up(cls):
        """ Force the set up of the class
        """
        if not cls._set_up:
            cls._set_up_model()

    @classmethod
    def relations(cls):
        """ A method to be run when the class is set up. Intendeed to init relations.
        """
        pass
    
    @classmethod
    def craft(cls, return_model=True, **values):
        """ Create a record in the database and save it. If the model has a primary key, return the model.

            Args:
                return_model: Wheter to return or not the model, if it has a primary key, after being saved.
                **values: The values of the model to be created.
            
            Return:
                True if the model has no primary key or the return_model is false.
                A self model of the stored class if not.
        """
        if not cls._set_up:
            cls._set_up_model()

        O.db.create(cls.table_name, **values)

        if return_model and not cls._dumb:
            return cls.where(cls.primary_key, '=', O.db.last_id()).first()
        else:
            return True

    @classmethod
    def find(cls, *indeces):
        """ Find the models with the specified primary key(s).

            Args:
                *indeces: An assortment of primary key values of the models to fetch.
            
            Returns:
                A model if the index is only one. A model collection if there's more than one index.

            Raises:
                ArgumentError: If no index value is passed.
                ModelHasNoPrimaryKeyError: If the model has no primary key.
        """
        if not cls._set_up:
            cls._set_up_model()

        indeces_amount = len(indeces)

        if not indeces_amount:
            raise ArgumentError('No indeces passed. Required at least one.') 
        if cls._dumb:
            raise ModelHasNoPrimaryKeyError(cls, 'find')

        result = cls.where_in(cls.primary_key, indeces)
        
        if indeces_amount == 1:
            return result.first()
        else:
            return result.get()

    @classmethod
    def destroy(cls, *indeces):
        """ Delete the models with the specified primary key(s).

            Args:
                *indeces: An assortment of primary key values of the models to delete.
            
            Returns:
                True

            Raises:
                ArgumentError: If no index value is passed.
                ModelHasNoPrimaryKeyError: If the model has no primary key.
        """
        if not cls._set_up:
            cls._set_up_model()

        if not len(indeces):
            raise ArgumentError('No indeces passed. Required at least one.') 
        if cls._dumb:
            raise ModelHasNoPrimaryKeyError(cls, 'destroy')

        cls.where_in(cls.primary_key, indeces).delete() 

        return True

    def get_primary(self):
        """ Get the primary key value of the model.

            Return:
                The primary key value of the model

            Raises:
                ModelHasNoPrimaryKeyError: If the model has no primary key.
        """
        if self._dumb:
            raise ModelHasNoPrimaryKeyError(cls, 'get_primary')

        return getattr(self, self.primary_key)
                                
    def save(self):
        """ Commit the current changes to the database.

            Return:
                self
        """
        values_for_db = {}
        for field_name, field_instance in self._fields.items():
            values_for_db[field_name] = field_instance.db_set(self, self._field_values[field_name])

        with O.db.transaction():            
            if self._creating_new:
                O.db.create(self.table_name, **values_for_db)
            else:
                if self._dumb:
                    self.__class__.where_many(self._convert_orig_values_to_conditions()).update(values_for_db)
                else:
                    self.__class__.where(self.primary_key, '=', self.get_primary()).update(values_for_db)

            for rel_function in self._rel_queue:
                rel_function()

            if not self._dumb:
                id_of_row = O.db.last_id() if self._creating_new else self.get_primary()

                for pivot in self._pivots.values():
                    if pivot is None:
                        continue

                    pivot.set_self_id(id_of_row)
                    pivot.save()

                row = QueryBuilder.table(self.table_name).where(self.primary_key, '=', id_of_row).first()
                self._update_values(dict(zip(row.keys(), tuple(row))))

            self._creating_new = False

        return self

    def delete(self):
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

    def being_created(self):
        """ Wheter the model is being created or not.

            Return:
                bool.
        """
        return self._creating_new

    @classmethod
    def pivots(self, rel):
        return self._pivot_classes[rel]

    @property
    def pivot(self):
        return self._pivot_query.add_model_id(self._pivot_query, self.get_primary()).first()
    
    def __eq__(self, other_model):
        return isinstance(other_model, Model) and self._field_values == other_model._field_values