import sqlite3
import json
import abc

from collections import namedtuple

from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.ModelContainer import ModelContainer
from OxygenRM.internals.RelationQueryBuilder import HasQueryBuilder

class Field(metaclass=abc.ABCMeta):
    _attr = None

    _valid_types = []

    """ The base class for defining a Model column.
    """
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
    pass

class Has(Relation):
    """ Define a 'has' relationship with another database table.

        Args:
            how_much: Either 'one' or 'many'
            model: The related model class
            on_other_col: The name of the related model column to use for the join.
                By default it will be the #{lower case model name}_id
            on_self_col: The name of the own column, for use in the join.
                By the default it will be the id column.
    """
    def __init__(self, how_much, model, on_other_col='', on_self_col=None):
        if how_much not in ('many', 'one'):
            raise ValueError('Invalid relation {}. Expected "many" or "one"'.format(how_much))

        self.model = model
        self.how_much = how_much

        if how_much == 'one':
            self._extend_model()

        self.on_self_col = on_self_col
        self.on_other_col = on_other_col  

    def get(self, starting_model):
        if not self.on_other_col:
            self.on_other_col = starting_model.__class__.__name__.lower() + '_id'

        if not self.on_self_col:
            self.on_self_col = starting_model.primary_key

        qb = HasQueryBuilder(self.model, starting_model, self).where(self.on_other_col, '=', getattr(starting_model, self.on_self_col))
        
        if self.how_much == 'many':
            return qb
        else:
            model = qb.get()
            model.parting_model = starting_model
            return model

    def set(self, starting_model, value):
        if not isinstance(starting_model, ModelContainer):
            self.get(starting_model).assign(value)

    def _extend_model(self):
        model = self.model
        class HasModelWrapper(model):
            _lazy_load = True

            def __init__(self, result):
                self.result = result
                self._loaded = False

            def __getattribute__(self, attr):
                prop = getattr(model, attr, None)

                if not super().__getattribute__('_loaded') and (isinstance(prop, property) or callable(prop)):
                    super().__getattribute__('_load')()

                return super().__getattribute__(attr)

            def _load(self):
                self._loaded = True

                row = next(self.result())
                super().__init__(False, **dict(zip(row.keys(), tuple(row))))

        def assign(wrapped_self, other_model):
            """ Make the specified model the only model that the parent possesses.

                Args:
                    other_model: The new model to assign
            """
            other_id = other_model.get_primary()
            self_id = getattr(wrapped_self.parting_model, self.on_self_col)

            def pending_function():
                QueryBuilder.table(wrapped_self.table_name).where(self.on_other_col, '=', self_id).update({self.on_other_col: None})
                QueryBuilder.table(wrapped_self.table_name).where(other_model.primary_key, '=', other_id).update({self.on_other_col: self_id})

            wrapped_self.parting_model._rel_queue.append(pending_function)

            return wrapped_self

        def deassign(wrapped_self):
            """ Remove the associated model(s) from the parent.
            """
            self_id = getattr(wrapped_self.parting_model, self.on_self_col)

            def pending_function():
                QueryBuilder.table(wrapped_self.table_name).where(self.on_other_col, '=', self_id).update({self.on_other_col: None})

            wrapped_self.parting_model._rel_queue.append(pending_function)
            return wrapped_self

        HasModelWrapper.assign = assign
        HasModelWrapper.deassign = deassign

        self.model = HasModelWrapper

