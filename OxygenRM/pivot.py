from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.fields import Field, Relation
from OxygenRM.models import Model

import OxygenRM as O

class Pivot(Model):
    """ The model class for ManyToMany middle table classes
    """
    @classmethod
    def _set_up_model(cls):
        """ Set up the internals and relations of the Model
        """
        cls._fields = dict()
        cls._rel_queue = list()
        cls._pivot_classes = dict()
        
        for attr, value in cls.__dict__.items():
            if isinstance(value, Field):
                value._attr = attr
                
                row_prop = property(fget=value.get, fset=value.set) 
                setattr(cls, attr, row_prop)
                
                cls._fields[attr] = value

        cls._set_up = True

    def save(self, base_model=None):
        values_for_db = {}

        # The ids of the related models        
        self_id = getattr(self, self._self_name, None) 
        other_id = getattr(self, self._other_name, None)

        if self_id is None or other_id is None:
            raise ValueError('Cannot save pivot model if relation ids are None: {}:{} and {}:{}'.format(
                self._self_name, self_id, self._other_name, other_id
            )) 
        
        if base_model == None:
            for field_name, field_instance in self._fields.items():
                values_for_db[field_name] = field_instance.db_set(self, self._field_values[field_name])
            
            if self._creating_new:
                O.db.create(self.table_name, **values_for_db)

    def _update_values(self, values):
        self._field_values = {}

        for field, col in self._fields.items():
            field_val = values.get(field, None)

            self._field_values[field] = col.db_get(field_val)

    @classmethod
    def new(cls):
        return cls()

    def set_self_id(self, id):
        """ Set the id of the initial model id for this row. (Useful for new model creation)

            Args:
                id: The value of the inital model id.
        """
        setattr(self, self._self_name, id)