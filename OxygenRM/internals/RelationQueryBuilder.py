from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.ModelContainer import ModelContainer
import OxygenRM as O

class RelationQueryBuilder(QueryBuilder):
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

        return self._parting_model

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

        return self._parting_model

class HasManyQueryBuilder(RelationQueryBuilder):
    """ A query builder specially designed for Has Many relationships.

        Args:
            target_model: The model class to get as a result.
            parting_model: The model instance to get the related models from.
            self_name: The name of target_model table column to use for the relation.
            other_name:The name of parting_model table column to use for the relation.
    """

    def __init__(self, target_model, parting_model, self_name, other_name):
        super().__init__(target_model.table_name, target_model)

        self._parting_model = parting_model
        self._self_name = self_name
        self._other_name = other_name
        self._table_name = target_model.table_name
        
        self.where(other_name, '=', getattr(parting_model, self_name))

    def reset(self, parting_model):
        super().reset()

        self._parting_model = parting_model
        
        return self.where(self._other_name, '=', getattr(self._parting_model, self._self_name))

    def deassign(self, other_model):
        """ Remove the passed model from the parent, if it is associated.
        """
        self_id = self._parting_model.get_primary()
        other_id = other_model.get_primary()

        def pending_function():
            QueryBuilder.table(self._middle_table).where_many([
                (self._parting_model.primary_key, '=', self_id), 
                (other_model.primary_key, '=', other_id)
            ]).delete()

        self._parting_model._rel_queue.append(pending_function)

        return self._parting_model

    def deassign_all(self):
        """ Remove the associated model(s) from the parent.
        """
        self_id = self._parting_model.get_primary()

        def pending_function():
            QueryBuilder.table(self._table_name).where(self._other_name, '=', self_id).update({self._other_name: None})

        self._parting_model._rel_queue.append(pending_function)

        return self._parting_model

    def add(self, other_model):
        """ Associate the specified model to the parent, doing nothing with the ones already there.

            Args:
                other_model: A model to add. 

            Raises:
                TypeError: If the passed model is not a correct model type.
                ValueError: If the passed model has not yet been saved on the database.
        """
        if not isinstance(other_model, self._model):
            raise TypeError('Cannot add relationship to type {}. Expected a {}.'.format(type(other_model), self._model))
        if other_model.being_created():
            raise ValueError('Tried to add an unsaved model.')

        other_id = other_model.get_primary()
        self_id = getattr(self._parting_model, self._self_name)

        def pending_function():
            QueryBuilder.table(self._table_name).where(other_model.primary_key, '=', other_id).update({self._other_name: other_id})    
        
        self._parting_model._rel_queue.append(pending_function)

        return self._parting_model

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
                raise TypeError('Cannot add relationship to type {}. Expected a {}.'.format(type(model), self._model))
            if model.being_created():
                raise ValueError('Tried to add an unsaved model.')

            conditions.append( (model.primary_key, '=', model.get_primary()) )

        self_id = getattr(self._parting_model, self._self_name)

        def pending_function():
            QueryBuilder.table(self._table_name).or_where_many(conditions).update({self._other_name: self_id})
        
        self._parting_model._rel_queue.append(pending_function)

        return self._parting_model

class BelongsToManyQueryBuilder(RelationQueryBuilder):
    """ A query builder specially designed for Belongs To relationships.

        Args:
            target_model: The model class to get as a result.
            parting_model: The model instance to get the related models from.
            self_name: The name of target_model table column to use for the relation.
            other_name:The name of parting_model table column to use for the relation.
    """
    def _wrap_in_model(self, result):
        pivot_query = None

        if self._pivot:
            pivot_query = self._pivot.where(self._self_name, '=', self._parting_model.get_primary())
            
            def add_model_id(builder, model_id):
                return builder.where(self._other_name, '=', model_id)

            pivot_query.add_model_id = add_model_id
        
        return ModelContainer(result, self._model, pivot_query=pivot_query)

    def __init__(self, target_model, parting_model, self_name, other_name, middle_table, attr, pivot):
        super().__init__(target_model.table_name + ' oxygent', target_model)

        self._parting_model = parting_model
        self._self_name = self_name
        self._other_name = other_name
        self._table_name = target_model.table_name
        self._middle_table = middle_table
        self._attr = attr
        self._pivot = pivot

        self.select('oxygent.*').where(middle_table + '.' + self_name,'=', parting_model.get_primary()).cross_join(middle_table).on(
            'oxygent' + '.' + target_model.primary_key, '=', middle_table + '.' + other_name
        )

    def deassign(self, other_model):
        """ Remove the passed model from the parent, if it is associated.
        """
        self_id = self._parting_model.get_primary()
        other_id = other_model.get_primary()

        def pending_function():
            QueryBuilder.table(self._middle_table).where_many([
                (self._self_name, '=', self_id), 
                (self._other_name, '=', other_id)
            ]).update({self._other_name: None})

        self._parting_model._rel_queue.append(pending_function)

        return self._parting_model

    def deassign_all(self):
        """ Remove the associated model(s) from the parent.
        """
        self_id = self._parting_model.get_primary()

        def pending_function():
            QueryBuilder.table(self._middle_table).where(self._self_name, '=', self_id).delete()

        self._parting_model._rel_queue.append(pending_function)

        return self._parting_model

    # BE CAREFUL ABOUT ADDING ALREADY ADDED RECORDS
    def add(self, other_model):
        """ Associate the specified model to the parent, doing nothing with the ones already there.

            Args:
                other_model: A model to add. 

            Raises:
                TypeError: If the passed model is not a correct model type.
                ValueError: If the passed model has not yet been saved on the database.
        """
        if not isinstance(other_model, self._model):
            raise TypeError('Cannot add relationship to type {}. Expected a {}.'.format(type(other_model), self._model))
        if other_model.being_created():
            raise ValueError('Tried to add an unsaved model.')

        other_id = other_model.get_primary()
        self_id = self._parting_model.get_primary()

        def pending_function():
            O.db.create(self._middle_table, **{self._other_name: other_id, self._self_name: self_id})
        
        self._parting_model._rel_queue.append(pending_function)

        return self._parting_model

    def add_many(self, other_models):
        """ Associate the specified models to the parent, doing nothing with the ones already there.

            Args:
                other_models: An iterator of models to assign.

            Raises:
                TypeError: If one of the passed model is not a correct model type.
                ValueError: If one of the passed model has not yet been saved on the database. 
        """
        self_id = self._parting_model.get_primary()
        other_models = tuple(other_models)
        values = []

        for model in other_models:
            if not isinstance(model, self._model):
                raise TypeError('Cannot add relationship to type {}. Expected a {}.'.format(type(model), self._model))
            if model.being_created():
                raise ValueError('Tried to add an unsaved model.')

            values.append( (self_id, model.get_primary()) )

        def pending_function():
            O.db.create_many(self._middle_table, (self._self_name, self._other_name), values)
        
        self._parting_model._rel_queue.append(pending_function)

        return self._parting_model

    @property
    def pivot(self):
        loaded_pivots = self._parting_model._pivots
        
        if loaded_pivots[self._attr]:
            return loaded_pivots[self._attr]
        
        pivot = self._pivot(**{self._self_name: self._parting_model.get_primary()})
        loaded_pivots[self._attr] = pivot

        return pivot