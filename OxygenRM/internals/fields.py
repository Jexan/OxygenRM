import sqlite3
import pickle
import json
import abc

from collections import namedtuple

from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.ModelContainer import ModelContainer
from OxygenRM.internals.RelationQueryBuilder import RelationQueryBuilder

class Field(metaclass=abc.ABCMeta):
    """ The base class for defining a Model property that is in the database as a column.
    """

    """ The name of the attribute of this field in the belonging model.
    """
    _attr = None

    _valid_types = []

    def __init__(self, null=False):
        self.null = null

    def get(self, model):
        """ The getter for model fields.

            Args:
                model: The model instance. 

            Returns:
                The value of the model
        """
        return self.value_formatter(model._field_values[self._attr])

    def set(self, model, value):
        """ Validate and set the the value of the column.

            Args:
                model: The model instance.
                value: The value to be assigned.
        """
        self.validate(value)
        
        model._field_values[self._attr] = self.value_processor(value)

    def validate(self, value):
        """ Decide wheter a non-null value that wants to be set is valid.

            Args:
                value: The value to be set internally
        
            Raises:
                TypeError: If the value is invalid.
        """
        return True

    def value_processor(self, value):
        """ Transform the value given. Used in the setter.

            Args:
                value: The value to be processed
        
            Returns:
                A processed value
        """
        return value

    def value_formatter(self, value):
        """ Format the value given. Used in the getter.

            Args:
                value: The value to be processed
        
            Returns:
                A processed value
        """
        return value

    def db_set(self, value):
        """ The value formatter for the database if the field does not implement __conform__.
        """
        return self.value_formatter(value)

    def db_get(self, value):
        return self.value_formatter(value)

class Text(Field):
    """ A basic Text column.
    """
    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError('Invalid value {}. Expected str.'.format(value))

class Bool(Field):
    """ A boolean column. Implemented as a small int.

        The possible values to be setted, in a model, are bool, 1 or 0. 
    """
    def validate(self, value):
        if value not in (0, 1, True, False):
            raise TypeError('Invalid value {}. Expected 1, 0 or bool.'.format(value))

    # We want to keep the value internally as a 1 or 0.
    def value_processor(self, value):
        return 1 if value else 0

