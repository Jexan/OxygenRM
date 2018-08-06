import json

from itertools import chain

# A container for models
class ModelContainer():
    def __init__(self, result, model, calculated_models=None):
        self._calculated_models = calculated_models

        if calculated_models:
            self._iteration_done = True
        else:
            self._calculated_models = list()
            self._result = result
            self._model = model 
            self._iteration_done = False

    def __iter__(self):
        for row in chain(self._calculated_models, self._craft_own_result()):
            yield row
        
        self._iteration_done = True
            
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
            model_from_row = self._model(False, **dict(zip(row.keys(), tuple(row)))) 
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
    
    def first(self):
        """ Get the first value of the collection.

            Returns:
                The first model.
        """
        return self.__getitem__(0)

    def first_or_none(self):
        """ Get the first value of the collection or None if empty.

            Returns:
                The first model if exists, else None. 
        """
        try:
            return self.__getitem__(0)
        except IndexError:
            return None

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

    def __repr__(self):
        return self.pretty()

    def __str__(self):
        return self.pretty()