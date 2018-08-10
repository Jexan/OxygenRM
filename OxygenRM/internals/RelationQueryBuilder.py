from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.ModelContainer import ModelContainer

class RelationQueryBuilder(QueryBuilder):
    """ A query builder specially designed for Has Many relationships.

        Args:
            target_model: The model class to get as a result.
            parting_model: The model instance to get the related models from.
            on_self_col: The name of target_model table column to use for the relation.
            on_other_col:The name of parting_model table column to use for the relation.
    """
    def __init__(self, target_model, parting_model, on_self_col, on_other_col):
        super().__init__(target_model.table_name, target_model)

        self._parting_model = parting_model
        self._on_self_col = on_self_col
        self._on_other_col = on_other_col
        self._table_name = target_model.table_name
        
        self.where(on_other_col, '=', getattr(parting_model, on_self_col))

    def reset(self):
        super().reset()
        
        return self.where(self._on_other_col, '=', getattr(self._parting_model, self._on_self_col))

    def assign(self, other_model):
        """ Make the specified model the only model that the parent possesses.

            Args:
                other_model: The new model to assign.

            Raises:
                TypeError: If the passed model is not a correct model type.
                ValueError: If the passed model has not yet been saved on the database.
        """
        self.deassign_all()
        self.add(other_model)

    def assign_many(self, other_models):
        """ Removes all the associated models and then associate the passed ones to the parent.

            Args:
                other_modelds: An iterator of models to assign.

            Raises:
                TypeError: If one of the passed model is not a correct model type.
                ValueError: If one of the passed model has not yet been saved on the database.
        """
        self.deassign_all()
        self.add_many(other_models)    

    def deassign(self, model):
        """ Remove the passed model from the parent, if it is associated.
        """
        self_id = getattr(self._parting_model, self._on_self_col)
        other_id = other_model.get_primary()

        def pending_function():
            QueryBuilder.table(self._table_name).where_many([
                (self._on_other_col, '=', self_id), 
                (other_model.primary_key, '=', other_id)
            ]).update({self._on_other_col: None})

        self._parting_model._rel_queue.append(pending_function)

    def deassign_all(self):
        """ Remove the associated model(s) from the parent.
        """
        self_id = getattr(self._parting_model, self._on_self_col)

        def pending_function():
            QueryBuilder.table(self._table_name).where(self._on_other_col, '=', self_id).update({self._on_other_col: None})

        self._parting_model._rel_queue.append(pending_function)

    def add(self, other_model):
        """ Associate the specified model to the parent, doing nothing with the ones already there.

            Args:
                other_model: A model to add. 

            Raises:
                TypeError: If the passed model is not a correct model type.
                ValueError: If the passed model has not yet been saved on the database.
        """
        if not isinstance(other_model, self._model):
            raise TypeError('Cannot add relationship to type {}. Expected a {}.'.format(type(other_model), wrapped_self._base_class))
        if other_model.being_created():
            raise ValueError('Tried to add an unsaved model.')

        other_id = other_model.get_primary()
        self_id = getattr(self._parting_model, self._on_self_col)

        def pending_function():
            QueryBuilder.table(self._table_name).where(other_model.primary_key, '=', other_id).update({self._on_other_col: other_id})
        
        self._parting_model._rel_queue.append(pending_function)

    def add_many(self, other_models):
        """ Associate the specified models to the parent, doing nothing with the ones already there.

            Args:
                other_models: An iterator of models to assign.

            Raises:
                TypeError: If one of the passed model is not a correct model type.
                ValueError: If one of the passed model has not yet been saved on the database. 
        """
        other_models = tuple(other_models)
        conditions = []

        for model in other_models:
            if not isinstance(model, self._model):
                raise TypeError('Cannot add relationship to type {}. Expected a {}.'.format(type(model), wrapped_self._base_class))
            if model.being_created():
                raise ValueError('Tried to add an unsaved model.')

            conditions.append( (model.primary_key, '=', model.get_primary()) )

        self_id = getattr(self._parting_model, self._on_self_col)

        def pending_function():
            QueryBuilder.table(self._table_name).or_where_many(conditions,).update({self._on_other_col: self_id})
        
        self._parting_model._rel_queue.append(pending_function)