class Integer(Field):
    """ A basic integer column.
    """
    def validate(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError('Invalid value {}. Expected an int.'.format(value))
    
class Float(Field):
    """ A basic float column.
    """
    def validate(self, value):
        if type(value) not in (int, float) or isinstance(value, bool):
            raise TypeError('Invalid value {}. Expected a float or int.'.format(value))

    def value_processor(self, value):
        return float(value)

class Id(Integer):
    """ An auto-incrementing, unsigned integer. Used as a primary key.
    """
    def __init__(self):
        self.null = False

class Relation(Field):
    """ Define a 'has' relationship with another database table.

        Args:
            how_much: Either 'one' or 'many'
            model: The related model class
            on_other_col: The name of the related model column to use for the join.
                By default it will be the #{lower case model name}_id (HAS) or primary key (BELONGS) 
            on_self_col: The name of the own column, for use in the join.
                By the default it will be the primary key (HAS) or #{lower case model name}_id (BELONGS) column.
    """
    def __init__(self, how_much, model, on_other_col=None, on_self_col=None):
        if how_much not in ('many', 'one'):
            raise ValueError('Invalid relation {}. Expected "many" or "one"'.format(how_much))

        self._model = model
        self._how_much = how_much

        if how_much == 'one':
            self._model = self._extend_model()

        self._on_self_col = on_self_col
        self._on_other_col = on_other_col  
        self._setted_up = False

    def _extend_model(self):
        """ Extend the base model class, adding Relational Operations and lazy loading.
        """
        model = self._model

        class ModelWrapper(model):
            """ A model with the possibility to add simple relations.

                Args:
                    result: A SQL result function.
            """

            """ A flag to let ModelContainer know that the model to wrap 
                has lazy loading.
            """
            _lazy_load = True

            def reset(self):
                self.empty = False
                self._loaded = False

                return self

            def __init__(self, result):
                self._result = result
                self._loaded = False
                self.empty = False

            def __bool__(self):
                return self.empty

            def __getattribute__(self, attr):
                prop = getattr(model, attr, None)

                if not super().__getattribute__('_loaded') and (isinstance(prop, property) or callable(prop)):
                    super().__getattribute__('_load')()

                return super().__getattribute__(attr)

            def _load(self):
                """ Load the model from the database.
                """
                self._loaded = True

                row = tuple(self._result())
                if row:
                    super().__init__(False, **dict(zip(row[0].keys(), tuple(row[0]))))
                else:
                    self.empty = True 

        return ModelWrapper

    def get(self, starting_model):
        if not self._setted_up:
            self._set_up(starting_model)

            self._qb = RelationQueryBuilder(self._model, starting_model, self._on_self_col, self._on_other_col)
            
            if self._how_much == 'one':
                self._result_model = self._qb.get()
                self._result_model.parting_model = starting_model

        if self._how_much == 'many':
            return self._qb.reset()
        else:
            return self._result_model.reset()

class Has(Relation):
    def set(self, starting_model, value):
        if not isinstance(starting_model, ModelContainer):
            self.get(starting_model).assign(value)

    def _set_up(self, starting_model):
        if not self._on_other_col:
            self._on_other_col = starting_model.__class__.__name__.lower() + '_id'

        if not self._on_self_col:
            self._on_self_col = starting_model.primary_key

    def _extend_model(self):
        ext_model = super()._extend_model()

        def assign(wrapped_self, other_model):
            """ Queue the action of making the specified model the only model that the parent possesses.

                Args:
                    other_model: The new model to assign
            """
            other_id = other_model.get_primary()
            self_id = getattr(wrapped_self.parting_model, self._on_self_col)

            def pending_function():
                QueryBuilder.table(wrapped_self.table_name).where(self._on_other_col, '=', self_id).update({self._on_other_col: None})
                QueryBuilder.table(wrapped_self.table_name).where(other_model.primary_key, '=', other_id).update({self._on_other_col: self_id})

            wrapped_self.parting_model._rel_queue.append(pending_function)

            return wrapped_self.parting_model

        def deassign(wrapped_self):
            """ Queue the removal of the associated model(s) from the parent.
            """
            self_id = getattr(wrapped_self.parting_model, self._on_self_col)

            def pending_function():
                QueryBuilder.table(wrapped_self.table_name).where(self._on_other_col, '=', self_id).update({self._on_other_col: None})

            wrapped_self.parting_model._rel_queue.append(pending_function)
            return wrapped_self.parting_model

        ext_model.assign = assign
        ext_model.deassign = deassign
        return ext_model

class BelongsTo(Relation):
    def set(self):
        raise NotImplementedError('Setting relationship models not yet allowed')

    def _set_up(self, starting_model):
        if not self._on_other_col:
            self._on_other_col = starting_model.primary_key

        if not self._on_self_col:
            self._on_self_col = starting_model.__class__.__name__.lower() + '_id'

    def _extend_model(self):
        ext_model = super()._extend_model()

        def assign(wrapped_self, other_model):
            """ Queue the action of making the specified model the only model that the parent possesses.

                Args:
                    other_model: The new model to assign
            """
            other_id = getattr(other_model, self._on_other_col)
            self_id = wrapped_self.parting_model.get_primary()
            self_primary = wrapped_self.parting_model.primary_key

            def pending_function():
                QueryBuilder.table(wrapped_self.parting_model.table_name).where(self_primary, '=', self_id).update({self._on_self_col: other_id})

            wrapped_self.parting_model._rel_queue.append(pending_function)

            return wrapped_self.parting_model

        def deassign(wrapped_self):
            """ Queue the removal of the associated model(s) from the parent.
            """
            return wrapped_self.assign(None)

        ext_model.assign = assign
        ext_model.deassign = deassign
        return ext_model
 
class Multiple(Relation):
    """ Define a 'many to many' relationship with another database table.

        Args:
            target_model: The related model class
            middle_table: The name of the table to use for the join.
                By default, it will be the tables names, sorted alphabetically,
                with an underscore as a separation.
            self_name: The name of the current model reference in the middle table.
                By default it will be the #{lower case model name}_id
            other_name: The name of the target model reference in the middle table.
                By default it will be the #{lower case model name}_id
            middle_class: The class to use for the pivot table model.
                By default one will be created with just the fields.
    """
    def __init__(self, target_model, middle_table=None, self_name=None, other_name=None, middle_class=None):
        self._model = target_model
        self._middle_table = middle_table
        self._self_name = self_name
        self._other_name = other_name
        self._middle_class = middle_class

        self._setted_up = False

    def get(self, parting_model):
        if not self._setted_up:
            self._set_up(parting_model)

        return QueryBuilder.raw(self.query, (parting_model.get_primary(),), self._model, False)

        # builder = QueryBuilder.table(self._model.table_name + ' oxygent', self._model)
        # builder.where(self._self_name,'=', parting_model.get_primary()).join(self._middle_table).on('oxygent' + self._model.primary_key, '=', )

    def _set_up(self, parting_model):
        """ Set up the relation with the relevant variables

            Args:
                parting_model: The model to part from.
        """
        parting_model_name = parting_model.__class__.__name__.lower()
        target_model_name = self._model.__name__.lower()

        if not self._middle_table:
            self._middle_table = '_'.join(sorted((parting_model_name, target_model_name)))

        if not self._self_name:
            self._self_name = self._middle_table + '.' + parting_model_name + '_id'

        if not self._other_name:
            self._other_name = target_model_name + '_id'

        # if not self._middle_class:
        #     self._middle_class = _create_middle_model_class()
            
        query = '''SELECT oxygent.* FROM {target_table} oxygent CROSS JOIN {middle_table} 
                    ON oxygent.{target_primary} = {middle_table}.{middle_target_name}
                    WHERE {middle_self_name} = ?'''

        self.query = query.format(
            target_table=self._model.table_name,
            middle_table=self._middle_table,
            target_primary=self._model.primary_key,
            middle_target_name=self._other_name,
            middle_self_name=self._self_name
        )

        self._setted_up = True

    def _create_middle_model_class(self):
        """ Craft the model class to be used for the middle classes

            Returns:
                The crafted class.
        """
        table_name = self._middle_table

        class MiddleClass(self._model.__class__):
            table_name = table_name

        cols_types = OxygenRM.db.table_fields_types(table_name)

        for col_name, col_type in cols_types.items():
            setattr(MiddleClass, col_name, field_types[OxygenRM.db.driver][col_type])

        MiddleClass.set_up()

        return MiddleClass

class JSON(Field):
    """ A field for dealing with JSON strings boilerplate.
        
        Allows the edition of the column as JSONable Python data structures without
        worrying about the conversion when it's time to update/create the model.

        Args:
            default_class: A constructor that will determine which should be the 
                default Python data structure to use if the field is empty.
                The class passed must subclass dict or list.
    """

    def __init__(self, default_class=dict):
        if default_class not in (dict, list):
            raise ValueError('Wrong default constructor {}. Must be a class constructor of dict or list'.format(default_class))

        self._default_constructor = JSON._make_container_jsonable(default_class)

    def validate(self, value):
        if not isinstance(value, (dict, list, str)):
            raise TypeError('Invalid value {}. Expected a dict or string.'.format(value))

    def value_processor(self, value):
        if isinstance(value, str):
            value = json.loads(value)
        elif getattr(value, 'conformable', None):
            return value
        
        constructor = self._make_container_jsonable(value.__class__)
        return constructor(value)

    def db_get(self, value):
        if value is None:
            value = self._default_constructor()
        else:
            json_val = json.loads(value)
            constructor = self._make_container_jsonable(json_val.__class__)
            
            value = constructor(json_val)

        return value

    @staticmethod
    def _make_container_jsonable(constructor):
        """ Wrap the default data structure in a conformable and easy to jsonize 
            structure.

            Args:
                constructor: The data structure class to wrap.

            Returns:
                The wrapped class.

        """
        class JSONableContainer(constructor):
            """ A container that makes easier the conversion to JSON.
            """ 

            """ A flag to identify the model as already wrapped.
            """
            conformable = True

            def __str__(self):
                return self.to_json()

            def to_json(self, *args):
                """ Transform the data structure to JSON.

                    Args:
                        *args: The same args that would be passed to json.dumps
                """
                return json.dumps(self, *args)

            def __conform__(self, protocol):
                if protocol is sqlite3.PrepareProtocol:
                    return str(self)

        return JSONableContainer

class Pickle(Field):
    def __init__(self, default_cons=None, args=(), kwargs={}, strict=False):
        self.default_cons = default_cons if callable(default_cons) else lambda: default_cons

        self.null = default_cons is None
        self.args = args
        self.kwargs = {}
        self.strict = strict 

    def value_processor(self, value):
        if self.strict and not isinstance(value, self.default_cons):
            raise TypeError('Attempted to set strict Pickle column to type {}. {} expected'.format(type(value), self.default_cons))

        return value

    def db_set(self, value):
        if isinstance(value, bytes):
            return value
        else:
            return pickle.dumps(value)

    def db_get(self, value):
        if value is None and not self.null:
            value = self.default_cons(*self.args, **self.kwargs)
        elif isinstance(value, bytes):
            try:
                value = pickle.loads(value)
            except pickle.UnpicklingError as e:
                pass

        return value

field_types = {
    'sqlite3': {
        'text': Text,
        
        'real': Float,
        
        'integer': Integer,
        'int': Integer,

        'boolean': Bool,

        'json': JSON,
    }
}