class BelongsTo(Relation):
    """ Define a 'belongs to' relationship with another database table.

        Args:
            how_much: Either 'one' or 'many'
            model: The related model class
            on_other_col: The name of the related model column to use for the join.
                By default it will be the #{lower case model name}_id
            on_self_col: The name of the own column, for use in the join.
                By the default it will be the id column.
    """
    def __init__(self, how_much, model, on_other_col='id', on_self_col=''):
        if how_much not in ('many', 'one'):
            raise ValueError('Invalid relation {}. Expected "many" or "one"'.format(how_much))

        self.model = model
        self.how_much = how_much

        self.on_self_col = on_self_col 
        self.on_other_col = on_other_col  

    def get(self, starting_model):
        if not self.on_self_col:
            self.on_self_col = starting_model.__class__.__name__.tolower() + '_id'
        
        qb = QueryBuilder(self.model.table_name, self.model).where(self.on_other_col, '=', getattr(starting_model, self.on_self_col))
        
        if self.how_much == 'many':
            return qb.get()
        else:
            return qb.limit(1).get().first_or_none()

    def set(self):
        raise NotImplementedError('Setting relationship models not yet allowed')
    
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
        self.model = target_model
        self.table = middle_table
        self.self_name = self_name
        self.other_name = other_name
        self.middle_class = middle_class

        self._setted_up = False

    def get(self, parting_model):
        if not self._setted_up:
            self._set_up(parting_model)

        return QueryBuilder.raw(self.query, (parting_model.get_primary(),), self.model, False)

        # builder = QueryBuilder.table(self.model.table_name + ' oxygent', self.model)
        # builder.where(self.self_name,'=', parting_model.get_primary()).join(self.table).on('oxygent' + self.model.primary_key, '=', )

    def _set_up(self, parting_model):
        """ Set up the relation with the relevant variables

            Args:
                parting_model: The model to part from.
        """
        parting_model_name = parting_model.__class__.__name__.lower()
        target_model_name = self.model.__name__.lower()

        if not self.table:
            self.table = '_'.join(sorted((parting_model_name, target_model_name)))

        if not self.self_name:
            self.self_name = self.table + '.' + parting_model_name + '_id'

        if not self.other_name:
            self.other_name = target_model_name + '_id'

        # if not self.middle_class:
        #     self.middle_class = _create_middle_model_class()
            
        query = '''SELECT oxygent.* FROM {target_table} oxygent CROSS JOIN {middle_table} 
                    ON oxygent.{target_primary} = {middle_table}.{middle_target_name}
                    WHERE {middle_self_name} = ?'''

        self.query = query.format(
            target_table=self.model.table_name,
            middle_table=self.table,
            target_primary=self.model.primary_key,
            middle_target_name=self.other_name,
            middle_self_name=self.self_name
        )

        self._setted_up = True

    def _create_middle_model_class(self):
        """ Craft the model class to be used for the middle classes

            Returns:
                The crafted class.
        """
        table_name = self.table

        class MiddleClass(self.model.__class__):
            table_name = table_name

        cols_types = OxygenRM.db.table_fields_types(table_name)

        for col_name, col_type in cols_types.items():
            setattr(MiddleClass, col_name, field_types[OxygenRM.db.driver][col_type])

        MiddleClass.set_up()

        return MiddleClass

class JSON(Field):
    """ A field for dealing with JSON strings boilerplate.
    """

    def __init__(self, default=dict, null=False):
        if default not in (dict, list):
            raise ValueError('Wrong default constructor {}. Must be a class constructor of dict or list'.format(default))

        self.default_constructor = self._make_container_jsonable(default)

    def get(self, model):
        original_val = super().get(model)
        
        if getattr(original_val, 'conformable', False):
            return original_val

        if original_val is None:
            value = self.default_constructor()
        else:
            json_val = json.loads(original_val)
            constructor = self._make_container_jsonable(json_val.__class__)
            
            value = constructor(json_val)
            
        model._field_values[self._attr] = value
        return value

    def validate(self, value):
        if not isinstance(value, (dict, list, str)):
            raise TypeError('Invalid value {}. Expected a dict or string.'.format(value))

    def value_processor(self, value):
        if isinstance(value, str):
            value = json.loads(value)
        
        constructor = self._make_container_jsonable(value.__class__)
        return constructor(value)

    def _make_container_jsonable(self, constructor):
        class JSONableContainer(constructor):
            """ A container that makes easier the conversion to JSON.
            """    
            def __str__(self):
                return self.to_json()

            def to_json(self, *args):
                return json.dumps(self, *args)

            def __conform__(self, protocol):
                if protocol is sqlite3.PrepareProtocol:
                    return str(self)

            conformable = True

        return JSONableContainer

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