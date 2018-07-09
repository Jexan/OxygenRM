import json

# A container for models
class ModelContainer():
    def __init__(self, result, model):
        self._result = result
        self._model = model 
        self._calculated_models = []
        self._iteration_done = False

    # An iterator that yields all the rows
    def __iter__(self):
        for row in self._calculated_models:
            yield row

        for row in self._result:
            model_from_row = self._model(**dict(zip(row.keys(), tuple(row)))) 
            self._calculated_models.append(model_from_row)
            yield model_from_row

        self._iteration_done = True
            
    def __getitem__(self, key):
        length = len(self._calculated_models) 
        iterator = iter(self)

        while length < key + 1:
            next(iterator)
            length += 1

        return self._calculated_models[key]
        
    # Returns the first record
    def first(self):
        return self[0]
    
    def to_list(self):
        if self._iteration_done:
            return self._calculated_models
        else:
            return list(self)

    def to_json(self):
        return json.dumps(list(self.to_dict()))

    def pluck(self, attr):
        for row in self:
            yield getattr(row, attr)

    def to_dict(self):
        for row in self:
            yield row.to_dict()

    def pretty(self):
        pretty_str = self._model.__name__.capitalize() + ':\n'

        for index, model_dict in enumerate(self.to_dict(), 1):
            pretty_str +=  '\t' + str(index) + ':\n' 

            for key, value in model_dict.items():
                pretty_str += '\t\t' + key + ': ' + str(value) + '\n'

        return pretty_str