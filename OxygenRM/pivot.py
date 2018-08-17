from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.models import Model

class Pivot(Model):
    @classmethod
    def _set_up_model(self):
        # Set up the relation indeces
        ...

    def save(self, base_model):
        for index in self._ids:
            if getattr(self, index, None) is None:
                raise ValueError('Cannot save pivot model without all specified ids') 

    def __init__(self, creating_new=True, **values):
        ...

    @classmethod
    def new(cls):
        return cls()

    @classmethod
    def generate_pivot(cls, table_name):
        return cls()