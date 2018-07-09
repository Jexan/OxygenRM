import json

# A container for models
class ModelContainer():
    def __init__(self, result, model):
        self._result = result
        self._model = model 
        self._calculated_models = []
        self._iteration_done = False

    def __iter__(self):
        for row in self._calculated_models:
            yield row

        for row in self._result:
            model_from_row = self._model(**dict(zip(row.keys(), tuple(row)))) 
            self._calculated_models.append(model_from_row)
            yield model_from_row

        self._iteration_done = True
            
    def __getitem__(self, index):
        ''' Obtain the item nº index of the collection.

            Args:
                index: An nonegative integer.

            Returns:
                The model at position index.
        '''
        length = len(self._calculated_models) 
        iterator = iter(self)

        while length < index + 1:
            next(iterator)
            length += 1

        return self._calculated_models[index]
    
    # Returns the first record
    def first(self):
        ''' Get the first value of the collection.

            Returns:
                The first model.
        '''
        return self[0]

    def to_json(self):
        ''' Give the models representation as a JSON structure.

            Returns:
                The JSONified container.
        '''
        return json.dumps(list(self.to_dict()))

    def pluck(self, attr):
        ''' Get all the values of the given attribute of the models

            Args:
                attr: The models attr as a string.

            Yields:
                The values of every model.attr.
        '''
        for row in self:
            yield getattr(row, attr)

    def to_dict(self):
        ''' Yield the models as dictionaries.

            Yields:
                The dictionary of field:values of every model.
        '''
        for row in self:
            yield row.to_dict()

    def pretty(self):
        ''' Get the model pretty printed.

            Return:
                A formatted string showing the collection values and fields
        '''
        pretty_str = self._model.__name__.capitalize() + ':\n'

        for index, model_dict in enumerate(self.to_dict(), 1):
            pretty_str +=  '\t' + str(index) + ':\n' 

            for key, value in model_dict.items():
                pretty_str += '\t\t' + key + ': ' + str(value) + '\n'

        return pretty_str