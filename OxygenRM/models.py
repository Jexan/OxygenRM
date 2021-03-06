from copy import deepcopy

from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.fields import *

import OxygenRM as O

class ModelHasNoIdError(Exception):
    def __init__(self, model, method):
        """ An error to be raised when an operation that requires a model with
            an Id is attempted, but the target model has no configured Id.

            Args:
                model: The model whose method access triggered the exception.
                method: The infringing method where the exception was raised.
        """
        super.__init__('The model {} has no index column. Impossible to use method {}'.format(model.__name__, method))
        self.model = model
        self.method = method

class MetaModel(type):
    """ The metaclass that allows the model subclasses to construct queries, when
        accessing static methods. 
    """
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
        
        id_key = None
        for attr, value in cls.__dict__.items():
            # Checks every class attribute to find the model DB fields
            if isinstance(value, Field):
                if not isinstance(value, Relation):
                    cls._fields[attr] = value
                
                value._attr = attr

                row_prop = property(fget=value.get, fset=value.set) 
                setattr(cls, attr, row_prop)

            # Relations are set up differently than most fields
            if isinstance(value, Relation):
                cls._relations[attr] = value
                value.parting_model = cls

                if isinstance(value, Multiple):
                    cls._pivot_classes[attr] = value.pivot

            # Set Up the Id
            if isinstance(value, Id):
                id_key = attr

        cls.id_key = id_key   
        cls._dumb = id_key is None
        cls._set_up = True
        cls._self_name = cls.__name__
        cls._fields_names = frozenset(cls._fields)

    def _convert_orig_values_to_conditions(self):
        """ Convert the internal _original_values
            to conditions, for a where_many method.

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

        # Set's up the internal values using the special setters
        for field, col in self._fields.items():
            field_val = values.get(field, None)

            self._field_values[field] = col.db_get(field_val)

        # Sets up the values that are not "assigned" to the model. Useful for relations
        field_values_not_in_model = ((field, values[field]) for field in frozenset(values) - self._fields_names)  
        for field, value in field_values_not_in_model:
            setattr(self, field, value)

    # PUBLIC
    
    """ A string of the associated table name. Can be specified by
        subclasses. If not, it will be assumed to be the model name + s.
        @static
    """
    table_name = ''

    """ The table id key name.
        @static
    """
    id_key = ''

    def __init__(self, creating_new=True, pivot_query=None, **values):
        """ The model base class. It allows ORM operations, and it's supossed 
            to be subclassed.

            Args:
                creating_new: Wheter the model is not in the database already.
                pivot_query: If the model is gotten from a Multiple query, 
                    this argument will be a QueryBuilder to get the pivot middle table.
                values: The values of the model to initialize.
        """
        if not self._set_up:
            self.__class__._set_up_model()

        self._creating_new = creating_new
        self._pivot_query = pivot_query
        self._pivots = {attr: None for attr in self._pivot_classes}
        self.relations_loaded = {}

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
        """ Create a record in the database and save it. If the model has an id key, return the model.

            Args:
                return_model: Wheter to return or not the model if it has an id key, after being saved.
                **values: The values of the model to be created.
            
            Return:
                True if the model has no id key or the return_model is false.
                A self model of the stored row if not.
        """
        if not cls._set_up:
            cls._set_up_model()

        O.db.create(cls.table_name, **values)

        if return_model and not cls._dumb:
            return cls.where(cls.id_key, '=', O.db.last_id()).first()
        else:
            return True

    @classmethod
    def find(cls, *indexes):
        """ Find the models with the specified id value(s).

            Args:
                *indexes: An assortment of id values of the models to fetch.
            
            Returns:
                A model if the id value is only one. A ModelContainer if there's more than one id value.

            Raises:
                ArgumentError: If no id value value is passed.
                ModelHasNoIdError: If the model has no Id column.
        """
        if not cls._set_up:
            cls._set_up_model()

        indexes_amount = len(indexes)

        if not indexes_amount:
            raise ArgumentError('No indexes passed. Required at least one.') 
        if cls._dumb:
            raise ModelHasNoIdError(cls, 'find')

        result = cls.where_in(cls.id_key, indexes)
        
        if indexes_amount == 1:
            return result.first()
        else:
            return result.get()

    @classmethod
    def destroy(cls, *indexes):
        """ Delete the models with the specified id value(s).

            Args:
                *indexes: Id value(s) of the model(s) to delete.
            
            Returns:
                True

            Raises:
                ArgumentError: If no id value is passed.
                ModelHasNoIdError: If the model has no Id column.
        """
        if not cls._set_up:
            cls._set_up_model()

        if not len(indexes):
            raise ArgumentError('No indexes passed. Required at least one.') 
        if cls._dumb:
            raise ModelHasNoIdError(cls, 'destroy')

        cls.where_in(cls.id_key, indexes).delete() 

        return True

    def get_id(self):
        """ Get the id value of the model.

            Return:
                The id value of the model

            Raises:
                ModelHasNoIdError: If the model has no Id column.
        """
        if self._dumb:
            raise ModelHasNoIdError(cls, 'get_id')

        return getattr(self, self.id_key)
                                
    def save(self):
        """ Commit the current changes to the database.

            Return:
                self
        """
        values_for_db = {}
        for field_name, field_instance in self._fields.items():
            values_for_db[field_name] = field_instance.db_set(self, self._field_values[field_name])

        # Make sure that the model + the relationships are saved in a transaction
        with O.db.transaction():            
            if self._creating_new:
                O.db.create(self.table_name, **values_for_db)
            else:
                if self._dumb:
                    # If the model has no primary key, then do a "where_many" with all fields and hope for the best 
                    O.warn(f"Updating model {self.table_name} without primary key is error prone.")
                    self.__class__.where_many(self._convert_orig_values_to_conditions()).update(values_for_db)
                else:
                    self.__class__.where(self.id_key, '=', self.get_id()).update(values_for_db)

            # Deal with all simple relations
            for rel_function in self._rel_queue:
                rel_function()

            if not self._dumb:
                id_of_row = O.db.last_id() if self._creating_new else self.get_id()

                # Deal with ManyToMany middle table saving
                for pivot in self._pivots.values():
                    if pivot is None:
                        continue

                    pivot.set_self_id(id_of_row)
                    pivot.save()

                # When updating, update the values with the one gotten from the database
                row = QueryBuilder.table(self.table_name).where(self.id_key, '=', id_of_row).first()
                self._update_values(dict(zip(row.keys(), tuple(row))))

            self._creating_new = False

        return self

    def delete(self):
        """ Remove the working model from the database.
        """
        if self._creating_new:
            raise Exception('Can not destroy model that doesn\'t exist in the database')

        if self._dumb:
            O.warn("Deleting {self.table_name} without primary key is error prone")
            self.__class__.where_many(self._convert_orig_values_to_conditions()).delete()
        else:
            self.destroy(self.get_id())

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
        """ A way to access the pivot classes of the model, allowing the
            construction and querying of pivots.

            Args:
                rel: The Multiple relation as string.

            Returns:
                A Pivot class.
        """
        return self._pivot_classes[rel]

    @classmethod
    def get_relation(self, relation):
        """ Get a relation field class.

            Args:
                relation: A string with the relation name.

            Returns:
                A Relation subclass.
        """
        return self._relations[relation]

    def rel(self, relation):
        """ Get a QueryBuilder that targets the specified relation rows.

            Args:
                relation: A string with the relation name.

            Returns:
                A QueryBuilder subclass object, depending of the type of relation.
        """
        return self._relations[relation].query_builder(self)

    @property
    def pivot(self):
        """ If the model was obtained from a Multiple query, this property will
            return the respective pivot model, if it was specified.

            Returns:
                A Pivot instance.
        """
        if getattr(self, '_loaded_pivot', None):
            return self._loaded_pivot
        
        self._loaded_pivot = self._pivot_query.add_model_id(self._pivot_query, self.get_id()).first() 
        
        return self._loaded_pivot
    
    def __eq__(self, other_model):
        """ Equality operator with other models.

            Two models are equal only if their field values are the same.
        """
        return isinstance(other_model, Model) and self._field_values == other_model._field_values

    @classmethod
    def get_existence_conditions(cls, rel):
        """ Get the conditions for doing relation related QueryBuilding.

            Not intended to be used for model building.
            
            Args:
                rel: The relation name.

            Returns:
                (self table field, related model field, relation key table name)
        """
        if not cls._set_up:
            cls._set_up_model()

        relation_class = cls._relations.get(rel, None)

        if relation_class is None:
            raise ValueError('Model {} has no associated relation {}.'.format(cls.__name__, rel))

        return relation_class.get_existence_conditions()

    def __hash__(self):
        return hash(self.get_id())

def generate_model_class(table_name, *, id_name='id', model_name=''):
    """ Generate a model class automatically from a table in the database.

        Args:
            table_name: Table
    """
    columns = O.db.get_all_columns(table_name)
    type_dict = field_types[O.db.driver]

    class GeneratedModel(Model):
        pass

    GeneratedModel.table_name = table_name

    for column in columns:
        col_name = column.name
        if id_name == col_name:
            setattr(GeneratedModel, id_name, Id())
        else:
            setattr(GeneratedModel, col_name, type_dict[column.type]())

    GeneratedModel.set_up()

    if model_name:
        GeneratedModel.__name__ = model_name
        GeneratedModel.__qualname__ = model_name

    return GeneratedModel