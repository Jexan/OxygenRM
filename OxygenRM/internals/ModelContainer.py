import json

from itertools import chain

# A container for models
class ModelContainer():
    def __init__(self, result=None, model=None, calculated_models=None, pivot_query=None, relations=None):
        self._calculated_models = calculated_models

        if calculated_models:
            self._iteration_done = True
        else:
            self._calculated_models = list()
            self._result = result
            self._model = model 
            self._iteration_done = False
            self._pivot_query = pivot_query
            if relations:
                self._add_relations(relations)

    def __iter__(self):
        for row in chain(self._calculated_models, self._craft_own_result()):
            yield row
        
        self._iteration_done = True
            
    def _add_relations(self, relations):
        self_ids = self.pluck(self._model.primary_key)
        relations = {rel: builder(self_ids).get() for rel, builder in relations.items()}

        for model in self:
            for relation, container in relations.items():
                model.relations_loaded[relation] = container

    def __getitem__(self, index):
        """ Obtain the item nº index of the collection.

            Args:
                index: An nonegative integer.

            Returns:
                The model at position index.
        """
        is_slice = isinstance(index, slice)
        if is_slice:
            wanted_index = index.stop

            if not wanted_index:
                wanted_index = float('inf')
        else:
            wanted_index = index

            if wanted_index < 0:
                wanted_index = float('inf')

        self._make_calculated_models_until(wanted_index)

        if is_slice:
            return ModelContainer(None, None, self._calculated_models[index])
        else:
            return self._calculated_models[index]

    def __delitem__(self, index):
        """ Invoked when del self[index] is called

            Args:
                index: An nonegative integer.
        """
        self._make_calculated_models_until(index)
        del self._calculated_models[index]

    def _craft_own_result(self):
        """ Generate the results from the sql query passed.

            Yields:
                Database result rows.
        """
        if self._iteration_done:
            return

        if callable(self._result):
            self._result = self._result()

        for row in self._result:
            model_from_row = self._model(False, pivot_query=self._pivot_query, **dict(zip(row.keys(), tuple(row)))) 
            self._calculated_models.append(model_from_row)
            yield model_from_row 

    def _make_calculated_models_until(self, wanted_access_index):
        """ Make sure that there's at least n calculated models

            Args:
                wanted_access_index: The number of minimum models to have cached.

            Raises:
                IndexError: If n is grether than the available models
        """
        if self._iteration_done:
            return 

        length = len(self._calculated_models)
        for row in self._craft_own_result():
            length += 1
            if wanted_access_index < length:
                return

        return

    def __len__(self):
        """ Calculate the number of models in the container.
        """
        if self._iteration_done:
            return len(self._calculated_models)
        else:
            return len(list(iter(self)))
    
    def first_or_fail(self):
        """ Get the first value of the collection.

            Returns:
                The first model.
        """
        return self.__getitem__(0)

    def first(self):
        """ Get the first value of the collection or None if empty.

            Returns:
                The first model if exists, else None. 
        """
        try:
            return self.__getitem__(0)
        except IndexError:
            return None

    def find(self, predicate):
        for row in self:
            if predicate(row):
                return row 

    def filter(self, predicate):
        return ModelContainer(calculated_models=filter(predicate, self))

    def to_json(self):
        """ Give the models representation as a JSON structure.

            Returns:
                The JSONified container.
        """
        return json.dumps(list(self.to_dict()))

    def pluck(self, attr):
        """ Get all the values of the given attribute of the models

            Args:
                attr: The models attr as a string.

            Yields:
                The values of every model.attr.
        """
        for row in self:
            yield getattr(row, attr)

    def to_dict(self):
        """ Yield the models as dictionaries.

            Yields:
                The dictionary of field:values of every model.
        """
        for row in self:
            yield row.to_dict()

    def pretty(self):
        """ Get the model pretty printed.

            Return:
                A formatted string showing the collection values and fields
        """
        pretty_str = self._model.__name__.capitalize() + ':\n'

        for index, model_dict in enumerate(self.to_dict(), 1):
            pretty_str +=  '\t' + str(index) + ':\n' 

            for key, value in model_dict.items():
                pretty_str += '\t\t' + key + ': ' + str(value) + '\n'

        return pretty_str

    def load(self, *rels):
        """ Eager load the specified relations for all the models in the container.

            Args:
                *rels: The relations to load.
            
            Returns:
                Self.
        """
        model = self._model
        relations_builders = {}

        if not model:
            raise ValueError('Cannot fetch relations of no model')

        for relation in rels:
            rel_instance = model.get_relation(relation)
            relations_builders[relation] = rel_instance.eager_load_builder()

        self._add_relations(relations_builders)
        return self    

    def __repr__(self):
        return self.pretty()

    def __str__(self):
        return self.pretty()