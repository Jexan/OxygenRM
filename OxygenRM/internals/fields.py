import datetime
import sqlite3
import pickle
import json
import abc

from functools import partial

from collections import namedtuple

from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.ModelContainer import ModelContainer
from OxygenRM.internals.RelationQueryBuilder import HasManyQueryBuilder, BelongsToManyQueryBuilder

class Field(metaclass=abc.ABCMeta):

    """ The name of the attribute of this field in the belonging model.
    """
    _attr = None

    def __init__(self, null=False):
        """ The abstract base class for defining a Model property that is in the database as a column.

            Args:
                null: Whether the model can be null 
        """
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

    def db_set(self, model, value):
        """ The value formatter for the database if the field does not implement __conform__.

            Args:
                value: The value to process.

            Returns:
                The processed value.
        """
        return self.value_formatter(value)

    def db_get(self, value):
        """ The value formatter to process the value when the raw values are passed to the model.

            Args:
                value: The value to format.

            Returns:
                The formatted value.
        """
        return self.value_processor(value)

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
        value_is_pure_int = isinstance(value, int) and not isinstance(value, bool)

        if not value_is_pure_int and value is not None:
            raise TypeError('Invalid value {}. Expected an int.'.format(value))
    
class Float(Field):
    """ A basic float column.
    """
    def validate(self, value):
        if type(value) not in (int, float) or isinstance(value, bool):
            raise TypeError('Invalid value {}. Expected a float or int.'.format(value))

    def value_processor(self, value):
        if value is not None:
            return float(value)
        else:
            return 0

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

        self._self_name = on_self_col
        self._other_name = on_other_col  
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
            _base_class = model

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
            self._set_up()

        # Move elsewhere
        model_container = starting_model.relations_loaded.get(self._attr)
        
        if model_container:
            model_primary = starting_model.get_primary()

            predicate = lambda model: getattr(model, self._other_name) == model_primary
            
            if self._how_much == 'many':
                return model_container.filter(predicate)
            else:
                return model_container.find(predicate)
            
        qb = HasManyQueryBuilder(self._model, starting_model, self._self_name, self._other_name)

        if self._how_much == 'many':
            return qb
        else:
            result_model = qb.get()
            result_model.parting_model = starting_model

            return result_model

    def eager_load_builder(self):
        if not self._setted_up:
            self._set_up()

        builder = QueryBuilder(self._model.table_name, self._model).where(self._other_name, 'IS NOT', None)
        return partial(builder.where_in, self._other_name)

    def get_existence_conditions(self):
        """ Get the conditions for doing relation related QueryBuilding.
    
            Returns:
                (self table field, related model field, relation key table name)
        """
        if not self._setted_up:
            self._set_up()

        return 'oxygent.' + self._self_name, self._model.table_name + '.' + self._other_name, self._model.table_name
    
class Has(Relation):
    def _set_up(self):
        if not self._other_name:
            self._other_name = self.parting_model.__class__.__name__.lower() + '_id'

        if not self._self_name:
            self._self_name = self.parting_model.primary_key

    def _extend_model(self):
        ext_model = super()._extend_model()

        def assign(wrapped_self, other_model):
            """ Queue the action of making the specified model the only model that the parent possesses.

                Args:
                    other_model: The new model to assign
            """
            other_id = other_model.get_primary()
            self_id = getattr(wrapped_self.parting_model, self._self_name)

            def pending_function():
                QueryBuilder.table(wrapped_self.table_name).where(self._other_name, '=', self_id).update({self._other_name: None})
                QueryBuilder.table(wrapped_self.table_name).where(other_model.primary_key, '=', other_id).update({self._other_name: self_id})

            wrapped_self.parting_model._rel_queue.append(pending_function)

            return wrapped_self.parting_model

        def deassign(wrapped_self):
            """ Queue the removal of the associated model(s) from the parent.
            """
            self_id = getattr(wrapped_self.parting_model, self._self_name)

            def pending_function():
                QueryBuilder.table(wrapped_self.table_name).where(self._other_name, '=', self_id).update({self._other_name: None})

            wrapped_self.parting_model._rel_queue.append(pending_function)
            return wrapped_self.parting_model

        ext_model.assign = assign
        ext_model.deassign = deassign
        return ext_model

class BelongsTo(Relation):
    def _set_up(self):
        if not self._other_name:
            self._other_name = self.parting_model.primary_key

        if not self._self_name:
            self._self_name = self.parting_model.__class__.__name__.lower() + '_id'

    def _extend_model(self):
        ext_model = super()._extend_model()

        def assign(wrapped_self, other_model):
            """ Queue the action of making the specified model the only model that the parent possesses.

                Args:
                    other_model: The new model to assign
            """
            if other_model is not None:
                if not isinstance(other_model, wrapped_self._base_class):
                    raise TypeError('Cannot assign relationship to type {}. Expected a {} or None.'.format(type(other_model), wrapped_self._base_class))
                if other_model.being_created():
                    raise ValueError('Tried to assign an unsaved model.')

            other_id = getattr(other_model, self._other_name, None)
            setattr(wrapped_self.parting_model, self._self_name, other_id)

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
            pivot: The class to use for the pivot table model.
                By default one will be created with just the fields.
    """
    def __init__(self, target_model, middle_table=None, self_name=None, other_name=None, pivot=None):
        self._model = target_model
        self._middle_table = middle_table
        self._self_name = self_name
        self._other_name = other_name
        self.pivot = pivot 

        self._setted_up = False

    def get(self, parting_model):
        if not self._setted_up:
            self._set_up()

        builder = BelongsToManyQueryBuilder(
            self._model, parting_model, self._self_name, self._other_name, self._middle_table, self._attr, self.pivot
        )

        return builder

    def _set_up(self):
        """ Set up the relation with the relevant variables

            Args:
                parting_model: The model to part from.
        """
        parting_model_name = self.parting_model.__name__.lower()
        target_model_name = self._model.__name__.lower()

        if not self._middle_table:
            self._middle_table = '_'.join(sorted((parting_model_name, target_model_name)))

        if not self._self_name:
            self._self_name = parting_model_name + '_id'

        if not self._other_name:
            self._other_name = target_model_name + '_id'

        if self.pivot:
            self.pivot._self_name = self._self_name
            self.pivot._other_name = self._other_name
            if not getattr(self.pivot, 'table_name', None):
                self.pivot.table_name = self._middle_table 
        
        self._setted_up = True

    def get_existence_conditions(self):
        if not self._setted_up:
            self._set_up()

        return 'oxygent.' + self.parting_model.primary_key , self._middle_table + '.' + self._self_name, self._middle_table

    def eager_load_builder(self):
        if not self._setted_up:
            self._set_up()

        return partial(builder.where_in, self._other_name)

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
    """ A field for dealing with Pickle objects boilerplate.
        
        Args:
            default_cons: A function or class that when called should return a value, which will be
                the default value. If the value is not callable, then that one shall be used instead.
                Example:
                    list, dict, 1, {a: 2}
            args: If the default_cons is callable, the args will be passed as *args to it.
            kwargs: If the default_cons is callable, the args will be passed as **kwargs to it.
            strict: Whether to mmake sure that the the column must have just the default_cons type.
    """
    def __init__(self, default_cons=None, args=(), kwargs={}, strict=False):
        self.default_cons = default_cons if callable(default_cons) else lambda: default_cons

        if strict:
            self._default_class = default_cons if callable(default_cons) else type(default_cons)

        self.null = default_cons is None
        self.args = args
        self.kwargs = {}
        self.strict = strict 

    def value_processor(self, value):
        if self.strict and not isinstance(value, self._default_class):
            raise TypeError('Attempted to set strict Pickle column to type {}. {} expected'.format(type(value), self.default_cons))

        return value

    def db_set(self, model, value):
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

class DateField(Field, metaclass=abc.ABCMeta):
    def __init__(self, time_format='', create_date=False, update_date=False, tz=datetime.timezone.utc):
        self.created_date = create_date
        self.update_date = update_date
        self.tz = tz
        self.time_format = time_format

class Datetime(DateField):
    def db_set(self, model, value):
        should_add_created_timestamp = self.created_date and model.being_created()
        if self.update_date or should_add_created_timestamp:
            return datetime.datetime.now(tz=self.tz).timestamp()

        if value is None:
            return None

        return value.timestamp()

    def value_processor(self, value):
        value_type = type(value)

        if value_type in (int, float):
            return datetime.datetime.fromtimestamp(value, tz=self.tz)
        elif value_type is str:
            return datetime.datetime.strptime(value, self.time_format)
        elif value_type is datetime.datetime:
            return value
        elif value is None:
            return None
        else:
            raise ValueError("Invalid Datetime field assign type. Expected timestamp, formated string or a datetime object. Got {}".format(type(value)))

class Date(DateField):
    ISO_FORMAT = "%Y-%m-%d"

    def db_set(self, model, value):
        if value is None:
            return None

        should_add_created_timestamp = self.created_date and model.being_created()
        if self.update_date or should_add_created_timestamp:
            value = datetime.date.today()

        return value.strftime(self.ISO_FORMAT)

    def value_processor(self, value):
        value_type = type(value)

        if value_type in (int, float):
            return datetime.datetime.fromtimestamp(value, tz=self.tz).date()
        elif value_type is str:
            return datetime.datetime.strptime(value, self.ISO_FORMAT).date()
        elif value_type is datetime.datetime:
            return value.date()
        elif value_type is datetime.date:
            return value
        elif value is None:
            return None
        else:
            raise ValueError("Invalid Date field assign type. Expected timestamp, formated string, date or datetime object. Got {}".format(type(value)))

class Time(DateField):
    ISO_FORMAT = "%H:%M:%S.%f"

    def db_set(self, model, value):
        if value is None:
            return None

        should_add_created_timestamp = self.created_date and model.being_created()
        if self.update_date or should_add_created_timestamp:
            value = datetime.datetime.now(tz=self.tz).time()

        return value.strftime(self.ISO_FORMAT)

    def value_processor(self, value):
        value_type = type(value)

        if value_type is str:
            return datetime.datetime.strptime(value, self.ISO_FORMAT).time()
        elif value_type is datetime.datetime:
            return value.time()
        elif value_type is datetime.time:
            return value
        elif value is None:
            return None
        else:
            raise ValueError("Invalid Time field assign type. Expected formated string, time or datetime object. Got {}".format(type(value)))

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